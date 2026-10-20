"""NR-3 N1：既有结果回归与稿件保留数字的来源核对（两组参数四种控制、能力代表点、正文与补充材料中
可由无回流模型复算的数字）。

运行（仓库根目录）：
    conda run --no-capture-output -n thesis python nr_audit/audit_baseline.py
输出：results/regression.json（全精度：表 2 的两条路径与旧值、能力代表点、保留数字登记、文中定性陈述的数值核对）
     results/regression.md（汇总）
只读稿件与旧结果文件；不改稿件。判定见 audit_common.Registry。
"""
import math

import numpy as np
from scipy.optimize import brentq, minimize_scalar

import allocation as AL
import params as PR
import simulate as SM
import sources as SRC
import state_integrals as SI
import tdinn as TD
from audit_common import RESULTS, Registry, dump, num, rel, tex_table_rows

NUM = 'paper/sections/06_numerics.tex'
XT = 'paper/sections/07_xian.tex'
# 常量名与 Registry 的证据 ID 保持 NR 历史身份；字符串仅定位 NEW-4g 现稿。
S1 = 'paper/supplement_sections/S2_single_control.tex'
S2 = 'paper/supplement_sections/S3_inflection.tex'
S3 = 'paper/supplement_sections/S6_xian.tex'
S5 = 'paper/supplement_sections/S2_single_control.tex'
S6 = 'paper/supplement_sections/S8_numerics.tex'
TABLE_LAWS = ('c_only', 'alpha', 'q_only', 'opt')
STRAT = {'q_only': 'quarantine_only', 'c_only': 'contact_only', 'alpha': 'alpha_0.5', 'opt': 'minimum_cost'}
REG = Registry()
CLAIMS = []


def claim(id_, where, statement, holds, **values):
    CLAIMS.append(dict(id=id_, where=where, statement=statement, holds=bool(holds), values=values))


# ---------------------------------------------------------------- 单控制的快速量（闭式与状态路径）
def q_only(P):
    return SI.state_path(SI.Policy(P, 'q_only'), with_quad=False)


def dt_q_closed(P):
    return SI.closed_forms(P)['dt_q_only']


def I_peak0(P):
    Sc = P.S_c
    return P.I0 if P.S0 <= Sc else P.I0 + P.kappa0 * (P.S0 - Sc + Sc * math.log(Sc / P.S0))


def c0_trigger(P):
    """触发边界 c_{0,min}(η)：I_max^0(c0) = η（补充 S2，lem:s1:trigger-boundary）。"""
    lo = P.gamma * P.N / (P.beta * (1 - P.q0) * P.S0) * (1 + 1e-12)
    return brentq(lambda c: I_peak0(P.with_(c0=c)) - P.eta, lo, 100.0, xtol=1e-14, rtol=1e-14)


def argmax(f, a, b, n=400):
    """先在 n 点网格上找最大值，再在相邻两格内有界搜索；返回 (x*, f(x*))。"""
    xs = np.linspace(a, b, n)
    fs = np.nan_to_num(np.array([f(x) for x in xs]), nan=-np.inf)
    k = int(np.argmax(fs))
    lo, hi = xs[max(k - 1, 0)], xs[min(k + 1, n - 1)]
    r = minimize_scalar(lambda x: -f(x), bounds=(lo, hi), method='bounded', options=dict(xatol=1e-12))
    return float(r.x), float(-r.fun), bool(0 < k < n - 1)


def lam(P):
    """拐点前时长占比 λ（式 3.13）；无内部拐点时返回 nan。"""
    st = SI.start_state(P)
    if st['status'] != 'ok':
        return float('nan')
    Ss, Sc, Sb = st['S_star'], P.S_c, P.S_bar
    if not (Sc < 2 * Sb < Ss):
        return float('nan')
    return math.log((Ss - Sb) / Sb) / math.log((Ss - Sb) / (Sc - Sb))


# ---------------------------------------------------------------- 表 2 与能力代表点
def _isnum(v):
    try:
        float(v)
        return v not in ("True", "False")
    except (TypeError, ValueError):
        return False


