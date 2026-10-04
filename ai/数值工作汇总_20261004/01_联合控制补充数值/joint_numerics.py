"""联合阈值控制的补充数值（探索性，2026-10-03）。

不修改冻结包与正式复现输出；参数来源：
  基准：ai/threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json
  西安：reproducibility/results/20261003_release_final/xian/reference.json（I0_abs），eta=0.002N

方法：
  1. 平台类内逐状态全局最小。s=S/Sc, x=c/c0, sbar=Sbar/Sc,
       min_x  [wc(1-x)^2 + wq(1-1/(xs))^2 + kappa] / (x s - sbar),
     x 取值 [max(1/s, cmin/c0), min(1, (1-q0)/((1-qcap)s))]。
     向量化细网格找全局最小格点，再用抛物线插值与有界一维搜索加密。
  2. 三阶段时间开环完整 ODE：常规控制至 I=eta（上升）；平台期用名义 S(t)
     预先构造 c(t),q(t) 的时间函数输入完整 SIQR；S 到 Sc 后恢复常规，至 I=1（下降）。
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp, simpson, cumulative_trapezoid
from scipy.optimize import brentq, minimize_scalar

ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------- 参数
def baseline_params():
    js = json.loads((ROOT / "ai/threshold_control_reproducible_release_20261002/numerics/inputs/"
                     "baseline_parameters.json").read_text(encoding="utf-8"))
    p = dict(js["parameters"])
    return p


def xian_params():
    ref = json.loads((ROOT / "reproducibility/results/20261003_release_final/xian/reference.json")
                     .read_text(encoding="utf-8"))
    p = dict(ref["parameters"])
    p["I0"] = ref["I0_abs"]
    p["S0"] = p["N"] - p["I0"]
    p["eta"] = 0.002 * p["N"]
    p["wc"], p["wq"] = 1.0, 2.0
    return p, ref


def basics(p):
    N, b, g, c0, q0 = p["N"], p["beta"], p["gamma"], p["c0"], p["q0"]
    Sc = g * N / (b * c0 * (1 - q0))
    Sbar = g * N * (1 - b) / (b * c0)
    b1 = c0 * (b + q0 * (1 - b)) / N
    b2 = b * c0 * (1 - q0) / N
    rho = g / b1
    C0 = p["I0"] + b2 / b1 * p["S0"] - rho * np.log(p["S0"])
    Sstar = brentq(lambda S: p["eta"] + b2 / b1 * S - rho * np.log(S) - C0, Sc, p["S0"],
                   xtol=1e-12, rtol=1e-15)
    return Sc, Sbar, Sstar


# ---------------------------------------------------------------- 逐状态最小
def bounds(s, p, cmin=0.0, qcap=1.0):
    lo = np.maximum(1.0 / s, cmin / p["c0"])
    hi = np.ones_like(s) if qcap >= 1.0 else np.minimum(1.0, (1 - p["q0"]) / ((1 - qcap) * s))
    return lo, hi


def f_int(x, s, sbar, wc, wq, kappa):
    return (wc * (1 - x) ** 2 + wq * (1 - 1 / (x * s)) ** 2 + kappa) / (x * s - sbar)


def allocate(p, s, wc=1.0, wq=2.0, kappa=0.0, cmin=0.0, qcap=1.0, nx=4001, polish=False):
    """返回 x*(s)、每个 s 上网格局部极小个数。"""
    Sc, Sbar, _ = basics(p)
    sbar = Sbar / Sc
    lo, hi = bounds(s, p, cmin, qcap)
    if np.any(hi < lo - 1e-12):
        raise ValueError("能力限制下允许区间为空")
    t = np.linspace(0.0, 1.0, nx)
    X = lo[:, None] + (hi - lo)[:, None] * t[None, :]
    V = f_int(X, s[:, None], sbar, wc, wq, kappa)
    k = np.argmin(V, axis=1)
    # 局部极小个数（含端点）
    left = np.concatenate([np.full((len(s), 1), np.inf), V[:, :-1]], axis=1)
    right = np.concatenate([V[:, 1:], np.full((len(s), 1), np.inf)], axis=1)
    nloc = np.sum((V <= left) & (V <= right), axis=1)
    x = X[np.arange(len(s)), k]
    inner = (k > 0) & (k < nx - 1)
    if np.any(inner):
        i = np.where(inner)[0]
        v0, v1, v2 = V[i, k[i] - 1], V[i, k[i]], V[i, k[i] + 1]
        h = (hi[i] - lo[i]) / (nx - 1)
        den = v0 - 2 * v1 + v2
        shift = np.where(den > 0, 0.5 * (v0 - v2) / np.where(den > 0, den, 1), 0.0) * h
        x[i] = np.clip(x[i] + shift, lo[i], hi[i])
    if polish:
        for j in range(len(s)):
            if 0 < k[j] < nx - 1:
                h = (hi[j] - lo[j]) / (nx - 1)
                a, b_ = max(lo[j], x[j] - 2 * h), min(hi[j], x[j] + 2 * h)
                r = minimize_scalar(lambda z: f_int(z, s[j], sbar, wc, wq, kappa),
                                    bounds=(a, b_), method="bounded", options={"xatol": 1e-14})
                if f_int(r.x, s[j], sbar, wc, wq, kappa) <= f_int(x[j], s[j], sbar, wc, wq, kappa):
                    x[j] = r.x
    return x, nloc


def plateau_quantities(p, s, x, wc=1.0, wq=2.0):
    """由 x(s) 计算 Δt、J、J_c、J_q 与守恒律量（平台期）。"""
    Sc, Sbar, Sstar = basics(p)
    sbar = Sbar / Sc
    pref = p["N"] / (p["eta"] * p["c0"])
    dens_t = 1.0 / (x * s - sbar)
    uc, uq = 1 - x, 1 - 1 / (x * s)
    dT = pref * simpson(dens_t, x=s)
    J = pref * simpson((wc * uc ** 2 + wq * uq ** 2) * dens_t, x=s)
    Jc = pref * simpson(uc * dens_t, x=s)
    Jq = pref * simpson(uq * dens_t, x=s)
    b, g, eta = p["beta"], p["gamma"], p["eta"]
    inf = b * (Sstar - Sc) + g * eta * (1 - b) * dT
    sq = (1 - b) * (Sstar - Sc - g * eta * dT)
    return dict(dT=dT, J=J, Jc=Jc, Jq=Jq, J_lin=wc * Jc + wq * Jq, inf_plateau=inf,
                Sq_plateau=sq, q_max=float(np.max(1 - (1 - p["q0"]) / (x * s))),
                c_min=float(np.min(p["c0"] * x)))


def s_grid(p, ns=8001):
    Sc, _, Sstar = basics(p)
    return np.linspace(1.0, Sstar / Sc, ns)


def x_policy(name, s, alpha=0.5):
    if name == "quarantine_only":
        return np.ones_like(s)
    if name == "contact_only":
        return 1.0 / s
    if name.startswith("alpha"):
        return alpha + (1 - alpha) / s
    raise KeyError(name)


# ---------------------------------------------------------------- 完整 ODE
def _rhs(t, y, p, cfun, qfun):
    S, I, Sq, Iq, R = y[:5]
    c, q = cfun(t), qfun(t)
    b, g, dq, N, c0, q0 = p["beta"], p["gamma"], p["delta_q"], p["N"], p["c0"], p["q0"]
    inc = c * S * I / N
    uc = max(c0 - c, 0.0) / c0
    uq = max(q - q0, 0.0) / (1 - q0)
    return [-(b + (1 - b) * q) * inc, b * (1 - q) * inc - g * I, (1 - b) * q * inc,
            b * q * inc - dq * Iq, g * I + dq * Iq,
            b * inc, (1 - b) * q * inc, b * q * inc,
            p["wc"] * uc ** 2 + p["wq"] * uq ** 2, uc, uq]


def full_run(p, s, x, rtol=1e-11, atol_frac=1e-13, n_out=4000):
    """三阶段时间开环。返回指标与采样轨迹。"""
    Sc, Sbar, Sstar = basics(p)
    c0, q0, N, eta = p["c0"], p["q0"], p["N"], p["eta"]
    atol = atol_frac * N
    y0 = [p["S0"], p["I0"], 0, 0, N - p["S0"] - p["I0"], 0, 0, 0, 0, 0, 0]
    const_c, const_q = (lambda t: c0), (lambda t: q0)
    ev1 = lambda t, y, *a: y[1] - eta
    ev1.terminal, ev1.direction = True, 1
    r1 = solve_ivp(_rhs, (0, 1e4), y0, args=(p, const_c, const_q), method="DOP853",
                   rtol=rtol, atol=atol, events=ev1, dense_output=True)
    t1 = r1.t_events[0][0]
    y1 = r1.y_events[0][0]
    # 名义平台轨迹：tau(s) = pref ∫_s^{s*} ds'/(x s' - sbar)
    sbar = Sbar / Sc
    pref = N / (eta * c0)
    dens = 1.0 / (x * s - sbar)
    tau = pref * cumulative_trapezoid(dens[::-1], -s[::-1], initial=0.0)[::-1]
    dT_nom = tau[0]
    tt = tau[::-1]          # 递增时间
    ss = s[::-1]
    xx = x[::-1]

    def s_of(t):
        return np.interp(t - t1, tt, ss)

    def cfun(t):
        return c0 * np.interp(t - t1, tt, xx)

    def qfun(t):
        sv, xv = s_of(t), np.interp(t - t1, tt, xx)
        return 1 - (1 - q0) / (xv * sv)

    r2 = solve_ivp(_rhs, (t1, t1 + dT_nom), y1, args=(p, cfun, qfun), method="DOP853",
                   rtol=rtol, atol=atol, dense_output=True, max_step=dT_nom / 4000)
    y2 = r2.y[:, -1]
    t2 = r2.t[-1]
    ev3 = lambda t, y, *a: y[1] - 1.0
    ev3.terminal, ev3.direction = True, -1
    r3 = solve_ivp(_rhs, (t2, t2 + 1e5), y2, args=(p, const_c, const_q), method="DOP853",
                   rtol=rtol, atol=atol, events=ev3, dense_output=True)
    t_end = r3.t_events[0][0]
    y_end = r3.y_events[0][0]
    # 轨迹采样
    T = np.concatenate([np.linspace(0, t1, n_out // 8), np.linspace(t1, t2, n_out // 2),
                        np.linspace(t2, t_end, n_out // 4)])
    Y = np.concatenate([r1.sol(T[T <= t1]).T if T[0] <= t1 else np.empty((0, 11)),
                        r2.sol(T[(T > t1) & (T <= t2)]).T,
                        r3.sol(T[T > t2]).T])
    Cc = np.where((T > t1) & (T <= t2), [cfun(t) for t in T], c0)
    Qq = np.where((T > t1) & (T <= t2), [qfun(t) for t in T], q0)
    Ipl = r2.sol(np.linspace(t1, t2, 2001))[1]
    tot = Y[:, 1] + Y[:, 3]
    return dict(t1=t1, t2=t2, dT=t2 - t1, t_end=t_end,
                total_infections=y_end[5], plateau_infections=y2[5] - y1[5],
                plateau_Sq=y2[6] - y1[6], plateau_Iq_new=y2[7] - y1[7],
                Sq_end=y_end[2], J=y_end[8], Jc=y_end[9], Jq=y_end[10],
                peak_I_plus_Iq=float(tot.max()), t_peak_I_plus_Iq=float(T[np.argmax(tot)]),
                peak_Iq=float(Y[:, 3].max()),
                max_rel_drift=float(np.max(np.abs(Ipl / eta - 1))),
                traj=dict(t=T, S=Y[:, 0], I=Y[:, 1], Sq=Y[:, 2], Iq=Y[:, 3], c=Cc, q=Qq))


def tdinn_run(p, rtol=1e-11):
    c0 = p["c0"]
    cfun = lambda t: (c0 - 3.4625) * np.exp(-(0.0463 * t) ** 2) + 3.4625
    qfun = lambda t: (0.3230 - 0.9844) * np.exp(-(0.0452 * t) ** 2) + 0.9844
    N = p["N"]
    y0 = [p["S0"], p["I0"], 0, 0, N - p["S0"] - p["I0"], 0, 0, 0, 0, 0, 0]
    up = lambda t, y, *a: y[1] - 1.0
    up.terminal, up.direction = True, 1
    r0 = solve_ivp(_rhs, (0, 1e3), y0, args=(p, cfun, qfun), method="DOP853", rtol=rtol,
                   atol=1e-13 * N, events=up, dense_output=True)
    ta = r0.t_events[0][0]
    dn = lambda t, y, *a: y[1] - 1.0
    dn.terminal, dn.direction = True, -1
    r1 = solve_ivp(_rhs, (ta, 1e3), r0.y_events[0][0], args=(p, cfun, qfun), method="DOP853",
                   rtol=rtol, atol=1e-13 * N, events=dn, dense_output=True)
    te = r1.t_events[0][0]
    ye = r1.y_events[0][0]
    T = np.linspace(0, te, 6000)
    Y = np.concatenate([r0.sol(T[T <= ta]).T, r1.sol(T[T > ta]).T])
    tot = Y[:, 1] + Y[:, 3]
    return dict(t_end=te, total_infections=ye[5], J=ye[8], Jc=ye[9], Jq=ye[10],
                peak_I=float(Y[:, 1].max()), peak_I_plus_Iq=float(tot.max()),
                Sq_end=ye[2], traj=dict(t=T, I=Y[:, 1], Iq=Y[:, 3],
                                        c=np.array([cfun(t) for t in T]),
                                        q=np.array([qfun(t) for t in T])))
