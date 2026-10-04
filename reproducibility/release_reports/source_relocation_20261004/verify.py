"""冻结来源迁移的逐字节与入口核查；不重算、不发布、不删除文件。"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
OLD = 'ai/threshold_control_reproducible_release_20261002'
NEW = 'joint_control/threshold_control_reproducible_release_20261002'
BACKUP = ROOT / 'reproducibility/backups/before_source_relocation_20261004'
CHECKS = ROOT / 'reproducibility/dev_source_relocation_20261004'
EDITED = [
    '.gitattributes', '.gitignore', 'AGENTS.md', 'README.md',
    'reproducibility/README.md', 'reproducibility/future_plan.md',
    'reproducibility/configuration.md', 'reproducibility/configuration_index.json',
    'reproducibility/registry.json', 'reproducibility/bootstrap.py',
    'reproducibility/integrity.py', 'reproducibility/joint.py',
    'reproducibility/paper_sync.py', 'reproducibility/registry.py',
    'reproducibility/theory_trace.py', 'reproducibility/xian.py',
    'reproducibility/publish_verified.py',
    'reproducibility/publication/publish_artifacts.py',
]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def dump(name, value):
    (REPORT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                         allow_nan=False) + '\n', encoding='utf-8')


def files(directory):
    paths = sorted(p for p in directory.rglob('*') if p.is_file())
    for path in [directory, *directory.rglob('*')]:
        if path.is_symlink() or path.is_junction():
            raise RuntimeError('发现链接，停止：' + str(path))
        if not path.resolve().is_relative_to(ROOT):
            raise RuntimeError('路径越界：' + str(path))
    return paths


def snapshot(paths):
    return {p.relative_to(ROOT).as_posix(): {'sha256': sha(p), 'size_bytes': p.stat().st_size}
            for p in paths}


def capture():
    if (REPORT / 'before.json').exists() or BACKUP.exists() or CHECKS.exists():
        raise RuntimeError('本轮记录/备份/核查目录已存在，不覆盖')
    frozen = files(ROOT / OLD)
    manifest = load(ROOT / OLD / 'MANIFEST_SHA256.json')
    expected = set(manifest['files']) | {'MANIFEST_SHA256.json'}
    if {p.relative_to(ROOT / OLD).as_posix() for p in frozen} != expected:
        raise RuntimeError('冻结包文件集合与清单不一致')
    for relative, info in manifest['files'].items():
        path = ROOT / OLD / relative
        if sha(path) != info['sha256'] or path.stat().st_size != info['size_bytes']:
            raise RuntimeError('冻结包内容已变：' + relative)
    protected = files(ROOT / 'latex')
    protected += files(ROOT / '真实数据') + files(ROOT / 'reproducibility/results')
    protected += [p for p in files(ROOT / 'reproducibility/release_reports')
                  if not p.is_relative_to(REPORT)]
    plans = [p for p in files(ROOT / 'ai') if not p.is_relative_to(ROOT / OLD)]
    baseline = {'old_prefix': OLD, 'new_prefix': NEW,
                'frozen': snapshot(frozen), 'protected': snapshot(protected),
                'discussion_files': snapshot(plans),
                'edited_before': snapshot([ROOT / p for p in EDITED]),
                'git_status_before': subprocess.run(['git', 'status', '--short'], cwd=ROOT,
                    capture_output=True, text=True, encoding='utf-8', errors='replace', check=True).stdout}
    for relative in EDITED:
        destination = BACKUP / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    dump('before.json', baseline)
    print('CAPTURE_PASSED frozen_files=' + str(len(frozen)))


def verify():
    baseline = load(REPORT / 'before.json')
    if (ROOT / OLD).exists() or not (ROOT / NEW).is_dir():
        raise RuntimeError('旧路径仍存在或新路径缺失')
    frozen = files(ROOT / NEW)
    relocated = {p.relative_to(ROOT / NEW).as_posix(): sha(p) for p in frozen}
    expected = {p.removeprefix(OLD + '/'): v['sha256'] for p, v in baseline['frozen'].items()}
    if relocated != expected:
        raise RuntimeError('迁移前后冻结包字节或文件集合改变')
    for kind in ('protected', 'discussion_files'):
        if any(not (ROOT / p).is_file() or sha(ROOT / p) != v['sha256']
               for p, v in baseline[kind].items()):
            raise RuntimeError('保护内容改变：' + kind)
    logic = []
    for relative in EDITED:
        if not relative.endswith('.py'):
            continue
        before = (BACKUP / relative).read_text(encoding='utf-8-sig')
        after = (ROOT / relative).read_text(encoding='utf-8-sig')
        adapted = before.replace(OLD, NEW).replace("ROOT / 'ai' /", "ROOT / 'joint_control' /")
        if ast.dump(ast.parse(adapted)) != ast.dump(ast.parse(after)):
            raise RuntimeError('除路径外代码逻辑改变：' + relative)
        logic.append(relative)
    for relative in ('reproducibility/configuration_index.json', 'reproducibility/registry.json'):
        before = (BACKUP / relative).read_text(encoding='utf-8-sig').replace(OLD, NEW)
        if json.loads(before) != load(ROOT / relative):
            raise RuntimeError('索引除来源路径外发生改变：' + relative)
    child_environment = dict(os.environ, PYTHONIOENCODING='utf-8')
    locked = subprocess.run([sys.executable, '-B', str(ROOT / NEW / 'scripts/verify_release.py')],
                            cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                            env=child_environment, check=True)
    dump('frozen_locked_check.json', json.loads(locked.stdout))
    sys.path.insert(0, str(ROOT / 'reproducibility'))
    import bootstrap, integrity, joint, paper_sync, registry, theory_trace
    for name in ('xian', 'publish_verified'):
        importlib.import_module(name)
    # 仅加载原核心和输入，不调用 compute、ODE、拟合或求根。
    core = joint._load_core(ROOT)
    config = load(ROOT / joint.PACKAGE / 'numerics/inputs/baseline_parameters.json')
    params = core.Parameters(**config['parameters'])
    checks = []
    for number in (1, 2):
        output = CHECKS / ('run_' + str(number))
        workspace = bootstrap.prepare_workspace(output, ROOT)
        version = integrity.run(ROOT, output)
        coverage = registry.build_registry(ROOT, output)
        if not coverage['passed']:
            raise RuntimeError('来源索引结构不完整')
        trace = theory_trace.run(ROOT, output,
                    (ROOT / paper_sync.RELEASE / 'flatten_curve_analysis_cn.tex').read_text(encoding='utf-8-sig'))
        checks.append({'empty_output_before_run': True, 'workspace_created': workspace.is_dir(),
                       'integrity_passed': version['passed'], 'registry': coverage,
                       'frozen_theory_source_read_passed': trace['passed']})
    # 文案回归沿用已有验收输出，不把旧 CSV 当作新计算证据。
    results = ROOT / 'reproducibility/results/20261003_release_final'
    sync_output = CHECKS / 'wording_regression'
    sync_output.mkdir()
    for name in ('xian', 'population', 'c0', 'joint'):
        shutil.copytree(results / name, sync_output / name)
    shutil.copytree(results / 'baseline', sync_output /
                   'workspace/scenario1_threshold_landscape/current_run/output_csv')
    _, _, wording = paper_sync.prepare_manuscript(ROOT, sync_output)
    if not wording['passed']:
        raise RuntimeError('隔离文案回归失败')
    for kind in ('protected', 'discussion_files'):
        if any(sha(ROOT / p) != v['sha256'] for p, v in baseline[kind].items()):
            raise RuntimeError('测试写入保护文件：' + kind)
    ignored = subprocess.run(['git', 'check-ignore', '--no-index', *
                             [(ROOT / NEW / p).relative_to(ROOT).as_posix() for p in relocated]],
                            cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if ignored.returncode not in (0, 1) or ignored.stdout.strip():
        raise RuntimeError('迁移包有被 Git 忽略的文件：' + ignored.stdout + ignored.stderr)
    attributes = subprocess.run(['git', 'check-attr', 'text', '--', *
                                [(ROOT / NEW / p).relative_to(ROOT).as_posix() for p in relocated]],
                               cwd=ROOT, capture_output=True, text=True, encoding='utf-8', check=True)
    if len(attributes.stdout.splitlines()) != len(relocated) or any(
            not line.endswith(': text: unset') for line in attributes.stdout.splitlines()):
        raise RuntimeError('冻结包字节属性不完整')
    dump('relocation_manifest.json', {'files': [
        {'old_path': OLD + '/' + p, 'new_path': NEW + '/' + p, 'sha256': digest,
         'size_bytes': (ROOT / NEW / p).stat().st_size, 'content_unchanged': True}
        for p, digest in relocated.items()]})
    dump('verification.json', {'passed': True, 'frozen_files': len(relocated),
         'python_executable': sys.executable, 'python_version': sys.version,
         'frozen_content_unchanged': True, 'protected_files': len(baseline['protected']),
         'discussion_files_retained': len(baseline['discussion_files']), 'deleted_files': [],
         'path_only_python_changes': logic, 'empty_workspace_checks': checks,
         'joint_core_loaded': True, 'joint_parameters': config['parameters'],
         'joint_Sc_loaded': params.Sc, 'wording_regression_passed': wording['passed'],
         'wording_uses_existing_results': 'reproducibility/results/20261003_release_final',
         'wording_source_main': wording['source_main'], 'git_attributes_checked': True,
         'scientific_calculations_rerun': False, 'latex_recompiled': False,
         'formal_manuscript_pdf_and_figures_unchanged': True, 'git_commit_or_push': False,
         'scope': '来源搬迁、版本完整性和入口/文案回归；不是新的全文科学复现或数学证明验收。'})
    print('RELOCATION_VERIFIED frozen_files=' + str(len(relocated)) + ' deleted_files=0')


def final_inventory():
    """记录成功核查后的现场变化，不恢复或清理并发新增/删除的文件。"""
    baseline = load(REPORT / 'before.json')
    protected_changes = [p for p, v in baseline['protected'].items()
                         if not (ROOT / p).is_file() or sha(ROOT / p) != v['sha256']]
    frozen = {p.relative_to(ROOT / NEW).as_posix(): sha(p) for p in files(ROOT / NEW)}
    expected = {p.removeprefix(OLD + '/'): v['sha256'] for p, v in baseline['frozen'].items()}
    missing = [p for p in baseline['discussion_files'] if not (ROOT / p).is_file()]
    changed = [p for p, v in baseline['discussion_files'].items()
               if (ROOT / p).is_file() and sha(ROOT / p) != v['sha256']]
    current = snapshot(files(ROOT / 'ai'))
    new_files = {p: v for p, v in current.items() if p not in baseline['discussion_files']}
    passed = not protected_changes and frozen == expected
    dump('final_inventory.json', {'source_and_protected_passed': passed,
         'protected_changes': protected_changes, 'frozen_files': len(frozen),
         'discussion_missing_since_successful_check': missing,
         'discussion_changed_since_successful_check': changed,
         'new_discussion_files': new_files, 'deleted_files_by_this_task': [],
         'restored_external_changes': False,
         'scope': '最终现场盘点；发现成功核查之后的讨论区外部变化，保留现场，不将其冒充本轮删除。'})
    if not passed:
        raise RuntimeError('最后盘点发现来源或保护材料改变')
    print('FINAL_SOURCE_INVENTORY_PASSED external_missing_discussion=' + str(len(missing)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('capture', 'verify', 'final-inventory'))
    args = parser.parse_args()
    {'capture': capture, 'verify': verify, 'final-inventory': final_inventory}[args.action]()
