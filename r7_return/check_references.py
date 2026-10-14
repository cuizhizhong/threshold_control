"""R7-1 与参考值的对照：生成 results/r7_1_reference_check.json（全精度）与 .md（展示）。

运行：conda run -n thesis python r7_return/check_references.py
内容：
  1. ω = 0：四种控制的 Δt、J（S 坐标求积与事件法）对照全精度参考；控制期感染、计至清零、t→∞；
  2. 立即返回对照模型：四种控制的 Δt、J、K_q 与执行计划第 5 节对照；切换位置与退出附近分担比例；
  3. 平均停留 14 天：事件法、反馈重放与执行计划第 5 节旧值；
  4. 释放用数（ω = 0，仅隔离）；
  5. 网格：N_x（逐状态最小化，只核对根法）与 N_z（状态求积与切换位置）分开报告。
本脚本只做对照，不是 R7-3 的正式数值表。
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import alloc as AL  # noqa: E402
import endpoints as E  # noqa: E402
import references as REF  # noqa: E402
import replay_feedback as RF  # noqa: E402
import simulate as S  # noqa: E402
from params import CASES  # noqa: E402


def rel(a, b):
    return abs(a - b) / abs(b)


def main():
    refs, derived = REF.load_noreturn_refs()
    out = dict(noreturn={}, immediate={}, omega14={}, release={}, grids={})
    md = []

    # 1. ω = 0
    md.append('### ω = 0（全精度参考：reproducibility/.../joint_extra/compare_*.csv）\n')
    md.append('| 参数 | 控制 | Δt 参考 | Δt 求积 | Δt 事件法 | J 参考 | J 求积 | J 事件法 | 最大相对差 |')
    md.append('|---|---|---|---|---|---|---|---|---|')
    for case in ('base', 'xian'):
        for law in REF.LAWS_NORETURN:
            a = E.arc_noreturn(CASES[case], law)
            ev = S.run(CASES[case], law)
            r = refs[(case, law)]
            d = dict(dt_ref=r['dt'], dt_quad=a['dt'], dt_event=ev['dt'], J_ref=r['J'], J_quad=a['J'],
                     J_event=ev['J'], arc_inf_ref=r['plateau_infections'], arc_inf_identity=a['infections_identity'],
                     arc_inf_flux_event=ev['arc_infections'], C_t_end_ref=r['total_infections_to_clearance'],
                     C_t_end_event=ev['C_t_end'], t_end_ref=r['t_end'], t_end_event=ev['t_end'],
                     C_inf_event=ev['C_inf'], tail_increment=ev['tail_increment'], L=CASES[case].L_bound,
                     identity_residual_rel=ev['identity_residual_rel'],
                     event_residuals=dict(trigger=ev['trigger_event_rel'], exit=ev['exit_event_rel'],
                                          clearance=ev['clearance_event_abs']))
            d['max_rel'] = max(rel(d['dt_quad'], d['dt_ref']), rel(d['dt_event'], d['dt_ref']),
                               rel(d['J_quad'], d['J_ref']), rel(d['J_event'], d['J_ref']))
            out['noreturn'][f'{case}|{law}'] = d
            md.append(f"| {case} | {law} | {d['dt_ref']:.6f} | {d['dt_quad']:.6f} | {d['dt_event']:.6f} | "
                      f"{d['J_ref']:.6f} | {d['J_quad']:.6f} | {d['J_event']:.6f} | {d['max_rel']:.1e} |")
    md.append('\n| 参数 | 控制 | 控制期感染 参考 / 流量积分 | 计至清零 参考 / 事件法 | t→∞（S_∞ 补尾） | 执行计划 t→∞ | L = U(0)-S_c |')
    md.append('|---|---|---|---|---|---|---|')
    for case in ('base', 'xian'):
        for law in REF.LAWS_NORETURN:
            d = out['noreturn'][f'{case}|{law}']
            plan = REF.PLAN_NORETURN_INF[case] if law == 'q_only' else None
            md.append(f"| {case} | {law} | {d['arc_inf_ref']:.6g} / {d['arc_inf_flux_event']:.6g} | "
                      f"{d['C_t_end_ref']:.7g} / {d['C_t_end_event']:.7g} | {d['C_inf_event']:.7g} | "
                      f"{format(plan, 'g') if plan is not None else '—'} | {d['L']:.7g} |")

    # 2. 立即返回
    md.append('\n### 立即返回对照模型（执行计划第 5 节）\n')
    md.append('| 参数 | 控制 | Δt 计划 | Δt 求积 | J 计划 | J 求积 | K_q | 相对差 |')
    md.append('|---|---|---|---|---|---|---|---|')
    for case in ('base', 'xian'):
        st = E.start_state_immediate(CASES[case])
        out['immediate'][f'{case}|state'] = dict(S_star_inf=st['S_star'], S_c=CASES[case].S_c,
                                                 infections=st['S_star'] - CASES[case].S_c,
                                                 I_peak_ir=st['I_peak_ir'], A=st['A'],
                                                 lambertw_vs_brentq_rel=st['lambertw_vs_brentq_rel'],
                                                 plan=REF.PLAN_IMMEDIATE_STATE[case])
        for law in ('q_only', 'alpha', 'opt_immediate', 'c_only'):
            a = E.arc_immediate(CASES[case], law)
            p = REF.PLAN_IMMEDIATE[(case, law)]
            d = dict(dt_plan=p['dt'], dt=a['dt'], J_plan=p['J'], J=a['J'], Kq=a['Kq_quad'],
                     Kq_identity=a['Kq_identity'], infections=a['infections'],
                     max_rel=max(rel(a['dt'], p['dt']), rel(a['J'], p['J'])))
            if law == 'opt_immediate':
                d['breakpoints'] = a['structure']['breakpoints']
                d['steep_points'] = a['structure']['steep_points']
            out['immediate'][f'{case}|{law}'] = d
            md.append(f"| {case} | {law} | {p['dt']} | {a['dt']:.5f} | {p['J']} | {a['J']:.5f} | "
                      f"{a['Kq_quad']:.6g} | {d['max_rel']:.1e} |")
    z = 1 + 1e-6
    out['immediate']['terminal_share_z=1+1e-6'] = AL.terminal_share(AL.argmin_immediate(z, 1.0, 2.0)[0], z)
    md.append(f"\n切换位置 z = {out['immediate']['base|opt_immediate']['breakpoints'][0]['z']:.12f}（计划 ≈3.000）；"
              f"陡峭点 z = {out['immediate']['base|opt_immediate']['steep_points'][0]:.12f}（2√2 = {2*math.sqrt(2):.12f}）；"
              f"退出附近分担比例 {out['immediate']['terminal_share_z=1+1e-6']:.6f}（计划 ≈0.667）。")
    for case in ('base', 'xian'):
        s = out['immediate'][f'{case}|state']
        md.append(f"{case}：S*_∞ = {s['S_star_inf']:.9g}（计划 {s['plan']['S_star_inf']:g}），"
                  f"S_c = {s['S_c']:.9g}（计划 {s['plan']['S_c']:g}），控制期感染 {s['infections']:.9g}（计划 {s['plan']['infections']:g}）。")

    # 3. 平均停留 14 天
    md.append('\n### 平均停留 14 天（事件法 / 反馈重放 / 执行计划旧值）\n')
    md.append('| 参数 | 控制律 | Δt 事件 / 重放 / 旧 | J 事件 / 重放 / 旧 | 终止时累计感染（尾部判据） | 首次 I<1 时累计感染 / 旧 | 尾部上界 | e |')
    md.append('|---|---|---|---|---|---|---|---|')
    for case in ('base', 'xian'):
        for law in ('q_only', 'opt_noreturn', 'c_only'):
            P = CASES[case]
            ev = S.run(P, law, omega=1 / 14)
            rp = RF.replay(P, AL.get_law(law, P), 1 / 14)
            old = REF.PLAN_OMEGA14_OLD[(case, law)]
            d = dict(dt_event=ev['dt'], dt_replay=rp['dt_ctrl'], dt_old=old['dt'], J_event=ev['J'],
                     J_replay=rp['J'], J_old=old['J'], C_term=ev['C_term'], C_below_one=ev.get('C_below_one'),
                     C_old=old['C_end'], C_replay_first_below_one=rp['inf_total'], tail_bound=ev['tail_bound'],
                     final_reliable=ev['final_reliable'], excess_over_L_rel=ev['excess_over_L_rel'],
                     e=ev['e'], crossing=ev['crossing'], regrowth=ev['regrowth_after_below_one'],
                     termination=ev['termination'], T_term=ev['T_term'],
                     identity_residual_rel=ev['identity_residual_rel'],
                     replay_n_episodes=rp['n_episodes'], replay_n_would_reopen=rp['n_would_reopen'],
                     rel_dt_event_replay=rel(rp['dt_ctrl'], ev['dt']), rel_J_event_replay=rel(rp['J'], ev['J']))
            out['omega14'][f'{case}|{law}'] = d
            md.append(f"| {case} | {law} | {d['dt_event']:.4f} / {d['dt_replay']:.4f} / {d['dt_old']} | "
                      f"{d['J_event']:.4f} / {d['J_replay']:.4f} / {d['J_old']} | {d['C_term']:.7g} | "
                      f"{d['C_below_one']:.7g} / {d['C_old']:g} | {d['tail_bound']:.3g} | {d['e']:.1e} |")

    # 4. 释放
    md.append('\n### 在 t2 释放（ω = 0，仅隔离控制，ξ = 1）\n')
    for case in ('base', 'xian'):
        ev = S.run(CASES[case], 'q_only', xi=1.0)
        d = dict(Sq_t2_over_Sc=ev['Sq_t2_over_Sc'], Re_after_release=ev['Re_after_release'],
                 plan=REF.PLAN_RELEASE[case], e=ev['e'], C_inf=ev['C_inf'])
        out['release'][case] = d
        md.append(f"- {case}：S_q(t2)/S_c = {d['Sq_t2_over_Sc']:.6f}（计划 {d['plan']['Sq_over_Sc']}），"
                  f"R_e(t2⁺) = {d['Re_after_release']:.6f}（计划 {d['plan']['Re']}）。")

    # 5. 网格
    md.append('\n### 网格（N_x 只核对根法；N_z 用于状态求积与切换位置）\n')
    md.append('| 参数 | 模型 | max(网格最小 - 根法最小)：N_x = 2001 / 4001 / 8001 |')
    md.append('|---|---|---|')
    for case in ('base', 'xian'):
        P = CASES[case]
        for model in ('noreturn', 'immediate'):
            if model == 'noreturn':
                zs = E.start_state_noreturn(P)['z_star']
                am = lambda z: AL.argmin_noreturn(z, P.z_bar, 1.0, 2.0)
                dens = lambda z: (lambda x: AL.density_noreturn(x, z, P.z_bar, 1.0, 2.0))
            else:
                zs = E.start_state_immediate(P)['z_star']
                am = lambda z: AL.argmin_immediate(z, 1.0, 2.0)
                dens = lambda z: (lambda x: AL.density_immediate(x, z, 1.0, 2.0))
            gaps = {}
            for n in (2001, 4001, 8001):
                g = []
                for zz in np.linspace(1.001, zs, 300):
                    zz = float(zz)
                    g.append(AL.grid_min(dens(zz), zz, n)[1] - am(zz)[1])
                gaps[n] = dict(max=float(np.max(g)), min=float(np.min(g)))
            out['grids'][f'{case}|{model}|N_x'] = gaps
            md.append(f"| {case} | {model} | {gaps[2001]['max']:.2e} / {gaps[4001]['max']:.2e} / {gaps[8001]['max']:.2e} |")
    md.append('\n| 参数 | 控制律 | N_z | Δt | J | 切换位置 z | 与 quad 的 Δt 相对差 |')
    md.append('|---|---|---|---|---|---|---|')
    for case in ('base', 'xian'):
        for model, law in (('noreturn', 'opt_noreturn'), ('immediate', 'opt_immediate')):
            for nz in (1001, 2001, 4001):
                a = E.arc(model, CASES[case], law, N_z=nz)
                bz = a['structure']['breakpoints'][0]['z']
                out['grids'][f'{case}|{law}|N_z={nz}'] = dict(dt=a['dt'], J=a['J'], z_switch=bz,
                                                              dt_quad=a['dt_quad'], J_quad=a['J_quad'])
                md.append(f"| {case} | {law} | {nz} | {a['dt']:.10f} | {a['J']:.10f} | {bz:.12f} | "
                          f"{rel(a['dt'], a['dt_quad']):.1e} |")

    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
    with open(os.path.join(HERE, 'results', 'r7_1_reference_check.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, default=float)
    with open(os.path.join(HERE, 'results', 'r7_1_reference_check.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(md) + '\n')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
