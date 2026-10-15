"""NR-3 N4：收敛（控制网格、状态网格与积分容差分开报告）。

(a) 控制网格 N_x = 2001/4001/8001：只核对逐状态根法（网格值是否低于根法值、最小点的 x 差）；不参与求积。
(b) 状态网格 N_z = 1001/2001/4001/8001：成本最优控制的 Δt、J 与结构变化点位置（N_z 也是结构扫描的网格）；
    与 N_z = 8001 及 quad 比较。
(c) 积分容差三档（rtol、各分量 atol、max_step 同时改变）：基准（1e-12、×1、0.5 d）、收紧（1e-13、×0.1、0.25 d）、
    放宽（1e-11、×10、1 d）；两组参数四种控制、能力代表点上的成本最优控制、西安的 TDINN 与常规控制。报告核心量
    在档间的最大相对变化，以及事件残差、平台偏离、质量与恒等式残差。solve_ivp 没有单独的事件容差参数。

运行：conda run --no-capture-output -n thesis python nr_audit/audit_convergence.py
输出：results/convergence.json、results/convergence.md
"""
import math

import numpy as np

import allocation as AL
import params as PR
import simulate as SM
import state_integrals as SI
import tdinn as TD
from audit_common import RESULTS, dump, rel

TIERS = {'base': SM.Config(), 'tight': SM.Config(rtol=1e-13, atol_scale=0.1, max_step=0.25),
         'loose': SM.Config(rtol=1e-11, atol_scale=10.0, max_step=1.0)}
WEIGHTS = {'base': (2.0, 3.13, 3.24, 13.0, 13.44), 'xian': (2.0, 2.65, 2.74, 7.41, 7.66)}


def control_grid():
    out = []
    for case in ('base', 'xian'):
        P = PR.CASES[case]
        zs = SI.start_state(P)['z_star']
        settings = [('free', r, None) for r in WEIGHTS[case]] + [('cap', 2.0, PR.REP_CAPACITY[case])]
        for kind, r, cap in settings:
            x_min, h = AL.cap_factors(P, cap)
            gaps, xg = {}, {}
            for N_x in (2001, 4001, 8001):
                g = [AL.grid_check(float(z), P.z_bar, 1.0, r, 0.0, x_min, h, N_x)
                     for z in np.r_[1 + 1e-7, 1 + 1e-4, np.linspace(1.002, zs, 198)]]
                gaps[N_x] = max(x['gap_rel'] for x in g)
                xg[N_x] = max(x['x_gap'] for x in g)
            out.append(dict(case=case, kind=kind, r=r, n_states=200, max_gap_rel=gaps, max_x_gap=xg))
    return out


def state_grid():
    out = []
    for case in ('base', 'xian'):
        P = PR.CASES[case]
        for kind, r, cap in [('free', r, None) for r in WEIGHTS[case]] + [('cap', 2.0, PR.REP_CAPACITY[case])]:
            res = {}
            for N_z in (1001, 2001, 4001, 8001):
                pol = SI.Policy(P, 'opt', cap=cap, wq=r, N_z=N_z)
                a = SI.arc_integrals(pol, N_z=N_z, with_quad=(N_z == 8001))
                res[N_z] = dict(dt=a['dt'], J=a['J'], breaks=pol.breaks, splits=a['simpson']['splits'],
                                dt_quad=a.get('dt_quad'), J_quad=a.get('J_quad'))
            ref = res[8001]
            rows = {N: dict(dt_rel=rel(v['dt'], ref['dt']), J_rel=rel(v['J'], ref['J']),
                            n_breaks=len(v['breaks']),
                            max_break_shift=max((abs(b - c) for b, c in zip(v['breaks'], ref['breaks'])), default=0.0)
                            if len(v['breaks']) == len(ref['breaks']) else None)
                    for N, v in res.items()}
            out.append(dict(case=case, kind=kind, r=r, values=res, vs_8001=rows,
                            quad_rel=dict(dt=rel(ref['dt'], ref['dt_quad']), J=rel(ref['J'], ref['J_quad']))))
    return out


CORE = ('t1', 'dt', 'J', 't_end', 'total_infections_to_clearance', 'total_infections_inf', 'peak_I_plus_Iq_over_eta',
        'arc_Sq_new', 'arc_infections')
RESID = ('plateau_abs_dev', 'mass_residual_persons', 'identity_residual_rel', 'exit_S_error', 'exit_I_error',
         'clearance_I_error', 'n_steps')


