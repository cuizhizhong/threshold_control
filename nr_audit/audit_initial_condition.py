"""NR-3 N2：西安固定人口初值诊断（六条前向轨迹）。

固定西安的 N、η = 0.002N、传播参数与权重（w_c = 1、w_q = 2）；I0 取拟合值 0.00100659188867187 的 0.1、1、10 倍，
S0 = N - I0，其余初始仓室为零；仅隔离控制与成本最优控制两种，共六条。报告 t1、S*、Δt、J 及相对拟合初值的变化，
另附清零时间与计至清零的总累计新增感染。不重新拟合；不是参数置信区间，也不表示三个初值都与观测相容。
两条路径：状态路径（t1 为式 3.2 的求积）与开环完整方程（t1 为触发事件）。

运行：conda run --no-capture-output -n thesis python nr_audit/audit_initial_condition.py
输出：results/initial_condition.json、results/initial_condition.md
"""
import params as PR
import simulate as SM
import state_integrals as SI
from audit_common import RESULTS, dump, rel

FACTORS = (0.1, 1.0, 10.0)
LAWS = ('q_only', 'opt')
KEYS = ('t1', 'S_star', 'dt', 'J', 't_end', 'total_infections_to_clearance')


def main():
    X = PR.XIAN
    rows = []
    for f in FACTORS:
        I0 = f * PR.XIAN_I0
        P = X.with_(I0=I0, S0=X.N - I0)
        for law in LAWS:
            pol = SI.Policy(P, law)
            st, od = SI.state_path(pol), SM.run(pol)
            rows.append(dict(factor=f, I0=I0, S0=P.S0, law=law,
                             state={k: st[k] for k in KEYS},
                             ode=dict(t1=od['t1'], S_star=od['S_t1'], dt=od['dt'], J=od['J'], t_end=od['t_end'],
                                      total_infections_to_clearance=od['total_infections_to_clearance']),
                             path_max_rel=max(rel(od[k2], st[k]) for k, k2 in
                                              (('t1', 't1'), ('S_star', 'S_t1'), ('dt', 'dt'), ('J', 'J'), ('t_end', 't_end'))),
                             plateau_abs_dev=od['plateau_abs_dev'], identity_residual_rel=od['identity_residual_rel']))
    base = {r['law']: r['state'] for r in rows if r['factor'] == 1.0}
    for r in rows:
        r['change_vs_fit'] = {k: (r['state'][k] - base[r['law']][k]) / base[r['law']][k] for k in KEYS}
        r['change_vs_fit']['t1_abs_days'] = r['state']['t1'] - base[r['law']]['t1']
    span = {law: {k: max(abs(r['change_vs_fit'][k]) for r in rows if r['law'] == law) for k in KEYS}
            for law in LAWS}
    dump('initial_condition.json', dict(
        description='N2：西安固定人口，I0 为拟合值的 0.1/1/10 倍，仅隔离与成本最优控制。change_vs_fit 为相对拟合初值的相对变化'
                    '（t1_abs_days 为绝对变化，天）。',
        settings=dict(N=X.N, eta=X.eta, I0_fit=PR.XIAN_I0, factors=FACTORS, weights=(X.wc, X.wq)),
        rows=rows, max_abs_relative_change=span))
    L = ['# NR-3 N2：西安固定人口初值诊断', '',
         f'N = {X.N:.0f}，η = 0.002N，I0 = 拟合值 {PR.XIAN_I0} 的 0.1、1、10 倍，S0 = N − I0；状态路径（完整方程开环路径与之最大相对差见末列）。', '',
         '| 控制 | I0 倍数 | t1 (d) | S*（人） | Δt (d) | J (d) | t_end (d) | 总累计（人） | Δt1 (d) | S* 相对变化 | Δt 相对变化 | J 相对变化 | 两路径最大相对差 |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        s, c = r['state'], r['change_vs_fit']
        L.append(f"| {r['law']} | {r['factor']:g} | {s['t1']:.4f} | {s['S_star']:.6e} | {s['dt']:.6f} | {s['J']:.6f} | "
                 f"{s['t_end']:.4f} | {s['total_infections_to_clearance']:.6e} | {c['t1_abs_days']:+.4f} | {c['S_star']:+.2e} | "
                 f"{c['dt']:+.2e} | {c['J']:+.2e} | {r['path_max_rel']:.1e} |")
    (RESULTS / 'initial_condition.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L[4:]))


if __name__ == '__main__':
    main()
