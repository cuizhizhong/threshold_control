"""NR-7（G-N3 方案 B）：从回流分支按固定提交导入补充材料用到的指数回流数值，记录来源，不重算。

N10：共用结果由一个分支产出、另一分支按源提交复用，用 `git show <提交>:<路径>` 读取，不合并分支。这里只导入回流分支 R7-3（G2 作者
2026-10-15 通过）的 `r7_return/results/r7_3_exponential_return.json` 中平均停留 7、14、30 d、三种控制律、两组参数共 18 条轨迹的
终止时累计感染 `C_term`、退出后是否越过阈值 `crossing` 与相关字段；不导入其宏文件 `r7_numbers.tex`，不运行回流代码。

终点：退出后 I 首次降到 1 时截断（与本稿清零时间的约定相同）；控制律：仅隔离、仅减少接触、迁移律（`opt_noreturn`，即 ω=0 的成本最优
律原样用于 ω>0，不重新优化，不称成本最优）。导入内容的 SHA-256 与 git blob 记入输出，供 `make_numbers.py` 的来源映射引用。

运行：conda run --no-capture-output -n thesis python nr_audit/import_return_numbers.py
输出：results/return_import.json
"""
import hashlib
import json
import subprocess

from audit_common import ROOT, dump

SOURCE_BRANCH = 'research/return-effects'
SOURCE_COMMIT = 'bb52b96'          # R7-3：G2 通过（回流分支 AGENTS/STATUS 记录，作者 2026-10-15）
SOURCE_PATH = 'r7_return/results/r7_3_exponential_return.json'
STAYS = (7, 14, 30)
LAWS = ('q_only', 'opt_noreturn', 'c_only')
KEYS = ('status', 'dt', 'J', 'C_term', 'L', 'crossing', 't_end', 'termination', 'C_term_below_L', 'U_below_Sc_at_end')


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=True).stdout


def main():
    raw = git('show', f'{SOURCE_COMMIT}:{SOURCE_PATH}')
    blob = git('rev-parse', f'{SOURCE_COMMIT}:{SOURCE_PATH}').decode().strip()
    full_commit = git('rev-parse', SOURCE_COMMIT).decode().strip()
    d = json.loads(raw.decode('utf-8'))
    assert d['model'] == 'exponential_return' and d['endpoint'] == 'first_below_one'
    assert d['weights'] == {'w_c': 1.0, 'w_q': 2.0}
    runs = {}
    for case in ('base', 'xian'):
        for s in STAYS:
            for law in LAWS:
                r = d['runs'][f'{case}|{s}|{law}']
                assert r['status'] == 'ok' and r['termination'] == 'first_below_one' and r['reached']
                runs[f'{case}|{s}|{law}'] = {k: r[k] for k in KEYS}
    out = dict(
        description='NR-7：自回流分支按固定提交导入的指数回流数值（不重算）。平均停留 7、14、30 d，三种控制律，两组参数，共 18 条；'
                    '终点为退出后 I 首次 <1 的截断；迁移律 = ω=0 成本最优律原样用于 ω>0，不称成本最优。',
        source=dict(branch=SOURCE_BRANCH, commit=full_commit, path=SOURCE_PATH, blob=blob,
                    sha256=hashlib.sha256(raw).hexdigest(),
                    acceptance='回流分支 R7-3 的 G2（作者 2026-10-15 通过；终点按作者 10-15 决定取首次 I<1 截断）',
                    use='N10 复用：模型（含回流，ω>0）、参数（AGENTS 第 8 节）、控制律、初值（S_q(0)=0）、终点均同回流分支记录；'
                        '本分支不重算，只在补充材料的小表中引用'),
        runs=runs,
        all_not_crossed=all(r['crossing'] == 'not_crossed' for r in runs.values()),
        all_above_L=all(not r['C_term_below_L'] for r in runs.values()))
    assert out['all_not_crossed'] and out['all_above_L']
    dump('return_import.json', out)
    print(f"导入 {len(runs)} 条；来源 {SOURCE_COMMIT} blob {blob[:8]}；全部未越过阈值：{out['all_not_crossed']}；全部不低于 L：{out['all_above_L']}")


if __name__ == '__main__':
    main()
