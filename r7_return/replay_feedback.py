"""旧的反馈实现（只作独立重放核验）。

复制自 ai/R7_回流检验/fast_return.py 的 simulate（“首次关闭即退出”的一次性退出版本），
并按 ai/数值工作汇总_20261004/02_隔离易感者返回检验/sq_return.py 的写法补上 J 与追踪人次的累计。
原文件未改动。

实现要点（与原程序相同）：
- 人数尺度的方程，定步长 RK4（基准 dt = 0.005，西安 dt = 0.05），控制在一步内保持不变；
- I ≥ 0.999η 且所需 c(1-q) 低于常规值时开启控制，所需值由跟踪 I = η 的反馈给出：
      c(1-q) = (γ - k (I-η)/I) N/(βS)，增益 k = 2；
  c = min(max(c0 x(S/S_c), 所需值/(1-q0)), c0)，q = 1 - 所需值/c；
- 控制首次关闭的时刻记为 t2，此后永不重启（oneshot = True）。
这是与事件法（simulate.py）不同的第二种实现，只用于交叉核对；不以控制器某一步的开关状态
代替理论退出事件，结果也不是真值。

新增的诊断（不改变原逻辑）：
- n_episodes：控制开启的段数；
- n_would_reopen：退出后若不禁止重启、反馈规则会开启控制的步数（只计数，不实施）。
"""
import numpy as np


def replay(P, xfun, omega=0.0, dt=None, T=None, k=2.0, oneshot=True, wc=None, wq=None):
    """P：params.Params；xfun(z)：控制律 c/c0（z = S/S_c）；omega：回流率。
    返回 dict(t1, t2, dt_ctrl, J, inf_total, Kq_arc, Imax_after_eta, n_episodes, n_would_reopen, t_end)。"""
    N, b, g, dq, c0, q0, eta = P.N, P.beta, P.gamma, P.delta_q, P.c0, P.q0, P.eta
    wc = P.wc if wc is None else wc
    wq = P.wq if wq is None else wq
    if dt is None:
        dt = 0.005 if P.name == 'base' else 0.05
    if T is None:
        T = 3000.0 if P.name == 'base' else 5000.0
    lam = omega
    Sc = g * N / (b * c0 * (1 - q0))
    base = c0 * (1 - q0)
    y = np.array([P.S0, P.I0, P.Sq0, P.Iq0, P.R0], float)
    t, on_prev, exited = 0.0, False, False
    t1 = t2 = None
    inf = sq_in = J = 0.0
    inf_t1 = inf_t2 = sqin_t1 = sqin_t2 = 0.0
    Imax_after = 0.0
    t_end = None
    n_episodes = 0
    n_would_reopen = 0

    def rhs(y, c, q):
        S, I, Sq, Iq, R = y
        inc = c * S * I / N
        return np.array([-(b + (1 - b) * q) * inc + lam * Sq, b * (1 - q) * inc - g * I,
                         (1 - b) * q * inc - lam * Sq, b * q * inc - dq * Iq, g * I + dq * Iq]), inc

    while t < T:
        S, I = y[0], y[1]
        on = False
        c, q = c0, q0
        if I >= 0.999 * eta:
            req = (g - k * (I - eta) / I) * N / (b * S)
            if req < base:
                if not exited:
                    c = min(max(c0 * xfun(S / Sc), req / (1 - q0)), c0)
                    q = 1 - req / c
                    on = True
                else:
                    n_would_reopen += 1      # 诊断：退出后不实施
        if on and not on_prev:
            n_episodes += 1
            if t1 is None:
                t1, inf_t1, sqin_t1 = t, inf, sq_in
        if on_prev and not on:
            if t2 is None:
                t2, inf_t2, sqin_t2 = t, inf, sq_in
            if oneshot:
                exited = True
        on_prev = on
        k1, i1 = rhs(y, c, q)
        k2, i2 = rhs(y + .5 * dt * k1, c, q)
        k3, i3 = rhs(y + .5 * dt * k2, c, q)
        k4, i4 = rhs(y + dt * k3, c, q)
        incm = (i1 + 2 * i2 + 2 * i3 + i4) / 6
        y = y + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        inf += dt * b * incm
        sq_in += dt * (1 - b) * q * incm
        J += dt * (wc * (1 - c / c0) ** 2 + wq * ((q - q0) / (1 - q0)) ** 2)
        t += dt
        if t2 is not None:
            Imax_after = max(Imax_after, y[1])
        if t_end is None and t2 is not None and y[1] < 1:
            t_end = t
            break
    return dict(t1=t1, t2=t2, dt_ctrl=(t2 - t1) if t2 is not None else None, J=J, t_end=t_end,
                inf_total=inf, inf_arc=inf_t2 - inf_t1, Kq_arc=sqin_t2 - sqin_t1,
                Imax_after_eta=Imax_after / eta, n_episodes=n_episodes, n_would_reopen=n_would_reopen,
                step=dt, gain=k, U_end=y[0] + y[2])