def tolerance_tiers():
    out = []
    cases = [(c, l, False) for c in ('base', 'xian') for l in ('q_only', 'c_only', 'alpha', 'opt')]
    cases += [(c, 'opt', True) for c in ('base', 'xian')]
    for case, law, cap in cases:
        P = PR.CASES[case]
        pol = SI.Policy(P, law, cap=PR.REP_CAPACITY[case] if cap else None)
        runs = {t: SM.run(pol, cfg) for t, cfg in TIERS.items()}
        trig = {t: abs(o['I_t1'] / P.eta - 1) for t, o in runs.items()}
        ch = {k: max(rel(runs[t][k], runs['base'][k]) for t in ('tight', 'loose')) for k in CORE}
        out.append(dict(case=case, law=law, capacity=cap, max_rel_change_vs_base=ch,
                        tight_vs_base={k: rel(runs['tight'][k], runs['base'][k]) for k in CORE},
                        residuals={t: dict({k: o[k] for k in RESID}, trigger_rel=trig[t]) for t, o in runs.items()},
                        values={t: {k: o[k] for k in CORE} for t, o in runs.items()}))
    X = PR.XIAN
    for name, ctrl in (('tdinn', TD.tdinn), ('routine', TD.routine_of(X))):
        runs = {t: TD.run(X, ctrl, cfg)[0] for t, cfg in TIERS.items()}
        keys = ('t_end', 'total', 'J', 'peak_I')
        out.append(dict(case='xian', law=name, capacity=False,
                        max_rel_change_vs_base={k: max(rel(runs[t][k], runs['base'][k]) for t in ('tight', 'loose'))
                                                if runs['base'][k] else max(abs(runs[t][k]) for t in TIERS) for k in keys},
                        residuals={t: dict(mass_residual_persons=o['mass_residual_persons'],
                                           identity_residual_rel=o['identity_residual_rel'],
                                           clearance_I_error=o['clearance_I_error']) for t, o in runs.items()},
                        values={t: {k: o[k] for k in keys} for t, o in runs.items()}))
    return out


def main():
    cg, sg, tt = control_grid(), state_grid(), tolerance_tiers()
    dump('convergence.json', dict(description=__doc__.split('\n\n')[0],
                                  tiers={k: v.__dict__ for k, v in TIERS.items()},
                                  control_grid=cg, state_grid=sg, tolerance_tiers=tt))
    L = ['# NR-3 N4：收敛', '', '## (a) 控制网格 N_x（只核对根法）', '',
         '| 参数 | 设置 | r | 网格低于根法的最大相对量 N_x=2001/4001/8001 | 最小点 x 的最大差 |', '|---|---|---|---|---|']
    for r in cg:
        L.append(f"| {r['case']} | {r['kind']} | {r['r']} | " + ' / '.join(f"{r['max_gap_rel'][n]:.1e}" for n in (2001, 4001, 8001))
                 + ' | ' + ' / '.join(f"{r['max_x_gap'][n]:.1e}" for n in (2001, 4001, 8001)) + ' |')
    L += ['', '## (b) 状态网格 N_z（成本最优控制，相对 N_z = 8001）', '',
          '| 参数 | 设置 | r | Δt：1001/2001/4001 | J：1001/2001/4001 | 结构点位移（4001） | N_z=8001 与 quad：Δt / J |', '|---|---|---|---|---|---|---|']
    for r in sg:
        v = r['vs_8001']
        L.append(f"| {r['case']} | {r['kind']} | {r['r']} | " + ' / '.join(f"{v[n]['dt_rel']:.1e}" for n in (1001, 2001, 4001))
                 + ' | ' + ' / '.join(f"{v[n]['J_rel']:.1e}" for n in (1001, 2001, 4001))
                 + f" | {v[4001]['max_break_shift']} | {r['quad_rel']['dt']:.1e} / {r['quad_rel']['J']:.1e} |")
    L += ['', '## (c) 积分容差三档（核心量相对基准档的最大相对变化；残差取三档最大）', '',
          '| 参数 | 控制 | 核心量最大变化 | 平台偏离（人） | 质量残差（人） | 恒等式残差/初始易感者 | 触发残差 | 退出 S 误差（人） | 清零 I 误差（人） |',
          '|---|---|---|---|---|---|---|---|---|']
    for r in tt:
        res = r['residuals']
        mx = lambda k: max(abs(res[t].get(k, 0.0) or 0.0) for t in TIERS)
        lab = r['law'] + ('（能力）' if r['capacity'] else '')
        L.append(f"| {r['case']} | {lab} | {max(r['max_rel_change_vs_base'].values()):.1e} | {mx('plateau_abs_dev'):.1e} | "
                 f"{mx('mass_residual_persons'):.1e} | {mx('identity_residual_rel'):.1e} | {mx('trigger_rel'):.1e} | "
                 f"{mx('exit_S_error'):.1e} | {mx('clearance_I_error'):.1e} |")
    (RESULTS / 'convergence.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
