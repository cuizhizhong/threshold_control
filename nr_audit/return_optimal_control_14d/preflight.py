"""只记录输入、环境与保护文件身份，不启动科学求解。"""
import hashlib
import importlib.metadata
import json
import pathlib
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    out = HERE / 'results'
    out.mkdir(exist_ok=True)
    initial = out / 'protected_initial.json'
    paths = subprocess.check_output(['git', 'ls-files', '-z', 'paper', 'r7_return',
        'reproducibility', 'refs', '真实数据'], cwd=ROOT).decode('utf-8').split('\0')
    protected = {p: {'sha256': sha(ROOT / p), 'size': (ROOT / p).stat().st_size}
                 for p in paths if p and (ROOT / p).is_file()}
    if not initial.exists():
        initial.write_text(json.dumps(protected, ensure_ascii=False, indent=2), encoding='utf-8')
    sources = ['r7_return/params.py', 'r7_return/model.py', 'r7_return/alloc.py',
        'r7_return/results/r7_3_exponential_return.json',
        'r7_return/results/r7_3_convergence.json', 'nr_audit/results/return_import.json',
        'ai/return_optimal_control_numerical_plan_20261027.md']
    expected = {'r7_return/results/r7_3_exponential_return.json':
        '3ca0a3d245314230df83c0717e07ed73ab67129803c284ea46eab8921cdfb05f',
        'r7_return/results/r7_3_convergence.json':
        'bbd7e4ea49a1d8e94623c3c2d27bdc67d690b592a5c189a01129a17f150b1d3b'}
    hashes = {p: sha(ROOT / p) for p in sources}
    for p, expected_hash in expected.items():
        if hashes[p] != expected_hash:
            raise RuntimeError(f'冻结科学来源身份不符：{p}')
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(),
        'authorization': '作者于2026-10-27明确启动计划，仅数值研究核验，不改论文、不推送。',
        'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
        'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'git_status_initial': subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
        'packages': {p: importlib.metadata.version(p) for p in ['numpy', 'scipy', 'matplotlib', 'pytest']},
        'sources': hashes, 'protected_file_count': len(protected),
        'dependency_attempts': [
            {'action': 'task-local pip install casadi --no-deps in sandbox',
             'status': 'failed', 'reason': 'proxy 127.0.0.1:7897 WinError 10013'},
            {'action': 'same install with authorized network escalation',
             'status': 'succeeded', 'version': '3.8.2', 'location': '_runtime'}],
        'scope': {'cases': ['base', 'xian'], 'mean_stay_days': 14,
                  'objectives': ['time', 'infections', 'cost'],
                  'postexit_threshold_required': True,
                  'new_scientific_optimization_calls': 0}}
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copyfile(ROOT / sources[-1], HERE / 'plan_snapshot.md')
    print(json.dumps({'source_identity': 'pass', 'protected_files': len(protected),
                      'scientific_solves': 0, 'manifest': str(out / 'manifest.json')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
