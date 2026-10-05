"""第7节v2局部整合的基准、保护及差异记录；不执行科学计算。"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import csv
import math

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VERSION = '20261005_sec7_v2_refinement'
REPORT = ROOT / 'reproducibility/release_reports' / VERSION
BACKUP = ROOT / 'reproducibility/backups/sec7_v2_refinement_20261005'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def section(text, begin, end):
    left = text.rfind('\\section', 0, text.index('\\label{' + begin + '}'))
    right = text.rfind('\\section', 0, text.index('\\label{' + end + '}'))
    return text[left:right]


def baseline():
    path = REPORT / 'baseline.json'
    if path.exists():
        raise FileExistsError('基准已锁定，不覆盖')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if commit != '894fd49c99cc52fbaf8e2992c08457ff456c4749':
        raise RuntimeError('HEAD不再是批准基准，需重新核对')
    from manuscript_version import inventory
    main = (ROOT / 'latex/flatten_curve_analysis_cn.tex').read_text(encoding='utf-8-sig')
    supplement = (ROOT / 'latex/flatten_curve_supplement_cn.tex').read_text(encoding='utf-8-sig')
    immutable = {}
    trees = ['joint_control', '真实数据', 'reproducibility/results',
             'reproducibility/release_reports', 'reproducibility/manuscript_versions',
             'ai/第7节文字修改_20261005_v2']
    for tree in trees:
        for file in (ROOT / tree).rglob('*'):
            if file.is_file() and not file.is_relative_to(REPORT) and file.name != 'current.json':
                if file.is_symlink():
                    raise RuntimeError('保护范围不接受链接：' + str(file))
                immutable[file.relative_to(ROOT).as_posix()] = sha(file)
    for relative in ['refs/Tang_Zhang_2026_BMB.pdf', 'latex/references.bib', 'latex/elegantpaper.cls']:
        if (ROOT / relative).is_file():
            immutable[relative] = sha(ROOT / relative)
    figures = {item['image']: sha(ROOT / 'latex/figures' / item['image']) for item in inventory(main)['figures']}
    if len(figures) != 24:
        raise RuntimeError('正式图件不是预期24幅')
    # 源码在任何任务编辑前保留，生成运行记录不覆盖旧备份。
    for file in list((ROOT / 'reproducibility').glob('*.py')) + list((ROOT / 'reproducibility/joint_extra').glob('*.py')):
        target = BACKUP / file.relative_to(ROOT)
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target)
    record = {'baseline_commit': commit, 'version': VERSION,
              'initial_git_status': subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True, encoding='utf-8'),
              'backup': str(BACKUP), 'immutable_files': immutable, 'formal_figures': figures,
              'main_inventory': inventory(main), 'supplement_inventory': inventory(supplement),
              'acceptance_sha256': sha(ROOT / 'reproducibility/joint_extra/acceptance.json'),
              'evidence_boundary': '仅基准锁定；不是科学复算或出版验收。'}
    dump(path, record)
    print(json.dumps({'baseline_locked': True, 'protected_files': len(immutable), 'figures': len(figures)}))


def protect(name, source_directory=None):
    from manuscript_version import inventory
    old = json.loads((REPORT / 'baseline.json').read_text(encoding='utf-8'))
    prior = (BACKUP / 'latex/flatten_curve_analysis_cn.tex').read_text(encoding='utf-8-sig')
    source = Path(source_directory or ROOT/'latex').resolve()
    if not source.is_relative_to(ROOT) or source.is_symlink():
        raise ValueError('稿源保护核查路径越界或为链接')
    current = (source / 'flatten_curve_analysis_cn.tex').read_text(encoding='utf-8-sig')
    supplement = (source / 'flatten_curve_supplement_cn.tex').read_text(encoding='utf-8-sig')
    changed = [relative for relative, expected in old['immutable_files'].items()
               if not (ROOT / relative).is_file() or sha(ROOT / relative) != expected]
    figures = [relative for relative, expected in old['formal_figures'].items()
               if sha(ROOT / 'latex/figures' / relative) != expected]
    proof_pattern = r'\\begin\{proof\}.*?\\end\{proof\}'
    equation_pattern = r'\\begin\{(equation|align)\}.*?\\end\{\1\}'
    checks = {'immutable_files_unchanged': not changed,
              'only_approved_figure_changed': set(figures) <= {'joint_v2/joint_frontier_baseline.pdf'},
              'main_inventory_equal': inventory(current) == old['main_inventory'],
              'supplement_inventory_equal': inventory(supplement) == old['supplement_inventory'],
              'proofs_equal': re.findall(proof_pattern, prior, re.S) == re.findall(proof_pattern, current, re.S),
              'numbered_equations_equal': [m.group(0) for m in re.finditer(equation_pattern, prior, re.S)] == [m.group(0) for m in re.finditer(equation_pattern, current, re.S)],
              'citations_equal': re.findall(r'\\cite\w*\{[^}]+\}', prior) == re.findall(r'\\cite\w*\{[^}]+\}', current),
              'sec9_equal': section(prior, 'sec:dominance', 'sec:discussion') == section(current, 'sec:dominance', 'sec:discussion'),
              'acceptance_unchanged': sha(ROOT / 'reproducibility/joint_extra/acceptance.json') == old['acceptance_sha256']}
    record = {'passed': all(checks.values()), 'checks': checks, 'changed_protected_files': changed,
              'changed_formal_figures': figures, 'source_directory': str(source),
              'main_sha256': sha(source / 'flatten_curve_analysis_cn.tex'),
              'supplement_sha256': sha(source / 'flatten_curve_supplement_cn.tex')}
    dump(REPORT / (name + '.json'), record)
    patch = ''.join(difflib.unified_diff(prior.splitlines(True), current.splitlines(True), fromfile='baseline.tex', tofile='current.tex'))
    (REPORT / (name + '.patch')).write_text(patch, encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False))
    if not record['passed']:
        raise RuntimeError('保护核查失败，禁止发布')


def scientific_regression():
    """静态对照本轮已实际完成结果；本步骤本身不执行模型。"""
    from compare_runs import _json_errors
    old = ROOT/'reproducibility/results/joint_integration_20261004/joint_extra'
    parent = ROOT/'reproducibility/runs'/VERSION
    tasks = ['compare_baseline.csv', 'compare_xian.csv', 'trajectories_baseline.csv',
             'trajectories_xian.csv', 'capacity.json', 'capacity_baseline.npz', 'capacity_xian.npz',
             'capacity_traj_baseline.csv', 'capacity_traj_xian.csv', 'phase.json',
             'phase_baseline.npz', 'phase_xian.npz', 'candidate_checks_A.json',
             'candidate_checks_B.json', 'candidate_checks_C.json', 'alpha_family_baseline.csv',
             'TDINN_external_reference.json']

    def rows(path):
        with path.open(encoding='utf-8-sig', newline='') as stream:
            return list(csv.DictReader(stream))

    records = []
    for name in ('run_1', 'run_2'):
        fresh = parent/name/'joint_extra'
        validation = json.loads((fresh/'validation.json').read_text(encoding='utf-8'))
        if validation.get('passed') is not True or not all(validation['tasks'][t]['passed'] for t in 'ABCD'):
            raise RuntimeError('A-D 尚未实际全部通过：' + name)
        for filename in tasks:
            a, b = old/filename, fresh/filename
            errors = []
            if a.suffix == '.npz':
                with np.load(a) as aa, np.load(b) as bb:
                    if aa.files != bb.files:
                        errors.append('array keys')
                    else:
                        for key in aa.files:
                            if not np.array_equal(aa[key], bb[key], equal_nan=True):
                                errors.append(key)
            elif a.suffix == '.json':
                errors = _json_errors(json.loads(a.read_text(encoding='utf-8')),
                                      json.loads(b.read_text(encoding='utf-8')), old, fresh)
            elif a.read_bytes() != b.read_bytes():
                errors.append('CSV bytes changed')
            records.append({'run': name, 'file': filename, 'passed': not errors,
                            'exact_bytes_equal': sha(a) == sha(b), 'errors': errors})
        old_rows = rows(old/'frontier_baseline.csv')
        new_rows = rows(fresh/'frontier_baseline.csv')
        lookup = {float(row['kappa']): row for row in new_rows}
        errors = []
        for old_row in old_rows:
            kappa = float(old_row['kappa'])
            if kappa not in lookup:
                errors.append({'kappa': kappa, 'field': 'missing old float'})
                continue
            for key, expected in old_row.items():
                if key in {'duration_gap_before', 'connection_group'}:
                    continue
                actual = lookup[kappa][key]
                try:
                    matched = math.isclose(float(expected), float(actual), rel_tol=1e-10, abs_tol=1e-9)
                except ValueError:
                    matched = expected == actual
                if not matched:
                    errors.append({'kappa': kappa, 'field': key, 'old': expected, 'new': actual})
        records.append({'run': name, 'file': 'frontier_baseline.csv:original_points',
                        'passed': not errors and len(new_rows) == 470 and len(old_rows) == 310,
                        'old_count': len(old_rows), 'new_count': len(new_rows), 'errors': errors,
                        'old_gaps': sum(row['duration_gap_before']=='True' for row in old_rows),
                        'new_gaps': sum(row['duration_gap_before']=='True' for row in new_rows),
                        'connection_fields_recomputed_not_regression_targets': True})
        old_diag = json.loads((old/'candidate_checks_D.json').read_text(encoding='utf-8'))
        new_diag = json.loads((fresh/'candidate_checks_D.json').read_text(encoding='utf-8'))
        diag_lookup = {row['kappa']: row for row in new_diag['scan']}
        diag_errors = []
        for row in old_diag['scan']:
            if row['kappa'] not in diag_lookup:
                diag_errors.append('missing kappa ' + str(row['kappa']))
            else:
                diag_errors.extend(_json_errors(row, diag_lookup[row['kappa']], old, fresh))
        diag_errors.extend(_json_errors(old_diag['time_representatives'], new_diag['time_representatives'], old, fresh))
        records.append({'run': name, 'file': 'candidate_checks_D.json:original_points_and_time_representatives',
                        'passed': not diag_errors, 'old_scan_count': len(old_diag['scan']),
                        'new_scan_count': len(new_diag['scan']), 'errors': diag_errors})
    record = {'passed': all(r['passed'] for r in records), 'records': records,
              'numeric_tolerance': {'relative': 1e-10, 'absolute': 1e-9},
              'scope': '本轮独立 A-D 计算与指定旧验收逐项回归；不重新计算旧上游或证明一般前沿。'}
    dump(REPORT/'scientific_regression.json', record)
    print(json.dumps({'passed': record['passed'], 'records': len(records)}, ensure_ascii=False))
    if not record['passed']:
        raise RuntimeError('旧点或 A-C 回归失败，禁止发布')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['baseline', 'protect', 'science'])
    parser.add_argument('--name', default='protection_current')
    parser.add_argument('--source-directory', type=Path)
    args = parser.parse_args()
    if args.mode == 'baseline':
        baseline()
    elif args.mode == 'science':
        scientific_regression()
    else:
        protect(args.name, args.source_directory)
