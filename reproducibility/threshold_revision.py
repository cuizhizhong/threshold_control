"""用户批准新版整稿的受控迁移；继承科学验收，不执行任何科学求解或绘图。"""
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
from document_revision import (MAIN, SUPPLEMENT, SOURCE_NAMES, json_ready,
                               read, require_hash, safe_path, validate_inheritance,
                               validate_review as validate_previous_review)
from manuscript_version import (CURRENT_POINTER, activate_version, freeze_current_version,
                                inventory, load_version, version_bibliography,
                                version_build_script, version_texts,
                                threshold_exogenous_sec9_transition)
from threshold_revision_text import (assert_citations_resolved, assert_protected_unchanged,
                                     validate_source_bundle)

VERSION_ID = '20261006_threshold_exogenous'
BASE_VERSION = '20261005_icu_conditional_link'
DOCUMENT_NAMES = (MAIN + '.tex', SUPPLEMENT + '.tex', 'references.bib', 'build_paper.ps1')


def normalized(text: str) -> str:
    return text.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')


def output_path(root: Path, output: Path) -> Path:
    return safe_path(root, output, within=root / 'reproducibility/release_reports')


def stage(root: Path, output: Path, science_source: Path) -> dict:
    root, output = root.resolve(), output_path(root, output)
    if output.exists():
        raise FileExistsError('本轮候选目录已存在，拒绝覆盖：' + str(output))
    package_check = validate_source_bundle(root)
    current = load_version(root, required=True)
    if current['version'] != BASE_VERSION:
        raise RuntimeError('新版导入须从批准的ICU条件性联系版本开始')
    for role, name in (('main', MAIN + '.tex'), ('supplement', SUPPLEMENT + '.tex')):
        require_hash(root, root / 'latex' / name, current['documents'][role]['sha256'])
    bibliography = version_bibliography(current)
    if bibliography is None or sha(root / 'latex/references.bib') != sha(bibliography):
        raise RuntimeError('当前正式文献库与活动版本不一致')
    inheritance = validate_inheritance(root, science_source)
    output.mkdir(parents=True)
    baseline, candidate = output / 'baseline', output / 'candidate'
    baseline.mkdir(); candidate.mkdir()
    for name in SOURCE_NAMES + (MAIN + '.pdf', SUPPLEMENT + '.pdf'):
        shutil.copy2(root / 'latex' / name, baseline / name)
    shutil.copy2(root / CURRENT_POINTER, baseline / 'current.json')
    source_archive = output / 'source_bundle'
    shutil.copytree(root / 'ai/icu', source_archive)
    for name in (MAIN + '.tex', SUPPLEMENT + '.tex', 'build_paper.ps1'):
        shutil.copy2(source_archive / 'latex' / name, candidate / name)
    for name in ('references.bib', 'elegantpaper.cls'):
        shutil.copy2(baseline / name, candidate / name)
    before_main = (baseline / (MAIN + '.tex')).read_text(encoding='utf-8-sig')
    before_si = (baseline / (SUPPLEMENT + '.tex')).read_text(encoding='utf-8-sig')
    main = (candidate / (MAIN + '.tex')).read_text(encoding='utf-8-sig')
    si = (candidate / (SUPPLEMENT + '.tex')).read_text(encoding='utf-8-sig')
    protections = assert_protected_unchanged(before_main, main, before_si, si)
    citations = assert_citations_resolved(main, si, (candidate / 'references.bib').read_text(encoding='utf-8-sig'))
    transition = threshold_exogenous_sec9_transition(baseline / (MAIN + '.tex'), candidate / (MAIN + '.tex'))
    figures = {item['image']: sha(root / 'latex/figures' / item['image']) for item in inventory(main)['figures']}
    protected = dict(current['inherited_science_sha256'])
    protected.update(inheritance['files_sha256'])
    frozen = root / 'joint_control/threshold_control_reproducible_release_20261002'
    protected.update({p.relative_to(root).as_posix(): sha(p) for p in frozen.rglob('*') if p.is_file()})
    protected.update({'latex/figures/' + name: digest for name, digest in figures.items()})
    protected['latex/elegantpaper.cls'] = sha(root / 'latex/elegantpaper.cls')
    protected['latex/references.bib'] = sha(root / 'latex/references.bib')
    for relative, digest in read(science_source / 'accepted_runs.json')['shared_identity']['raw_inputs'].items():
        require_hash(root, root / relative, digest, protected)
    manifest = freeze_current_version(root, VERSION_ID, approved_tasks=current['approved_tasks'],
        textwidth_bp=current['textwidth_bp'], baseline_main=baseline / (MAIN + '.tex'),
        inherited_science=current['inherited_science_reference'], original_figure_hashes=figures,
        source_paths={'main': candidate / (MAIN + '.tex'), 'supplement': candidate / (SUPPLEMENT + '.tex')},
        bibliography_path=candidate / 'references.bib', build_script_path=candidate / 'build_paper.ps1',
        approved_sec9_transition=transition, activate=False,
        generated_figure_labels=current.get('generated_figure_labels'),
        publication_cost_digits=current.get('publication_cost_digits'))
    manifest['provenance'] = '用户批准ai/icu完整源码导入；从本轮隔离候选冻结，经保护检查后受控发布，原冻结包不改。'
    manifest['document_revision'] = {'source': 'ai/icu', 'scientific_calculation_reexecuted': False,
        'all_figure_assets_inherited': True, 'figure_count': len(figures),
        'original_scientific_version': inheritance['original_manuscript_version'],
        'generated_figure_labels_scope': '仅保留未来科学复跑配置；本轮未绘图，24图全部继承原哈希。'}
    manifest_path = root / 'reproducibility/manuscript_versions' / VERSION_ID / 'manifest.json'
    dump(manifest_path, manifest)
    archive_files = {p.relative_to(source_archive).as_posix(): sha(p) for p in source_archive.rglob('*') if p.is_file()}
    record = {'schema': 'threshold-document-revision-v1', 'version': VERSION_ID, 'base_version': BASE_VERSION,
        'created_utc': datetime.now(timezone.utc).isoformat(), 'previous_pointer_sha256': sha(root / CURRENT_POINTER),
        'manifest_sha256': sha(manifest_path), 'baseline_sha256': {name: sha(baseline / name) for name in SOURCE_NAMES},
        'candidate_sha256': {name: sha(candidate / name) for name in SOURCE_NAMES},
        'source_bundle_sha256': archive_files, 'source_bundle_check': json_ready(package_check),
        'approved_sec9_transition': transition, 'protections': protections, 'citations': citations,
        'inheritance': inheritance, 'protected_files_sha256': dict(sorted(protected.items())),
        'scientific_calculation_reexecuted': False, 'formal_files_published': False, 'activated': False}
    dump(output / 'revision.json', record)
    for name in (MAIN + '.tex', SUPPLEMENT + '.tex', 'build_paper.ps1'):
        difference = difflib.unified_diff((baseline / name).read_text(encoding='utf-8-sig').splitlines(keepends=True),
            (candidate / name).read_text(encoding='utf-8-sig').splitlines(keepends=True),
            fromfile='before/' + name, tofile='candidate/' + name)
        (output / (name + '.diff')).write_text(''.join(difference), encoding='utf-8')
    dump(output / 'stage_report.json', {'passed': True, 'version': VERSION_ID,
                                      'scientific_calculation_reexecuted': False})
    return record


