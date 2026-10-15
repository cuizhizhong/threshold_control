"""运行 nr_audit 的测试并写出实际结果（不预填任何通过状态）。

用法（仓库根目录）：
    conda run --no-capture-output -n thesis python nr_audit/run_tests.py            # 全部（约 2.5 分钟，235 项）
    conda run --no-capture-output -n thesis python nr_audit/run_tests.py --level quick   # 跳过 slow（约 1.5 分钟）
    conda run --no-capture-output -n thesis python nr_audit/run_tests.py --level smoke   # 小型入口（约 45 秒，基准参数）
全部级别写出 results/nr2_test_report.json（逐项结果、耗时、测试记录的实测量）与 .md；
quick、smoke 写出 results/nr2_test_report_<level>.{json,md}。退出码即 pytest 的退出码。
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import platform
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
LEVELS = {
    'full': [],
    'quick': ['-m', 'not slow'],
    'smoke': ['-m', 'not slow', '-k', 'not roots_vs_grid and not xian and not frontier and not contact_only_never'],
}


class Collector:
    def __init__(self):
        self.rows = []

    def pytest_runtest_logreport(self, report):
        if report.when == 'call' or (report.when == 'setup' and report.outcome != 'passed'):
            props = {k: _plain(v) for k, v in report.user_properties}
            msg = None
            if report.outcome == 'failed':
                msg = str(report.longrepr).splitlines()[-1][:400] if report.longrepr else ''
            elif report.outcome == 'skipped':
                msg = report.longrepr[2] if isinstance(report.longrepr, tuple) else str(report.longrepr)
            self.rows.append(dict(nodeid=report.nodeid, outcome=report.outcome, when=report.when,
                                  duration=round(report.duration, 3), properties=props, message=msg))


def _plain(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return str(v)


def _git(*args):
    try:
        return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--level', choices=list(LEVELS), default='full')
    a = ap.parse_args()
    col = Collector()
    args = [str(HERE / 'tests'), '-q', '-p', 'no:cacheprovider', *LEVELS[a.level]]
    t0 = datetime.datetime.now()
    code = pytest.main(args, plugins=[col])
    t1 = datetime.datetime.now()
    import numpy, scipy, sympy, mpmath
    counts = {}
    for r in col.rows:
        counts[r['outcome']] = counts.get(r['outcome'], 0) + 1
    rep = dict(level=a.level, pytest_args=args, exit_code=int(code), started=t0.isoformat(timespec='seconds'),
               seconds=round((t1 - t0).total_seconds(), 1), counts=counts,
               git_head=_git('rev-parse', 'HEAD'), git_status_short=_git('status', '--short', '--', 'nr_audit'),
               # 运行时被测源码的 SHA-256（换行统一为 LF 后计算，与 git 中的 blob 内容对应，不受检出时 CRLF 转换影响）：
               # 报告与提交中的文件逐一对照（报告先于提交生成时用它确认一致）
               source_sha256={f.relative_to(ROOT).as_posix(): hashlib.sha256(f.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
                              for f in sorted(list(HERE.glob('*.py')) + list((HERE / 'tests').glob('*.py'))) + [HERE / 'pytest.ini']},
               environment=dict(python=sys.version.split()[0], platform=platform.platform(), numpy=numpy.__version__,
                                scipy=scipy.__version__, sympy=sympy.__version__, mpmath=mpmath.__version__,
                                pytest=pytest.__version__),
               tests=col.rows)
    suffix = '' if a.level == 'full' else f'_{a.level}'
    out = HERE / 'results' / f'nr2_test_report{suffix}'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
    md = [f'# nr_audit 测试结果（{a.level}）', '',
          f'- 运行：{rep["started"]}，{rep["seconds"]} s；pytest 退出码 {code}',
          f'- 计数：' + '，'.join(f'{k} {v}' for k, v in sorted(counts.items())),
          f'- 运行时 HEAD：`{rep["git_head"]}`；nr_audit 未提交改动：' + ('无' if not rep['git_status_short'] else '有（见 JSON）'),
          f'- 环境：Python {rep["environment"]["python"]}，numpy {numpy.__version__}，scipy {scipy.__version__}，'
          f'sympy {sympy.__version__}，pytest {pytest.__version__}；{rep["environment"]["platform"]}', '',
          '| 测试 | 结果 | 耗时 (s) | 记录的实测量 |', '|---|---|---|---|']
    for r in col.rows:
        props = '；'.join(f'{k} = {v:.3g}' if isinstance(v, float) else f'{k} = {v}' for k, v in r['properties'].items())
        if r['message']:
            props = (props + '；' if props else '') + r['message'].replace('|', '/')
        md.append(f"| `{r['nodeid'].split('tests/')[-1]}` | {r['outcome']} | {r['duration']} | {props} |")
    out.with_suffix('.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(f'写出 {out.with_suffix(".json").relative_to(ROOT)} 与 .md；计数 {counts}；退出码 {code}')
    return int(code)


if __name__ == '__main__':
    sys.exit(main())
