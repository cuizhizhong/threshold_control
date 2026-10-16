"""NR-7：无回流 t→∞ 累计感染的交叉核对（NR 计划 5.2 节 N6 的核对部分，不重复生产回流分支的表）。

回流分支（research/return-effects）在 R7-3 第 4 项（提交 bb52b96，G2 通过）给出了无回流模型（ω=0）四种控制、两组参数的
t→∞ 累计新增感染 C_π(0) 与 L = U(0) − S_c。本脚本用本模块的闭式路径（定理 3.7 以 S_∞ 代替 S_end）独立重算，并与回流分支
记录的数值（手抄自 `r7_return/results/r7_3_numerics.md` 第 4 节，只读）对照；同时核对条件性推论的前提 C_π(0) < L。
模型、参数、控制律（默认权重）、终点（t→∞，不用计至 I=1 的数）与本稿一致；不实现 ω>0。

运行：conda run --no-capture-output -n thesis python nr_audit/audit_noreturn_inf.py
输出：results/noreturn_inf_crosscheck.json、results/noreturn_inf_crosscheck.md
"""
import params as PR
import state_integrals as SI
from audit_common import RESULTS, dump

# 回流分支 R7-3 第 4 项的记录值（r7_3_numerics.md 第 4 节，提交 bb52b96；只读来源，手抄）
RETURN_BRANCH = {
    ('base', 'q_only'): 286.5897318, ('base', 'alpha'): 324.2472668,
    ('base', 'opt'): 307.4986535, ('base', 'c_only'): 629.5087552,
    ('xian', 'q_only'): 2377947.609, ('xian', 'alpha'): 2639000.128,
    ('xian', 'opt'): 2534833.094, ('xian', 'c_only'): 3856646.091,
}
RETURN_BRANCH_L = {'base': 586.83983, 'xian': 10188874.59}


def main():
    rows = []
    for name, P in (('base', PR.BASE), ('xian', PR.XIAN)):
        L = P.S0 + P.Sq0 - P.S_c
        for law in ('q_only', 'alpha', 'opt', 'c_only'):
            st = SI.state_path(SI.Policy(P, law))
            c_inf, c_clr = st['total_infections_inf'], st['total_infections_to_clearance']
            r = RETURN_BRANCH[(name, law)]
            rows.append(dict(case=name, law=law, C_inf=c_inf, C_to_clearance=c_clr, L=L,
                             return_branch=r, rel_vs_return_branch=abs(c_inf - r) / r,
                             premise_C_lt_L=bool(c_inf < L), ratio_L_over_C=L / c_inf))
    Ldiff = {n: abs(next(r['L'] for r in rows if r['case'] == n) - v) / v for n, v in RETURN_BRANCH_L.items()}
    out = dict(description='NR-7：无回流 t→∞ 累计感染与 L=U(0)−S_c 的交叉核对（模型 (2.1)，默认权重，S_q(0)=0）。'
                           'return_branch 为回流分支 bb52b96 记录值（手抄，只读来源）。',
               rows=rows, L_rel_diff=Ldiff, max_rel_vs_return_branch=max(r['rel_vs_return_branch'] for r in rows))
    dump('noreturn_inf_crosscheck.json', out)
    L = ['# NR-7 无回流 t→∞ 累计感染的交叉核对', '',
         '| 参数 | 控制 | C_π(0)（t→∞，本模块） | 计至清零 | 回流分支记录值 | 相对差 | L = U(0)−S_c | C_π(0)<L | L/C_π(0) |',
         '|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        L.append(f"| {r['case']} | {r['law']} | {r['C_inf']:.7g} | {r['C_to_clearance']:.7g} | {r['return_branch']:.7g} | "
                 f"{r['rel_vs_return_branch']:.1e} | {r['L']:.7g} | {'满足' if r['premise_C_lt_L'] else '不满足'} | {r['ratio_L_over_C']:.2f} |")
    L += ['', f"L 与回流分支记录值的相对差：{Ldiff}；C_π(0) 的最大相对差 {out['max_rel_vs_return_branch']:.2e}。"]
    (RESULTS / 'noreturn_inf_crosscheck.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