def table2(runs):
    rows = tex_table_rows(NUM, 'tab:joint:compare')
    assert len(rows) == 8
    refs = {}
    for case, fid in (('base', 'compare_baseline'), ('xian', 'compare_xian')):
        for r in SRC.read_csv(fid):
            refs[(case, r['strategy'])] = {k: float(v) for k, v in r.items() if _isnum(v)}
    out = {}
    for j, row in enumerate(rows):
        case = 'base' if j < 4 else 'xian'
        law = TABLE_LAWS[j % 4]
        st, od = runs[(case, law)]['state'], runs[(case, law)]['ode']
        old = refs[(case, STRAT[law])]
        unit = 1.0 if case == 'base' else 1e6
        fields = [('dt', st['dt'], od['dt'], old['duration'], 1.0),
                  ('t_end', st['t_end'], od['t_end'], old['t_end'], 1.0),
                  ('total_to_clearance', st['total_infections_to_clearance'], od['total_infections_to_clearance'],
                   old['total_infections'], unit),
                  ('Sq_new_arc', st['sq_identity'], od['arc_Sq_new'], old['Sq_increment_plateau'], unit),
                  ('J', st['J'], od['J'], old['J'], 1.0),
                  ('peak_I_plus_Iq_over_eta', None, od['peak_I_plus_Iq_over_eta'], old['peak_I_plus_Iq_over_eta'], 1.0)]
        rec = {}
        for k, (name, sv, ov, oldv, u) in enumerate(fields):
            disp = row[k + 1]
            main = sv if sv is not None else ov
            REG.add(f'tab2.{case}.{law}.{name}', f'{NUM} 表 tab:joint:compare', disp, main / u,
                    unit='' if u == 1.0 else '10^6 人', old=oldv / u,
                    old_source=f'joint_extra/compare_{"baseline" if case == "base" else "xian"}.csv',
                    source='state_path' if sv is not None else 'simulate.run（开环完整方程）')
            rec[name] = dict(state=sv, ode=ov, old=oldv, display=disp,
                             rel_state_old=None if sv is None else rel(sv, oldv), rel_ode_old=rel(ov, oldv),
                             rel_ode_state=None if sv is None else rel(ov, sv))
        rec.update(t1=dict(state=st['t1'], ode=od['t1'], old=old['t1']), t2=dict(state=st['t2'], ode=od['t2'], old=old['t2']),
                   plateau_infections=dict(state=st['inf_identity'], ode=od['arc_infections'], old=old['plateau_infections_time']),
                   total_inf_t_inf=dict(state=st['total_infections_inf'], ode=od['total_infections_inf']),
                   plateau_abs_dev_persons=od['plateau_abs_dev'], identity_residual_rel=od['identity_residual_rel'],
                   mass_residual_persons=od['mass_residual_persons'])
        out[f'{case}|{law}'] = rec
    return out


def capacity(runs):
    ref = SRC.load_json('capacity')
    out = {}
    for case, key in (('base', 'baseline'), ('xian', 'xian')):
        P, C = PR.CASES[case], PR.REP_CAPACITY[case]
        st, od = runs[(case, 'opt', 'cap')]['state'], runs[(case, 'opt', 'cap')]['ode']
        m = ref[key]['metrics']
        x_min, h = AL.cap_factors(P, C)
        z_star = st['z_star']
        q_max_free = SI.start_state(P)['q_max']
        seg0 = od['segments'][0]
        out[case] = dict(point=dict(c_min=C.c_min, q_cap=C.q_cap),
                         q_only_feasible=bool(C.q_cap >= q_max_free),
                         c_only_feasible=bool(C.c_min <= P.c0 / z_star),
                         joint_feasible=bool(C.c_min * (1 - C.q_cap) <= P.c0 * (1 - q_max_free)),
                         dt=dict(state=st['dt'], ode=od['dt'], old=m['duration']),
                         J=dict(state=st['J'], ode=od['J'], old=m['J']),
                         t_end=dict(state=st['t_end'], ode=od['t_end'], old=m['t_end']),
                         total=dict(state=st['total_infections_to_clearance'], ode=od['total_infections_to_clearance'],
                                    old=m['total_infections_to_clearance']),
                         peak=dict(ode=od['peak_I_plus_Iq_over_eta'], old=m['peak_I_plus_Iq_over_eta']),
                         front_segment=dict(z_hi=seg0['z_hi'], z_lo=seg0['z_lo'], duration=seg0['duration'],
                                            h=h, contact_reduction_at_start=1 - h / z_star),
                         upper=dict(dt=runs[(case, 'cap_upper', 'cap')]['state']['dt']),
                         lower=dict(dt=runs[(case, 'cap_lower', 'cap')]['state']['dt']))
        claim(f'cap.{case}.joint_required', f'{NUM} §6.4', '代表点只有联合控制可行',
              (not out[case]['q_only_feasible']) and (not out[case]['c_only_feasible']) and out[case]['joint_feasible'])
        claim(f'cap.{case}.higher', f'{NUM} §6.4', '能力约束下成本最优控制的 J 与 Δt 都高于表 2',
              st['J'] > runs[(case, 'opt')]['state']['J'] and st['dt'] > runs[(case, 'opt')]['state']['dt'],
              J=st['J'], J_free=runs[(case, 'opt')]['state']['J'], dt=st['dt'], dt_free=runs[(case, 'opt')]['state']['dt'])
        claim(f'cap.{case}.qcap_until_h', f'{NUM} §6.4', '启动后一段内隔离比例停在上限，直到 S 降到 (1-q0)S_c/(1-q_cap)',
              abs(seg0['z_lo'] - h) <= 1e-12 * h and abs(st['q_max'] - C.q_cap) <= 1e-12)
    return out