def check_revision(root: Path, output: Path) -> tuple[dict, dict]:
    record = read(output / 'revision.json')
    if (record.get('schema') != 'threshold-document-revision-v1' or record.get('version') != VERSION_ID or
            record.get('base_version') != BASE_VERSION or record.get('scientific_calculation_reexecuted') is not False):
        raise RuntimeError('本轮文案修订身份不符或冒充科学运行')
    for name, digest in record['baseline_sha256'].items():
        require_hash(root, output / 'baseline' / name, digest)
    for name, digest in record['candidate_sha256'].items():
        require_hash(root, output / 'candidate' / name, digest)
    for name, digest in record['source_bundle_sha256'].items():
        require_hash(root, output / 'source_bundle' / name, digest)
    for relative, digest in record['protected_files_sha256'].items():
        require_hash(root, root / relative, digest)
    inheritance = validate_inheritance(root, Path(record['inheritance']['run_directory']))
    if inheritance != record['inheritance']:
        raise RuntimeError('继承的原科学验收身份变化')
    version = load_version(root, required=True, version_id=VERSION_ID,
                           expected_manifest_sha256=record['manifest_sha256'])
    baseline, candidate = output / 'baseline', output / 'candidate'
    main, si = version_texts(version)
    for role, name, text in (('main', MAIN + '.tex', main), ('supplement', SUPPLEMENT + '.tex', si)):
        if normalized(text) != normalized((candidate / name).read_text(encoding='utf-8-sig')):
            raise RuntimeError('受控快照与批准候选不同：' + role)
    assert_protected_unchanged((baseline / (MAIN + '.tex')).read_text(encoding='utf-8-sig'), main,
        (baseline / (SUPPLEMENT + '.tex')).read_text(encoding='utf-8-sig'), si)
    assert_citations_resolved(main, si, version_bibliography(version).read_text(encoding='utf-8-sig'))
    if sha(version_bibliography(version)) != record['candidate_sha256']['references.bib']:
        raise RuntimeError('受控文献库与批准候选不符')
    if sha(version_build_script(version)) != record['candidate_sha256']['build_paper.ps1']:
        raise RuntimeError('受控编译脚本与批准候选不符')
    transition = threshold_exogenous_sec9_transition(baseline / (MAIN + '.tex'), candidate / (MAIN + '.tex'))
    if transition != record['approved_sec9_transition']:
        raise RuntimeError('第9节局部批准记录不符')
    return record, version


