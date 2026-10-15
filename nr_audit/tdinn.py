"""TDINN 控制与常规控制下的完整方程（时间开环，无回流模型 2.1）：西安的外部参照值与拟合窗口（NR-3 的 N1、N5）。

控制函数取自稿件式 (7.1)（He、Tang、Xiao 2023 表 3 的 c_2、q_2），与 reproducibility/xian.py 的 controls
逐项相同（原文件只读、未运行）。c0、q0 取两函数在 t = 0 的值（稿件表 1）。时间原点 t = 0 为 2021-12-09 的开始，
第 k 个日区间为 [k, k+1]。

状态与 simulate.py 相同：[s, ln i, s_q, i_q, r, cI, cIq, ∫i, J, J_c, J_q]；cI、cIq 为独立积分的流量
（进入 I、进入 I_q，即社区与隔离发现的新增病例的模型对应量）。J 从初始时刻计（TDINN 在 t > 0 时都在加强）。
"""
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

import model as M
import simulate as SM

IS, ILI, ISQ, IIQ, IR, ICI, ICIQ, IINT, IJ, IJC, IJQ = range(11)


def c_tdinn(t):
    return (12.8872 - 3.4625) * math.exp(-(0.0463 * t) ** 2) + 3.4625


def q_tdinn(t):
    return (0.3230 - 0.9844) * math.exp(-(0.0452 * t) ** 2) + 0.9844


def tdinn(t):
    return c_tdinn(t), q_tdinn(t)


def routine_of(P):
    return lambda t: (P.c0, P.q0)


def _rhs(P, control, wc, wq):
    def f(t, y):
        c, q = control(t)
        s, i = y[IS], math.exp(y[ILI])
        ds, di, dsq, diq, dr = M.rhs_N(s, i, y[ISQ], y[IIQ], y[IR], c, q, P)
        _, into_I, into_Iq, _ = M.flows_N(s, i, c, q, P)
        uc, uq = M.intensities(c, q, P)
        return [ds, M.log_growth_rate(s, c, q, P), dsq, diq, dr, into_I, into_Iq, i,
                M.cost_rate(uc, uq, wc, wq), uc, uq]
    return f


def run(P, control, cfg=None, t_stop=None, t_max=2000.0, wc=None, wq=None):
    """从 t = 0 积分。t_stop 给定时积分到该时刻（不判清零）；否则积分到清零：I 上升后由上方降到 1（终止事件）。
    返回 dict（人数以人计）与 solve_ivp 的解（稠密输出）。"""
    cfg = cfg or SM.Config()
    wc = P.wc if wc is None else wc
    wq = P.wq if wq is None else wq
    atol = SM.default_atol(P, cfg.atol_scale)
    y0 = [P.s0_N, math.log(P.i0_N), P.Sq0 / P.N, P.Iq0 / P.N, P.R0 / P.N, 0, 0, 0, 0, 0, 0]
    l_one = math.log(1.0 / P.N)
    ev = None
    if t_stop is None:
        ev = lambda t, y: y[ILI] - l_one
        ev.terminal, ev.direction = True, -1
    sol = solve_ivp(_rhs(P, control, wc, wq), (0.0, t_stop if t_stop is not None else t_max), y0,
                    method=cfg.method, rtol=cfg.rtol, atol=atol, max_step=cfg.max_step,
                    events=ev, dense_output=True)
    if sol.status == -1:
        raise RuntimeError(sol.message)
    out = dict(settings=dict(method=cfg.method, rtol=cfg.rtol, atol=atol.tolist(), max_step=cfg.max_step))
    if t_stop is None:
        if not len(sol.t_events[0]):
            raise RuntimeError('未清零')
        T, yT = float(sol.t_events[0][0]), sol.y_events[0][0]
        out.update(t_end=T, n_clearance_events=len(sol.t_events[0]),
                   clearance_I_error=math.exp(yT[ILI]) * P.N - 1.0)
    else:
        T, yT = float(sol.t[-1]), sol.y[:, -1]
    out.update(T=T, cI=yT[ICI] * P.N, cIq=yT[ICIQ] * P.N, total=(yT[ICI] + yT[ICIQ]) * P.N,
               J=yT[IJ], Jc=yT[IJC], Jq=yT[IJQ], S_T=yT[IS] * P.N)
    # 质量与流量恒等式（全部积分步上）
    Y = sol.y
    i = np.exp(Y[ILI])
    out['mass_residual_persons'] = float(np.max(np.abs(Y[IS] + i + Y[ISQ] + Y[IIQ] + Y[IR] - 1.0))) * P.N
    s0q0 = P.s0_N + P.Sq0 / P.N
    out['identity_residual_rel'] = float(np.max(np.abs(Y[ICI] + Y[ICIQ] - (s0q0 - Y[IS] - Y[ISQ])))) / s0q0
    # 非隔离感染者峰值：采样最大值，再在 d ln I/dt 由正变负处用 brentq 加密
    tt = np.unique(np.r_[np.linspace(0.0, T, 4001), sol.t[sol.t <= T]])
    li = sol.sol(tt)[ILI]
    k = int(np.argmax(li))
    cands = [(float(li[k]), float(tt[k]))]
    g = lambda t: M.log_growth_rate(float(sol.sol(t)[IS]), *control(t), P)
    gv = np.array([g(t) for t in tt])
    for a, b, ga, gb in zip(tt[:-1], tt[1:], gv[:-1], gv[1:]):
        if ga > 0 >= gb:
            tr = brentq(g, a, b, xtol=1e-12, rtol=1e-14)
            cands.append((float(sol.sol(tr)[ILI]), tr))
    lmax, tmax = max(cands)
    out.update(peak_I=math.exp(lmax) * P.N, t_peak_I=tmax)
    return out, sol


def daily(P, sol, days=40):
    """拟合窗口的模型观测量：第 k 个日区间 [k, k+1] 的社区、隔离新增（流量 cI、cIq 的日积分）与 k+1 时刻的累计。"""
    edges = np.arange(days + 1, dtype=float)
    Y = sol.sol(edges)
    cc, cq = Y[ICI] * P.N, Y[ICIQ] * P.N
    return dict(community_new=np.diff(cc), quarantine_new=np.diff(cq), community_cum=cc[1:], quarantine_cum=cq[1:])
