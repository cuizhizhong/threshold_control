"""R7 探索性计算：隔离易感者回流的两个极限与真正的一次性退出。

A. 快速回流极限 lam->inf（被追踪的未感染者立即返回 S，S_q≡0）：
   S' = -beta c S I/N。阈值控制期内 S' = -(beta eta/N) c S，
   即无回流理论中取 Sbar=0、前因子 N/eta 换为 N/(beta eta)。
   检查：时长排序、控制期感染（应恒为 S*-S_c）、隔离人次（应为 (1-b)/b [S*-S_c-g eta dT]）、
   成本最优控制的结构（S_sw 应为 3 S_c）与退出比例 2/3。
B. 用大 lam 的完整模型模拟核对 A。
C. lam=1/14 下真正的一次性退出（控制首次关闭后永不重启）：退出后 I 的最大值。
   （02 目录的 sq_return.py 中 oneshot 标志在控制关闭时不会被置位，oneshot 实际等同 feedback。）
D. 审稿人情景：无回流模型按原文控制到 t_end，随后全部 S_q 一次性返回 S，常规控制下的反弹。
"""
import sys, json, os
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import simpson

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '数值工作汇总_20261004', '02_隔离易感者返回检验'))
import joint_cost_optimal as M  # noqa: E402
from sq_return import XIAN, BASE  # noqa: E402


# ---------------- A. 快速回流极限的解析/求积 ----------------
def limit_quantities(p):
    N, b, g, c0, q0, eta, S0, I0 = (p[k] for k in ('N', 'beta', 'gamma', 'c0', 'q0', 'eta', 'S0', 'I0'))
    Sc = g * N / (b * c0 * (1 - q0))
    Ifun = lambda S: I0 + (1 - q0) * (S0 - S) + g * N / (b * c0) * np.log(S / S0)
    Sstar = brentq(lambda S: Ifun(S) - eta, Sc * (1 + 1e-12), S0)
    return Sc, Sstar


def limit_policy(p, policy, wc=1.0, wq=2.0, ns=8001, alpha=0.5):
    N, b, g, c0, q0, eta = (p[k] for k in ('N', 'beta', 'gamma', 'c0', 'q0', 'eta'))
    Sc, Sstar = limit_quantities(p)
    s = np.linspace(1.0, Sstar / Sc, ns)
    if policy == 'q_only':
        x = np.ones_like(s)
    elif policy == 'c_only':
        x = 1.0 / s
    elif policy == 'alpha':
        x = alpha + (1 - alpha) / s
    else:
        x = np.array([M.pointwise_global_min(si, p, 0.0, wc, wq, 0.0)[0] for si in s])
    pref = N / (b * eta * c0)          # dt = pref * ds / (x s)，s = S/Sc
    q = 1 - (1 - q0) / (x * s)
    dT = pref * simpson(1 / (x * s), x=s)
    J = pref * simpson((wc * (1 - x) ** 2 + wq * (1 - 1 / (x * s)) ** 2) / (x * s), x=s)
    # 控制期计数：总感染 = S*-S_c；隔离人次 = (1-b)/b * ∫ q dS
    entries_direct = (1 - b) / b * Sc * simpson(q, x=s)
    entries_formula = (1 - b) / b * (Sstar - Sc - g * eta * dT)
    out = dict(Sc=Sc, Sstar=Sstar, sstar=Sstar / Sc, dT=dT, J=J, infections_arc=Sstar - Sc,
               untraced_arc=g * eta * dT, entries_direct=entries_direct, entries_formula=entries_formula,
               inflow_ratio_start=1 / (1 - q[-1]))
    if policy == 'optimal':
        inner = np.where(x < 1 - 1e-9)[0]
        out['s_switch_numeric'] = float(s[inner.max()]) if len(inner) else None
        k = 5  # 退出附近
        out['terminal_contact_share'] = float((1 - x[k]) / (1 - 1 / s[k]))
        out['s_sw_theory_Sbar0'] = 3.0
    return out