# ---------------------------------------------------------------- 主程序
def main():
    B, X = PR.BASE, PR.XIAN
    runs = {}
    for case in ('base', 'xian'):
        P = PR.CASES[case]
        for law in TABLE_LAWS:
            pol = SI.Policy(P, law)
            runs[(case, law)] = dict(state=SI.state_path(pol), ode=SM.run(pol))
        for law in ('opt', 'cap_upper', 'cap_lower'):
            pol = SI.Policy(P, law, cap=PR.REP_CAPACITY[case])
            runs[(case, law, 'cap')] = dict(state=SI.state_path(pol), ode=SM.run(pol) if law == 'opt' else None)
    t2 = table2(runs)
    cap = capacity(runs)
    R = lambda case, law: runs[(case, law)]

    # ---------------- 第 6.2 节
    sq = R('base', 'q_only')['state']
    REG.add('s62.routine_peak', f'{NUM} §6.2', '300.4', SI.start_state(B)['I_peak'], source='式 (2.6)')
    REG.add('s62.t1', f'{NUM} §6.2', '3.175', sq['t1'], source='式 (3.2)')
    REG.add('s62.q_max', f'{NUM} §6.2', '0.7565', sq['q_max'], source='式 (3.10)')
    REG.add('s62.dt', f'{NUM} §6.2', '5.903', sq['dt'], source='式 (3.6)')
    for f, ddisp, tdisp in ((0.002, '152.1', '173.0'), (0.02, '15.04', '233.8')):
        s = q_only(B.with_(eta=f * B.N))
        REG.add(f's62.eta{f}.dt', f'{NUM} §6.2', ddisp, s['dt'], source='仅隔离控制，η = %gN' % f)
        REG.add(f's62.eta{f}.total', f'{NUM} §6.2', tdisp, s['total_infections_to_clearance'])
    c_arg, dt_max, interior = argmax(lambda c: dt_q_closed(B.with_(c0=c)), 3.4, 12.0)
    REG.add('s62.c0_argmax', f'{S1} sec:sup:baseline-contact-scan', '5.1', c_arg, source='Δt(c0) 的数值极大（式 3.6，网格 + 有界搜索）')
    REG.add('s62.dt_max', f'{S1} sec:sup:baseline-contact-scan', '7.579', dt_max)
    claim('s62.c0_interior_max', f'{S1} sec:sup:baseline-contact-scan', 'Δt 随 c0 先增后减（所考察的范围内取得内部极大）', interior)
    c0min = c0_trigger(B)
    REG.add('s62.c0min', f'{S1} sec:sup:baseline-contact-scan', '3.327', c0min, source='I_max^0(c0) = η')

    # ---------------- 第 6.3 节与表 2 表注
    for case, (dj, ddt, dtot) in (('base', ('4.7', '31.4', '7.3')), ('xian', ('6.7', '27.9', '6.6'))):
        q, o = R(case, 'q_only')['state'], R(case, 'opt')['state']
        REG.add(f's63.{case}.J_drop_pct', f'{NUM} §6.3', dj, 100 * (1 - o['J'] / q['J']))
        REG.add(f's63.{case}.dt_rise_pct', f'{NUM} §6.3', ddt, 100 * (o['dt'] / q['dt'] - 1))
        REG.add(f's63.{case}.total_rise_pct', f'{NUM} §6.3', dtot,
                100 * (o['total_infections_to_clearance'] / q['total_infections_to_clearance'] - 1))
    for case, disp, dred in (('base', '1.61', '19.8'), ('xian', '25.46', '28.2')):
        P = PR.CASES[case]
        o = R(case, 'opt')
        z_sw = AL.z_sw_formula(P.z_bar)
        Ss, Sw = o['state']['S_star'], z_sw * P.S_c
        front = P.N / (P.c0 * P.eta) * math.log((Ss - P.S_bar) / (Sw - P.S_bar))
        REG.add(f's63.{case}.front_duration', f'{NUM} §6.3', disp, front, source='S* → S_sw 段的仅隔离闭式',
                note=f"完整方程名义时钟第一段 {o['ode']['segments'][0]['duration']!r}")
        claim(f's63.{case}.front_half', f'{NUM} §6.3', '前段完成阈值控制期 S 下降的一半以上',
              (Ss - Sw) / (Ss - P.S_c) > 0.5, share=(Ss - Sw) / (Ss - P.S_c))
        REG.add(f's63.{case}.max_contact_drop_pct', f'{NUM} §6.3', dred, 100 * (1 - o['state']['x_min']))
    for law, disp in (('q_only', '1.92'), ('opt', '1.89'), ('c_only', '1.02')):
        REG.add(f's63.base.peak.{law}', f'{NUM} §6.3', disp, R('base', law)['ode']['peak_I_plus_Iq_over_eta'])
    ob, ox = R('base', 'opt')['ode'], R('xian', 'opt')['ode']
    claim('s63.base.peak_in_back', f'{NUM} §6.3', '基准参数下峰值出现在后段（两者并用段）',
          ob['t_peak_I_plus_Iq'] > ob['t1'] + ob['segments'][0]['duration'], t_peak=ob['t_peak_I_plus_Iq'])
    xq = R('xian', 'q_only')['ode']
    REG.add('s63.xian.peak_after_start', f'{NUM} §6.3', '7.62', ox['t_peak_I_plus_Iq'] - ox['t1'])
    claim('s63.xian.peak_in_front_equal', f'{NUM} §6.3', '西安参数下峰值在前段，仅隔离与成本最优控制的峰值相同',
          ox['t_peak_I_plus_Iq'] - ox['t1'] < ox['segments'][0]['duration']
          and rel(ox['peak_I_plus_Iq'], xq['peak_I_plus_Iq']) < 1e-10,
          rel_peak=rel(ox['peak_I_plus_Iq'], xq['peak_I_plus_Iq']))
    for case, ds, dw in (('base', '4.044', '2.265'), ('xian', '4.378', '2.548')):
        P = PR.CASES[case]
        REG.add(f'tab2note.{case}.zstar', f'{NUM} 表 2 注', ds, SI.start_state(P)['z_star'])
        REG.add(f'tab2note.{case}.zsw', f'{NUM} 表 2 注', dw, AL.z_sw_formula(P.z_bar))
    for case in ('base', 'xian'):
        d = {l: R(case, l)['state']['dt'] for l in TABLE_LAWS}
        claim(f's63.{case}.order', f'{NUM} §6.3', '控制时长从长到短：仅减少接触、α = 0.5、成本最优、仅隔离',
              d['c_only'] > d['alpha'] > d['opt'] > d['q_only'], **d)
        claim(f's63.{case}.Sstar_above_Ssw', f'{NUM} §6.3', 'S* 高于 S_sw',
              SI.start_state(PR.CASES[case])['z_star'] > AL.z_sw_formula(PR.CASES[case].z_bar))

    # ---------------- 第 6.4 节与补充 S8（证据 ID 保留原 S6）
    REG.add('s64.base.c_only_drop_pct', f'{NUM} §6.4', '75.3', 100 * (1 - 1 / R('base', 'q_only')['state']['z_star']))
    for case, dJ, ddt in (('base', '2.361', '8.34'), ('xian', '41.62', '116.8')):
        st = runs[(case, 'opt', 'cap')]['state']
        REG.add(f's64.{case}.cap.J', f'{NUM} §6.4', dJ, st['J'], old=cap[case]['J']['old'], old_source='joint_extra/capacity.json')
        REG.add(f's64.{case}.cap.dt', f'{NUM} §6.4', ddt, st['dt'], old=cap[case]['dt']['old'], old_source='joint_extra/capacity.json')
    REG.add('S6.base.cap_front', f'{S6} sec:sup:numerics 能力代表点与时长前沿', '1.94', cap['base']['front_segment']['duration'])
    REG.add('S6.base.cap_contact_drop_pct', f'{S6} sec:sup:numerics 能力代表点与时长前沿', '39.1', 100 * cap['base']['front_segment']['contact_reduction_at_start'])
    REG.add('S6.xian.cap_front', f'{S6} sec:sup:numerics 能力代表点与时长前沿', '30.38', cap['xian']['front_segment']['duration'])

    # ---------------- 第 6.5 节（乘子曲线：旧的 470 个计算点，用本模块复核所用的点）
    Jmin = R('base', 'opt')['state']['J']
    REG.add('s65.Jq_over_Jmin', f'{NUM} §6.5', '1.05', R('base', 'q_only')['state']['J'] / Jmin)
    REG.add('s65.Jc_over_Jmin', f'{NUM} §6.5', '5.64', R('base', 'c_only')['state']['J'] / Jmin)
    REG.add('s65.c_only_dt', f'{NUM} §6.5', '36.26', R('base', 'c_only')['state']['dt'])
    fr = SRC.read_csv('frontier')
    within = [r for r in fr if float(r['J']) <= 1.10 * Jmin]
    best = max(within, key=lambda r: float(r['duration']))
    chk = SI.arc_integrals(SI.Policy(B, 'opt', kappa=float(best['kappa'])), with_quad=True)
    REG.add('s65.longest_within_110', f'{NUM} §6.5', '11.09', chk['dt'], old=float(best['duration']),
            old_source='joint_extra/frontier_baseline.csv（470 点中 J ≤ 1.10 J_min 的最长者）',
            note=f"κ = {best['kappa']}；本模块复算该点 J/J_min = {chk['J'] / Jmin!r}")
    claim('s65.frontier_points', f'{S6} sec:sup:numerics 能力代表点与时长前沿', '乘子曲线由 470 个点构成', len(fr) == 470, n=len(fr))

    # ---------------- 补充 S2 的 tab:sup:baseline（证据 ID 保留原 S1）
    rows = tex_table_rows(S1, 'tab:sup:baseline')
    labels = []
    for row in rows:
        key = row[0]
        if 'c_0' in key:
            c = c0min + 0.02 if '\\approx' in key else num(key.split('=')[1])
            P = B.with_(c0=c)
            labels.append(('c0', c, P))
        else:
            f = num(key.split('=')[1]) / 100
            labels.append(('eta', f, B.with_(eta=f * B.N)))
    for (kind, v, P), row in zip(labels, rows):
        s = q_only(P)
        tag = f'S1.{kind}{v:.6g}'
        if kind == 'c0' and '\\approx' in row[0]:
            REG.add(tag + '.c0', f'{S1} 表 tab:sup:baseline', row[0].split('approx')[1].strip('$ '), v, note='c0 = c_{0,min} + 0.02')
        for k, (name, val) in enumerate((('t1', s['t1']), ('dt', s['dt']), ('t_end', s['t_end']), ('q_max', s['q_max']),
                                         ('J', s['J']), ('total', s['total_infections_to_clearance']))):
            REG.add(f'{tag}.{name}', f'{S1} 表 tab:sup:baseline', row[k + 1], val)
    REG.add('S1.q_inf', f'{S1} sec:sup:baseline-scan', '0.4083', 1 - 1 / (2 * (1 - B.beta)), source='式 (3.12) 的 q_inf（公式常数）')

    # ---------------- 补充 S6 的 tab:sup:eta 与第 7.3 节（证据 ID 保留原 S3）
    rows = tex_table_rows(S3, 'tab:sup:eta')
    for row in rows:
        f = num(row[0])
        s = q_only(X.with_(eta=f * X.N))
        for k, (name, val) in enumerate((('q_max', s['q_max']), ('dt', s['dt']), ('t_end', s['t_end']), ('J', s['J']),
                                         ('total', s['total_infections_to_clearance']))):
            REG.add(f'S3.eta{f:g}.{name}', f'{S3} 表 tab:sup:eta', row[k + 1], val)
    REG.add('s73.dt_eta0.01', f'{XT} §7.3', '16.6', q_only(X.with_(eta=0.01 * X.N))['dt'])
    REG.add('s73.dt_eta0.0001', f'{XT} §7.3', '1711', q_only(X.with_(eta=0.0001 * X.N))['dt'])
    dt_low = q_only(X.with_(eta=152.55))['dt']
    REG.add('s73.dt_TDINN_peak_years', f'{XT} §7.3', '40.5', dt_low / 365.0,
            note=f'η = 152.55，Δt = {dt_low!r} d，按 365 d/年；按 365.25 d/年为 {dt_low / 365.25!r}（显示应为 40.4）')
    REG.add('s73.lower_bound', f'{XT} §7.3', '1.53e6', X.beta * (X.S0 - X.S_c), source='命题 4.9')

    # ---------------- 第 7 章：TDINN、常规控制与仅隔离控制（表 3 与正文）
    td, _ = TD.run(X, TD.tdinn)
    rt, _ = TD.run(X, TD.routine_of(X))
    xq_s = R('xian', 'q_only')['state']
    xq_o = R('xian', 'q_only')['ode']
    ref = SRC.load_json('xian_reference')
    rows = tex_table_rows(XT, 'tab:xian_summary')
    vals = {0: (td['peak_I'], td['total'], td['t_end'], td['J']),
            1: (xq_o['max_I'], xq_s['total_infections_to_clearance'], xq_s['t_end'], xq_s['J']),
            2: (rt['peak_I'], rt['total'], rt['t_end'], rt['J'])}
    for j, row in enumerate(rows):
        for k, name in enumerate(('peak_I', 'total', 't_end', 'J')):
            REG.add(f'tab3.{["tdinn", "q_only", "routine"][j]}.{name}', f'{XT} 表 tab:xian_summary', row[k + 1], vals[j][k])
    for name, disp, v, oldv in (('t1', '16.90', xq_s['t1'], None), ('t2', '101.97', xq_s['t2'], None),
                                ('dt', '85.07', xq_s['dt'], None),
                                ('tdinn.peak', '152.55', td['peak_I'], ref['I_peak_T']),
                                ('tdinn.total', '2105.63', td['total'], ref['Itcum_T']),
                                ('tdinn.t_end', '45.29', td['t_end'], ref['t_end_T']),
                                ('tdinn.J', '49.39', td['J'], ref['J_T'])):
        REG.add(f'tab3note.{name}', f'{XT} 表 3 注', disp, v, old=oldv,
                old_source=None if oldv is None else 'xian/reference.json')
    for name, disp, v in (('J_q_only', '40.77', xq_s['J']), ('J_tdinn', '49.39', td['J']),
                          ('total_q_only', '2.38e6', xq_s['total_infections_to_clearance']), ('t_end_q_only', '258.1', xq_s['t_end']),
                          ('total_tdinn', '2106', td['total']), ('t_end_tdinn', '45.29', td['t_end']),
                          ('Re0', '4.43', X.S0 / X.S_c), ('q_max', '0.85', xq_s['q_max']),
                          ('tdinn_c_inf_share_pct', '27', 100 * 3.4625 / 12.8872), ('tdinn_q_inf', '0.98', 0.9844)):
        REG.add(f's72.{name}', f'{XT} §7.2', disp, v,
                source='式 (7.1) 的常数' if name.startswith('tdinn_') else '')
    floor = td['cI'] + td['cIq'] / X.beta
    REG.add('s74.N_floor', f'{XT} §7.4', '1.06e4', floor, source='命题 7.1，TDINN 轨迹计至清零')
    REG.add('s74.floor_ratio', f'{XT} §7.4', '5.04', floor / td['total'])
    REG.add('s74.untraced_per_traced', f'{XT} §7.4', '5.7', (1 - X.beta) / X.beta, source='公式常数')
    td40, sol40 = TD.run(X, TD.tdinn, t_stop=40.0)
    REG.add('S6.tdinn_40', f'{S6} sec:sup:numerics TDINN 终点', '2098.9747', td40['total'])
    REG.add('S6.tdinn_t_end', f'{S6} sec:sup:numerics TDINN 终点', '45.2874', td['t_end'])
    REG.add('S6.tdinn_total', f'{S6} sec:sup:numerics TDINN 终点', '2105.6330', td['total'])
    tight = SM.Config(rtol=1e-13, atol_scale=0.1, max_step=0.25)
    td_t, _ = TD.run(X, TD.tdinn, cfg=tight)
    old_impl = dict(
        S6_plateau_base_ode45=dict(display='1.07e-7', meaning='旧 ode45 基准轨迹的阈值控制期 max|I-η|（人）',
                                   nr_audit=R('base', 'q_only')['ode']['plateau_abs_dev']),
        S6_plateau_xian_xianpy=dict(display='1.35e-6', meaning='旧 xian.py 仅隔离控制的 max|I-η|（人）',
                                    nr_audit=xq_o['plateau_abs_dev']),
        S6_tdinn_tolerance=dict(display='3.61e-8', meaning='旧 xian.py 收紧容差后 TDINN 总累计的变化（人）',
                                nr_audit=abs(td_t['total'] - td['total']), nr_audit_settings=tight.__dict__))

    # ---------------- 补充 S2 的西安人口缩放情景（证据 ID 保留原 S5）
    def P5(c0):
        return X.with_(name='s5', N=2e4, S0=2e4 - X.I0, eta=0.002 * 2e4, c0=c0)
    cf = lambda c: SI.closed_forms(P5(c))
    trig = c0_trigger(P5(10.0))
    REG.add('S5.trigger', f'{S5} 图 fig:c0-scan', '3.334', trig)
    infl = brentq(lambda c: SI.start_state(P5(c))['S_star'] - 2 * P5(c).S_bar, trig * (1 + 1e-6), 6.0, xtol=1e-14)
    REG.add('S5.inflection', f'{S5} 图 fig:c0-scan', '3.543', infl)
    # 代表点的 c0 取原程序（reproducibility/c0.py 的 reps）：触发边界 ×1.03 与拐点边界 + 0.05，稿件显示为 3.43、3.59
    c_a, c_b = trig * 1.03, infl + 0.05
    REG.add('S5.c0_near_trigger', f'{S5} sec:dom:c0', '3.43', c_a, note='触发边界 × 1.03（原程序 c0.py）')
    REG.add('S5.c0_post_inflection', f'{S5} sec:dom:c0', '3.59', c_b, note='拐点边界 + 0.05（原程序 c0.py）')
    REG.add('S5.qmax_3.43', f'{S5} sec:dom:c0', '0.383', cf(c_a)['q_max'])
    REG.add('S5.qmax_3.59', f'{S5} sec:dom:c0', '0.423', cf(c_b)['q_max'])
    REG.add('S5.q_inf', f'{S5} sec:dom:c0', '0.4119', 1 - 1 / (2 * (1 - X.beta)), source='公式常数')
    cdt, dtmax, i1 = argmax(lambda c: cf(c)['dt_q_only'], trig * 1.0001, 30.0)
    REG.add('S5.dt_argmax', f'{S5} 图 fig:c0-scan', '6.607', cdt)
    REG.add('S5.dt_argmax_text', f'{S5} app:c0_scan', '6.61', cdt)
    REG.add('S5.dt_max', f'{S5} app:c0_scan', '103.2', dtmax)
    cJ, Jmax, i2 = argmax(lambda c: cf(c)['J_q_only'], trig * 1.0001, 30.0)
    REG.add('S5.J_argmax', f'{S5} app:c0_scan', '18.12', cJ)
    REG.add('S5.J_max', f'{S5} app:c0_scan', '42.80', Jmax)
    cI, Imax, i3 = argmax(lambda c: cf(c)['Itcum_q_only_to_clearance'], trig * 1.0001, 30.0)
    REG.add('S5.I_argmax', f'{S5} app:c0_scan', '13.88', cI)
    REG.add('S5.I_max', f'{S5} app:c0_scan', '3610', Imax)
    claim('S5.interior_maxima', f'{S5} app:c0_scan', '三个极大值都在扫描范围内部', i1 and i2 and i3)
    REG.add('S5.t_end_3.43', f'{S5} app:c0_scan', '367', q_only(P5(c_a))['t_end'])
    REG.add('S5.t_end_30', f'{S5} app:c0_scan', '102', q_only(P5(30.0))['t_end'])
    REG.add('S5.beta_max', f'{S5} app:c0_beta', '0.261448', 1 - 1 / (2 * (1 - X.q0)), source='q_inf = q0（公式常数）')

    # ---------------- 补充 S3（λ 对 q0 的局部极大；证据 ID 保留原 S2）
    for beta, disp in ((0.10, '0.0736525'), (0.12, '0.1969606'), (0.155, '0.3890712')):
        Pb = B.with_(beta=beta)
        q_arg, lmax, inner = argmax(lambda q0: lam(Pb.with_(q0=q0)), 0.0, 0.39, n=800)
        REG.add(f'S2.q0dagger.beta{beta}', f'{S2} sec:sup:inflection 数值结果', disp, q_arg, note=f'λ_max = {lmax!r}')
        claim(f'S2.q0dagger.beta{beta}.interior', f'{S2}', 'q0† 在 [0, 0.39] 内部', inner)

    dump('regression.json', dict(
        description='NR-3 N1：表 2 的两条路径（状态路径、开环完整方程）与旧全精度结果；能力代表点；稿件保留数字的复算与显示核对；'
                    '文中定性陈述的数值核对；旧实现的数值与本模块的对应值。',
        table2=t2, capacity=cap, registry=REG.rows, registry_summary=REG.summary(), claims=CLAIMS,
        old_implementation_numbers=old_impl,
        tdinn=dict(clearance=td, routine=rt, window40=td40, tight_tolerance=td_t,
                   reference=dict(I_peak_T=ref['I_peak_T'], Itcum_T=ref['Itcum_T'], t_end_T=ref['t_end_T'], J_T=ref['J_T']))))
    write_md(t2, cap, old_impl)
    print('regression.json：', REG.summary(), '；定性陈述', sum(c['holds'] for c in CLAIMS), '/', len(CLAIMS), '成立')


