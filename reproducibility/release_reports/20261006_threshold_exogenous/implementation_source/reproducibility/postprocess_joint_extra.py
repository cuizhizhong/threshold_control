"""承接同一运行中已经完成的联合计算；只生成图文、编译和登记，不重算科学量。"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import traceback

from bootstrap import ROOT, dump, environment, prepare_workspace, sha
from manuscript_version import load_version, version_bibliography, version_build_script


CALCULATION_FILES = ('core.py', 'run.py', 'validation.py', 'acceptance.json')
COMMON_RESULTS = ('input_manifest.json', 'validation.json', 'acceptance.json',
                  'derived_summary.json', 'candidate_checks.json', 'convergence.json')
TASK_RESULTS = {
    'A': ('compare_baseline.csv', 'compare_xian.csv', 'trajectories_baseline.csv',
          'trajectories_xian.csv', 'candidate_checks_A.json', 'TDINN_external_reference.json'),
    'B': ('capacity.json', 'capacity_baseline.npz', 'capacity_xian.npz',
          'capacity_traj_baseline.csv', 'capacity_traj_xian.csv', 'candidate_checks_B.json'),
    'C': ('phase.json', 'phase_baseline.npz', 'phase_xian.npz', 'candidate_checks_C.json'),
    'D': ('frontier_baseline.csv', 'alpha_family_baseline.csv', 'candidate_checks_D.json'),
}


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8-sig'))


def _reject_link_path(path: Path) -> None:
    # 必须在 resolve() 之前检查，否则符号链接/Windows junction 的身份会丢失。
    for candidate in (path.absolute(), *path.absolute().parents):
        if candidate.is_symlink() or (hasattr(candidate, 'is_junction') and candidate.is_junction()):
            raise ValueError('运行路径不能含符号链接或 Windows junction：' + str(candidate))


def scientific_snapshot(directory: Path) -> dict[str, str]:
    """只读清单；不允许链接或绘图目录混入纯计算输出。"""
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError('科学输出必须为正常目录，不接受符号链接。')
    result = {}
    for path in directory.iterdir():
        if path.is_symlink() or not path.is_file():
            raise ValueError('纯计算输出中存在链接或子目录：' + str(path))
        result[path.name] = sha(path)
    return result


def validate_completed_results(output: Path, root: Path, version: dict) -> dict:
    """静态核对计算期身份与已存验收，不执行拟合、求根、扫描或 ODE。"""
    _reject_link_path(Path(output))
    output, root = Path(output).resolve(), Path(root).resolve()
    if not output.is_relative_to(root/'reproducibility'):
        raise ValueError('后处理运行必须位于项目 reproducibility 下。')
    for ancestor in (output, *output.parents):
        if ancestor.is_symlink():
            raise ValueError('运行路径不能含符号链接。')
        if ancestor == root:
            break
    science = output/'joint_extra'
    if not output.is_dir() or set(output.iterdir()) != {science}:
        raise FileExistsError('首次后处理运行根只能含 joint_extra；不覆盖旧检查或出版产物。')
    snapshot = scientific_snapshot(science)
    required = set(COMMON_RESULTS)
    for task in version['approved_tasks']:
        required.update(TASK_RESULTS[task])
    missing = sorted(required - set(snapshot))
    if missing:
        raise FileNotFoundError('已计算结果缺失：' + ', '.join(missing))
    manifest = _read(science/'input_manifest.json')
    validation = _read(science/'validation.json')
    if manifest.get('schema') != 'joint-extra-v2' or Path(manifest.get('root', '')).resolve() != root:
        raise RuntimeError('计算输入清单版本或项目来源不匹配。')
    declared = manifest.get('calculation_source_hashes', {})
    if set(declared) != set(CALCULATION_FILES):
        raise RuntimeError('计算期源码清单不完整或含未经批准的文件。')
    current = {name: sha(root/'reproducibility/joint_extra'/name) for name in CALCULATION_FILES}
    if current != declared:
        raise RuntimeError('科学计算结束后的计算源码发生变化；禁止以新代码身份发布旧结果。')
    expected_inputs = {
        'baseline': root/'joint_control/threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json',
        'xian_reference': root/version['inherited_science_reference']/'xian/reference.json',
    }
    inputs = manifest.get('inputs', {})
    if set(inputs) != set(expected_inputs):
        raise RuntimeError('科学输入清单不是指定的基准及已验收西安参照。')
    for key, expected in expected_inputs.items():
        source = Path(inputs[key]['path']).resolve()
        if source != expected.resolve() or sha(source) != inputs[key].get('sha256'):
            raise RuntimeError('科学输入路径或哈希已改变：' + key)
    acceptance = _read(root/'reproducibility/joint_extra/acceptance.json')
    if manifest.get('acceptance') != acceptance or _read(science/'acceptance.json') != acceptance:
        raise RuntimeError('计算前锁定的验收规则与当前记录不一致。')
    requested = manifest.get('tasks_requested', [])
    if not set(version['approved_tasks']) <= set(requested):
        raise RuntimeError('批准出版任务没有在本轮计算请求中。')
    if validation.get('status') not in {'passed', 'partial', 'failed'}:
        raise RuntimeError('科学计算尚未结束，不能承接运行中结果。')
    tasks = validation.get('tasks', {})
    if set(tasks) != {'A', 'B', 'C', 'D'}:
        raise RuntimeError('逐任务验收状态不完整。')
    for task in version['approved_tasks']:
        if tasks[task].get('passed') is not True or tasks[task].get('status') != 'passed':
            raise RuntimeError('批准任务的实际验收未通过：' + task)
    versions = {'python': platform.python_version(),
                'numpy': importlib.metadata.version('numpy'),
                'scipy': importlib.metadata.version('scipy')}
    if manifest.get('software') != versions:
        raise RuntimeError('后处理 Python/NumPy/SciPy 与科学计算期版本不一致。')
    return {'passed': True, 'calculation_started_at': manifest.get('created'),
            'input_manifest_sha256': snapshot['input_manifest.json'],
            'calculation_source_hashes': current, 'input_sources': inputs,
            'scientific_results_sha256': snapshot, 'approved_tasks': version['approved_tasks'],
            'validation_overall_passed': validation.get('passed') is True, 'tasks': tasks,
            'scope': '静态身份及原验收状态核对；本步骤不重新进行科学计算。'}


def postprocess(output: Path, root: Path = ROOT) -> dict:
    _reject_link_path(Path(output))
    output, root = Path(output).resolve(), Path(root).resolve()
    version = load_version(root, required=True)
    identity = validate_completed_results(output, root, version)
    stages = {'computed_joint_identity': identity}
    # 以上所有拒绝均发生在任何写入之前；后续产物只首次写入新位置。
    phase = 'postprocess_workspace'
    try:
        prepare_workspace(output, root, precomputed_science=output/'joint_extra')
        snapshot_time = dt.datetime.now(dt.timezone.utc).isoformat()
        dump(output/'postprocessing_manifest.json', {
            'schema': 'joint-extra-postprocess-v1', 'created_utc': snapshot_time,
            'manuscript_version': version['version'], 'manuscript_manifest_sha256': sha(version['_manifest_path']),
            'publication_source_snapshot_phase': 'after_completed_scientific_calculation',
            'calculation_phase': identity,
            'scientific_calculation_reexecuted': False,
            'scope': '科学期四文件哈希来自原 input_manifest；完整出版源码在后处理开始时另行锁定，不冒充运行前记录。'})
        environment(output)
        from integrity import run as check_integrity
        stages['source_integrity'] = check_integrity(root, output)
        dump(output/'validation/source_integrity_initial.json', stages['source_integrity'])
        from run_all import _integrated_figures
        phase = 'integrated_figures'
        stages[phase] = _integrated_figures(output, version, inherited=True)
        from paper_sync import prepare_manuscript
        phase = 'manuscript_sync'
        main, supplement, changes = prepare_manuscript(root, output,
            scientific_reference=root/version['inherited_science_reference'])
        dump(output/'manuscript_changes.json', changes)
        if not changes.get('passed'):
            raise RuntimeError('受控出版文案生成未通过。')
        from theory_trace import run as trace
        phase = 'theory_trace'
        stages[phase] = trace(root, output, main)
        if not stages[phase]['passed']:
            raise RuntimeError('受控理论片段保护未通过。')
        from build import run as build
        phase = 'document'
        stages[phase] = build(output, root, figure_dir=output/'figures', main_text=main, supplement_text=supplement,
            bibliography_path=version_bibliography(version),build_script_path=version_build_script(version))
        from registry import build_registry
        phase = 'registry'
        stages[phase] = build_registry(root, output)
        if not stages[phase]['passed']:
            raise RuntimeError('逐项对应清单不完整。')
        phase = 'source_integrity_final'
        stages[phase] = check_integrity(root, output)
        for key in ('runner_source_hashes', 'static_art_assets', 'raw_inputs', 'source_input_hashes', 'frozen_manifest_sha256'):
            if stages['source_integrity'][key] != stages[phase][key]:
                raise RuntimeError('后处理期间输入或出版源码发生变化：' + key)
        if scientific_snapshot(output/'joint_extra') != identity['scientific_results_sha256']:
            raise RuntimeError('后处理改变了科学原始输出。')
        dump(output/'stage_results.json', stages)
        report = {'passed': True, 'numerical_and_build_complete': True,
                  'scientific_scope': 'joint-extra', 'scientific_execution': 'completed_prior_to_postprocess',
                  'scientific_calculation_reexecuted_in_postprocess': False,
                  'inherited_old_science': True, 'manuscript_version': version['version'],
                  'validation_overall_passed': identity['validation_overall_passed'],
                  'approved_tasks': version['approved_tasks'], 'visual_review': 'pending',
                  'formal_files_published': False, 'stages': stages,
                  'scope': '本轮已计算的联合结果加同一工作副本文案/编译；旧科学结果及旧图按锁定身份继承。'}
        dump(output/'run_report.json', report)
        return report
    except Exception as exc:
        dump(output/'run_report.json', {'passed': False, 'failed_stage': phase,
              'formal_files_published': False, 'scientific_calculation_reexecuted_in_postprocess': False,
              'error': str(exc), 'traceback': traceback.format_exc(), 'stages': stages})
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path, help='只含已完成 joint_extra 的本轮运行根目录')
    parser.add_argument('--check-only', action='store_true', help='只读身份核对，不生成任何产物')
    args = parser.parse_args()
    if args.check_only:
        version = load_version(ROOT, required=True)
        result = validate_completed_results(args.output, ROOT, version)
    else:
        result = postprocess(args.output)
    print(json.dumps({'passed': result['passed'], 'output': str(args.output.resolve()),
                      'scientific_calculation_reexecuted': False}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