def verify(root: Path, output: Path) -> dict:
    from paper_sync import prepare_manuscript
    from build import run as build
    root, output = root.resolve(), output_path(root, output)
    if (output / 'verification.json').exists():
        raise FileExistsError('已有核查记录，拒绝覆盖')
    record, version = check_revision(root, output)
    main, si = version_texts(version)
    regressions = []
    for name in ('generation_1', 'generation_2'):
        directory = output / name
        if directory.exists():
            raise FileExistsError('文案回归必须使用全新目录：' + name)
        generated, generated_si, report = prepare_manuscript(root, directory,
            scientific_reference=root / version['inherited_science_reference'],
            joint_extra_directory=Path(record['inheritance']['joint_extra_directory']),
            manuscript_version_id=VERSION_ID, expected_manifest_sha256=record['manifest_sha256'],
            inherited_joint_publication=record['inheritance'])
        if normalized(generated) != normalized(main) or normalized(generated_si) != normalized(si):
            raise RuntimeError('全文生成回归改变新版正文或补充材料')
        if report.get('scientific_calculation_reexecuted') is not False:
            raise RuntimeError('文案回归被错误标记为科学重跑')
        regressions.append({'directory': name, 'passed': True,
            'main_sha256_lf': hashlib.sha256(normalized(generated).encode()).hexdigest(),
            'supplement_sha256_lf': hashlib.sha256(normalized(generated_si).encode()).hexdigest(),
            'scientific_calculation_reexecuted': False})
    built = build(output, root, main_text=main, supplement_text=si,
                  bibliography_path=version_bibliography(version), build_script_path=version_build_script(version))
    import pymupdf
    markers = ('社区感染上限', '外生', '设计情景', '干预成本与启动状态', '人口归一化与低阈值',
               '设定与比较基准', '讨论', '结论', '参考文献')
    required = {1}
    with pymupdf.open(output / 'document/latex' / (MAIN + '.pdf')) as pdf:
        for i, page in enumerate(pdf):
            text = ''.join(page.get_text().split())
            if any(marker in text for marker in markers):
                for n in (i, i + 1, i + 2):
                    if 1 <= n <= len(pdf): required.add(n)
    built['required_detail_pages'] = sorted(required)
    built['required_supplement_detail_pages'] = list(range(1, built['documents'][SUPPLEMENT]['page_count'] + 1))
    dump(output / 'document/build_report.json', built)
    result = {'passed': True, 'manuscript_version': VERSION_ID, 'manifest_sha256': record['manifest_sha256'],
        'generation_regression': regressions, 'build_report_sha256': sha(output / 'document/build_report.json'),
        'scientific_calculation_reexecuted': False, 'manual_page_review': 'pending',
        'documents': built['documents'], 'source_sha256': record['candidate_sha256']}
    dump(output / 'verification.json', result)
    return result


def validate_review(review: dict, built: dict, directory: Path) -> None:
    validate_previous_review(review, built, directory)
    if not set(built.get('required_supplement_detail_pages', [])).issubset(review['detail_pages_viewed']['supplement']):
        raise RuntimeError('补充材料新增推导及参考文献未完整细查')


def run_tests(root: Path, output: Path) -> dict:
    """实际运行文案/接口单测并锁定所用源码；不调用科学求解器测试目录。"""
    root, output = root.resolve(), output_path(root, output)
    if (output / 'tests.json').exists():
        raise FileExistsError('已有单测记录，拒绝覆盖')
    paths = list((root / 'reproducibility').glob('*.py'))
    paths += list((root / 'reproducibility/tests').glob('*.py'))
    sources = {path.relative_to(root).as_posix(): sha(path) for path in sorted(paths)}
    with (output / 'tests.log').open('w', encoding='utf-8') as log:
        result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover',
            '-s', 'reproducibility/tests', '-v'], cwd=root, stdout=log,
            stderr=subprocess.STDOUT, timeout=180)
    report = {'passed': result.returncode == 0, 'returncode': result.returncode,
        'source_sha256': sources, 'log_sha256': sha(output / 'tests.log'),
        'scientific_calculation_reexecuted': False,
        'scope': '文案、接口、发布守卫及隔离假数据测试；不是A–D或整稿科学复算。'}
    dump(output / 'tests.json', report)
    if result.returncode:
        raise RuntimeError('文案/接口单测失败，见tests.log')
    return report


