"""只继承原科学验收的稿件修订；不执行拟合、求解、扫描或绘图。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import traceback

from bootstrap import ROOT, dump, sha
from manuscript_version import (CURRENT_POINTER, activate_version, freeze_current_version,
                                inventory, load_version, version_bibliography, version_texts)

VERSION_ID = '20261005_icu_conditional_link'
BASE_VERSION = '20261005_sec7_v2_refinement'
MAIN = 'flatten_curve_analysis_cn'
SUPPLEMENT = 'flatten_curve_supplement_cn'
SOURCE_NAMES = (MAIN + '.tex', SUPPLEMENT + '.tex', 'references.bib',
                'elegantpaper.cls', 'build_paper.ps1')


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8-sig'))


def safe_path(root: Path, path: Path, *, within: Path | None = None) -> Path:
    """核对真实路径及每一级链接，防止审阅/发布路径越界。"""
    root = root.resolve()
    unresolved = path if path.is_absolute() else root / path
    target = unresolved.resolve()
    boundary = (within or root).resolve()
    if not target.is_relative_to(boundary):
        raise ValueError('稿件修订路径越界：' + str(path))
    probe = unresolved
    while probe != root and probe != probe.parent:
        if probe.is_symlink() or (hasattr(probe, 'is_junction') and probe.is_junction()):
            raise ValueError('稿件修订不接受链接：' + str(probe))
        probe = probe.parent
    return target


def require_hash(root: Path, path: Path, expected: str, records: dict | None = None) -> Path:
    path = safe_path(root, path)
    if not path.is_file() or sha(path) != expected:
        raise RuntimeError('继承/保护文件缺失或改变：' + str(path))
    if records is not None:
        records[path.relative_to(root.resolve()).as_posix()] = expected
    return path


def validate_inheritance(root: Path, parent: Path) -> dict:
    """按旧记录验证旧身份；绝不套用新稿身份，也不改写或重新选择旧运行。"""
    root = root.resolve()
    parent = safe_path(root, parent, within=root / 'reproducibility/runs')
    selection_path = parent / 'accepted_runs.json'
    selection = read(selection_path)
    if selection.get('schema') != 'accepted-runs-v1' or len(selection.get('runs', [])) != 2:
        raise RuntimeError('必须指定原已验收的两轮选择清单')
    publication_directory = root / 'reproducibility/release_reports' / parent.name / 'publication'
    publication_path = publication_directory / 'publication_manifest.json'
    publication = read(publication_path)
    if publication.get('passed') is not True or publication.get('formal_files_published') is not True:
        raise RuntimeError('继承来源没有完成原稿发布验收')
    if publication.get('accepted_runs_manifest_sha256') != sha(selection_path):
        raise RuntimeError('原发布与选择清单不一致')
    repeat_path = parent / 'repeatability.json'
    repeat = read(repeat_path)
    names = [item['name'] for item in selection['runs']]
    if (repeat.get('passed') is not True or repeat.get('run_names') != names or
            repeat.get('run_identity_check', {}).get('passed') is not True or
            publication.get('accepted_run_names') != names):
        raise RuntimeError('原双跑身份或重复性未通过')
    records = {p.relative_to(root).as_posix(): sha(p)
               for p in (selection_path, publication_path, repeat_path)}
    source_versions = []
    run_directories = []
    for item in selection['runs']:
        run = safe_path(root, parent / item['directory'], within=parent)
        if run.parent != parent or run.name != item['name']:
            raise RuntimeError('原科学运行目录身份异常')
        run_directories.append(run)
        for relative, expected in item['report_files_sha256'].items():
            require_hash(root, safe_path(root, run / relative, within=run), expected, records)
        report = read(run / 'run_report.json')
        ledger = read(run / 'postprocessing_manifest.json')
        validation = read(run / 'joint_extra/validation.json')
        version_id = report.get('manuscript_version')
        if version_id != BASE_VERSION or ledger.get('manuscript_version') != version_id:
            raise RuntimeError('本轮只继承指定旧稿验收，不接受重新包装的科学身份')
        if report.get('passed') is not True or validation.get('passed') is not True:
            raise RuntimeError('原科学验收未通过')
        if set(ledger['calculation_phase']['approved_tasks']) != set('ABCD') or not all(
                validation.get('tasks', {}).get(task, {}).get('passed') is True for task in 'ABCD'):
            raise RuntimeError('原A–D逐任务验收不完整')
        source_manifest = root / 'reproducibility/manuscript_versions' / version_id / 'manifest.json'
        old_version = load_version(root, required=True, version_id=version_id,
                                   expected_manifest_sha256=ledger['manuscript_manifest_sha256'])
        records[source_manifest.relative_to(root).as_posix()] = sha(source_manifest)
        source_versions.append(version_id)
        for doc in old_version['documents'].values():
            require_hash(root, old_version['_directory'] / doc['file'], doc['sha256'], records)
        phase = ledger['calculation_phase']
        if (set(phase['calculation_source_hashes']) != {'core.py', 'run.py', 'validation.py', 'acceptance.json'} or
                set(phase['input_sources']) != {'baseline', 'xian_reference'}):
            raise RuntimeError('原科学源码及参数来源清单不完整')
        for name, expected in phase['calculation_source_hashes'].items():
            require_hash(root, root / 'reproducibility/joint_extra' / name, expected, records)
        for source in phase['input_sources'].values():
            require_hash(root, Path(source['path']), source['sha256'], records)
        science = run / 'joint_extra'
        actual = {p.name for p in science.iterdir() if p.is_file()}
        if actual != set(phase['scientific_results_sha256']):
            raise RuntimeError('原科学输出文件集合改变')
        for name, expected in phase['scientific_results_sha256'].items():
            require_hash(root, safe_path(root, science / name, within=science), expected, records)
        for artifact in publication['scientific_artifacts'][item['name']]:
            require_hash(root, safe_path(root, run / artifact['file'], within=run), artifact['sha256'], records)
    collection_path = publication_directory / 'collection_manifest.json'
    collection = read(collection_path)
    if (collection.get('passed') is not True or
            collection.get('accepted_runs_manifest_sha256') != sha(selection_path)):
        raise RuntimeError('原未取整汇集记录未通过或不是同一选择')
    records[collection_path.relative_to(root).as_posix()] = sha(collection_path)
    for item in collection['files']:
        require_hash(root, root / item['file'], item['sha256'], records)
        # 活动文案/registry/发布代码允许在后续修订改变；其原始版本由汇集副本锁定。
        # 旧运行和未取整结果本身则仍必须与原汇集的来源哈希一致。
        origin = safe_path(root, root / item['source'])
        if origin.is_relative_to(parent) or origin.is_relative_to(root / 'reproducibility/results'):
            require_hash(root, origin, item['sha256'], records)
    return {'passed': True, 'run_directory': str(parent), 'original_manuscript_version': BASE_VERSION,
            'original_run_names': names, 'joint_extra_directory': str(run_directories[0] / 'joint_extra'),
            'accepted_runs_sha256': sha(selection_path), 'files_sha256': dict(sorted(records.items())),
            'scientific_calculation_reexecuted': False,
            'scope': '核对原科学验收身份与未取整文件，不重新执行科学计算。'}


def json_ready(value):
    """批准接口含Path的内部定位字段；记录时递归转路径字符串，不丢批准证据。"""
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return value


def _output(root: Path, output: Path) -> Path:
    return safe_path(root, output, within=root / 'reproducibility/release_reports')


def _normalized(text: str) -> str:
    return text.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')


def _write_like(path: Path, text: str, original: bytes) -> None:
    """候选生成保留原稿换行；补充材料直接复制，避免无关字节变化。"""
    newline = '\r\n' if b'\r\n' in original else '\n'
    encoding = 'utf-8-sig' if original.startswith(b'\xef\xbb\xbf') else 'utf-8'
    with path.open('w', encoding=encoding, newline=newline) as stream:
        stream.write(_normalized(text))


def stage(root: Path, output: Path, science_source: Path, version_id: str = VERSION_ID) -> dict:
    from icu_revision_text import candidate_texts, assert_protected_unchanged
    root = root.resolve()
    output = _output(root, output)
    if output.exists():
        raise FileExistsError('候选目录已存在，拒绝覆盖：' + str(output))
    current = load_version(root, required=True)
    if current['version'] != BASE_VERSION or version_id != VERSION_ID:
        raise RuntimeError('ICU修订须从已批准的第7节v2版本开始')
    for role, name in [('main', MAIN + '.tex'), ('supplement', SUPPLEMENT + '.tex')]:
        require_hash(root, root / 'latex' / name, current['documents'][role]['sha256'])
    inheritance = validate_inheritance(root, science_source)
    output.mkdir(parents=True)
    baseline = output / 'baseline'
    candidate = output / 'candidate'
    baseline.mkdir(); candidate.mkdir()
    for name in SOURCE_NAMES:
        shutil.copy2(root / 'latex' / name, baseline / name)
    shutil.copy2(root / 'AGENTS.md', baseline / 'AGENTS.md')
    before_main = (baseline / (MAIN + '.tex')).read_text(encoding='utf-8-sig')
    before_si = (baseline / (SUPPLEMENT + '.tex')).read_text(encoding='utf-8-sig')
    main, bibliography, merge = candidate_texts(root, before_main,
                                                (baseline / 'references.bib').read_text(encoding='utf-8-sig'))
    assert_protected_unchanged(before_main, main, before_si, before_si)
    _write_like(candidate / (MAIN + '.tex'), main, (baseline / (MAIN + '.tex')).read_bytes())
    _write_like(candidate / 'references.bib', bibliography, (baseline / 'references.bib').read_bytes())
    shutil.copy2(baseline / (SUPPLEMENT + '.tex'), candidate / (SUPPLEMENT + '.tex'))
    figures = {item['image']: sha(root / 'latex/figures' / item['image'])
               for item in inventory(main)['figures']}
    frozen = root / 'joint_control/threshold_control_reproducible_release_20261002'
    protected = {p.relative_to(root).as_posix(): sha(p) for p in frozen.rglob('*') if p.is_file()}
    protected.update(current['inherited_science_sha256'])
    protected.update(inheritance['files_sha256'])
    for image, digest in figures.items():
        protected['latex/figures/' + image] = digest
    for relative, digest in read(science_source / 'accepted_runs.json')['shared_identity']['raw_inputs'].items():
        require_hash(root, root / relative, digest, protected)
    previous_pointer_hash = sha(root / CURRENT_POINTER)
    manifest = freeze_current_version(root, version_id, approved_tasks=current['approved_tasks'],
        textwidth_bp=current['textwidth_bp'], baseline_main=baseline / (MAIN + '.tex'),
        inherited_science=current['inherited_science_reference'], original_figure_hashes=figures,
        source_paths={'main': candidate / (MAIN + '.tex'), 'supplement': candidate / (SUPPLEMENT + '.tex')},
        bibliography_path=candidate / 'references.bib', activate=False,
        generated_figure_labels=current.get('generated_figure_labels'),
        publication_cost_digits=current.get('publication_cost_digits'))
    manifest_path = root / 'reproducibility/manuscript_versions' / version_id / 'manifest.json'
    # 生成标签是以后科学复跑的配置，不是本轮动作；本轮不调用绘图入口。
    manifest['document_revision'] = {'scientific_calculation_reexecuted': False,
        'all_figure_assets_inherited': True, 'figure_count': len(figures),
        'original_scientific_version': BASE_VERSION,
        'generated_figure_labels_scope': '保留以后完整科学复跑配置；本轮24图全部按原SHA继承，未执行绘图。'}
    dump(manifest_path, manifest)
    baseline_hashes = {name: sha(baseline / name) for name in SOURCE_NAMES}
    record = {'schema': 'document-revision-v1', 'version': version_id, 'base_version': current['version'],
              'created_utc': datetime.now(timezone.utc).isoformat(), 'previous_pointer_sha256': previous_pointer_hash,
              'manifest_sha256': sha(manifest_path), 'baseline_sha256': baseline_hashes,
              'candidate_sha256': {name: sha(candidate / name) for name in (MAIN + '.tex', SUPPLEMENT + '.tex', 'references.bib')},
              'inheritance': inheritance, 'protected_files_sha256': dict(sorted(protected.items())),
              'merge': merge, 'scientific_calculation_reexecuted': False,
              'formal_files_published': False, 'activated': False}
    dump(output / 'revision.json', record)
    differences = difflib.unified_diff(before_main.splitlines(keepends=True), main.splitlines(keepends=True),
                                      fromfile='before/main.tex', tofile='candidate/main.tex')
    (output / 'manuscript.diff').write_text(''.join(differences), encoding='utf-8')
    dump(output / 'stage_report.json', {'passed': True, 'version': manifest['version'],
                                      'scientific_calculation_reexecuted': False})
    return record


def check_revision(root: Path, output: Path) -> tuple[dict, dict]:
    from icu_revision_text import candidate_texts, assert_protected_unchanged
    record = read(output / 'revision.json')
    if record.get('schema') != 'document-revision-v1' or record.get('scientific_calculation_reexecuted') is not False:
        raise RuntimeError('文案修订记录身份异常')
    baseline, candidate = output / 'baseline', output / 'candidate'
    for name, digest in record['baseline_sha256'].items():
        require_hash(root, baseline / name, digest)
    for name, digest in record['candidate_sha256'].items():
        require_hash(root, candidate / name, digest)
    for relative, digest in record['protected_files_sha256'].items():
        require_hash(root, root / relative, digest)
    inheritance = validate_inheritance(root, Path(record['inheritance']['run_directory']))
    if inheritance != record['inheritance']:
        raise RuntimeError('继承验收身份与候选创建时不同')
    version = load_version(root, required=True, version_id=record['version'],
                           expected_manifest_sha256=record['manifest_sha256'])
    before_main = (baseline / (MAIN + '.tex')).read_text(encoding='utf-8-sig')
    before_si = (baseline / (SUPPLEMENT + '.tex')).read_text(encoding='utf-8-sig')
    main, bibliography, _ = candidate_texts(root, before_main, (baseline / 'references.bib').read_text(encoding='utf-8-sig'))
    if (_normalized(main) != _normalized((candidate / (MAIN + '.tex')).read_text(encoding='utf-8-sig')) or
            _normalized(bibliography) != _normalized((candidate / 'references.bib').read_text(encoding='utf-8-sig')) or
            (baseline / (SUPPLEMENT + '.tex')).read_bytes() != (candidate / (SUPPLEMENT + '.tex')).read_bytes()):
        raise RuntimeError('候选超出批准的局部文本修改')
    assert_protected_unchanged(before_main, main, before_si, before_si)
    return record, version


def verify(root: Path, output: Path) -> dict:
    from paper_sync import prepare_manuscript
    from build import run as build
    from icu_revision_text import assert_protected_unchanged
    root, output = root.resolve(), _output(root, output)
    if (output / 'verification.json').exists():
        raise FileExistsError('已有本轮核查记录，不覆盖')
    record, version = check_revision(root, output)
    main, supplement = version_texts(version)
    regressions = []
    for name in ('generation_1', 'generation_2'):
        directory = output / name
        generated, generated_si, report = prepare_manuscript(root, directory,
            scientific_reference=root / version['inherited_science_reference'],
            joint_extra_directory=Path(record['inheritance']['joint_extra_directory']),
            manuscript_version_id=record['version'], expected_manifest_sha256=record['manifest_sha256'],
            inherited_joint_publication=record['inheritance'])
        assert_protected_unchanged(main, generated, supplement, generated_si)
        if _normalized(generated) != _normalized(main) or _normalized(generated_si) != _normalized(supplement):
            raise RuntimeError('完整文案回归改变批准候选，不能覆盖正式稿')
        regressions.append({'directory': name, 'passed': True,
                            'main_sha256_lf': hashlib.sha256(_normalized(generated).encode()).hexdigest(),
                            'supplement_sha256_lf': hashlib.sha256(_normalized(generated_si).encode()).hexdigest(),
                            'scientific_calculation_reexecuted': False})
    built = build(output, root, main_text=main, supplement_text=supplement,
                  bibliography_path=version_bibliography(version))
    import pymupdf
    required_pages = {1}
    markers = ('本文以社区非隔离感染人数为直接控制对象', '为说明该上界与医疗容量的联系',
               '初始时刻之前已经感染者', '全过程固定的本病可用容量',
               '比例参考情景', '实际随机占用', '医疗需求充分条件', '参考文献')
    with pymupdf.open(output / 'document/latex' / (MAIN + '.pdf')) as pdf:
        for i, page in enumerate(pdf):
            text = ''.join(page.get_text().split())
            if any(marker in text for marker in markers):
                required_pages.add(i + 1)
    built['required_detail_pages'] = sorted(required_pages)
    dump(output / 'document/build_report.json', built)
    result = {'passed': True, 'manuscript_version': record['version'], 'manifest_sha256': record['manifest_sha256'],
              'generation_regression': regressions, 'build_report_sha256': sha(output / 'document/build_report.json'),
              'scientific_calculation_reexecuted': False, 'manual_page_review': 'pending',
              'documents': built['documents'], 'printed_reference_count': len(built['printed_bibliography_keys']),
              'source_sha256': record['candidate_sha256']}
    dump(output / 'verification.json', result)
    return result


def validate_review(review: dict, build: dict, directory: Path) -> None:
    if review.get('passed') is not True or review.get('failures'):
        raise RuntimeError('缺少通过的实际页面审阅记录')
    for stem, prefix in ((MAIN, 'main'), (SUPPLEMENT, 'supplement')):
        info = build['documents'][stem]
        if (review.get(prefix + '_pdf_sha256') != info['pdf_sha256'] or
                sha(directory / (stem + '.pdf')) != info['pdf_sha256'] or
                set(review.get(prefix + '_contact_pages_viewed', [])) != set(range(1, info['page_count'] + 1))):
            raise RuntimeError('人工审阅没有绑定本轮PDF或页面覆盖不完整')
    detail = review.get('detail_pages_viewed')
    if (not isinstance(detail, dict) or set(detail) != {'main', 'supplement'} or
            review.get('scientific_calculation_reexecuted') is not False):
        raise RuntimeError('人工记录缺少修改页细查或科学证据边界')
    for stem, prefix in ((MAIN, 'main'), (SUPPLEMENT, 'supplement')):
        pages = detail[prefix]
        maximum = build['documents'][stem]['page_count']
        if (not isinstance(pages, list) or not pages or any(type(page) is not int or not 1 <= page <= maximum for page in pages)):
            raise RuntimeError('重点页清单类型或页码范围错误')
    if not set(build.get('required_detail_pages', [])).issubset(detail['main']):
        raise RuntimeError('重点页清单遗漏修改内容或参考文献')


def publish(root: Path, output: Path) -> dict:
    from publish_verified import compare_documents
    root, output = root.resolve(), _output(root, output)
    destination = output / 'publication.json'
    if destination.exists():
        raise FileExistsError('已有文案发布记录，不覆盖')
    record, version = check_revision(root, output)
    verification = read(output / 'verification.json')
    if (verification.get('passed') is not True or
            verification.get('manifest_sha256') != record['manifest_sha256'] or
            verification.get('scientific_calculation_reexecuted') is not False):
        raise RuntimeError('文案及编译核查没有通过')
    if sha(output / 'document/build_report.json') != verification['build_report_sha256']:
        raise RuntimeError('实际编译记录发生变化')
    built = read(output / 'document/build_report.json')
    if built.get('passed') is not True:
        raise RuntimeError('实际编译没有通过')
    checked = output / 'document/latex'
    for name in (MAIN + '.tex', SUPPLEMENT + '.tex', 'references.bib'):
        expected = (output / 'candidate' / name).read_text(encoding='utf-8-sig')
        if _normalized((checked / name).read_text(encoding='utf-8-sig')) != _normalized(expected):
            raise RuntimeError('已编译源与受控候选不一致：' + name)
    validate_review(read(output / 'manual_review.json'), built, checked)
    if sha(root / CURRENT_POINTER) != record['previous_pointer_sha256']:
        raise RuntimeError('候选审阅期间活动指针已变化，拒绝覆盖')
    for name, digest in record['baseline_sha256'].items():
        require_hash(root, root / 'latex' / name, digest)
    formal_previous = output / 'before_publication'
    if formal_previous.exists():
        raise FileExistsError('已有发布备份，须检查上次发布状态')
    formal_previous.mkdir()
    for name in SOURCE_NAMES + (MAIN + '.pdf', SUPPLEMENT + '.pdf'):
        shutil.copy2(root / 'latex' / name, formal_previous / name)
    copied = []
    try:
        for name in (MAIN + '.tex', SUPPLEMENT + '.tex', 'references.bib'):
            shutil.copy2(output / 'candidate' / name, root / 'latex' / name)
            copied.append(name)
        with (output / 'formal_build_stdout.log').open('w', encoding='utf-8') as stream:
            subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                            str(root / 'latex/build_paper.ps1')], cwd=root, stdout=stream,
                           stderr=subprocess.STDOUT, check=True, timeout=1800)
        documents = {stem: compare_documents(root / 'latex' / (stem + '.pdf'), checked / (stem + '.pdf'))
                     for stem in (MAIN, SUPPLEMENT)}
        check_revision(root, output)
        activation = json_ready(activate_version(root, record['version'],
            expected_current_sha256=record['previous_pointer_sha256'],
            expected_manifest_sha256=record['manifest_sha256'],
            approval_reason='本轮批准的ICU条件性联系已通过保护核查、继承科学身份、双文案回归、完整编译和实际全页/重点页审阅；没有科学重算。'))
        result = {'passed': True, 'formal_files_published': True, 'manuscript_version': version['version'],
                  'scientific_calculation_reexecuted': False, 'inherited_scientific_acceptance': record['inheritance'],
                  'documents': documents, 'version_activation': activation, 'git_writes': False,
                  'clinical_validation': False, 'scope': '本轮文案、编译和页面验收；原科学验收原样继承。'}
        dump(destination, result)
        return result
    except Exception as error:
        dump(output / ('publication_failure_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.json'),
             {'passed': False, 'error': str(error), 'copied_sources': copied, 'recoverable_backup': str(formal_previous),
              'scientific_calculation_reexecuted': False, 'partial_publication_possible': True,
              'note': '没有自动删除或回滚；检查备份和当前工程，失败不能标记完成。'})
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('stage', 'verify', 'publish'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--science-source', type=Path)
    parser.add_argument('--version', default=VERSION_ID)
    args = parser.parse_args()
    try:
        if args.mode == 'stage':
            if args.science_source is None:
                parser.error('stage须显式指定--science-source')
            result = stage(ROOT, args.output, args.science_source.resolve(), args.version)
        elif args.mode == 'verify':
            result = verify(ROOT, args.output)
        else:
            result = publish(ROOT, args.output)
        print(json.dumps({'passed': True, 'mode': args.mode,
                          'scientific_calculation_reexecuted': False,
                          'version': result.get('manuscript_version', result.get('version'))}, ensure_ascii=False))
    except Exception as error:
        target = _output(ROOT, args.output)
        if target.exists():
            dump(target / ('failure_' + args.mode + '_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.json'),
                 {'passed': False, 'error': str(error), 'traceback': traceback.format_exc(),
                  'scientific_calculation_reexecuted': False})
        raise


if __name__ == '__main__':
    main()
