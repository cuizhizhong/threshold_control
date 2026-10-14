"""R7-3 正式数值：端点小表、指数回流表、释放用数、无回流 t→∞ 对照与收敛核验。

运行（仓库根目录）：
    conda run --no-capture-output -n thesis python r7_return/r7_3_numerics.py
约 5–10 分钟。全部结果以全精度写入 results/r7_3_*.json，展示用的表写入 results/r7_3_numerics.md。

任务与输出（执行计划 ai/R7_回流修订_分步执行计划.md 第 6 节 R7-3 的编号）：
  1. 端点小表（立即返回对照模型）：两组参数 × 四种控制，S 坐标求积为主结果，事件法交叉核对
     → results/r7_3_endpoint_immediate.json
  2. 指数回流表：1/ω ∈ {7, 14, 30, 60, 120, 365} d × 两组参数 × 三种控制律（仅隔离、仅减少接触、
     无回流最优律迁移），事件法；退出后 İ=0 事件与稠密采样两种方式核对峰值；反馈重放交叉核对
     → results/r7_3_exponential_return.json
  3. 释放用数（ω = 0，仅隔离，ξ = 1）：S_q(t2)/S_c 与 R_e(t2⁺)，事件法与解析式
     → results/r7_3_release.json
  4. 无回流 t→∞ 对照：四种控制的 C_π(0)（定理 3.5 的 S_∞ 补尾），与 L = U(0) − S_c 并列，
     事件法与闭式（定理 3.6 + 推论 4.7）两种算法 → results/r7_3_noreturn_inf.json
  6. 收敛（本分支部分）：立即返回端的 N_x、N_z；迁移律所用状态范围上 ω = 0 逐状态最小化的 N_x 核对；
     上述全部事件法轨迹的积分容差（基准 / 收紧 / 放宽）→ results/r7_3_convergence.json
  8. 容差收紧复核：非零指标相对变化 < 1e-3；e 与残差用绝对判据（见 TOL_CHECK）
  另：与执行计划第 5 节参考值的逐项对照 → results/r7_3_plan_comparison.json

R7-3 第 5 项（固定人口初值诊断、四项拟合误差）与第 6 项中 ω = 0 的部分（ω = 0 端的逐状态最小化网格、
表 S5 权重转折、ω = 0 的积分容差收敛表）按无回流分支 NR-0 的登记（作者 2026-10-14 确认）由无回流分支
NR-3 产出，本分支不重复执行，写入时按源提交复用（AGENTS.md 开头“双分支安排”）。
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import alloc as AL  # noqa: E402
import endpoints as E  # noqa: E402
import references as REF  # noqa: E402
import replay_feedback as RF  # noqa: E402
import simulate as S  # noqa: E402
from params import CASES  # noqa: E402

RESULTS = os.path.join(HERE, 'results')

STAYS = (7, 14, 30, 60, 120, 365)                       # 平均停留 1/ω（天）
LAWS_RETURN = ('q_only', 'c_only', 'opt_noreturn')      # ω > 0 时 opt_noreturn 即“无回流最优律迁移”
LAWS_IR = ('q_only', 'alpha', 'opt_immediate', 'c_only')
LAWS_NR = ('q_only', 'alpha', 'opt_noreturn', 'c_only')

# 积分容差的三档：基准（正式结果）、收紧、放宽（同时改 rtol、各分量 atol 与 max_step）
CONFIGS = {
    'base': dict(rtol=1e-11, atol_scale=1.0, max_step=1.0),
    'tight': dict(rtol=1e-12, atol_scale=0.1, max_step=0.5),
    'loose': dict(rtol=1e-10, atol_scale=10.0, max_step=2.0),
}

# 判据（执行计划第 5 节）：非零量相对变化 < 1e-3；e、残差用绝对判据
TOL_CHECK = dict(rel_nonzero=1e-3, e_abs=1e-8, identity_rel=1e-8, trigger_rel=1e-10, exit_rel=1e-10,
                 clearance_abs_persons=1e-8)


def cfg_of(name, keep=False):
    return S.Config(keep_solutions=keep, **CONFIGS[name])


def rel(a, b):
    if a is None or b is None:
        return None
    if b == 0:
        return abs(a - b)
    return abs(a - b) / abs(b)


def clean(v):
    """转成可写 JSON 的类型；非有限浮点数写 None（另有状态字段说明原因）。"""
    if isinstance(v, dict):
        return {str(k): clean(w) for k, w in v.items()}
    if isinstance(v, (list, tuple)):
        return [clean(w) for w in v]
    if isinstance(v, (np.floating, float)):
        v = float(v)
        return v if math.isfinite(v) else None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v


def dump(name, obj):
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, name), 'w', encoding='utf-8') as fh:
        json.dump(clean(obj), fh, indent=1, ensure_ascii=False, allow_nan=False)


# ---------------------------------------------------------------------------
# 事件法轨迹与附加诊断
# ---------------------------------------------------------------------------
def run_with_checks(P, law, omega=0.0, model='return', xi=0.0, cfg_name='base'):
    """事件法一条轨迹，另加：阈值弧上 z = S/S_c 的范围；退出后 I 的稠密采样核对。"""
    res = S.run(P, law, omega=omega, model=model, xi=xi, cfg=cfg_of(cfg_name, keep=True))
    sols = res.pop('_sols', [])
    phases = res['phases']
    if 'plateau' in phases:
        sp = sols[phases.index('plateau')]          # simulate._plain 已把 OdeResult 转成 dict
        z = sp['y'][S.IS] / P.sc_N
        res['plateau_z_min'] = float(np.min(z))
        res['plateau_z_max'] = float(np.max(z))
        res['plateau_z_at_trigger'] = float(z[0])
    if 'post' in phases and res.get('t2') is not None:
        res['post_dense'] = post_dense_check(res, sols[phases.index('post')], P)
    return res


def post_dense_check(res, sol, P, n_sub=8):
    """退出后 I 的稠密采样：每个积分步内取 n_sub 个等分点（连续解），与 İ=0 事件定位的结果对照。
    返回 (t2, T] 上的最大 I/η − 1（剔除紧邻 t2 的点），以及首次 I<1 之前、之后各自的最大值。"""
    t = sol['t']
    if len(t) < 2:
        return None
    frac = np.arange(n_sub) / n_sub
    tt = (t[:-1, None] + (t[1:] - t[:-1])[:, None] * frac[None, :]).ravel()
    tt = np.append(tt, t[-1])
    t2 = res['t2']
    tt = tt[tt - t2 > S.T2_EVENT_GUARD * (1.0 + t2)]
    if len(tt) == 0:
        return None
    I = P.N * np.exp(sol['sol'](tt)[S.ILI])
    k = int(np.argmax(I))
    out = dict(n_samples=int(len(tt)), e_dense=float(I[k] / P.eta - 1.0), t_dense_max=float(tt[k]),
               I_min_dense=float(np.min(I)))
    tb = res.get('below_one_time')
    if tb is not None:
        before = tt <= tb
        after = tt > tb
        out['e_dense_until_below_one'] = float(np.max(I[before]) / P.eta - 1.0) if before.any() else None
        out['max_I_after_below_one_dense'] = float(np.max(I[after])) if after.any() else None
    else:
        out['e_dense_until_below_one'] = out['e_dense']
        out['max_I_after_below_one_dense'] = None
    return out


# ---------------------------------------------------------------------------
# 1. 端点小表（立即返回对照模型）
# ---------------------------------------------------------------------------
def task_endpoint():
    out = dict(model='immediate_return', weights=dict(w_c=1.0, w_q=2.0), alpha=0.5, cases={})
    for case in ('base', 'xian'):
        P = CASES[case]
        st = E.start_state_immediate(P)
        c = dict(S_c=P.S_c, S_star_ir=st['S_star'], z_star_ir=st['z_star'], A=st['A'], I_peak_ir=st['I_peak_ir'],
                 eta=P.eta, I0=P.I0, S_star_lambertw_vs_brentq_rel=st['lambertw_vs_brentq_rel'],
                 trigger_condition=bool(0 < P.I0 < P.eta < st['I_peak_ir']),
                 arc_infections_common=st['S_star'] - P.S_c, laws={})
        for law in LAWS_IR:
            a = E.arc_immediate(P, law)
            ev = run_with_checks(P, law, model='immediate')
            d = dict(dt=a['dt'], J=a['J'], arc_infections=a['infections'], Kq=a['Kq_quad'],
                     Kq_identity=a['Kq_identity'], dt_quad=a['dt_quad'], J_quad=a['J_quad'],
                     dt_simpson_vs_quad_rel=rel(a['dt'], a['dt_quad']), J_simpson_vs_quad_rel=rel(a['J'], a['J_quad']),
                     Kq_quad_vs_identity_rel=rel(a['Kq_quad'], a['Kq_identity']),
                     event=dict(t1=ev['t1'], t2=ev['t2'], dt=ev['dt'], J=ev['J'], arc_infections=ev['arc_infections'],
                                arc_Kq=ev['arc_Kq'], C_inf=ev['C_inf'], t_end=ev.get('t_end'),
                                trigger_event_rel=ev['trigger_event_rel'], exit_event_rel=ev['exit_event_rel'],
                                identity_residual_rel=ev['identity_residual_rel'], e=ev.get('e'),
                                crossing=ev.get('crossing')),
                     event_vs_quad_rel=dict(dt=rel(ev['dt'], a['dt']), J=rel(ev['J'], a['J']),
                                            arc_infections=rel(ev['arc_infections'], a['infections']),
                                            Kq=rel(ev['arc_Kq'], a['Kq_quad'])))
            if law == 'q_only':
                d['dt_closed'] = a['dt_closed_q_only']
                d['dt_closed_vs_quad_rel'] = rel(a['dt'], a['dt_closed_q_only'])
            if law == 'c_only':
                d['dt_closed'] = a['dt_closed_c_only']
                d['dt_closed_vs_quad_rel'] = rel(a['dt'], a['dt_closed_c_only'])
            if law == 'opt_immediate':
                bps = a['structure']['breakpoints']
                d['breakpoints'] = bps
                d['steep_points'] = a['structure']['steep_points']
                d['switch_z'] = bps[0]['z'] if bps else None
                zz = 1.0 + 1e-6
                d['terminal_share_z=1+1e-6'] = AL.terminal_share(AL.argmin_immediate(zz, P.wc, P.wq)[0], zz)
            c['laws'][law] = d
        L = c['laws']
        c['cost_gap_vs_c_only'] = (L['c_only']['J'] - L['opt_immediate']['J']) / L['c_only']['J']
        c['cost_gap_vs_q_only'] = (L['q_only']['J'] - L['opt_immediate']['J']) / L['q_only']['J']
        order_dt = sorted(LAWS_IR, key=lambda l: L[l]['dt'])
        order_kq = sorted(LAWS_IR, key=lambda l: -L[l]['Kq'])
        c['dt_order'] = order_dt
        c['Kq_reverse_of_dt'] = order_dt == order_kq
        c['J_order'] = sorted(LAWS_IR, key=lambda l: L[l]['J'])
        out['cases'][case] = c
    dump('r7_3_endpoint_immediate.json', out)
    return out


# ---------------------------------------------------------------------------
# 2. 指数回流表
# ---------------------------------------------------------------------------
def summarize_return_run(P, r):
    """从事件法结果中取指数回流表的字段（全精度）。"""
    reached = r.get('termination') == 'tail'
    tm = r.get('post_interior_max') or []
    d = dict(
        status=r['status'], t1=r.get('t1'), t2=r.get('t2'), dt=r.get('dt'), J=r.get('J'),
        S_star=r.get('S_star'), Sq_t1=r.get('Sq_t1'), Sq_t2=r.get('Sq_t2'),
        plateau_z_min=r.get('plateau_z_min'), plateau_z_max=r.get('plateau_z_max'),
        plateau_z_at_trigger=r.get('plateau_z_at_trigger'),
        e=r.get('e'), e_interior=r.get('e_interior'), e_end=r.get('e_end'),
        n_post_interior_max=len(tm), post_interior_max=tm,
        crossing=r.get('crossing'), n_guarded_events=r.get('n_guarded_events'),
        below_one_time=r.get('below_one_time'), regrowth_after_below_one=r.get('regrowth_after_below_one'),
        # 终止时 U < S_c：此后 S ≤ U ≤ U(T) < S_c，İ = γI(S/S_c − 1) < 0，I 严格下降，不会再回升。
        # 终止前 I 未降到 1 以下时（below_one_time 为 None），“降到 1 以下后再回升”因而不会发生
        below_one_before_term=r.get('below_one_time') is not None,
        I_decreasing_after_term=bool(r.get('termination') == 'tail' and r.get('U_term', math.inf) < P.S_c),
        regrowth_peak_I=r.get('regrowth_peak_I'), recrossed_one=r.get('recrossed_one'),
        termination=r.get('termination'), reached=reached, T_term=r.get('T_term'),
        C_term=r.get('C_term'), U_term=r.get('U_term'), I_term=r.get('I_term'),
        L=P.L_bound, excess_abs=r['C_term'] - P.L_bound, excess_rel=(r['C_term'] - P.L_bound) / P.L_bound,
        tail_bound=r.get('tail_bound'), eps_tail=r.get('eps_tail'),
        final_reliable=r.get('final_reliable'),
        final_estimate=[r['C_term'], r['C_term'] + r['tail_bound']] if reached else None,
        final_excess_rel_interval=([(r['C_term'] - P.L_bound) / P.L_bound,
                                    (r['C_term'] + r['tail_bound'] - P.L_bound) / P.L_bound] if reached else None),
        C_below_one=r.get('C_below_one'),
        identity_residual_rel=r.get('identity_residual_rel'), mass_residual_abs=r.get('mass_residual_abs'),
        trigger_event_rel=r.get('trigger_event_rel'), exit_event_rel=r.get('exit_event_rel'),
        n_steps=r.get('n_steps'), post_dense=r.get('post_dense'))
    pdn = r.get('post_dense') or {}
    # 稠密采样与事件定位的一致性：稠密最大值不应超过事件给出的最大值（含端点 t2 的 I = η）
    if pdn:
        e_event = max([0.0] + ([d['e_interior']] if d['e_interior'] is not None else []) + [d['e_end']])
        d['dense_minus_event_e'] = pdn['e_dense'] - e_event
    return d


def task_return(with_replay=True):
    out = dict(model='exponential_return', stays_days=list(STAYS), laws=list(LAWS_RETURN),
               law_note='opt_noreturn 在 ω > 0 下实施即“无回流最优律迁移”', weights=dict(w_c=1.0, w_q=2.0),
               eps_tail_rel=S.Config().eps_tail_rel, e_abs_tol=S.E_ABS_TOL, runs={})
    for case in ('base', 'xian'):
        P = CASES[case]
        for stay in STAYS:
            for law in LAWS_RETURN:
                key = f'{case}|{stay}|{law}'
                t0 = time.time()
                r = run_with_checks(P, law, omega=1.0 / stay)
                d = summarize_return_run(P, r)
                if with_replay:
                    # 重放在退出后首次 I<1 时停止；积分上限取事件法首次 I<1 之后 10 d（没有时取终止时刻），
                    # 使两者比较同一时间窗
                    tb = d['below_one_time']
                    T_rp = (tb + 10.0) if tb is not None else d['T_term']
                    rp = RF.replay(P, AL.get_law(law, P), 1.0 / stay, T=T_rp)
                    pdn = d.get('post_dense') or {}
                    d['replay'] = dict(
                        t1=rp['t1'], t2=rp['t2'], dt=rp['dt_ctrl'], J=rp['J'], C_first_below_one=rp['inf_total'],
                        t_end=rp['t_end'], Imax_after_over_eta=rp['Imax_after_eta'], n_episodes=rp['n_episodes'],
                        n_would_reopen=rp['n_would_reopen'], step=rp['step'], gain=rp['gain'],
                        rel_dt=rel(rp['dt_ctrl'], d['dt']), rel_J=rel(rp['J'], d['J']),
                        T_replay=T_rp,
                        rel_C_first_below_one=(rel(rp['inf_total'], d['C_below_one'])
                                               if d['C_below_one'] and rp['t_end'] is not None else None),
                        event_e_until_below_one=pdn.get('e_dense_until_below_one'))
                d['wall_s'] = time.time() - t0
                out['runs'][key] = d
                print('R7-3 return', key, f"dt={d['dt']:.6g} C={d['C_term']:.9g} exc={d['excess_rel']:.4%} "
                      f"{d['crossing']} {d['termination']} ({d['wall_s']:.1f}s)", flush=True)
    # ω = 0 的反馈重放对照（与 ω > 0 同一套比较，便于列出事件法与重放的差异）
    out['replay_omega0'] = {}
    if with_replay:
        for case in ('base', 'xian'):
            P = CASES[case]
            for law in LAWS_NR:
                ev = S.run(P, law)
                rp = RF.replay(P, AL.get_law(law, P), 0.0)
                out['replay_omega0'][f'{case}|{law}'] = dict(
                    dt_event=ev['dt'], J_event=ev['J'], C_t_end_event=ev['C_t_end'], dt_replay=rp['dt_ctrl'],
                    J_replay=rp['J'], C_replay=rp['inf_total'], rel_dt=rel(rp['dt_ctrl'], ev['dt']),
                    rel_J=rel(rp['J'], ev['J']), rel_C=rel(rp['inf_total'], ev['C_t_end']),
                    n_episodes=rp['n_episodes'], n_would_reopen=rp['n_would_reopen'])
    dump('r7_3_exponential_return.json', out)
    return out


# ---------------------------------------------------------------------------
# 3. 释放用数（ω = 0，仅隔离，ξ = 1）
# ---------------------------------------------------------------------------
def task_release():
    out = dict(model='noreturn_omega0', law='q_only', xi=1.0, cases={})
    for case in ('base', 'xian'):
        P = CASES[case]
        ev = run_with_checks(P, 'q_only', xi=1.0)
        a = E.arc_noreturn(P, 'q_only', with_quad=False)
        # 解析：启动前进入 S_q 的人数 = (1-β)q0/(β+(1-β)q0)·(S0 - S*)，加平台上的新增隔离易感者（式 eq:joint:quarantine）
        pre = (1 - P.beta) * P.q0 / (P.beta + (1 - P.beta) * P.q0) * (P.S0 - a['S_star'])
        sq_t2_analytic = pre + a['Sq_new_identity']
        out['cases'][case] = dict(
            Sq_t2=ev['Sq_t2'], Sq_t2_over_Sc=ev['Sq_t2_over_Sc'], Re_after_release=ev['Re_after_release'],
            Sq_t2_analytic=sq_t2_analytic, Sq_t2_over_Sc_analytic=sq_t2_analytic / P.S_c,
            Re_analytic=1.0 + sq_t2_analytic / P.S_c, rel_event_vs_analytic=rel(ev['Sq_t2'], sq_t2_analytic),
            Idot_t2_plus_over_gamma_eta=sq_t2_analytic / P.S_c,
            # 释放后的演化（只作记录；注记只给 R_e 与 İ(t2⁺)）
            post_release_max_I=ev.get('max_I_after_exit'), post_release_e=ev.get('e'), C_inf=ev.get('C_inf'),
            termination=ev.get('termination'), identity_residual_rel=ev['identity_residual_rel'])
    dump('r7_3_release.json', out)
    return out


# ---------------------------------------------------------------------------
# 4. 无回流 t→∞ 对照
# ---------------------------------------------------------------------------
def closed_form_C_inf(P, dt_by_law):
    """C_π(0)：仅隔离控制用定理 3.6（S_end 换为定理 3.5 的 S_∞），其余用推论 4.7 第二式。"""
    from scipy.special import lambertw
    st = E.start_state_noreturn(P)
    S_star, Sc, Sbar = st['S_star'], P.S_c, P.S_bar
    a = P.beta + (1 - P.beta) * P.q0
    rho1 = P.gamma * P.N / (P.c0 * a)
    S_inf = float(-Sc * lambertw(-math.exp(-1.0 - P.eta / rho1), 0).real)
    lam = P.beta / a
    C_q = lam * (P.S0 - S_star + Sc - S_inf) + P.beta * (S_star - Sc + Sbar * math.log((S_star - Sbar) / (Sc - Sbar)))
    out = {}
    for law, dt in dt_by_law.items():
        out[law] = C_q + P.gamma * P.eta * (1 - P.beta) * (dt - dt_by_law['q_only'])
    return out, S_inf


def task_noreturn_inf():
    out = dict(model='noreturn_omega0', endpoint='t→∞（定理 3.5 的 S_∞ 解析补尾）', cases={})
    refs, _ = REF.load_noreturn_refs()
    for case in ('base', 'xian'):
        P = CASES[case]
        dts = {law: E.arc_noreturn(P, law, with_quad=False)['dt'] for law in LAWS_NR}
        cf, S_inf = closed_form_C_inf(P, dts)
        c = dict(L=P.L_bound, U0=P.U0, S_c=P.S_c, S_inf=S_inf, laws={})
        for law in LAWS_NR:
            ev = run_with_checks(P, law)
            C_inf = ev['C_inf']
            c['laws'][law] = dict(
                C_inf=C_inf, C_inf_closed=cf[law], rel_event_vs_closed=rel(C_inf, cf[law]),
                C_t_end=ev['C_t_end'], C_t_end_ref=refs[(case, law)]['total_infections_to_clearance'],
                tail_increment=ev['tail_increment'], S_inf_event=ev['S_inf'], t_end=ev['t_end'], dt=ev['dt'],
                below_L=bool(C_inf < P.L_bound), margin_L_minus_C=P.L_bound - C_inf,
                margin_rel=(P.L_bound - C_inf) / P.L_bound,
                identity_residual_rel=ev['identity_residual_rel'],
                tail_lambertw_vs_brentq_rel=ev['tail_lambertw_vs_brentq_rel'])
        out['cases'][case] = c
    dump('r7_3_noreturn_inf.json', out)
    return out


# ---------------------------------------------------------------------------
# 6. 收敛（本分支部分）
# ---------------------------------------------------------------------------
def z_samples(z_hi, n=1500):
    """逐状态最小化核对用的状态点：退出附近按对数加密，其余等距，另加特殊点 3、2√2（落在范围内时）。"""
    near = 1.0 + np.logspace(-9, -2, 120)
    mid = np.linspace(1.0 + 1e-2, z_hi, n)
    special = [3.0, 2.0 * math.sqrt(2.0), 3.0 * (1 - 1e-9), 3.0 * (1 + 1e-9)]
    zs = np.concatenate([near, mid, [s for s in special if 1.0 < s <= z_hi]])
    return np.unique(zs[(zs > 1.0) & (zs <= z_hi)])


def grid_vs_root(argmin_fn, dens_fn, zs, N_x_list=(2001, 4001, 8001), tol_abs=1e-14, tol_rel=1e-12):
    """根法最小值 ≤ 网格最小值 + tol_abs + tol_rel·|网格最小值|；差距随 N_x 缩小。"""
    out = {}
    roots = [argmin_fn(float(z)) for z in zs]
    for n in N_x_list:
        gaps, xdiff, viol = [], [], 0
        for z, (xr, vr, _) in zip(zs, roots):
            xg, vg = AL.grid_min(dens_fn(float(z)), float(z), n)
            g = vg - vr
            gaps.append(g)
            xdiff.append(abs(xg - xr))
            if vr > vg + tol_abs + tol_rel * abs(vg):
                viol += 1
        gaps = np.array(gaps)
        out[str(n)] = dict(max_gap=float(np.max(gaps)), min_gap=float(np.min(gaps)), max_abs_x_diff=float(np.max(xdiff)),
                           n_violations=viol, n_states=int(len(zs)))
    return out


def task_convergence(ret=None):
    out = dict(criteria=TOL_CHECK, configs=CONFIGS, pointwise={}, quadrature_N_z={}, tolerance={})
    # (a) 立即返回端：N_x 与根法
    for case in ('base', 'xian'):
        P = CASES[case]
        zs_ir = E.start_state_immediate(P)['z_star']
        zs = z_samples(zs_ir)
        out['pointwise'][f'{case}|immediate'] = dict(
            z_range=[float(zs[0]), float(zs[-1])],
            result=grid_vs_root(lambda z: AL.argmin_immediate(z, P.wc, P.wq),
                                lambda z: (lambda x: AL.density_immediate(x, z, P.wc, P.wq)), zs))
    # (b) 迁移律：ω = 0 的逐状态最小化在 ω > 0 平台上实际经过的状态范围内（可高于无回流 S*/S_c）
    if ret is not None:
        for case in ('base', 'xian'):
            P = CASES[case]
            zmax = max(v['plateau_z_max'] for k, v in ret['runs'].items()
                       if k.startswith(case + '|') and k.endswith('|opt_noreturn'))
            z0 = E.start_state_noreturn(P)['z_star']
            zs = z_samples(max(zmax, z0))
            out['pointwise'][f'{case}|migrated_law_range'] = dict(
                z_range=[float(zs[0]), float(zs[-1])], z_star_noreturn=z0, plateau_z_max_over_stays=zmax,
                result=grid_vs_root(lambda z: AL.argmin_noreturn(z, P.z_bar, P.wc, P.wq),
                                    lambda z: (lambda x: AL.density_noreturn(x, z, P.z_bar, P.wc, P.wq)), zs))
    # (c) 立即返回端：N_z 与自适应 quad
    for case in ('base', 'xian'):
        P = CASES[case]
        for law in LAWS_IR:
            rows = {}
            for nz in (1001, 2001, 4001):
                a = E.arc_immediate(P, law, N_z=nz)
                rows[str(nz)] = dict(dt=a['dt'], J=a['J'], Kq=a['Kq_quad'], dt_quad=a['dt_quad'], J_quad=a['J_quad'],
                                     rel_dt_quad=rel(a['dt'], a['dt_quad']), rel_J_quad=rel(a['J'], a['J_quad']),
                                     switch_z=(a['structure']['breakpoints'][0]['z']
                                               if a.get('structure') and a['structure']['breakpoints'] else None),
                                     steep_points=(a['structure']['steep_points'] if a.get('structure') else None))
            out['quadrature_N_z'][f'{case}|{law}'] = rows
    # (d) 积分容差：本步全部事件法轨迹，三档
    runs = []
    for case in ('base', 'xian'):
        for stay in STAYS:
            for law in LAWS_RETURN:
                runs.append((case, law, 1.0 / stay, 'return', 0.0, f'return|{case}|{stay}|{law}'))
        for law in LAWS_NR:
            runs.append((case, law, 0.0, 'return', 0.0, f'noreturn|{case}|{law}'))
        for law in LAWS_IR:
            runs.append((case, law, 0.0, 'immediate', 0.0, f'immediate|{case}|{law}'))
        runs.append((case, 'q_only', 0.0, 'return', 1.0, f'release|{case}|q_only'))
    keys = ('t1', 't2', 'dt', 'J', 'C_t2', 'Kq_t2', 'Sq_t2', 'C_term', 'C_inf', 'T_term', 'U_term')
    for case, law, omega, model, xi, key in runs:
        P = CASES[case]
        res = {name: run_with_checks(P, law, omega=omega, model=model, xi=xi, cfg_name=name) for name in CONFIGS}
        row = dict(values={}, rel_change={}, abs_change={}, residuals={})
        for name, r in res.items():
            vals = {k: r.get(k) for k in keys if r.get(k) is not None}
            tm = r.get('post_interior_max') or []
            vals['post_max_I'] = max((p['I'] for p in tm), default=None)
            vals['regrowth_peak_I'] = r.get('regrowth_peak_I')
            vals['e_interior'] = r.get('e_interior')
            vals['e'] = r.get('e')
            vals['crossing'] = r.get('crossing')
            vals['termination'] = r.get('termination')
            row['values'][name] = vals
            row['residuals'][name] = dict(trigger_event_rel=r.get('trigger_event_rel'),
                                          exit_event_rel=r.get('exit_event_rel'),
                                          clearance_event_abs=r.get('clearance_event_abs'),
                                          identity_residual_rel=r.get('identity_residual_rel'),
                                          mass_residual_abs=r.get('mass_residual_abs'),
                                          n_steps=r.get('n_steps'))
        b = row['values']['base']
        for other in ('tight', 'loose'):
            o = row['values'][other]
            rc, ac = {}, {}
            for k in list(keys) + ['post_max_I', 'regrowth_peak_I']:
                if b.get(k) is not None and o.get(k) is not None:
                    rc[k] = rel(o[k], b[k])
            for k in ('e_interior', 'e'):
                if b.get(k) is not None and o.get(k) is not None:
                    ac[k] = abs(o[k] - b[k])
            ac['same_crossing'] = b.get('crossing') == o.get('crossing')
            ac['same_termination'] = b.get('termination') == o.get('termination')
            row['rel_change'][other] = rc
            row['abs_change'][other] = ac
        rt, at = row['rel_change']['tight'], row['abs_change']['tight']
        rs = row['residuals']
        row['pass_tight'] = bool(
            all(v < TOL_CHECK['rel_nonzero'] for v in rt.values())
            and all(at.get(k, 0.0) < TOL_CHECK['e_abs'] for k in ('e_interior', 'e'))
            and at['same_crossing'] and at['same_termination']
            and all((rs[n]['identity_residual_rel'] or 0.0) < TOL_CHECK['identity_rel'] for n in ('base', 'tight'))
            and all((rs[n]['trigger_event_rel'] or 0.0) < TOL_CHECK['trigger_rel'] for n in ('base', 'tight'))
            and all((rs[n]['exit_event_rel'] or 0.0) < TOL_CHECK['exit_rel'] for n in ('base', 'tight'))
            and all((rs[n]['clearance_event_abs'] or 0.0) < TOL_CHECK['clearance_abs_persons'] for n in ('base', 'tight')))
        out['tolerance'][key] = row
        print('R7-3 tol', key, 'max rel (tight) %.2e' % max(rt.values(), default=0.0), 'pass' if row['pass_tight'] else 'FAIL',
              flush=True)
    allrel = [v for row in out['tolerance'].values() for v in row['rel_change']['tight'].values()]
    alle = [row['abs_change']['tight'].get(k) for row in out['tolerance'].values() for k in ('e_interior',)
            if row['abs_change']['tight'].get(k) is not None]
    out['tolerance_summary'] = dict(
        n_runs=len(out['tolerance']), all_pass=all(r['pass_tight'] for r in out['tolerance'].values()),
        max_rel_change_tight=max(allrel), max_abs_e_change_tight=max(alle) if alle else None,
        max_identity_residual=max(r['residuals'][n]['identity_residual_rel'] or 0.0
                                  for r in out['tolerance'].values() for n in CONFIGS),
        max_trigger_residual=max(r['residuals'][n]['trigger_event_rel'] or 0.0
                                 for r in out['tolerance'].values() for n in CONFIGS),
        max_exit_residual=max(r['residuals'][n]['exit_event_rel'] or 0.0
                              for r in out['tolerance'].values() for n in CONFIGS),
        max_clearance_residual=max(r['residuals'][n]['clearance_event_abs'] or 0.0
                                   for r in out['tolerance'].values() for n in CONFIGS),
        failed=[k for k, r in out['tolerance'].items() if not r['pass_tight']])
    dump('r7_3_convergence.json', out)
    return out


# ---------------------------------------------------------------------------
# 与执行计划第 5 节参考值的逐项对照
# ---------------------------------------------------------------------------
def task_plan_comparison(ep, ret, rel_, nr):
    """与执行计划第 5 节参考值逐项对照。参考值是按所示位数舍入的数，所以除相对差外另判
    “是否与参考值的舍入一致”（|本步 − 参考| ≤ 参考值末位的半个单位）。触发停止条件（flag）的项：
    关键数、相对差 > 1%，且与参考值的舍入不一致。"""
    rows = []

    def half_unit(plan, sig):
        return 0.5 * 10 ** (math.floor(math.log10(abs(plan))) - sig + 1)

    def add(item, ours, plan, sig=None, kind='rel', note='', key=False):
        d = dict(item=item, ours=ours, plan=plan, plan_sig=sig, kind=kind, key=key, note=note,
                 rel_diff=None, abs_diff=None, rounding_consistent=None, flag=False)
        if kind in ('rel', 'pp'):
            d['abs_diff'] = abs(ours - plan)
            d['rel_diff'] = rel(ours, plan)
            if sig is not None:
                d['rounding_consistent'] = bool(d['abs_diff'] <= half_unit(plan, sig) * (1 + 1e-12))
            d['flag'] = bool(key and d['rel_diff'] > 1e-2 and not d['rounding_consistent'])
        elif kind == 'range':               # plan = (lo, hi)
            d['rounding_consistent'] = bool(ours is not None and plan[0] <= ours <= plan[1])
        elif kind == 'bound':               # plan 为上界
            d['rounding_consistent'] = bool(ours < plan)
        rows.append(d)

    for (case, law), p in REF.PLAN_IMMEDIATE.items():
        d = ep['cases'][case]['laws'][law]
        add(f'立即返回 {case} {law} Δt', d['dt'], p['dt'], 5, key=True)
        add(f'立即返回 {case} {law} J', d['J'], p['J'], 5, key=True)
    for case, p in REF.PLAN_IMMEDIATE_STATE.items():
        c = ep['cases'][case]
        add(f'立即返回 {case} S*_ir', c['S_star_ir'], p['S_star_inf'], 6, key=True)
        add(f'立即返回 {case} S_c', c['S_c'], p['S_c'], 6)
        add(f'立即返回 {case} 控制期感染', c['arc_infections_common'], p['infections'], 5 if case == 'base' else 6,
            key=True)
        add(f'立即返回 {case} 成本最优切换 z', c['laws']['opt_immediate']['switch_z'], REF.PLAN_IMMEDIATE_SWITCH_Z, 4)
        add(f'立即返回 {case} 退出附近分担比例', c['laws']['opt_immediate']['terminal_share_z=1+1e-6'],
            REF.PLAN_IMMEDIATE_TERMINAL_SHARE, 3, note='计划写约 0.667（2/3）')
        add(f'立即返回 {case} 成本最优比仅减少接触低', c['cost_gap_vs_c_only'], REF.PLAN_IR_COST_GAP[case], 2,
            note='计划写“约 37%／40%”', key=True)
    for case in ('base', 'xian'):
        c = nr['cases'][case]
        add(f'无回流 {case} 仅隔离 t→∞', c['laws']['q_only']['C_inf'], REF.PLAN_NORETURN_INF[case], 6, key=True)
        add(f'无回流 {case} 清零后增量', c['laws']['q_only']['tail_increment'], REF.PLAN_NORETURN_INF_INCREMENT[case],
            3 if case == 'base' else 2, note='计划写“约”')
        add(f'{case} L = U(0) − S_c', c['L'], REF.PLAN_L_BOUND[case], 6, key=True)
        for law in LAWS_NR:
            disp = REF.TABLE2_DISPLAY[(case, law)][2] * REF.TABLE2_UNIT[case]
            add(f'无回流 {case} {law} 计至清零（表 2 展示值）', c['laws'][law]['C_t_end'], disp,
                4 if case == 'base' else 5, note='表 2 展示值已舍入')
    for (case, law), p in REF.PLAN_OMEGA14_OLD.items():
        d = ret['runs'][f'{case}|14|{law}']
        s5 = 4 if case == 'base' else 5
        add(f'1/ω=14 {case} {law} Δt（旧反馈实现）', d['dt'], p['dt'], s5, key=True,
            note='旧实现为定步长反馈（步长 0.005／0.05 d）')
        add(f'1/ω=14 {case} {law} J（旧反馈实现）', d['J'], p['J'], s5, key=True)
        add(f'1/ω=14 {case} {law} 终止时累计感染（尾部判据）vs 旧值（首次 I<1）', d['C_term'], p['C_end'], 4, key=True,
            note='统计终点不同：旧实现在退出后首次 I<1 停止')
        add(f'1/ω=14 {case} {law} 首次 I<1 时累计感染 vs 旧值', d['C_below_one'], p['C_end'], 4,
            note='同一统计终点的对照')
        add(f'1/ω=14 {case} {law} 退出后 max I/η（旧值 1.000）', 1.0 + d['e'], 1.0, 4, note='旧值按 3 位小数舍入')
    for stay, v in REF.PLAN_XIAN_QONLY_DT_OTHER.items():
        add(f'1/ω={stay} xian q_only Δt', ret['runs'][f'xian|{stay}|q_only']['dt'], v, 4, key=True,
            note='旧反馈实现')
    for (case, law), v in REF.PLAN_OMEGA14_EXCESS.items():
        d = ret['runs'][f'{case}|14|{law}']
        s = 3 if v >= 10 else 2
        add(f'1/ω=14 {case} {law} 超出下界幅度（%，尾部判据）', 100 * d['excess_rel'], v, s, kind='pp', key=True,
            note='统计终点不同')
        add(f'1/ω=14 {case} {law} 超出下界幅度（%，首次 I<1）', 100 * (d['C_below_one'] - d['L']) / d['L'], v, s,
            kind='pp', note='同一统计终点的对照')
    for stay in (120, 365):
        d = ret['runs'][f'base|{stay}|q_only']
        add(f'1/ω={stay} base q_only I<1 后回升峰值（人）', d['regrowth_peak_I'], REF.PLAN_REGROWTH_RANGE_BASE,
            kind='range', note='计划只给范围 10–12 人')
    for case in ('base', 'xian'):
        r = rel_['cases'][case]
        p = REF.PLAN_RELEASE[case]
        add(f'释放 {case} S_q(t2)/S_c', r['Sq_t2_over_Sc'], p['Sq_over_Sc'], 4, key=True)
        add(f'释放 {case} R_e(t2⁺)', r['Re_after_release'], p['Re'], 3, key=True)
    max_id = max(v['identity_residual_rel'] for v in ret['runs'].values())
    add('U 恒等式相对残差（指数回流 36 条，最大）', max_id, 1e-8, kind='bound', note='计划：<1e-8')
    out = dict(rows=rows, rule='flag = 关键数且相对差 > 1% 且与参考值按所示位数的舍入不一致',
               n_flag=sum(r['flag'] for r in rows), flagged=[r for r in rows if r['flag']],
               n_rel_over_1pct=sum(bool(r['rel_diff'] is not None and r['rel_diff'] > 1e-2) for r in rows),
               not_rounding_consistent=[r['item'] for r in rows if r['rounding_consistent'] is False])
    dump('r7_3_plan_comparison.json', out)
    return out


# ---------------------------------------------------------------------------
# 展示用 markdown（全精度在 JSON）
# ---------------------------------------------------------------------------
LAW_CN = {'q_only': '仅隔离', 'alpha': 'α=0.5', 'opt_immediate': '成本最优', 'opt_noreturn': '成本最优',
          'c_only': '仅减少接触'}
LAW_CN_RET = {'q_only': '仅隔离', 'c_only': '仅减少接触', 'opt_noreturn': '迁移律'}
CROSS_CN = {'crossed': '是', 'not_crossed': '否', 'undetermined': '数值上未确定', None: '—'}


def fmt_persons(case, v, nd_base=2, nd_xian=6):
    if v is None:
        return '—'
    return f'{v:.{nd_base}f}' if case == 'base' else f'{v:.{nd_xian}e}'


def write_markdown(ep, ret, rel_, nr, conv, cmp_):
    md = ['# R7-3 数值结果（自动生成；全精度见同名 JSON）', '']
    md += ['## 1 端点小表：立即返回对照模型（w_c=1, w_q=2；S 坐标求积，事件法交叉核对）', '',
           '| 参数 | 控制 | Δt（d） | 控制期累计感染 | K_q（人次） | J（d） | 事件法 Δt、J 相对差 |',
           '|---|---|---|---|---|---|---|']
    for case in ('base', 'xian'):
        c = ep['cases'][case]
        for law in LAWS_IR:
            d = c['laws'][law]
            md.append(f"| {case} | {LAW_CN[law]} | {d['dt']:.8g} | {fmt_persons(case, d['arc_infections'])} | "
                      f"{fmt_persons(case, d['Kq'])} | {d['J']:.8g} | "
                      f"{max(d['event_vs_quad_rel']['dt'], d['event_vs_quad_rel']['J']):.1e} |")
    for case in ('base', 'xian'):
        c = ep['cases'][case]
        sw = c['laws']['opt_immediate']
        md.append(f"\n- {case}：S*_ir = {c['S_star_ir']:.10g}，S_c = {c['S_c']:.10g}，A = {c['A']:.6f}，"
                  f"I_peak,ir = {c['I_peak_ir']:.6g}（触发条件 {c['trigger_condition']}）；成本最优比仅减少接触低 "
                  f"{100 * c['cost_gap_vs_c_only']:.2f}%，比仅隔离低 {100 * c['cost_gap_vs_q_only']:.2f}%；"
                  f"切换 z = {sw['switch_z']:.12f}，陡峭点 {sw['steep_points']}；退出附近分担比例 "
                  f"{sw['terminal_share_z=1+1e-6']:.6f}；Δt 排序 {c['dt_order']}，K_q 与 Δt 反序 {c['Kq_reverse_of_dt']}；"
                  f"J 排序 {c['J_order']}。")
    md += ['', '## 2 指数回流表（事件法，基准容差）', '',
           '| 参数 | 1/ω | 控制律 | Δt | J | e_int | 越过 η | I<1 后回升（峰值） | 终止 | 终止时累计感染 | 超出 L | 尾部上界 B | t→∞ 估计 |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for case in ('base', 'xian'):
        for stay in STAYS:
            for law in LAWS_RETURN:
                d = ret['runs'][f'{case}|{stay}|{law}']
                ei = '—' if d['e_interior'] is None else f"{d['e_interior']:.6f}"
                if d['below_one_time'] is None:
                    rg = '否（终止时 I>1，此后单调下降）'
                elif d['regrowth_after_below_one']:
                    rg = f"是（{d['regrowth_peak_I']:.4g} 人）"
                else:
                    rg = '否'
                fe = (f"[{fmt_persons(case, d['final_estimate'][0])}, {fmt_persons(case, d['final_estimate'][1])}]"
                      if d['final_estimate'] else '未可靠估计')
                md.append(f"| {case} | {stay} | {LAW_CN_RET[law]} | {d['dt']:.8g} | {d['J']:.8g} | {ei} | "
                          f"{CROSS_CN[d['crossing']]} | {rg} | {'是' if d['reached'] else '未到达'} | "
                          f"{fmt_persons(case, d['C_term'])} | {100 * d['excess_rel']:.4f}% | {d['tail_bound']:.3g} | {fe} |")
    md += ['', '### 事件法与反馈重放（ω > 0）', '',
           '| 参数 | 1/ω | 控制律 | Δt 相对差 | J 相对差 | 首次 I<1 时累计感染相对差 | 重放 max I/η（退出后至首次 I<1） | 事件法同窗口 e | 重放控制段数 | 退出后请求重启步数 |',
           '|---|---|---|---|---|---|---|---|---|---|']
    for case in ('base', 'xian'):
        for stay in STAYS:
            for law in LAWS_RETURN:
                rp = ret['runs'][f'{case}|{stay}|{law}'].get('replay')
                if not rp:
                    continue
                c1 = '—' if rp['rel_C_first_below_one'] is None else f"{rp['rel_C_first_below_one']:.1e}"
                ee = '—' if rp['event_e_until_below_one'] is None else f"{rp['event_e_until_below_one']:.2e}"
                md.append(f"| {case} | {stay} | {LAW_CN_RET[law]} | {rp['rel_dt']:.1e} | {rp['rel_J']:.1e} | {c1} | "
                          f"{rp['Imax_after_over_eta']:.6f} | {ee} | {rp['n_episodes']} | {rp['n_would_reopen']} |")
    if ret.get('replay_omega0'):
        md += ['', '### 事件法与反馈重放（ω = 0）', '', '| 参数 | 控制 | Δt 相对差 | J 相对差 | 计至清零累计感染相对差 |',
               '|---|---|---|---|---|']
        for k, v in ret['replay_omega0'].items():
            case, law = k.split('|')
            md.append(f"| {case} | {LAW_CN[law]} | {v['rel_dt']:.1e} | {v['rel_J']:.1e} | {v['rel_C']:.1e} |")
    md += ['', '## 3 释放用数（ω=0，仅隔离，ξ=1）', '']
    for case in ('base', 'xian'):
        r = rel_['cases'][case]
        md.append(f"- {case}：S_q(t2)/S_c = {r['Sq_t2_over_Sc']:.10f}（解析 {r['Sq_t2_over_Sc_analytic']:.10f}，相对差 "
                  f"{r['rel_event_vs_analytic']:.1e}），R_e(t2⁺) = {r['Re_after_release']:.10f}。")
    md += ['', '## 4 无回流 t→∞ 对照（ω=0）', '',
           '| 参数 | 控制 | C_π(0)（t→∞，事件法） | 闭式 | 相对差 | 计至清零 | L = U(0)−S_c | C_π(0) < L | L − C_π(0) |',
           '|---|---|---|---|---|---|---|---|---|']
    for case in ('base', 'xian'):
        c = nr['cases'][case]
        for law in LAWS_NR:
            d = c['laws'][law]
            md.append(f"| {case} | {LAW_CN[law]} | {d['C_inf']:.10g} | {d['C_inf_closed']:.10g} | {d['rel_event_vs_closed']:.1e} | "
                      f"{d['C_t_end']:.10g} | {c['L']:.10g} | {'满足' if d['below_L'] else '不满足'} | {d['margin_L_minus_C']:.6g} |")
    md += ['', '## 6 收敛', '', '### 逐状态最小化：N_x 网格最小值减根法最小值', '',
           '| 参数 | 范围 | 状态点数 | N_x=2001 max / min | 4001 max / min | 8001 max / min | 违反判据的状态数 |', '|---|---|---|---|---|---|---|']
    for k, v in conv['pointwise'].items():
        r = v['result']
        md.append(f"| {k} | z∈[{v['z_range'][0]:.9f}, {v['z_range'][1]:.6f}] | {r['2001']['n_states']} | "
                  f"{r['2001']['max_gap']:.2e} / {r['2001']['min_gap']:.1e} | {r['4001']['max_gap']:.2e} / {r['4001']['min_gap']:.1e} | "
                  f"{r['8001']['max_gap']:.2e} / {r['8001']['min_gap']:.1e} | "
                  f"{sum(r[n]['n_violations'] for n in ('2001', '4001', '8001'))} |")
    md += ['', '### 立即返回端：N_z（分段 Simpson）与自适应 quad', '',
           '| 参数 | 控制 | N_z | Δt | J | 与 quad 的 Δt / J 相对差 | 切换 z |', '|---|---|---|---|---|---|---|']
    for k, rows in conv['quadrature_N_z'].items():
        case, law = k.split('|')
        for nz, v in rows.items():
            sw = '—' if v['switch_z'] is None else f"{v['switch_z']:.12f}"
            md.append(f"| {case} | {LAW_CN[law]} | {nz} | {v['dt']:.12g} | {v['J']:.12g} | "
                      f"{v['rel_dt_quad']:.1e} / {v['rel_J_quad']:.1e} | {sw} |")
    ts = conv['tolerance_summary']
    md += ['', '### 积分容差（基准 → 收紧 / 放宽）', '',
           f"{ts['n_runs']} 条轨迹；收紧后非零指标的最大相对变化 {ts['max_rel_change_tight']:.2e}；"
           f"e_int 的最大绝对变化 {ts['max_abs_e_change_tight']}；全部通过：{ts['all_pass']}（未通过：{ts['failed']}）。"
           f"三档中最大残差：U 恒等式 {ts['max_identity_residual']:.1e}，触发 {ts['max_trigger_residual']:.1e}，"
           f"退出 {ts['max_exit_residual']:.1e}，清零 {ts['max_clearance_residual']:.1e} 人。", '',
           '| 轨迹 | 收紧：最大相对变化（指标） | 放宽：最大相对变化 | 收紧 |Δe_int| | t1、t2 相对变化（收紧） | 退出后峰值相对变化（收紧） | 通过 |',
           '|---|---|---|---|---|---|---|']
    for k, row in conv['tolerance'].items():
        rt, rl, at = row['rel_change']['tight'], row['rel_change']['loose'], row['abs_change']['tight']
        km = max(rt, key=rt.get) if rt else '—'
        md.append(f"| {k} | {rt.get(km, 0):.1e}（{km}） | {max(rl.values(), default=0):.1e} | "
                  f"{at.get('e_interior', '—') if at.get('e_interior') is None else format(at['e_interior'], '.1e')} | "
                  f"{rt.get('t1', 0):.1e}、{rt.get('t2', 0):.1e} | "
                  f"{'—' if rt.get('post_max_I') is None else format(rt['post_max_I'], '.1e')} | {'是' if row['pass_tight'] else '否'} |")
    md += ['', '## 与执行计划第 5 节参考值的对照', '',
           f"判据：{cmp_['rule']}。触发停止条件的项 {cmp_['n_flag']} 个；相对差 > 1% 的项 {cmp_['n_rel_over_1pct']} 个。", '',
           '| 项 | 本步 | 计划（所示有效位数） | 相对差 | 与舍入一致 | 停止条件 | 说明 |', '|---|---|---|---|---|---|---|']
    for r in cmp_['rows']:
        ours = r['ours'] if not isinstance(r['ours'], float) else f"{r['ours']:.8g}"
        plan = r['plan'] if r['plan_sig'] is None else f"{r['plan']}（{r['plan_sig']} 位）"
        rd = '—' if r['rel_diff'] is None else f"{r['rel_diff']:.1e}"
        rc = {True: '是', False: '否', None: '—'}[r['rounding_consistent']]
        md.append(f"| {r['item']} | {ours} | {plan} | {rd} | {rc} | {'**触发**' if r['flag'] else ''} | {r['note']} |")
    with open(os.path.join(RESULTS, 'r7_3_numerics.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(md) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-replay', action='store_true')
    ap.add_argument('--report-only', action='store_true',
                    help='不重算，只由已有 results/r7_3_*.json 重做参考值对照与 markdown')
    args = ap.parse_args()
    t0 = time.time()
    if args.report_only:
        def load(name):
            with open(os.path.join(RESULTS, name), encoding='utf-8') as fh:
                return json.load(fh)
        ep, ret, rel_, nr, conv = (load(f'r7_3_{n}.json') for n in
                                   ('endpoint_immediate', 'exponential_return', 'release', 'noreturn_inf', 'convergence'))
        cmp_ = task_plan_comparison(ep, ret, rel_, nr)
        write_markdown(ep, ret, rel_, nr, conv, cmp_)
        print('R7-3 report-only；触发停止条件的项 %d 个' % cmp_['n_flag'])
        return
    ep = task_endpoint()
    print('R7-3 endpoint done %.0fs' % (time.time() - t0), flush=True)
    ret = task_return(with_replay=not args.no_replay)
    print('R7-3 return done %.0fs' % (time.time() - t0), flush=True)
    rel_ = task_release()
    nr = task_noreturn_inf()
    print('R7-3 release/noreturn done %.0fs' % (time.time() - t0), flush=True)
    conv = task_convergence(ret)
    print('R7-3 convergence done %.0fs' % (time.time() - t0), flush=True)
    cmp_ = task_plan_comparison(ep, ret, rel_, nr)
    write_markdown(ep, ret, rel_, nr, conv, cmp_)
    print('R7-3 done %.0fs; 触发停止条件的项 %d 个' % (time.time() - t0, cmp_['n_flag']), flush=True)


if __name__ == '__main__':
    main()