# ---------------- 简单完整模型模拟（RK4 + 跟踪 I=eta 的反馈） ----------------
def simulate(p, xfun, lam, T, dt=0.01, k=2.0, oneshot=True, release_at=None, rec=False):
    """xfun(s) 给出 c/c0；oneshot=True 时控制首次关闭后永不重启。
    release_at：在该时刻把全部 S_q 一次性移回 S（审稿人情景）。"""
    N, b, g, dq, c0, q0, eta = (p[x] for x in ('N', 'beta', 'gamma', 'delta_q', 'c0', 'q0', 'eta'))
    Sc = g * N / (b * c0 * (1 - q0))
    base = c0 * (1 - q0)
    y = np.array([p['S0'], p['I0'], 0.0, 0.0, N - p['S0'] - p['I0']])
    t, on_prev, exited, released = 0.0, False, False, False
    t1 = t2 = None
    inf = sq_in = inf_t1 = inf_t2 = sqin_t1 = sqin_t2 = 0.0
    Imax_after = 0.0
    t_end = None
    traj = []

    def rhs(y, c, q):
        S, I, Sq, Iq, R = y
        inc = c * S * I / N
        return np.array([-(b + (1 - b) * q) * inc + lam * Sq, b * (1 - q) * inc - g * I,
                         (1 - b) * q * inc - lam * Sq, b * q * inc - dq * Iq, g * I + dq * Iq]), inc

    while t < T:
        S, I = y[0], y[1]
        on = False
        c, q = c0, q0
        if not exited and I >= 0.999 * eta:
            req = (g - k * (I - eta) / I) * N / (b * S)
            if req < base:
                c = min(max(c0 * xfun(S / Sc), req / (1 - q0)), c0)
                q = 1 - req / c
                on = True
        if on and not on_prev and t1 is None:
            t1, inf_t1, sqin_t1 = t, inf, sq_in
        if on_prev and not on:
            if t2 is None:
                t2, inf_t2, sqin_t2 = t, inf, sq_in
            if oneshot:
                exited = True
        on_prev = on
        if release_at is not None and not released and t >= release_at:
            y[0] += y[2]; y[2] = 0.0; released = True
        if rec and abs(t / 0.5 - round(t / 0.5)) < 1e-9:
            traj.append((t, *y))
        k1, i1 = rhs(y, c, q); k2, i2 = rhs(y + .5 * dt * k1, c, q)
        k3, i3 = rhs(y + .5 * dt * k2, c, q); k4, i4 = rhs(y + dt * k3, c, q)
        incm = (i1 + 2 * i2 + 2 * i3 + i4) / 6
        y = y + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        inf += dt * b * incm
        sq_in += dt * (1 - b) * q * incm
        t += dt
        if t2 is not None:
            Imax_after = max(Imax_after, y[1])
        if t_end is None and t2 is not None and y[1] < 1:
            t_end = t
            if release_at is None:
                break
        if release_at is not None and released and y[1] < 1 and t > release_at + 5:
            break
    return dict(t1=t1, t2=t2, dT=(t2 - t1) if t2 else None, t_end=t_end, inf_total=inf,
                inf_arc=inf_t2 - inf_t1, sqin_arc=sqin_t2 - sqin_t1, Imax_after_eta=Imax_after / eta,
                SplusSq_over_Sc=(y[0] + y[2]) / Sc, S_over_Sc=y[0] / Sc, traj=np.array(traj) if rec else None)


def xfun_from(p, policy, limit=False, wc=1.0, wq=2.0):
    if policy == 'q_only':
        return lambda s: 1.0
    if policy == 'c_only':
        return lambda s: 1.0 / max(s, 1.0)
    if limit:
        Sc, Sstar = limit_quantities(p)
        sg = np.linspace(1.0, Sstar / Sc, 2001)
        xg = np.array([M.pointwise_global_min(si, p, 0.0, wc, wq, 0.0)[0] for si in sg])
    else:
        sol = M.solve_allocation(p, wc, wq, policy='optimal', ns=2001)
        sg, xg = sol['s'], sol['x']
    return lambda s: float(np.interp(s, sg, xg))


if __name__ == '__main__':
    out = {}
    for name, p, T in (('base', BASE, 3000.0), ('xian', XIAN, 5000.0)):
        Sc0, Sbar0, Sstar0 = M.basic_quantities(p)
        out[f'{name}|no_return_ref'] = dict(Sc=Sc0, Sstar=Sstar0, sstar=Sstar0 / Sc0,
                                            s_sw=(3 + np.sqrt(9 - 8 * Sbar0 / Sc0)) / 2)
        for pol in ('q_only', 'alpha', 'optimal', 'c_only'):
            out[f'{name}|limit|{pol}'] = limit_policy(p, pol)
        print(name, json.dumps({k: v for k, v in out.items() if k.startswith(name)}, indent=1, default=float))

        # B. 大 lam 模拟核对极限（分配用极限下的成本最优）
        for lam in (1.0, 5.0):
            for pol in ('q_only', 'optimal', 'c_only'):
                r = simulate(p, xfun_from(p, pol, limit=True), lam, T, dt=0.005 if lam > 1 else 0.01)
                r.pop('traj')
                out[f'{name}|sim_lam={lam}|{pol}'] = r
                print(f'{name} lam={lam} {pol}: dT={r["dT"]:.2f} inf_arc={r["inf_arc"]:.5g} '
                      f'sqin_arc={r["sqin_arc"]:.5g} inf_total={r["inf_total"]:.5g} Imax_after/eta={r["Imax_after_eta"]:.4f}',
                      flush=True)

        # C. lam=1/14、真正的一次性退出（用无回流模型的成本最优分配，与 02 目录一致）
        for pol in ('q_only', 'optimal', 'c_only'):
            for one in (True, False):
                r = simulate(p, xfun_from(p, pol), 1 / 14, T, oneshot=one)
                r.pop('traj')
                out[f'{name}|lam=1/14|oneshot={one}|{pol}'] = r
                print(f'{name} lam=1/14 oneshot={one} {pol}: dT={r["dT"]:.2f} t_end={r["t_end"]} '
                      f'inf_total={r["inf_total"]:.5g} Imax_after/eta={r["Imax_after_eta"]:.4f} '
                      f'(S+Sq)/Sc_end={r["SplusSq_over_Sc"]:.3f}', flush=True)

        # D. 审稿人情景：无回流控制至 t_end，然后全部 S_q 一次性返回
        for pol in ('q_only', 'c_only'):
            r0 = simulate(p, xfun_from(p, pol), 0.0, T)
            r = simulate(p, xfun_from(p, pol), 0.0, T * 3, release_at=r0['t_end'])
            r.pop('traj'); r0.pop('traj')
            out[f'{name}|release_at_tend|{pol}'] = dict(no_release=r0, release=r)
            print(f'{name} release at t_end={r0["t_end"]:.1f} {pol}: inf_total {r0["inf_total"]:.5g} -> '
                  f'{r["inf_total"]:.5g}; I peak after release / eta = {r["Imax_after_eta"]:.2f}', flush=True)

    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, 'results', 'fast_return.json'), 'w', encoding='utf-8'),
              indent=1, default=float, ensure_ascii=False)