def publish(root: Path, output: Path) -> dict:
    from publish_verified import compare_documents
    root, output = root.resolve(), output_path(root, output)
    if (output / 'publication.json').exists():
        raise FileExistsError('已有本轮发布记录，拒绝覆盖')
    record, version = check_revision(root, output)
    tests = read(output / 'tests.json')
    if (tests.get('passed') is not True or tests.get('scientific_calculation_reexecuted') is not False or
            tests.get('log_sha256') != sha(output / 'tests.log')):
        raise RuntimeError('缺少本轮实际通过的文案/接口单测记录')
    for relative, digest in tests['source_sha256'].items():
        require_hash(root, root / relative, digest)
    verification = read(output / 'verification.json')
    if (verification.get('passed') is not True or verification.get('manifest_sha256') != record['manifest_sha256'] or
            verification.get('scientific_calculation_reexecuted') is not False or
            sha(output / 'document/build_report.json') != verification.get('build_report_sha256')):
        raise RuntimeError('实际文案及编译核查未通过或记录被修改')
    built = read(output / 'document/build_report.json')
    if built.get('passed') is not True:
        raise RuntimeError('实际编译失败')
    checked = output / 'document/latex'
    for name in SOURCE_NAMES:
        if normalized((checked / name).read_text(encoding='utf-8-sig')) != normalized((output / 'candidate' / name).read_text(encoding='utf-8-sig')):
            raise RuntimeError('实际编译来源与批准候选不符：' + name)
    validate_review(read(output / 'manual_review.json'), built, checked)
    if sha(root / CURRENT_POINTER) != record['previous_pointer_sha256']:
        raise RuntimeError('活动指针已改变，拒绝覆盖')
    for name, digest in record['baseline_sha256'].items():
        require_hash(root, root / 'latex' / name, digest)
    backup = output / 'before_publication'
    if backup.exists():
        raise FileExistsError('已有发布备份，须先核查上次状态')
    backup.mkdir()
    for name in SOURCE_NAMES + (MAIN + '.pdf', SUPPLEMENT + '.pdf'):
        shutil.copy2(root / 'latex' / name, backup / name)
    copied = []
    try:
        for name in DOCUMENT_NAMES:
            shutil.copy2(output / 'candidate' / name, root / 'latex' / name)
            copied.append(name)
        with (output / 'formal_build_stdout.log').open('w', encoding='utf-8') as log:
            subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                            str(root / 'latex/build_paper.ps1')], cwd=root, stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=1800)
        documents = {stem: compare_documents(root / 'latex' / (stem + '.pdf'), checked / (stem + '.pdf'))
                     for stem in (MAIN, SUPPLEMENT)}
        check_revision(root, output)
        activation = json_ready(activate_version(root, VERSION_ID,
            expected_current_sha256=record['previous_pointer_sha256'], expected_manifest_sha256=record['manifest_sha256'],
            approved_sec9_transition=record['approved_sec9_transition'],
            approval_reason='用户批准新版正文及补充材料迁移；保护核查、双文案回归、真实图件完整编译及页面检查通过，无科学重算。'))
        result = {'passed': True, 'formal_files_published': True, 'manuscript_version': VERSION_ID,
            'scientific_calculation_reexecuted': False, 'inherited_scientific_acceptance': record['inheritance'],
            'documents': documents, 'version_activation': activation, 'git_writes': False, 'clinical_validation': False,
            'tests_report_sha256': sha(output / 'tests.json'), 'page_review_sha256': sha(output / 'manual_review.json')}
        dump(output / 'publication.json', result)
        return result
    except Exception as error:
        dump(output / ('publication_failure_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.json'),
            {'passed': False, 'error': str(error), 'copied_sources': copied, 'recoverable_backup': str(backup),
             'scientific_calculation_reexecuted': False, 'partial_publication_possible': True})
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('stage', 'verify', 'tests', 'publish'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--science-source', type=Path)
    args = parser.parse_args()
    try:
        if args.mode == 'stage':
            if args.science_source is None: parser.error('stage须显式指定--science-source')
            result = stage(ROOT, args.output, safe_path(ROOT, args.science_source))
        elif args.mode == 'verify': result = verify(ROOT, args.output)
        elif args.mode == 'tests': result = run_tests(ROOT, args.output)
        else: result = publish(ROOT, args.output)
        print(json.dumps({'passed': True, 'mode': args.mode, 'version': VERSION_ID,
                          'scientific_calculation_reexecuted': False}, ensure_ascii=False))
    except Exception as error:
        target = output_path(ROOT, args.output)
        if target.exists():
            dump(target / ('failure_' + args.mode + '_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.json'),
                {'passed': False, 'error': str(error), 'traceback': traceback.format_exc(),
                 'scientific_calculation_reexecuted': False})
        raise


if __name__ == '__main__': main()
