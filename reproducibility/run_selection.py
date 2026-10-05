"""显式选择两个已通过机器验收的独立运行；不复制、不改编号、不覆盖历史。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from bootstrap import ROOT, dump, sha
from manuscript_version import load_version


SELECTION_FILE = 'accepted_runs.json'
INTEGRITY_KEYS = ('runner_source_hashes', 'static_art_assets', 'raw_inputs',
                  'source_input_hashes', 'frozen_manifest_sha256')


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8-sig'))


def _parent(path: Path) -> Path:
    path=Path(path).absolute()
    for candidate in (path,*path.parents):
        if candidate.is_symlink() or (hasattr(candidate,'is_junction') and candidate.is_junction()):
            raise ValueError('选择总目录路径不能含链接或Windows junction。')
    return path.resolve()


def _directory(parent: Path, name: str) -> Path:
    if not re.fullmatch(r'[A-Za-z0-9_-]+', name):
        raise ValueError('运行名称必须为直接子目录标识：' + str(name))
    candidate = parent/name
    if candidate.is_symlink() or (hasattr(candidate, 'is_junction') and candidate.is_junction()):
        raise ValueError('不能通过链接选择运行：' + name)
    resolved = candidate.resolve()
    if resolved.parent != parent or not resolved.is_dir():
        raise ValueError('选择运行越界或目录不存在：' + name)
    return resolved


def _inspect(run: Path) -> tuple[dict, dict]:
    report = _read(run/'run_report.json')
    if report.get('passed') is not True or report.get('numerical_and_build_complete') is not True:
        raise RuntimeError('所选运行未完成机器验收：' + run.name)
    build = _read(run/'document/build_report.json')
    registry = _read(run/'registry.json')
    if build.get('passed') is not True or registry.get('structure_passed') is not True:
        raise RuntimeError('所选运行编译或结构登记未通过：' + run.name)
    initial = _read(run/'validation/source_integrity_initial.json')
    final = _read(run/'validation/source_integrity.json')
    if initial.get('passed') is not True or final.get('passed') is not True:
        raise RuntimeError('所选运行源码完整性未通过：' + run.name)
    identity = {key: initial[key] for key in INTEGRITY_KEYS}
    if any(identity[key] != final[key] for key in INTEGRITY_KEYS):
        raise RuntimeError('所选运行期间来源发生变化：' + run.name)
    sync = _read(run/'manuscript_changes.json')
    if sync.get('passed') is not True:
        raise RuntimeError('所选运行文案同步未通过：' + run.name)
    identity.update(manuscript_version=report.get('manuscript_version'),
                    manuscript_source_sha256=sync.get('source_sha256'),
                    scientific_scope=report.get('scientific_scope', 'all'),
                    inherited_old_science=report.get('inherited_old_science', False),
                    approved_tasks=report.get('approved_tasks', sync.get('approved_tasks', [])))
    files = ['run_report.json', 'document/build_report.json', 'registry.json',
             'validation/source_integrity_initial.json', 'validation/source_integrity.json',
             'manuscript_changes.json']
    extra = run/'joint_extra'
    if extra.is_dir():
        manifest = _read(extra/'input_manifest.json')
        validation = _read(extra/'validation.json')
        approved = identity['approved_tasks']
        if not approved or not all(validation.get('tasks', {}).get(task, {}).get('passed') is True for task in approved):
            raise RuntimeError('所选运行的批准科学任务未通过：' + run.name)
        identity['joint_extra_input_identity'] = {
            'schema': manifest['schema'], 'inputs': manifest['inputs'],
            'parameters': {case: item['parameters'] for case, item in manifest['cases'].items()},
            'calculation_source_hashes': manifest['calculation_source_hashes'],
            'acceptance': manifest['acceptance'], 'settings': manifest['settings'],
            'software': manifest['software'], 'tasks_requested': manifest['tasks_requested'],
        }
        files += ['joint_extra/input_manifest.json', 'joint_extra/validation.json']
        if (run/'postprocessing_manifest.json').is_file():
            files.append('postprocessing_manifest.json')
    record = {'name': run.name, 'directory': run.name,
              'report_files_sha256': {name: sha(run/name) for name in files}}
    return record, identity


def select_runs(parent: Path, names: list[str], root: Path = ROOT) -> dict:
    """只首次写选择清单；成功标志仍不代替双跑比较和人工页面核查。"""
    parent, root = _parent(parent), Path(root).resolve()
    if not parent.is_relative_to(root/'reproducibility/runs') or parent == root/'reproducibility/runs':
        raise ValueError('选择总目录必须是项目隔离runs的一个版本目录。')
    target = parent/SELECTION_FILE
    if target.exists() or target.is_symlink():
        raise FileExistsError('已有选择清单，不覆盖：' + str(target))
    if len(names) != 2 or len(set(names)) != 2:
        raise ValueError('须明确选择两个不同的独立运行目录。')
    runs = [_directory(parent, name) for name in names]
    inspected = [_inspect(run) for run in runs]
    if inspected[0][1] != inspected[1][1]:
        raise RuntimeError('两个运行的源码、稿源、科学范围或完整输入身份不一致。')
    version = load_version(root)
    expected_version = version['version'] if version else 'frozen_20261002'
    if inspected[0][1]['manuscript_version'] != expected_version:
        raise RuntimeError('选择运行的稿源版本不是当前批准版本。')
    if version and inspected[0][1]['manuscript_source_sha256'] != {role:item['sha256'] for role,item in version['documents'].items()}:
        raise RuntimeError('选择运行的文案来源哈希不是当前批准稿源。')
    if not version and inspected[0][1]['scientific_scope'] == 'joint-extra':
        raise RuntimeError('新增联合运行必须对应受控稿源，不能选择旧冻结稿身份。')
    report = {'schema': 'accepted-runs-v1', 'run_directory': str(parent),
              'runs': [item[0] for item in inspected], 'shared_identity': inspected[0][1],
              'independent_directories_selected': True, 'scientific_results_copied': False,
              'old_runs_overwritten': False, 'manual_review_passed': False,
              'scope': '两个实际独立运行已通过各自机器验收；重复性及人工页面检查需另外执行，失败旧运行保留原位。'}
    dump(target, report)
    return report


def load_selection(parent: Path, root: Path = ROOT) -> dict:
    parent, root = _parent(parent), Path(root).resolve()
    if not parent.is_relative_to(root/'reproducibility/runs'):
        raise ValueError('选择清单目录越界。')
    target = parent/SELECTION_FILE
    if target.is_symlink():
        raise RuntimeError('选择清单不能为链接。')
    if not target.is_file():
        raise FileNotFoundError('必须先显式选择验收运行，不默认读取旧run_1/run_2：' + str(target))
    selection = _read(target)
    if selection.get('schema') != 'accepted-runs-v1' or Path(selection['run_directory']).resolve() != parent:
        raise RuntimeError('选择清单身份或总目录不匹配。')
    names = [item['name'] for item in selection['runs']]
    if len(names) != 2 or len(set(names)) != 2:
        raise RuntimeError('选择清单不是两个不同运行。')
    for item in selection['runs']:
        if item.get('directory') != item['name']:
            raise RuntimeError('选择清单运行路径异常。')
        run = _directory(parent, item['name'])
        for relative, expected in item['report_files_sha256'].items():
            source = (run/relative).resolve()
            if not source.is_relative_to(run) or not source.is_file() or sha(source) != expected:
                raise RuntimeError('选择之后验收报告或输入发生变化：' + item['name'] + '/' + relative)
        _, identity = _inspect(run)
        if identity != selection['shared_identity']:
            raise RuntimeError('选择之后共同身份发生变化：' + item['name'])
    return selection


def selected_directories(parent: Path, root: Path = ROOT) -> tuple[Path, Path]:
    selection = load_selection(parent, root)
    return tuple(Path(parent).resolve()/item['name'] for item in selection['runs'])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-directory', required=True, type=Path)
    parser.add_argument('--runs', nargs=2, metavar=('FIRST', 'SECOND'))
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    if args.check_only:
        report = load_selection(args.run_directory)
    else:
        if args.runs is None:
            parser.error('首次选择必须给出 --runs FIRST SECOND。')
        report = select_runs(args.run_directory, args.runs)
    print(json.dumps({'selected': [item['name'] for item in report['runs']],
                      'files_copied': False, 'manual_review_passed': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
