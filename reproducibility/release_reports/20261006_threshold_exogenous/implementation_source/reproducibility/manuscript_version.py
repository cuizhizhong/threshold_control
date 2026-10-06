"""受控投稿稿版本；冻结来源不变，活动版本不从 AI 整稿读取。"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
from datetime import datetime, timezone
from uuid import uuid4


VERSION_DIRECTORY = Path('reproducibility/manuscript_versions')
CURRENT_POINTER = VERSION_DIRECTORY / 'current.json'

# 本轮获批的唯一第9节过渡：固定整稿和段落哈希，不提供通用保护白名单。
_APPROVED_SEC9_TRANSITION = {
    'schema': 'approved-sec9-introduction-transition-v1',
    'parent_version': '20261005_icu_conditional_link',
    'version': '20261006_threshold_exogenous',
    'baseline_main_sha256': '977f5d2138587ba7329cb27c2f72d6a678de0044f4c81d8bf5871cf5bea6f03b',
    'candidate_main_sha256': 'cfd174f05f7a0f3a92a12097eadee50b7712e066f34c8e15d6102f85f299343c',
    'sec9_before_sha256': '33b0fadae6a60e8e26737daaca911499dd7c8e45c4a35e6300642dfdcc651870',
    'sec9_after_sha256': 'c2606f63e594b8ad072eceace2f0c049da82aaf29bef627dd4d64f8fc46deafa',
    'introduction_before_sha256': 'e156cd0d434f06853abd23f975445d2b1820f1c84c12ac5cdcfdb2f79509586e',
    'introduction_after_sha256': 'cd10d221e7bfb536f02458d1aa42c4a77dabf96950e78e4e8ea761d21d2df5ad',
}
_SEC9_OLD_LAST_SENTENCE = (
    r'本节的阈值仍是设计参数，不据此为各个有效人口推断 ICU 配置；在比例情景中固定 $\theta$'
    ' 相当于固定人均资源与换算系数，不等于固定全市床位总量。'
)
_SEC9_NEW_LAST_SENTENCE = '本节仍将感染阈值作为设计参数。'


def _text_sha(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _sec9(text: str) -> str:
    """原换行逐字提取；锚点缺失或不唯一时拒绝。"""
    for anchor in ('sec:dominance', 'sec:discussion'):
        if text.count('\\label{' + anchor + '}') != 1:
            raise ValueError('第9节保护锚点缺失或重复：' + anchor)
    left = text.rfind('\\section', 0, text.index('\\label{sec:dominance}'))
    right = text.rfind('\\section', 0, text.index('\\label{sec:discussion}'))
    if left < 0 or right <= left:
        raise ValueError('第9节保护段边界无效')
    return text[left:right]


def _sec9_intro(section: str) -> str:
    start = section.index('\\label{sec:dominance}') + len('\\label{sec:dominance}')
    end = section.find('\\subsection', start)
    if end < 0:
        raise ValueError('第9节引言末端锚点缺失')
    return section[start:end]


def _check_sec9_transition(record: dict, old: str, new: str,
                           *, version_id: str, baseline_sha256: str,
                           candidate_sha256: str) -> None:
    if record != _APPROVED_SEC9_TRANSITION or version_id != record.get('version'):
        raise RuntimeError('第9节过渡不是本轮明确批准的固定修订')
    if baseline_sha256 != record['baseline_main_sha256'] or candidate_sha256 != record['candidate_main_sha256']:
        raise RuntimeError('第9节获批过渡的旧新整稿哈希不符')
    if _text_sha(old) != record['sec9_before_sha256'] or _text_sha(new) != record['sec9_after_sha256']:
        raise RuntimeError('第9节获批过渡的旧新保护段哈希不符')
    old_intro, new_intro = _sec9_intro(old), _sec9_intro(new)
    if (_text_sha(old_intro) != record['introduction_before_sha256'] or
            _text_sha(new_intro) != record['introduction_after_sha256']):
        raise RuntimeError('第9节获批过渡的旧新引言哈希不符')
    if old_intro.count(_SEC9_OLD_LAST_SENTENCE) != 1 or new_intro.count(_SEC9_NEW_LAST_SENTENCE) != 1:
        raise RuntimeError('第9节获批末句缺失或重复')
    if old.replace(_SEC9_OLD_LAST_SENTENCE, _SEC9_NEW_LAST_SENTENCE, 1) != new:
        raise RuntimeError('第9节除获批引言末句之外的内容改变')


def threshold_exogenous_sec9_transition(baseline_main: Path, candidate_main: Path) -> dict:
    """仅返回经整稿及段落哈希验证的本轮批准；不创建版本或改变指针。"""
    prior = Path(baseline_main).read_bytes().decode('utf-8-sig')
    current = Path(candidate_main).read_bytes().decode('utf-8-sig')
    record = dict(_APPROVED_SEC9_TRANSITION)
    _check_sec9_transition(record, _sec9(prior), _sec9(current),
                          version_id=record['version'], baseline_sha256=sha(Path(baseline_main)),
                          candidate_sha256=sha(Path(candidate_main)))
    return record


def _version_directory(root: Path, version_id: str) -> Path:
    if not re.fullmatch(r'[A-Za-z0-9_-]+', version_id):
        raise ValueError('非法版本标识')
    directory = (root / VERSION_DIRECTORY / version_id).resolve()
    if not directory.is_relative_to((root / VERSION_DIRECTORY).resolve()):
        raise ValueError('受控稿源版本越界')
    return directory


def _atomic_json(path: Path, value: dict) -> None:
    """在同一文件系统暂存并原子替换；源文件写入不用于绕过版本保护。"""
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                     prefix=path.name + '.', suffix='.tmp', delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(text: str) -> dict:
    figures = []
    tables = []
    for kind, target in [('figure', figures), ('table', tables)]:
        for match in re.finditer(r'\\begin\{' + kind + r'\}(.*?)\\end\{' + kind + r'\}', text, re.S):
            labels = re.findall(r'\\label\{([^}]+)\}', match[1])
            if not labels:
                raise ValueError(f'{kind} 没有稳定标签')
            item = {'label': labels[0], 'aliases': labels}
            if kind == 'figure':
                images = re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', match[1])
                if len(images) != 1:
                    raise ValueError('每个正式图需一个明确资产路径：' + labels[0])
                relative = Path(images[0].removeprefix('figures/'))
                if relative.is_absolute() or '..' in relative.parts:
                    raise ValueError('图件路径越界：' + images[0])
                item['image'] = relative.as_posix()
            target.append(item)
    labels = re.findall(r'\\label\{([^}]+)\}', text)
    if len(set(labels)) != len(labels):
        raise ValueError('受控稿源含重复标签')
    return {'figures': figures, 'tables': tables, 'labels': labels}


def load_version(root: Path, *, required: bool = False, version_id: str | None = None,
                 expected_manifest_sha256: str | None = None) -> dict | None:
    """默认读取活动选择；显式候选必须同时锁定版本和清单哈希，不改变活动指针。"""
    root = Path(root).resolve()
    if version_id is not None:
        if not isinstance(expected_manifest_sha256, str) or not re.fullmatch(r'[0-9a-f]{64}', expected_manifest_sha256):
            raise ValueError('显式稿源读取须给出有效的expected_manifest_sha256')
        return _validate_version(root, version_id, expected_manifest_sha256)
    if expected_manifest_sha256 is not None:
        raise ValueError('显式清单哈希须与version_id共同给出')
    pointer = root / CURRENT_POINTER
    if not pointer.is_file():
        if required:
            raise FileNotFoundError('活动稿源指针尚未建立：' + str(pointer))
        return None
    selection = json.loads(pointer.read_text(encoding='utf-8-sig'))
    return _validate_version(root, selection['version'], selection['manifest_sha256'])


def _validate_version(root: Path, version_id: str, manifest_sha256: str,
                      *, check_origins: bool = False) -> dict:
    directory = _version_directory(root, version_id)
    manifest_path = directory / 'manifest.json'
    if sha(manifest_path) != manifest_sha256:
        raise RuntimeError('活动稿源清单改变，需重新批准版本')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    if manifest['version'] != version_id:
        raise RuntimeError('受控稿源版本标识与清单不一致')
    for role in ('main', 'supplement'):
        path = (directory / manifest['documents'][role]['file']).resolve()
        if not path.is_relative_to(directory) or sha(path) != manifest['documents'][role]['sha256']:
            raise RuntimeError('受控稿源缺失或改变：' + role)
        if inventory(path.read_text(encoding='utf-8-sig')) != manifest['inventory'][role]:
            raise RuntimeError('受控稿源标签/资产清单改变：' + role)
        if check_origins:
            origin = (root / manifest['documents'][role]['origin']).resolve()
            if not origin.is_relative_to(root) or sha(origin) != manifest['documents'][role]['sha256']:
                raise RuntimeError('受控稿源的本地来源改变：' + role)
    bibliography = manifest.get('bibliography')
    if bibliography is not None:
        path = (directory / bibliography['file']).resolve()
        if not path.is_relative_to(directory) or not path.is_file() or sha(path) != bibliography['sha256']:
            raise RuntimeError('受控文献库缺失或改变')
        if check_origins:
            origin = (root / bibliography['origin']).resolve()
            if not origin.is_relative_to(root) or not origin.is_file() or sha(origin) != bibliography['sha256']:
                raise RuntimeError('受控文献库的本地来源改变')
    script = manifest.get('build_script')
    if script is not None:
        path = (directory / script['file']).resolve()
        if not path.is_relative_to(directory) or not path.is_file() or sha(path) != script['sha256']:
            raise RuntimeError('受控编译脚本缺失或改变')
        if check_origins:
            origin = (root / script['origin']).resolve()
            if not origin.is_relative_to(root) or not origin.is_file() or sha(origin) != script['sha256']:
                raise RuntimeError('受控编译脚本的本地来源改变')
    protected = manifest.get('protected_previous_revision', {})
    transition = protected.get('approved_sec9_transition')
    if transition is not None:
        if transition != _APPROVED_SEC9_TRANSITION or version_id != transition['version']:
            raise RuntimeError('第9节过渡不是本轮明确批准的固定修订')
        main = (directory / manifest['documents']['main']['file']).read_bytes().decode('utf-8-sig')
        if (manifest['documents']['main']['sha256'] != transition['candidate_main_sha256'] or
                protected.get('baseline_main_sha256') != transition['baseline_main_sha256'] or
                _text_sha(_sec9(main)) != transition['sec9_after_sha256'] or
                _text_sha(_sec9_intro(_sec9(main))) != transition['introduction_after_sha256'] or
                protected.get('sec9_byte_preserved') is not False or
                protected.get('sec9_body_byte_preserved') is not True):
            raise RuntimeError('第9节获批过渡与受控快照不一致')
    for relative, expected in manifest.get('inherited_science_sha256', {}).items():
        source=(root/relative).resolve()
        if not source.is_relative_to(root) or sha(source) != expected:
            raise RuntimeError('继承的已验收科学输出改变：' + relative)
    for image, expected in manifest.get('inherited_figure_sha256', {}).items():
        source = (root / 'latex/figures' / image).resolve()
        if not source.is_relative_to((root / 'latex/figures').resolve()) or sha(source) != expected:
            raise RuntimeError('原正式图件改变：' + image)
    return {**manifest, '_directory': directory, '_manifest_path': manifest_path}


def version_texts(version: dict) -> tuple[str, str]:
    return tuple((version['_directory'] / version['documents'][role]['file']).read_text(encoding='utf-8-sig')
                 for role in ('main', 'supplement'))


def version_bibliography(version: dict) -> Path | None:
    """旧版本没有文献快照时返回None；新版本只返回哈希一致的受控文献库。"""
    item = version.get('bibliography')
    if item is None:
        return None
    directory = Path(version['_directory']).resolve()
    path = (directory / item['file']).resolve()
    if not path.is_relative_to(directory) or not path.is_file() or sha(path) != item['sha256']:
        raise RuntimeError('受控文献库缺失或改变')
    return path


def version_build_script(version: dict) -> Path | None:
    """旧版本无脚本快照时返回None；新版本只使用哈希一致的编译入口。"""
    item = version.get('build_script')
    if item is None:
        return None
    directory = Path(version['_directory']).resolve()
    path = (directory / item['file']).resolve()
    if not path.is_relative_to(directory) or not path.is_file() or sha(path) != item['sha256']:
        raise RuntimeError('受控编译脚本缺失或改变')
    return path


def expected_figures(root: Path, main_text: str | None = None) -> list[dict]:
    version = load_version(root)
    if version:
        expected = version['inventory']['main']['figures']
        if main_text is not None and inventory(main_text)['figures'] != expected:
            raise RuntimeError('稿件图标签/路径与批准版本不一致')
        return expected
    text = main_text if main_text is not None else (Path(root) / 'latex/flatten_curve_analysis_cn.tex').read_text(encoding='utf-8-sig')
    return inventory(text)['figures']


def report_directory(root: Path, parent: Path) -> Path:
    """新发布记录一运行一目录；旧根清单不改写。"""
    return Path(root) / 'reproducibility/release_reports' / Path(parent).name / 'publication'


def freeze_current_version(root: Path, version_id: str, *, approved_tasks: list[str],
                           textwidth_bp: float,
                           baseline_main: Path | None = None,
                           inherited_science: str = 'reproducibility/results/20261003_release_final',
                           original_figure_hashes: dict[str, str] | None = None,
                           source_paths: dict[str, Path] | None = None,
                           activate: bool = True,
                           generated_figure_labels: list[str] | None = None,
                           publication_cost_digits: int | None = None,
                           bibliography_path: Path | None = None,
                           build_script_path: Path | None = None,
                           approved_sec9_transition: dict | None = None) -> dict:
    """由已整合的本地主稿生成受控来源；只允许新版本目录，不覆盖既有版本。"""
    root = Path(root).resolve()
    directory = _version_directory(root, version_id)
    if not math.isfinite(textwidth_bp) or textwidth_bp <= 0:
        raise ValueError('实际打印宽度须为正有限数')
    if not approved_tasks or len(set(approved_tasks)) != len(approved_tasks) or not set(approved_tasks) <= {'A','B','C','D'}:
        raise ValueError('批准任务须为互不重复的A/B/C/D')
    reference=(root/inherited_science).resolve()
    if not reference.is_relative_to(root/'reproducibility/results') or not reference.is_dir():
        raise ValueError('继承科学参照须是项目内明确已有的results目录')
    if directory.exists():
        raise FileExistsError('受控稿源目录已存在，不覆盖：' + str(directory))
    pointer = root / CURRENT_POINTER
    if activate and pointer.exists():
        raise FileExistsError('活动指针已存在，请另行显式批准更新，不覆盖')
    names = {'main': 'flatten_curve_analysis_cn.tex', 'supplement': 'flatten_curve_supplement_cn.tex'}
    if source_paths is not None and set(source_paths) != set(names):
        raise ValueError('显式稿源须同时给出main与supplement')
    sources = {role: (Path(source_paths[role]) if source_paths is not None else root / 'latex' / name)
               for role, name in names.items()}
    for role, path in sources.items():
        path = (root / path).resolve() if not path.is_absolute() else path.resolve()
        if not path.is_relative_to(root) or path.is_relative_to(root / 'ai') or path.is_relative_to(root / 'joint_control'):
            raise ValueError('显式稿源须在项目内本地工作副本，不得取AI整稿或冻结包：' + role)
        if not path.is_file():
            raise FileNotFoundError('本地稿源缺失：' + str(path))
        sources[role] = path
    bibliography_source = None
    if bibliography_path is not None:
        path = Path(bibliography_path)
        path = (root / path).resolve() if not path.is_absolute() else path.resolve()
        if not path.is_relative_to(root) or path.is_relative_to(root / 'ai') or path.is_relative_to(root / 'joint_control'):
            raise ValueError('显式文献库须在项目内本地工作副本，不得取AI来源或冻结包')
        if not path.is_file():
            raise FileNotFoundError('本地文献库缺失：' + str(path))
        bibliography_source = path
    build_script_source = None
    if build_script_path is not None:
        path = Path(build_script_path)
        path = (root / path).resolve() if not path.is_absolute() else path.resolve()
        if not path.is_relative_to(root) or path.is_relative_to(root / 'ai') or path.is_relative_to(root / 'joint_control'):
            raise ValueError('显式编译脚本须在项目内本地工作副本，不得取AI来源或冻结包')
        if not path.is_file():
            raise FileNotFoundError('本地编译脚本缺失：' + str(path))
        build_script_source = path
    if approved_sec9_transition is not None:
        if baseline_main is None:
            raise ValueError('获批第9节过渡须同时给出旧稿基准')
        previous = load_version(root, required=True)
        if (approved_sec9_transition != _APPROVED_SEC9_TRANSITION or
                previous['version'] != approved_sec9_transition.get('parent_version') or
                version_id != approved_sec9_transition.get('version')):
            raise RuntimeError('获批第9节过渡的父版本或目标版本不符')
    texts = {role: path.read_text(encoding='utf-8-sig') for role, path in sources.items()}
    inventories = {role: inventory(text) for role, text in texts.items()}
    all_labels = inventories['main']['labels'] + inventories['supplement']['labels']
    if len(all_labels) != len(set(all_labels)):
        raise ValueError('正文/补充材料标签重复')
    if generated_figure_labels is not None:
        figures = {item['label'] for item in inventories['main']['figures']}
        if len(set(generated_figure_labels)) != len(generated_figure_labels) or not set(generated_figure_labels) <= figures:
            raise ValueError('生成图标签须是互不重复的正式图子集')
        inherited = set(original_figure_hashes or {})
        for item in inventories['main']['figures']:
            if item['label'] not in generated_figure_labels and item['image'] not in inherited:
                raise ValueError('未生成的正式图须有继承哈希：' + item['label'])
    if publication_cost_digits is not None and (type(publication_cost_digits) is not int or publication_cost_digits != 4):
        raise ValueError('新增出版成本精度仅支持四位小数')
    for image, expected in (original_figure_hashes or {}).items():
        if image not in {item['image'] for item in inventories['main']['figures']}:
            raise RuntimeError('原正式图件引用丢失：'+image)
        if sha(root / 'latex/figures' / image) != expected:
            raise RuntimeError('原正式图件改变：' + image)
    protected = {}
    if baseline_main is not None:
        prior=Path(baseline_main).read_bytes().decode('utf-8-sig')
        prior_inventory=inventory(prior)
        if not set(prior_inventory['labels']) <= set(inventories['main']['labels']):
            raise RuntimeError('已有标签丢失，不能冻结为本轮来源')
        current_images={item['label']:item['image'] for item in inventories['main']['figures']}
        if any(current_images.get(item['label']) != item['image'] for item in prior_inventory['figures']):
            raise RuntimeError('原正式图标签/资产对应改变')
        old = _sec9(prior)
        current = _sec9(sources['main'].read_bytes().decode('utf-8-sig'))
        if old != current:
            if approved_sec9_transition is None:
                raise RuntimeError('第9节保护段改变，不能冻结为本轮来源')
            _check_sec9_transition(approved_sec9_transition, old, current,
                                  version_id=version_id, baseline_sha256=sha(Path(baseline_main)),
                                  candidate_sha256=sha(sources['main']))
        elif approved_sec9_transition is not None:
            raise RuntimeError('未发生获批第9节末句过渡，拒绝附加批准记录')
        protected={'baseline_main_sha256':sha(Path(baseline_main)),
                   'sec9_sha256':hashlib.sha256(current.encode('utf-8')).hexdigest(),
                   'sec9_byte_preserved':old == current}
        if approved_sec9_transition is not None:
            protected['sec9_body_byte_preserved'] = True
            protected['approved_sec9_transition'] = dict(approved_sec9_transition)
    directory.mkdir(parents=True)
    documents = {}
    for role, name in names.items():
        source = sources[role]
        shutil.copy2(source, directory / name)
        documents[role] = {'file': name, 'sha256': sha(source), 'origin': source.relative_to(root).as_posix()}
    manifest = {'schema': 'controlled-manuscript-v1', 'version': version_id, 'documents': documents,
                'inventory': inventories, 'approved_tasks': approved_tasks, 'textwidth_bp': textwidth_bp,
                'inherited_science_reference': inherited_science,
                'inherited_science_sha256': {p.relative_to(root).as_posix(): sha(p)
                    for p in (root / inherited_science).rglob('*')
                    if p.is_file() and p.suffix in {'.json', '.csv', '.npz'}},
                'inherited_figure_sha256': original_figure_hashes or {},
                'protected_previous_revision':protected,
                'provenance': '本轮本地正式稿的受控快照，不从 AI 候选整稿替换；原冻结包不改。',
                'evidence_boundary': '版本与来源锁定不是新的科学验收或证明认证。'}
    if generated_figure_labels is not None:
        manifest['generated_figure_labels'] = generated_figure_labels
    if publication_cost_digits is not None:
        manifest['publication_cost_digits'] = publication_cost_digits
    if bibliography_source is not None:
        destination = directory / 'references.bib'
        shutil.copy2(bibliography_source, destination)
        expected = sha(bibliography_source)
        if sha(destination) != expected:
            raise RuntimeError('受控文献库复制后哈希不一致')
        manifest['bibliography'] = {'file': 'references.bib', 'sha256': expected,
                                    'origin': bibliography_source.relative_to(root).as_posix()}
    if build_script_source is not None:
        destination = directory / 'build_paper.ps1'
        shutil.copy2(build_script_source, destination)
        expected = sha(build_script_source)
        if sha(destination) != expected:
            raise RuntimeError('受控编译脚本复制后哈希不一致')
        manifest['build_script'] = {'file': 'build_paper.ps1', 'sha256': expected,
                                    'origin': build_script_source.relative_to(root).as_posix()}
    if approved_sec9_transition is not None:
        manifest['approved_revision'] = {
            'source': 'ai/icu', 'parent_version': approved_sec9_transition['parent_version'],
            'description': '用户批准的完整正文、补充材料与编译入口导入；科学结果继承，不重新计算。'}
        manifest['provenance'] = '由用户批准的ai/icu完整源码形成本地候选工作副本，再锁定受控快照；原冻结包不改。'
    manifest_path = directory / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    if activate:
        activate_version(root, version_id, expected_current_sha256=None,
                         expected_manifest_sha256=sha(manifest_path),
                         approval_reason='首次受控版本创建；默认仍拒绝覆盖已有活动指针。',
                         approved_sec9_transition=approved_sec9_transition)
    return manifest


def activate_version(root: Path, version_id: str, *, expected_current_sha256: str | None,
                     expected_manifest_sha256: str, approval_reason: str,
                     approved_sec9_transition: dict | None = None) -> dict:
    """显式批准版本；核对旧指针与新快照，保留旧选择及批准回执后原子切换。"""
    root = Path(root).resolve()
    if not isinstance(approval_reason, str) or not approval_reason.strip():
        raise ValueError('批准切换须记录明确原因')
    directory = _version_directory(root, version_id)
    pointer = root / CURRENT_POINTER
    pointer.parent.mkdir(parents=True, exist_ok=True)
    lock = pointer.with_suffix('.activation.lock')
    try:
        stream = lock.open('x', encoding='utf-8')
    except FileExistsError as error:
        raise RuntimeError('另一次版本批准正在进行，活动指针未改') from error
    try:
        stream.write(str(os.getpid()) + '\n')
        stream.close()
        actual = sha(pointer) if pointer.exists() else None
        if actual != expected_current_sha256:
            raise RuntimeError('活动指针哈希与批准基准不符，拒绝覆盖')
        previous_bytes = pointer.read_bytes() if pointer.exists() else None
        previous = load_version(root) if pointer.exists() else None
        target = _validate_version(root, version_id, expected_manifest_sha256, check_origins=True)
        if previous:
            prior_main, _ = version_texts(previous)
            new_main, _ = version_texts(target)
            old_inventory, new_inventory = inventory(prior_main), inventory(new_main)
            if not set(old_inventory['labels']) <= set(new_inventory['labels']):
                raise RuntimeError('已有标签丢失，拒绝批准切换')
            images = {item['label']: item['image'] for item in new_inventory['figures']}
            if any(images.get(item['label']) != item['image'] for item in old_inventory['figures']):
                raise RuntimeError('原正式图标签/资产对应改变，拒绝批准切换')
            # version_texts为生成器统一换行；保护验证仍逐字读取冻结文件原换行。
            prior_raw = (previous['_directory'] / previous['documents']['main']['file']).read_bytes().decode('utf-8-sig')
            new_raw = (target['_directory'] / target['documents']['main']['file']).read_bytes().decode('utf-8-sig')
            old_sec9, new_sec9 = _sec9(prior_raw), _sec9(new_raw)
            if old_sec9 != new_sec9:
                stored = target.get('protected_previous_revision', {}).get('approved_sec9_transition')
                if (approved_sec9_transition is None or stored != approved_sec9_transition or
                        previous['version'] != approved_sec9_transition.get('parent_version')):
                    raise RuntimeError('第9节保护段改变，拒绝批准切换；须显式给出本轮固定批准')
                _check_sec9_transition(approved_sec9_transition, old_sec9, new_sec9,
                                      version_id=version_id,
                                      baseline_sha256=previous['documents']['main']['sha256'],
                                      candidate_sha256=target['documents']['main']['sha256'])
            elif approved_sec9_transition is not None:
                raise RuntimeError('未发生获批第9节末句过渡，拒绝附加批准记录')
        elif approved_sec9_transition is not None:
            raise RuntimeError('获批第9节过渡须从指定父版本批准切换')
        approval_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '_' + uuid4().hex
        approvals = pointer.parent / 'approvals'
        approvals.mkdir(exist_ok=True)
        backup = approvals / (approval_id + '.previous.json')
        if previous_bytes is not None:
            with backup.open('xb') as saved:
                saved.write(previous_bytes)
        selection = {'version': version_id, 'manifest_sha256': expected_manifest_sha256}
        receipt = {'schema': 'controlled-manuscript-activation-v1', 'approval_id': approval_id,
                   'approval_reason': approval_reason.strip(), 'previous_pointer_sha256': actual,
                   'previous_pointer_backup': backup.relative_to(root).as_posix() if previous_bytes is not None else None,
                   'selection': selection, 'status': 'validated',
                   'evidence_boundary': '稿源批准不代表新增科学或排版验收。'}
        if approved_sec9_transition is not None:
            receipt['approved_sec9_transition'] = dict(approved_sec9_transition)
        receipt_path = approvals / (approval_id + '.json')
        _atomic_json(receipt_path, receipt)
        # 独占锁保护本接口的并发批准；再核对防止外部写入期间发生覆盖。
        if (sha(pointer) if pointer.exists() else None) != expected_current_sha256:
            raise RuntimeError('批准期间活动指针改变，拒绝覆盖')
        _atomic_json(pointer, selection)
        receipt['status'] = 'activated'
        receipt['current_pointer_sha256'] = sha(pointer)
        _atomic_json(receipt_path, receipt)
        return {**receipt, '_receipt_path': receipt_path, '_directory': directory}
    finally:
        stream.close()
        lock.unlink(missing_ok=True)