def write_md(t2, cap, old_impl):
    L = ['# NR-3 N1：回归与保留数字核对', '', f'登记 {len(REG.rows)} 个数字：{REG.summary()}。'
         '判定：consistent = 复算值按显示位数舍入后与显示值一致；display_differs = 不一致但相对差 ≤ 1%；stop = 相对差 > 1%。', '',
         '## 表 2（两条路径与旧值的最大相对差）', '', '| 参数 | 控制 | 状态路径–旧值 | 完整方程–旧值 | 完整方程–状态路径 |', '|---|---|---|---|---|']
    for key, rec in t2.items():
        case, law = key.split('|')
        a = max((v['rel_state_old'] or 0) for k, v in rec.items() if isinstance(v, dict) and 'rel_state_old' in v)
        b = max(v['rel_ode_old'] for k, v in rec.items() if isinstance(v, dict) and 'rel_ode_old' in v)
        c = max((v['rel_ode_state'] or 0) for k, v in rec.items() if isinstance(v, dict) and 'rel_ode_state' in v)
        L.append(f'| {case} | {law} | {a:.1e} | {b:.1e} | {c:.1e} |')
    L += ['', '## 显示值与复算不一致或需注意的项', '', '| id | 位置 | 显示 | 复算 | 判定 | 说明 |', '|---|---|---|---|---|---|']
    for r in REG.rows:
        if r['status'] != 'consistent':
            L.append(f"| {r['id']} | {r['where']} | {r['display']} | {r['value']:.10g} | {r['status']} | {r['note']} |")
    L += ['', '## 定性陈述', '', '| id | 陈述 | 成立 |', '|---|---|---|']
    for c in CLAIMS:
        L.append(f"| {c['id']} | {c['statement']} | {'是' if c['holds'] else '**否**'} |")
    L += ['', '## 旧实现的数值（不是本模块能复现的量）', '', '| 项 | 稿件值 | 含义 | 本模块对应值 |', '|---|---|---|---|']
    for k, v in old_impl.items():
        L.append(f"| {k} | {v['display']} | {v['meaning']} | {v['nr_audit']:.3g} |")
    (RESULTS / 'regression.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
