"""
隔离易感者返回（S_q -> S，速率 lam）对阈值控制结论的影响。

模型（lam=0 即原文模型）：
  S'  = -c[b+(1-b)q] S I/N + lam*Sq
  I'  =  b c (1-q) S I/N - g I
  Sq' = (1-b) c q S I/N - lam*Sq
  Iq' =  b c q S I/N - dq Iq
  R'  =  g I + dq Iq
控制：状态反馈，I 达到 eta 且常规控制不足以使 I 不增时，按分配规则把 c(1-q) 调到
  c(1-q) = (g - k (I-eta)/I) N/(b S)   （跟踪 I=eta 的反馈，k 为纠偏速率）
否则取常规 (c0,q0)。
规则 'feedback'：任何时候 I 回到 eta 都重新控制（I<=eta 始终成立）。
规则 'oneshot' ：原文规则，S 首次降到 S_c 即永久退出，之后不再控制。
"""
import numpy as np
from scipy.interpolate import interp1d
import joint_cost_optimal as M

XIAN = dict(N=13163000, S0=13163000 - 1.00659188867187e-3, I0=1.00659188867187e-3, beta=0.1498, gamma=0.2953,
            delta_q=0.3531, c0=12.8872, q0=0.3230, eta=0.002 * 13163000)
BASE = dict(N=763, S0=762, I0=1, beta=0.155, gamma=0.3504, delta_q=0.3504, c0=10,
            q0=0.01526, eta=0.05 * 763)


def make_alloc(p, policy, wc=1.0, wq=2.0):
    if policy == 'q_only':
        return lambda s: 1.0
    if policy == 'c_only':
        return lambda s: 1.0 / max(s, 1.0)
    sol = M.solve_allocation(p, wc, wq, policy='optimal', ns=4001)
    f = interp1d(sol['s'], sol['x'], bounds_error=False,
                 fill_value=(sol['x'][0], sol['x'][-1]))
    return lambda s: float(f(min(max(s, 1.0), sol['s'][-1])))


def simulate(p, policy='q_only', lam=0.0, rule='feedback', dt=0.01, T=3000.0,
             wc=1.0, wq=2.0, k=2.0, alloc=None, rec=None):
    N, b, g, dq, c0, q0, eta = (p[x] for x in ('N', 'beta', 'gamma', 'delta_q', 'c0', 'q0', 'eta'))
    Sc, Sbar, Sstar = M.basic_quantities(p)
    alloc = alloc or make_alloc(p, policy, wc, wq)
    base = c0 * (1 - q0)
    y = np.array([p['S0'], p['I0'], 0.0, 0.0, N - p['S0'] - p['I0']], float)
    cum = dict(inf=0.0, sq_in=0.0, J=0.0, tctrl=0.0)
    n_ep, on_prev, exited = 0, False, False
    pk = dict(I=0.0, Sq=0.0, Iq=0.0, Iq_plus_I=0.0, I_after_exit=0.0)
    t, t_exc, t_end, t_first_on, t_last_on = 0.0, None, None, None, None
    seg = []  # 控制段 (开始, 结束)
    traj, next_rec = [], 0.0

    def control(S, I):
        if exited or I < 0.999 * eta:
            return c0, q0, False
        req = (g - k * (I - eta) / I) * N / (b * S)
        if req >= base:
            return c0, q0, False
        if policy == 'q_only':
            c = c0
        elif policy == 'c_only':
            c = req / (1 - q0)
        else:
            c = c0 * alloc(S / Sc)
        c = min(max(c, req / (1 - q0)), c0)
        return c, 1 - req / c, True

    def rhs(y, c, q):
        S, I, Sq, Iq, R = y
        inc = c * S * I / N
        return np.array([-(b + (1 - b) * q) * inc + lam * Sq,
                         b * (1 - q) * inc - g * I,
                         (1 - b) * q * inc - lam * Sq,
                         b * q * inc - dq * Iq,
                         g * I + dq * Iq]), inc

    while t < T:
        S, I = y[0], y[1]
        c, q, on = control(S, I)
        if on and not on_prev:
            n_ep += 1
            seg.append([t, None])
            t_first_on = t if t_first_on is None else t_first_on
        if on_prev and not on:
            seg[-1][1] = t
        if on:
            t_last_on = t
            if rule == 'oneshot' and S <= Sc:
                exited = True
        on_prev = on
        if rec and t >= next_rec:
            traj.append((t, *y, cum['inf'], c, q))
            next_rec += rec
        # RK4（控制在步内保持不变，相当于以 dt 采样的反馈）
        k1, i1 = rhs(y, c, q)
        k2, i2 = rhs(y + 0.5 * dt * k1, c, q)
        k3, i3 = rhs(y + 0.5 * dt * k2, c, q)
        k4, i4 = rhs(y + dt * k3, c, q)
        inc = (i1 + 2 * i2 + 2 * i3 + i4) / 6
        y = y + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        cum['inf'] += dt * b * inc
        cum['sq_in'] += dt * (1 - b) * q * inc
        uc, uq = (c0 - c) / c0, (q - q0) / (1 - q0)
        cum['J'] += dt * (wc * uc ** 2 + wq * uq ** 2)
        cum['tctrl'] += dt * on
        t += dt
        pk['I'] = max(pk['I'], y[1]); pk['Sq'] = max(pk['Sq'], y[2])
        pk['Iq'] = max(pk['Iq'], y[3]); pk['Iq_plus_I'] = max(pk['Iq_plus_I'], y[1] + y[3])
        if exited:
            pk['I_after_exit'] = max(pk['I_after_exit'], y[1])
        if t_exc is None and y[1] > 1:
            t_exc = t
        if t_exc is not None and y[1] < 1 and t_end is None:
            t_end = t
            inf_at_end = cum['inf']
        if t_end is not None and y[1] > 1:   # 降到 1 以下后又反弹
            t_end = None
        if t_end is not None and t - t_end > 60 and not on:
            break
    if seg and seg[-1][1] is None:
        seg[-1][1] = t
    return dict(policy=policy, lam=lam, rule=rule, Sc=Sc, Sstar=Sstar, n_ep=n_ep,
                t1=t_first_on, t_last=t_last_on, tctrl=cum['tctrl'], t_end=t_end,
                inf=cum['inf'], sq_in=cum['sq_in'], J=cum['J'], pk=pk, seg=seg,
                y_end=y, P_end=y[0] + y[2], Imax_over_eta=pk['I'] / eta,
                traj=np.array(traj) if rec else None)


if __name__ == '__main__':
    import sys
    for name, p in (('xian', XIAN),):
        for pol in ('q_only', 'optimal', 'c_only'):
            r = simulate(p, pol, lam=0.0)
            print(name, pol, 'tctrl=%.2f J=%.2f inf=%.4g Imax/eta=%.4f t1=%.2f tend=%s'
                  % (r['tctrl'], r['J'], r['inf'], r['Imax_over_eta'], r['t1'], r['t_end']))
