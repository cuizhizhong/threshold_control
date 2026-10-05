"""受控投稿稿版本；冻结来源不变，活动版本不从 AI 整稿读取。"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
import shutil


VERSION_DIRECTORY = Path('reproducibility/manuscript_versions')
CURRENT_POINTER = VERSION_DIRECTORY / 'current.json'


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


def load_version(root: Path, *, required: bool = False) -> dict | None:
    root = Path(root).resolve()
    pointer = root / CURRENT_POINTER
    if not pointer.is_file():
        if required:
            raise FileNotFoundError('活动稿源指针尚未建立：' + str(pointer))
        return None
    selection = json.loads(pointer.read_text(encoding='utf-8-sig'))
    directory = (root / VERSION_DIRECTORY / selection['version']).resolve()
    if not directory.is_relative_to((root / VERSION_DIRECTORY).resolve()):
        raise ValueError('受控稿源版本越界')
    manifest_path = directory / 'manifest.json'
    if sha(manifest_path) != selection['manifest_sha256']:
        raise RuntimeError('活动稿源清单改变，需重新批准版本')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    for role in ('main', 'supplement'):
        path = (directory / manifest['documents'][role]['file']).resolve()
        if not path.is_relative_to(directory) or sha(path) != manifest['documents'][role]['sha256']:
            raise RuntimeError('受控稿源缺失或改变：' + role)
    for relative, expected in manifest.get('inherited_science_sha256', {}).items():
        source=(root/relative).resolve()
        if not source.is_relative_to(root) or sha(source) != expected:
            raise RuntimeError('继承的已验收科学输出改变：' + relative)
    return {**manifest, '_directory': directory, '_manifest_path': manifest_path}


def version_texts(version: dict) -> tuple[str, str]:
    return tuple((version['_directory'] / version['documents'][role]['file']).read_text(encoding='utf-8-sig')
                 for role in ('main', 'supplement'))


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
                           original_figure_hashes: dict[str, str] | None = None) -> dict:
    """由已整合的本地主稿生成受控来源；只允许新版本目录，不覆盖既有版本。"""
    root = Path(root).resolve()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', version_id):
        raise ValueError('非法版本标识')
    if not math.isfinite(textwidth_bp) or textwidth_bp <= 0:
        raise ValueError('实际打印宽度须为正有限数')
    if not approved_tasks or len(set(approved_tasks)) != len(approved_tasks) or not set(approved_tasks) <= {'A','B','C','D'}:
        raise ValueError('批准任务须为互不重复的A/B/C/D')
    reference=(root/inherited_science).resolve()
    if not reference.is_relative_to(root/'reproducibility/results') or not reference.is_dir():
        raise ValueError('继承科学参照须是项目内明确已有的results目录')
    directory = root / VERSION_DIRECTORY / version_id
    if directory.exists():
        raise FileExistsError('受控稿源目录已存在，不覆盖：' + str(directory))
    pointer = root / CURRENT_POINTER
    if pointer.exists():
        raise FileExistsError('活动指针已存在，请另行显式批准更新，不覆盖')
    names = {'main': 'flatten_curve_analysis_cn.tex', 'supplement': 'flatten_curve_supplement_cn.tex'}
    texts = {role: (root / 'latex' / name).read_text(encoding='utf-8-sig') for role, name in names.items()}
    inventories = {role: inventory(text) for role, text in texts.items()}
    all_labels = inventories['main']['labels'] + inventories['supplement']['labels']
    if len(all_labels) != len(set(all_labels)):
        raise ValueError('正文/补充材料标签重复')
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
        def section(text, begin, end):
            left=text.rfind('\\section',0,text.index('\\label{'+begin+'}'))
            right=text.rfind('\\section',0,text.index('\\label{'+end+'}'))
            return text[left:right]
        old=section(prior,'sec:dominance','sec:discussion')
        current=section((root/'latex'/names['main']).read_bytes().decode('utf-8-sig'),'sec:dominance','sec:discussion')
        if old != current:
            raise RuntimeError('第9节保护段改变，不能冻结为本轮来源')
        protected={'baseline_main_sha256':sha(Path(baseline_main)),
                   'sec9_sha256':hashlib.sha256(current.encode('utf-8')).hexdigest(),
                   'sec9_byte_preserved':True}
    directory.mkdir(parents=True)
    documents = {}
    for role, name in names.items():
        source = root / 'latex' / name
        shutil.copy2(source, directory / name)
        documents[role] = {'file': name, 'sha256': sha(source), 'origin': 'latex/' + name}
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
    manifest_path = directory / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    pointer.write_text(json.dumps({'version': version_id, 'manifest_sha256': sha(manifest_path)}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest
