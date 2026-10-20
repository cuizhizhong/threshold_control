"""NR-1 代数核对：无回流模型 (2.1) 中现稿公式的符号/数值代入检查。

只核对代数，不代替存在性、可测性、量词与逻辑论证；参数算例只说明可能性，不证明定理。

运行（仓库根目录）：
    conda run --no-capture-output -n thesis python nr_audit/theory_checks.py
输出：
    nr_audit/results/theory_checks.json   全部检查项（组、编号、说明、方法、结果、细节）
    nr_audit/results/theory_checks.md     汇总表

本脚本独立编写，不导入、不运行 r7_return/ 与 reproducibility/ 中的代码，也不写入这些目录。
"方法"一栏：symbolic = SymPy 化简为 0；numeric = 在随机容许参数点上以 mpmath 40 位精度代入；
example = 指定参数点上的数值算例（只作说明，证据类型 N）。
"""
from __future__ import annotations

import json
import pathlib
import random

import mpmath as mp
import numpy as np
import sympy as sp

OUT = pathlib.Path(__file__).resolve().parent / "results"
mp.mp.dps = 40
random.seed(20261014)

RESULTS: list[dict] = []


def record(group, cid, desc, ok, method, detail=""):
    RESULTS.append(dict(group=group, id=cid, desc=desc, ok=bool(ok), method=method, detail=str(detail)))


# ---------------------------------------------------------------- 符号与基本量
N, beta, gamma, c0, q0, eta = sp.symbols("N beta gamma c0 q0 eta", positive=True)
S, Ss, S0, I0, Ival, Sq, Iq = sp.symbols("S Sstar S0 I0 I Sq Iq", positive=True)
c, q, wc, wq, xi, t, t1, alpha = sp.symbols("c q w_c w_q xi t t1 alpha", positive=True)
cmin, qcap, z, x = sp.symbols("c_min q_cap z x", positive=True)

Sc = gamma * N / (beta * c0 * (1 - q0))
Sbar = (1 - beta) * gamma * N / (beta * c0)
b1 = c0 * (beta + q0 * (1 - beta)) / N
b2 = beta * c0 * (1 - q0) / N
rho1 = gamma / b1
kappa0 = beta / (beta + q0 * (1 - beta))

# 随机容许参数：0<beta<1，0<=q0<1，其余为正
RANGES = {
    N: (1e2, 1e7), beta: (0.03, 0.97), gamma: (0.05, 1.0), c0: (0.5, 30.0), q0: (0.0, 0.95),
    eta: (1.5, 1e4), S: (1.0, 1e7), Ss: (1.0, 1e7), S0: (1.0, 1e7), I0: (0.001, 10.0),
    Ival: (0.1, 1e4), Sq: (0.0, 1e5), Iq: (0.0, 1e4), c: (0.1, 30.0), q: (0.0, 0.99),
    wc: (0.1, 10.0), wq: (0.1, 10.0), xi: (0.0, 1.0), t: (0.0, 100.0), t1: (0.0, 50.0),
    alpha: (0.01, 1.0), cmin: (0.0, 30.0), qcap: (0.0, 0.99), z: (0.0, 0.9), x: (0.0, 1.0),
}


def _num_check(expr, n=8, rel=mp.mpf("1e-28"), sampler=None):
    syms = sorted(expr.free_symbols, key=lambda s: s.name)
    if not syms:
        v = mp.mpf(sp.N(expr, 50))
        return abs(v) <= rel, f"常数 {mp.nstr(v, 5)}"
    f = sp.lambdify(syms, expr, "mpmath")
    worst = mp.mpf(0)
    for _ in range(n):
        vals = dict(sampler()) if sampler else {}
        for s_ in syms:
            if s_ not in vals:
                vals[s_] = mp.mpf(random.uniform(*RANGES.get(s_, (0.1, 10.0))))
        v = f(*[vals[s_] for s_ in syms])
        worst = max(worst, abs(v))
    return worst <= rel, f"最大残差 {mp.nstr(worst, 3)}"


def check_zero(group, cid, desc, expr, sampler=None, scale=None):
    """先尝试符号化简；不行再随机数值代入（scale 为参照量级表达式，用于相对残差）。"""
    expr = sp.sympify(expr)
    try:
        s = sp.simplify(sp.together(sp.expand(expr)))
        if s == 0:
            record(group, cid, desc, True, "symbolic")
            return True
    except Exception:  # noqa: BLE001
        pass
    target = expr if scale is None else expr / scale
    ok, det = _num_check(target, sampler=sampler)
    record(group, cid, desc, ok, "numeric", det)
    return ok


def check_eq(group, cid, desc, a, b, sampler=None):
    return check_zero(group, cid, desc, sp.sympify(a) - sp.sympify(b), sampler=sampler,
                      scale=1 + sp.Abs(sp.sympify(a)) + sp.Abs(sp.sympify(b)))


def admissible_point():
    """满足触发条件 (2.7) 的一组参数（S0>Sc，I0<eta<Imax，eta>1），返回 mpf 字典。"""
    while True:
        p = {beta: mp.mpf(random.uniform(0.05, 0.6)), gamma: mp.mpf(random.uniform(0.1, 0.5)),
             c0: mp.mpf(random.uniform(3, 20)), q0: mp.mpf(random.uniform(0.0, 0.5)),
             N: mp.mpf(10) ** random.uniform(3, 7)}
        Scv = p[gamma] * p[N] / (p[beta] * p[c0] * (1 - p[q0]))
        I0v = p[N] * mp.mpf(10) ** random.uniform(-6, -3)
        S0v = p[N] - I0v
        if S0v <= Scv * mp.mpf("1.05"):
            continue
        b1v = p[c0] * (p[beta] + p[q0] * (1 - p[beta])) / p[N]
        b2v = p[beta] * p[c0] * (1 - p[q0]) / p[N]
        r1 = p[gamma] / b1v
        Imax = I0v + b2v / b1v * (S0v - Scv) + r1 * mp.log(Scv / S0v)
        lo = max(I0v, mp.mpf(1)) * mp.mpf("1.01")
        if Imax <= lo * mp.mpf("1.05"):
            continue
        etav = lo + (Imax - lo) * mp.mpf(random.uniform(0.05, 0.95))
        p.update({I0: I0v, S0: S0v, eta: etav})
        return p


def subsf(expr, p):
    return sp.lambdify(sorted(p, key=lambda s: s.name), expr, "mpmath")(*[p[s] for s in sorted(p, key=lambda s: s.name)])


# ======================================================================= A 模型
def group_A():
    g = "A"
    # 2.1 守恒
    dS = -c * (beta + (1 - beta) * q) / N * S * Ival
    dI = beta * c * (1 - q) / N * S * Ival - gamma * Ival
    dSq = (1 - beta) * c * q / N * S * Ival
    dIq = beta * c * q / N * S * Ival - sp.Symbol("delta_q", positive=True) * Iq
    dR = gamma * Ival + sp.Symbol("delta_q", positive=True) * Iq
    check_zero(g, "A1", "式(2.1)五式右端之和为 0（总人数守恒）", dS + dI + dSq + dIq + dR)
    Icum_rate = beta * c * (1 - q) / N * S * Ival
    Iqcum_rate = beta * c * q / N * S * Ival
    check_zero(g, "A2", "式(2.10)第一式：dI_cum/dt = dI/dt + gamma I", Icum_rate - (dI + gamma * Ival))
    check_zero(g, "A3", "式(2.10)第二式：dS_q/dt = (1-beta)/beta · dI_qcum/dt", dSq - (1 - beta) / beta * Iqcum_rate)
    check_zero(g, "A4", "-dS/dt = dItcum/dt + dS_q/dt（易感者流出只有感染与未感染隔离两条去路）",
               -dS - (Icum_rate + Iqcum_rate + dSq))
    check_eq(g, "A5", "常规控制下 R_e = beta c0 (1-q0) S/(gamma N) = S/S_c", beta * c0 * (1 - q0) * S / (gamma * N), S / Sc)
    check_eq(g, "A6", "beta2^0/beta1^0 = rho1/S_c（式 2.3 末式）", b2 / b1, rho1 / Sc)
    check_eq(g, "A7", "常规控制下 dI/dt = gamma I (S/S_c - 1)（附录 sec:proof:threshold-rationale(iii)、sec:proof:post-dynamics）",
             (b2 * S - gamma) * Ival, gamma * Ival * (S / Sc - 1))

    # Lambert W：三种 z_eta 写法相等；S* 满足首次积分且位于 (S_c,S0)；W0 分支给出 S<S_c
    C0 = I0 + b2 / b1 * S0 - rho1 * sp.log(S0)
    Imax = I0 + b2 / b1 * (S0 - Sc) + rho1 * sp.log(Sc / S0)
    z1 = -1 / Sc * sp.exp(-(C0 - eta) / rho1)
    z2 = -S0 / Sc * sp.exp(-S0 / Sc + (eta - I0) / rho1)
    z3 = -sp.exp(-1) * sp.exp(-(Imax - eta) / rho1)
    worst = mp.mpf(0)
    worst_orbit = mp.mpf(0)
    order_ok = True
    for _ in range(12):
        p = admissible_point()
        v1, v2, v3 = (subsf(e, p) for e in (z1, z2, z3))
        worst = max(worst, abs(v1 - v2) / abs(v1), abs(v1 - v3) / abs(v1))
        Scv = subsf(Sc, p)
        Sst = -Scv * mp.lambertw(v1, -1).real
        Slow = -Scv * mp.lambertw(v1, 0).real
        orbit = I0 + b2 / b1 * (S0 - S) + rho1 * sp.log(S / S0)
        res = subsf(orbit.subs(S, Sst), p) - p[eta]
        worst_orbit = max(worst_orbit, abs(res) / p[eta], abs(subsf(orbit.subs(S, Slow), p) - p[eta]) / p[eta])
        order_ok &= (Scv < Sst < p[S0]) and (0 < Slow < Scv) and (-1 / mp.e < v1 < 0)
    record(g, "A8", "式(3.1)三种 z_eta 写法相等，且 z_eta∈(-1/e,0)", worst < mp.mpf("1e-30") and order_ok, "numeric",
           f"最大相对差 {mp.nstr(worst, 3)}")
    record(g, "A9", "定理 3.1：S*=-S_c W_{-1}(z_eta) 满足 I(S*)=eta 且 S_c<S*<S0；W_0 分支给出 S<S_c 的交点",
           worst_orbit < mp.mpf("1e-25") and order_ok, "numeric", f"首次积分最大相对残差 {mp.nstr(worst_orbit, 3)}")

    # 定理 3.5：S_end、S_inf 由 W0 给出并满足退出后首次积分
    post = eta + b2 / b1 * (Sc - S) + rho1 * sp.log(S / Sc)
    worst = mp.mpf(0)
    order_ok = True
    for _ in range(12):
        p = admissible_point()
        Scv, r1 = subsf(Sc, p), subsf(rho1, p)
        Send = -Scv * mp.lambertw(-mp.exp(-1 - (p[eta] - 1) / r1), 0).real
        Sinf = -Scv * mp.lambertw(-mp.exp(-1 - p[eta] / r1), 0).real
        worst = max(worst, abs(subsf(post.subs(S, Send), p) - 1), abs(subsf(post.subs(S, Sinf), p)) / p[eta])
        order_ok &= (0 < Sinf < Send < Scv)
    record(g, "A10", "定理 3.5：S_end、S_inf 的 W_0 表达满足退出后首次积分(A.1)，且 0<S_inf<S_end<S_c",
           worst < mp.mpf("1e-25") and order_ok, "numeric", f"最大残差 {mp.nstr(worst, 3)}")


# ============================================================ B 仅隔离控制、状态参数化
def group_B():
    g = "B"
    check_eq(g, "B1", "式(3.4)：S̄/S_c=(1-beta)(1-q0)", Sbar / Sc, (1 - beta) * (1 - q0))
    check_eq(g, "B2", "S_c - S̄ = S_c(beta+q0(1-beta))>0", Sc - Sbar, Sc * (beta + q0 * (1 - beta)))
    # 平衡式下易感者方程
    qexpr = 1 - gamma * N / (beta * c * S)
    check_eq(g, "B3", "式(4.3) 两种写法相等：1-gamma N/(beta c S) = 1-c0(1-q0)S_c/(cS)", qexpr, 1 - c0 * (1 - q0) * Sc / (c * S))
    check_eq(g, "B4", "平衡式下 c[beta+(1-beta)q]S = cS - c0 S̄（式 4.1、附录 sec:proof:representation）",
             c * (beta + (1 - beta) * qexpr) * S, c * S - c0 * Sbar)
    check_eq(g, "B5", "平衡式即 beta c(1-q)S/N = gamma", beta * c * (1 - qexpr) * S / N, gamma)
    # 仅隔离控制
    qc_S = 1 - gamma * N / (beta * c0 * S)
    check_eq(g, "B6", "定理 3.2：c=c0、q=q_c(S)、I=eta 时 dS/dt = -(c0 eta/N)(S - S̄)",
             -c0 * (beta + (1 - beta) * qc_S) / N * S * eta, -c0 * eta / N * (S - Sbar))
    St = Sbar + (Ss - Sbar) * sp.exp(-c0 * eta * (t - t1) / N)
    check_zero(g, "B7", "式(3.6) 的 S(t) 满足上述线性方程且 S(t1)=S*",
               sp.diff(St, t) + c0 * eta / N * (St - Sbar) + (St.subs(t, t1) - Ss))
    Dt_q = N / (c0 * eta) * sp.log((Ss - Sbar) / (Sc - Sbar))
    check_eq(g, "B8", "式(3.7)：S(t1+Δt)=S_c", St.subs(t, t1 + Dt_q), Sc)
    qt1 = 1 - 1 / ((beta * c0 * Ss / (gamma * N) + beta - 1) * sp.exp(-c0 * eta * (t - t1) / N) + 1 - beta)
    t2 = t1 + Dt_q
    qt2 = 1 - 1 / ((q0 / (1 - q0) + beta) * sp.exp(c0 * eta * (t2 - t) / N) + 1 - beta)
    check_eq(g, "B9", "式(3.9) 第一种写法 = q_c(S(t))", qt1, qc_S.subs(S, St))
    check_eq(g, "B10", "式(3.9) 第二种写法 = q_c(S(t))", qt2, qc_S.subs(S, St))
    dq = sp.diff(qc_S.subs(S, St), t)
    check_eq(g, "B11", "式(3.11)：dq_c/dt = -(gamma eta/beta)(S-S̄)/S^2", dq,
             (-gamma * eta / beta * (S - Sbar) / S**2).subs(S, St))
    d2q = sp.diff(dq, t)
    check_eq(g, "B12", "式(3.14)：d²q_c/dt² = (gamma c0 eta²/(beta N))(S-S̄)(2S̄-S)/S³", d2q,
             (gamma * c0 * eta**2 / (beta * N) * (S - Sbar) * (2 * Sbar - S) / S**3).subs(S, St))
    check_eq(g, "B13", "式(3.13)：q_inf = q_c(2S̄) = 1 - 1/[2(1-beta)]", qc_S.subs(S, 2 * Sbar), 1 - 1 / (2 * (1 - beta)))
    tinf = t1 + N / (c0 * eta) * sp.log((Ss - Sbar) / Sbar)
    check_eq(g, "B14", "式(3.13)：S(t_inf)=2S̄", St.subs(t, tinf), 2 * Sbar)
    check_eq(g, "B15", "推论 3.3：1-q_max = gamma N/(beta c0 S*) = (1-q0)S_c/S*（推论 4.8 证明）",
             1 - qc_S.subs(S, Ss), (1 - q0) * Sc / Ss)
    # 能力约束端点（式 4.6）与可行条件（式 4.7）
    check_eq(g, "B16", "式(4.6)：q_c(S)=q_cap 时 c = c0(1-q0)S_c/((1-q_cap)S)",
             sp.solve(sp.Eq(1 - c0 * (1 - q0) * Sc / (c * S), qcap), c)[0], c0 * (1 - q0) * Sc / ((1 - qcap) * S))
    check_eq(g, "B17", "式(4.7) 两种写法：beta c_min(1-q_cap)S*/N - gamma ∝ c_min(1-q_cap) - c0(1-q_max)",
             (beta * cmin * (1 - qcap) * Ss / N - gamma) * N / (beta * Ss), cmin * (1 - qcap) - c0 * (1 - q0) * Sc / Ss)
    # 显式族
    cal = c0 * (alpha + (1 - alpha) * Sc / S)
    check_eq(g, "B18", "式(4.9) 与式(4.3) 一致：q_c(S;alpha)=1-(1-q0)S_c/[S_c+alpha(S-S_c)]",
             1 - c0 * (1 - q0) * Sc / (cal * S), 1 - (1 - q0) * Sc / (Sc + alpha * (S - Sc)))
    check_eq(g, "B19", "定理 4.3 证明：c_c(S;alpha)S - c0 S̄ = c0[S_c - S̄ + alpha(S-S_c)]", cal * S - c0 * Sbar,
             c0 * (Sc - Sbar + alpha * (S - Sc)))
    Sal = Sc + (Ss - Sc + (Sc - Sbar) / alpha) * sp.exp(-c0 * eta * alpha / N * (t - t1)) - (Sc - Sbar) / alpha
    check_zero(g, "B20", "式(4.10) 满足 dS/dt = -(eta/N)(c_c S - c0 S̄) 且 S(t1)=S*",
               sp.diff(Sal, t) + eta / N * (cal.subs(S, Sal) * Sal - c0 * Sbar) + (Sal.subs(t, t1) - Ss))
    Dal = N / (c0 * eta * alpha) * sp.log(1 + alpha * (Ss - Sc) / (Sc - Sbar))
    check_eq(g, "B21", "式(4.11)：S(t1+Δt(alpha))=S_c", Sal.subs(t, t1 + Dal), Sc)
    check_eq(g, "B22", "式(4.12)：alpha↓0 时 Δt(alpha) → N(S*-S_c)/(c0 eta(S_c-S̄))", sp.limit(Dal, alpha, 0),
             N * (Ss - Sc) / (c0 * eta * (Sc - Sbar)))
    check_eq(g, "B23", "式(4.11) 在 alpha=1 时等于式(3.7)", Dal.subs(alpha, 1), Dt_q)
    check_eq(g, "B24", "定理 4.5(ii)：∂c_c(S;alpha)/∂alpha = c0(1-S_c/S)（S>S_c 时 >0）", sp.diff(cal, alpha), c0 * (1 - Sc / S))
    lo = (cmin * Ss - c0 * Sc) / (c0 * (Ss - Sc))
    hi = Sc * (qcap - q0) / ((1 - qcap) * (Ss - Sc))
    check_eq(g, "B25", "推论 4.4：c(S*;lo)=c_min", cal.subs({S: Ss, alpha: lo}), cmin)
    check_eq(g, "B26", "推论 4.4：q(S*;hi)=q_cap", (1 - (1 - q0) * Sc / (Sc + alpha * (S - Sc))).subs({S: Ss, alpha: hi}), qcap)
    check_eq(g, "B27", "推论 4.4：(hi-lo)·c0(S*-S_c)(1-q_cap) = c0(1-q0)S_c - c_min(1-q_cap)S*（非空⇔式 4.7）",
             (hi - lo) * c0 * (Ss - Sc) * (1 - qcap), c0 * (1 - q0) * Sc - cmin * (1 - qcap) * Ss)


# ============================================================ C 排序与累计量
def group_C():
    g = "C"
    check_eq(g, "C1", "beta c0 S̄/N = gamma(1-beta)（式 4.15 证明）", beta * c0 * Sbar / N, gamma * (1 - beta))
    # 由 S*-S_c = (eta/N)∫cS dt - (c0 eta S̄/N)Δt 推出控制期感染
    K = sp.Symbol("K", positive=True)  # K = ∫ c S dt over [t1,t2]
    Dt = sp.Symbol("Dt", positive=True)
    infect = beta * eta / N * K
    K_from = sp.solve(sp.Eq(Ss - Sc, eta / N * K - c0 * eta * Sbar / N * Dt), K)[0]
    check_eq(g, "C2", "式(4.15)：beta(eta/N)∫cS dt = beta(S*-S_c)+gamma eta(1-beta)Δt", infect.subs(K, K_from),
             beta * (Ss - Sc) + gamma * eta * (1 - beta) * Dt)
    check_eq(g, "C3", "式(4.16)：(S*-S_c) - 控制期感染 = (1-beta)(S*-S_c-gamma eta Δt)",
             (Ss - Sc) - infect.subs(K, K_from), (1 - beta) * (Ss - Sc - gamma * eta * Dt))
    # 控制期新增隔离易感者的独立表达：∫(1-beta) c q S eta/N dt，与上式一致（由平衡式 c q S = cS - c0(1-q0)S_c）
    check_eq(g, "C4", "式(4.16) 的独立路径：ΔS_q=(1-beta)(eta/N)∫cqS dt，平衡式下 cqS=cS-c0(1-q0)S_c",
             (1 - beta) * eta / N * (K_from - c0 * (1 - q0) * Sc * Dt), (1 - beta) * (Ss - Sc - gamma * eta * Dt))
    # 仅隔离控制的累计感染平台项（定理 3.6）
    check_eq(g, "C5", "定理 3.6：∫_{S_c}^{S*} S/(S-S̄)dS = S*-S_c+S̄ ln[(S*-S̄)/(S_c-S̄)]",
             sp.integrate(S / (S - Sbar), (S, Sc, Ss)), Ss - Sc + Sbar * sp.log((Ss - Sbar) / (Sc - Sbar)),
             sampler=lambda: _ordered_sampler())
    Dt_q = N / (c0 * eta) * sp.log((Ss - Sbar) / (Sc - Sbar))
    check_eq(g, "C6", "定理 3.6 平台项 = beta(S*-S_c)+(1-beta)gamma eta Δt_q（与式 4.15 同形）",
             beta * (Ss - Sc + Sbar * sp.log((Ss - Sbar) / (Sc - Sbar))), beta * (Ss - Sc) + (1 - beta) * gamma * eta * Dt_q)
    check_eq(g, "C7", "前后常规阶段 beta c0 S I/N = kappa0·(-dS/dt)，kappa0=beta/(beta+q0(1-beta))",
             beta * c0 * S * Ival / N, kappa0 * c0 * (beta + q0 * (1 - beta)) / N * S * Ival)
    # 定理 4.5(i) 两界
    check_eq(g, "C8", "式(4.14) 左界 = ∫ dS/(c0(S-S̄)) 乘 N/eta", N / eta * sp.integrate(1 / (c0 * (S - Sbar)), (S, Sc, Ss)), Dt_q,
             sampler=lambda: _ordered_sampler())
    check_eq(g, "C9", "式(4.14) 右界 = ∫ dS/(c0(S_c-S̄)) 乘 N/eta", N / eta * (Ss - Sc) / (c0 * (Sc - Sbar)),
             N * (Ss - Sc) / (c0 * eta * (Sc - Sbar)))
    # 命题 4.9
    qq = sp.Symbol("qq", positive=True)
    rate_I = beta * c * S * Ival / N
    minus_dS = c * (beta + (1 - beta) * qq) * S * Ival / N
    check_eq(g, "C10", "命题 4.9：dItcum/dt = beta/(beta+(1-beta)q)·(-dS/dt)", rate_I, beta / (beta + (1 - beta) * qq) * minus_dS)
    check_zero(g, "C11", "命题 4.9：系数 beta/(beta+(1-beta)q) 关于 q 递减（导数 = -beta(1-beta)/(...)^2）",
               sp.diff(beta / (beta + (1 - beta) * qq), qq) + beta * (1 - beta) / (beta + (1 - beta) * qq) ** 2)
    # 命题 7.1（prop:dom:floor）
    Icum_T, Iqcum_T = sp.symbols("Icum_T Iqcum_T", positive=True)
    check_eq(g, "C12", "命题 7.1：S0-S(T) = I_cum + I_qcum + S_q(T) = I_cum + I_qcum/beta（S_q(0)=0）",
             Icum_T + Iqcum_T + (1 - beta) / beta * Iqcum_T, Icum_T + Iqcum_T / beta)


def _ordered_sampler():
    """随机点满足 0<S̄<S_c<S*（用于含对数积分的检查）。"""
    while True:
        p = {N: mp.mpf(random.uniform(1e2, 1e6)), beta: mp.mpf(random.uniform(0.05, 0.9)),
             gamma: mp.mpf(random.uniform(0.05, 1)), c0: mp.mpf(random.uniform(1, 20)),
             q0: mp.mpf(random.uniform(0, 0.9)), eta: mp.mpf(random.uniform(2, 1e3))}
        Scv = p[gamma] * p[N] / (p[beta] * p[c0] * (1 - p[q0]))
        p[Ss] = Scv * mp.mpf(random.uniform(1.01, 6))
        p[S] = Scv * mp.mpf(random.uniform(1.0, 6))
        for s in (I0, S0, Ival, Sq, Iq, c, q, wc, wq, xi, t, t1, alpha, cmin, qcap, z, x):
            p[s] = mp.mpf(random.uniform(*RANGES[s]))
        return p


# ============================================================ D 成本最优控制
def group_D():
    g = "D"
    D = c * S - c0 * Sbar
    n = wc * (1 - c / c0) ** 2 + wq * (1 - c0 * Sc / (c * S)) ** 2
    f = n / D
    # 时间积分换为 S 积分的被积函数
    qexpr = 1 - c0 * (1 - q0) * Sc / (c * S)
    check_eq(g, "D1", "式(5.2)：(q-q0)/(1-q0) = 1 - c0 S_c/(cS)", (qexpr - q0) / (1 - q0), 1 - c0 * Sc / (c * S))
    check_eq(g, "D2", "式(5.1)：成本率 × dt/dS = (N/eta) f，dt/dS = -N/(eta(cS-c0S̄))",
             (wc * ((c0 - c) / c0) ** 2 + wq * ((qexpr - q0) / (1 - q0)) ** 2) * N / (eta * D), N / eta * f)
    quintic = (wc * c**3 / c0**2 * (c - c0) * (c + c0 - 2 * c0 * Sbar / S)
               + wq * (c - c0 * Sc / S) * (-c**2 + 3 * c0 * Sc / S * c - 2 * c0**2 * Sbar * Sc / S**2))
    check_eq(g, "D3", "式(5.4)：∂f/∂c × c³(cS-c0S̄)²/S 恰等于五次式（附录 sec:proof:cost-minimum）", sp.diff(f, c) * c**3 * D**2 / S, quintic)
    lead = sp.Poly(sp.expand(quintic), c).LC()
    check_eq(g, "D4", "五次式最高次系数为 w_c/c0²", lead, wc / c0**2)
    check_eq(g, "D5", "附录 sec:proof:endpoint-properties：∂f/∂c·D² = n'(c)D - S n(c)", sp.diff(f, c) * D**2, sp.diff(n, c) * D - S * n)
    expr_end = sp.diff(n, c) * D - S * n
    check_eq(g, "D6", "附录 sec:proof:endpoint-properties 左端点 c=c0S_c/S 处的量", expr_end.subs(c, c0 * Sc / S),
             -2 * wc * (1 - Sc / S) * (Sc - Sbar) - S * wc * (1 - Sc / S) ** 2)
    check_eq(g, "D7", "附录 sec:proof:endpoint-properties 右端点 c=c0 处的量", expr_end.subs(c, c0),
             -wq / S * (1 - Sc / S) * (S**2 - 3 * Sc * S + 2 * Sc * Sbar))
    Ssw = (3 * Sc + sp.sqrt(9 * Sc**2 - 8 * Sc * Sbar)) / 2
    check_zero(g, "D8", "式(5.6)：S_sw 是 S²-3S_cS+2S_cS̄ 的较大根", (S**2 - 3 * Sc * S + 2 * Sc * Sbar).subs(S, Ssw))
    u = sp.Symbol("u", positive=True)
    ssw_ratio = (3 + sp.sqrt(9 - 8 * u)) / 2  # u = S̄/S_c ∈ (0,1)
    check_eq(g, "D9", "S_sw/S_c = (3+√(9-8u))/2，u=S̄/S_c=(1-beta)(1-q0)", Ssw / Sc, ssw_ratio.subs(u, (1 - beta) * (1 - q0)))
    ok = all(2 < ssw_ratio.subs(u, uu) < 3 for uu in [sp.Rational(k, 1000) for k in range(1, 1000, 7)])
    ok &= sp.simplify(ssw_ratio.subs(u, 0) - 3) == 0 and sp.simplify(ssw_ratio.subs(u, 1) - 2) == 0
    ok &= sp.simplify(sp.diff(ssw_ratio, u) + 2 / sp.sqrt(9 - 8 * u)) == 0  # 严格递减
    record(g, "D10", "5.3 节：0<S̄<S_c ⇒ 2S_c<S_sw<3S_c（比值关于 u 严格递减，u=0 处 3、u=1 处 2）", ok, "symbolic")
    small = (3 - sp.sqrt(9 - 8 * u)) / 2
    ok = sp.simplify(sp.diff(small, u) - 2 / sp.sqrt(9 - 8 * u)) == 0 and sp.simplify(small.subs(u, 1) - 1) == 0
    record(g, "D11", "附录 sec:proof:endpoint-properties：较小根/S_c=(3-√(9-8u))/2 严格增、在 u=1 处为 1，故 u<1 时小于 1（较小根 < S_c）", ok, "symbolic")

    # 附录 sec:proof:terminal-allocation：一般权重
    Sz = Sc / (1 - z)  # z = 1 - S_c/S
    cz = c0 * (1 - z * x)
    fz = f.subs(S, Sz).subs(c, cz)
    target = (wc * x**2 + wq * (1 - x) ** 2 / (1 - z * x) ** 2) / (c0 * (Sz * (1 - z * x) - Sbar))
    check_eq(g, "D12", "附录 sec:proof:terminal-allocation：f(S,c0(1-zx))/z² 的表达（一般权重）", fz / z**2, target)
    check_eq(g, "D13", "附录 sec:proof:terminal-allocation：(q-q0)/(1-q0)=z(1-x)/(1-zx)", ((qexpr - q0) / (1 - q0)).subs(S, Sz).subs(c, cz),
             z * (1 - x) / (1 - z * x))
    lim = sp.limit(target, z, 0)
    check_eq(g, "D14", "z→0 的极限函数 = [w_c x²+w_q(1-x)²]/(c0(S_c-S̄))", lim, (wc * x**2 + wq * (1 - x) ** 2) / (c0 * (Sc - Sbar)))
    xs = sp.solve(sp.diff(wc * x**2 + wq * (1 - x) ** 2, x), x)
    ok = len(xs) == 1 and sp.simplify(xs[0] - wq / (wc + wq)) == 0 and sp.simplify(sp.diff(wc * x**2 + wq * (1 - x) ** 2, x, 2) - 2 * (wc + wq)) == 0
    record(g, "D15", "极限函数严格凸，唯一最小点 x*=w_q/(w_c+w_q)（默认权重 2/3）", ok, "symbolic", f"x*={xs}")
    xstar = wq / (wc + wq)
    check_eq(g, "D16", "退出比例：接触降幅/(1-S_c/S) → w_q/(w_c+w_q)，隔离增幅/(1-S_c/S) → w_c/(w_c+w_q)",
             sp.limit((1 - xstar) / (1 - z * xstar), z, 0), wc / (wc + wq))
    check_eq(g, "D17", "两种归一化强度之比 → w_q/w_c（不是 c 与 q 原值之比）；图 7 的 y → r/(1+r)，r=w_q/w_c",
             xstar / (wc / (wc + wq)), wq / wc)
    record(g, "D18", "默认权重：2/3、1/3", sp.simplify(xstar.subs({wc: 1, wq: 2}) - sp.Rational(2, 3)) == 0, "symbolic")

    # 附录 B
    J_q_int = (1 - Sc / S) / (S - Sbar)
    pf1 = (Sc / Sbar) / S + (1 - Sc / Sbar) / (S - Sbar)
    check_eq(g, "D19", "附录 B.1 第一个部分分式", J_q_int, pf1)
    J_int = (1 - Sc / S) ** 2 / (S - Sbar)
    pf2 = Sc * (2 * Sbar - Sc) / (Sbar**2 * S) - Sc**2 / (Sbar * S**2) + (1 - Sc / Sbar) ** 2 / (S - Sbar)
    check_eq(g, "D20", "附录 B.1 第二个部分分式", J_int, pf2)
    Jq_closed = N / (c0 * eta) * (Sc / Sbar * sp.log(Ss / Sc) + (1 - Sc / Sbar) * sp.log((Ss - Sbar) / (Sc - Sbar)))
    J_closed = 2 * N / (c0 * eta) * (Sc * (2 * Sbar - Sc) / Sbar**2 * sp.log(Ss / Sc) + Sc**2 / Sbar * (1 / Ss - 1 / Sc)
                                      + (1 - Sc / Sbar) ** 2 * sp.log((Ss - Sbar) / (Sc - Sbar)))
    check_eq(g, "D21", "式(B.1) = (N/(c0 eta))∫J_q 被积函数", Jq_closed, N / (c0 * eta) * sp.integrate(pf1, (S, Sc, Ss)),
             sampler=_ordered_sampler)
    check_eq(g, "D22", "式(B.2) = (2N/(c0 eta))∫J 被积函数（默认权重 w_q=2）", J_closed,
             2 * N / (c0 * eta) * sp.integrate(pf2, (S, Sc, Ss)), sampler=_ordered_sampler)
    check_eq(g, "D23", "式 eq:cost:state：仅隔离控制 f(S,c0)=w_q(1-S_c/S)²/(c0(S-S̄))", f.subs(c, c0),
             wq * (1 - Sc / S) ** 2 / (c0 * (S - Sbar)))
    Jc_closed = N / (c0 * eta * (Sc - Sbar)) * (Ss - Sc**2 / Ss - 2 * Sc * sp.log(Ss / Sc))
    check_eq(g, "D24", "式(B.3)：仅减少接触的 J（w_c=1）", Jc_closed,
             N / eta * sp.integrate(f.subs(c, c0 * Sc / S).subs(wc, 1), (S, Sc, Ss)), sampler=_ordered_sampler)
    check_zero(g, "D25", "仅减少接触时 f 不含 w_q、与 w_c 成正比，故式(B.3) 对应 w_c=1（B.1 开头的“取默认权重”须覆盖 B.2）",
               sp.diff(f.subs(c, c0 * Sc / S), wq) + sp.diff(f.subs(c, c0 * Sc / S), wc, 2))
    # 式 (3.30) 归一化成本
    s = sp.Symbol("s", positive=True)
    theta = sp.Symbol("theta", positive=True)
    lhs = 2 * N / (c0 * theta * N) * sp.integrate((1 - Sc / S) ** 2 / (S - Sbar), (S, Sc, Ss))
    rhs = 2 / (c0 * theta) * sp.integrate((1 - (Sc / N) / s) ** 2 / (s - Sbar / N), (s, Sc / N, Ss / N))
    check_eq(g, "D26", "式(3.25)：J 的归一化表达与 S 积分一致（eta=theta N）", lhs, rhs, sampler=_ordered_sampler_theta(theta))
    # m(S)>0：两项同时为零只在 S=S_c
    sol = sp.solve([1 - c / c0, 1 - c0 * Sc / (c * S)], [c, S], dict=True)
    record(g, "D27", "命题 5.2 证明：两项归一化强度同时为零 ⇔ c=c0 且 S=S_c", len(sol) == 1 and sp.simplify(sol[0][S] - Sc) == 0,
           "symbolic", str(sol))
    # 注记 5.5：时长被积函数
    check_eq(g, "D28", "注记 5.5：Δt 的被积函数 (N/eta)/(cS-c0S̄)；J+kappa Δt 的逐状态被积函数为 f+kappa/(cS-c0S̄)",
             N / eta * (f + sp.Symbol("kappa") / D), N / eta * f + sp.Symbol("kappa") * N / (eta * D))


def _ordered_sampler_theta(theta):
    def smp():
        p = _ordered_sampler()
        p[theta] = p[eta] / p[N]
        return p
    return smp


# ============================================================ S 参数敏感性（附录敏感性证明、补充 S2/S3/S6）
def group_S():
    g = "S"
    Fexpr = I0 + b2 / b1 * (S0 - S) + rho1 * sp.log(S / S0) - eta
    check_eq(g, "S1", "附录 sec:proof:start-sensitivity：∂F/∂S = rho1(1/S - 1/S_c)", sp.diff(Fexpr, S), rho1 * (1 / S - 1 / Sc))
    check_eq(g, "S2", "附录 sec:proof:start-sensitivity：∂F/∂c0 = -(rho1/c0) ln(S/S0)", sp.diff(Fexpr, c0), -rho1 / c0 * sp.log(S / S0))
    dFb = q0 * (1 - q0) / (beta + q0 * (1 - beta)) ** 2 * (S0 - S) - rho1 * (1 - q0) / (beta + q0 * (1 - beta)) * sp.log(S / S0)
    check_eq(g, "S3", "附录 sec:proof:start-sensitivity：∂F/∂beta", sp.diff(Fexpr, beta), dFb)
    dFq = -beta / (beta + q0 * (1 - beta)) ** 2 * ((S0 - S) - Sbar * sp.log(S0 / S))
    check_eq(g, "S4", "附录 sec:proof:start-sensitivity：∂F/∂q0", sp.diff(Fexpr, q0), dFq)
    # S*>bar S 时 (S0-S*) - S̄ ln(S0/S*) > 0（ln x < x-1）：数值抽查
    worst = mp.mpf(1)
    for _ in range(2000):
        S0v = mp.mpf(random.uniform(1, 1e6))
        Sv = S0v * mp.mpf(random.uniform(1e-3, 0.999999))
        Sbv = Sv * mp.mpf(random.uniform(0, 0.999999))
        val = (S0v - Sv) - Sbv * mp.log(S0v / Sv)
        worst = min(worst, val / (S0v - Sv))
    record(g, "S5", "附录 sec:proof:start-sensitivity：S̄<S*<S0 ⇒ (S0-S*)-S̄ln(S0/S*)>0（另有 ln x<x-1 的证明）", worst > 0, "numeric",
           f"2000 点最小相对值 {mp.nstr(worst, 3)}")
    # ∂S*/∂p 的闭式
    dS_deta = -sp.diff(Fexpr, eta) / sp.diff(Fexpr, S)
    check_eq(g, "S6", "式 eq:s1:Sstar-eta-sign：∂S*/∂eta = 1/[rho1(1/S*-1/S_c)]", dS_deta, 1 / (rho1 * (1 / S - 1 / Sc)))
    dS_dc0 = -sp.diff(Fexpr, c0) / sp.diff(Fexpr, S)
    check_eq(g, "S7", "式 eq:s1:Sstar-eta-sign：∂S*/∂c0 = ln(S*/S0)/[c0(1/S*-1/S_c)]", dS_dc0, sp.log(S / S0) / (c0 * (1 / S - 1 / Sc)))
    dS_db = -sp.diff(Fexpr, beta) / sp.diff(Fexpr, S)
    check_eq(g, "S8", "式 eq:s1:Sstar-beta-sign：∂S*/∂beta", dS_db, dFb / (rho1 * (1 / Sc - 1 / S)))
    dS_dq = -sp.diff(Fexpr, q0) / sp.diff(Fexpr, S)
    check_eq(g, "S9", "式 eq:s1:Sstar-q0-sign：∂S*/∂q0", dS_dq,
             -beta * ((S0 - S) - Sbar * sp.log(S0 / S)) / ((beta + q0 * (1 - beta)) ** 2 * rho1 * (1 / Sc - 1 / S)))
    # 阈值取舍（附录 sec:proof:threshold-tradeoff）
    Sst = sp.Function("Sst")(eta)
    Dt = N / (c0 * eta) * sp.log((Sst - Sbar) / (Sc - Sbar))
    _check_func_eq(g, "S10", "附录 sec:proof:threshold-tradeoff：∂Δt/∂eta = -Δt/eta + N/(c0 eta (S*-S̄))·∂S*/∂eta",
                   sp.diff(Dt, eta) - (-Dt / eta + N / (c0 * eta * (Sst - Sbar)) * sp.diff(Sst, eta)))
    Send = sp.Function("Send")(eta)
    Itc = kappa0 * (S0 - Sst + Sc - Send) + beta * (Sst - Sc + Sbar * sp.log((Sst - Sbar) / (Sc - Sbar)))
    target = (beta * Sst / (Sst - Sbar) - kappa0) * sp.diff(Sst, eta) - kappa0 * sp.diff(Send, eta)
    _check_func_eq(g, "S11", "式 eq:cumulative-eta：∂Itcum/∂eta 的表达", sp.diff(Itc, eta) - target)
    check_eq(g, "S12", "附录 sec:proof:threshold-tradeoff：beta S_c/(S_c-S̄) = beta/(beta+q0(1-beta))", beta * Sc / (Sc - Sbar), kappa0)
    post = eta + b2 / b1 * (Sc - S) + rho1 * sp.log(S / Sc) - 1
    check_eq(g, "S13", "附录 sec:proof:threshold-tradeoff：∂S_end/∂eta = -1/[rho1(1/S_end-1/S_c)]", -sp.diff(post, eta) / sp.diff(post, S),
             -1 / (rho1 * (1 / S - 1 / Sc)))
    check_zero(g, "S14", "S/(S-S̄) 关于 S 的导数 = -S̄/(S-S̄)² <0", sp.diff(S / (S - Sbar), S) + Sbar / (S - Sbar) ** 2)
    # 接触率（补充 S2 sec:proof:contact-effects）
    check_eq(g, "S15", "补充 S2 sec:proof:contact-effects：∂S̄/∂beta = -gamma N/(c0 beta²)", sp.diff(Sbar, beta), -gamma * N / (c0 * beta**2))
    check_eq(g, "S16", "补充 S2 sec:proof:contact-effects：∂(S_c-S̄)/∂beta = -q0 S_c/beta", sp.diff(Sc - Sbar, beta), -q0 * Sc / beta)
    check_eq(g, "S17", "补充 S2 sec:proof:contact-effects：∂S̄/∂c0=-S̄/c0，∂S_c/∂c0=-S_c/c0，∂S_c/∂q0=S_c/(1-q0)",
             sp.diff(Sbar, c0) + Sbar / c0 + sp.diff(Sc, c0) + Sc / c0 + sp.diff(Sc, q0) - Sc / (1 - q0), 0)
    # 补充 S2 式 eq:duration-c0
    Sst_c = sp.Function("Sc0")(c0)
    Dt_c = N / (c0 * eta) * sp.log((Sst_c - Sbar) / (Sc - Sbar))
    dSdc0 = (sp.log(Sst_c / S0) / (c0 * (1 / Sst_c - 1 / Sc)))
    lhs = sp.diff(Dt_c, c0).subs(sp.Derivative(Sst_c, c0), dSdc0)
    rhs = N / (c0**2 * eta) * (Sst_c / (Sst_c - Sbar) * (1 + Sc / (Sst_c - Sc) * sp.log(S0 / Sst_c))
                               - sp.log((Sst_c - Sbar) / (Sc - Sbar)))
    _check_func_eq(g, "S18", "补充 S2 式 eq:duration-c0：∂Δt/∂c0 的表达（代入 ∂S*/∂c0）", lhs - rhs, func=Sst_c)
    # 补充 S2 引理 lem:s1:trigger-boundary
    Imax = I0 + b2 / b1 * (S0 - Sc) + rho1 * sp.log(Sc / S0)
    check_eq(g, "S19", "补充 S2 式 eq:s1:Imax-no-c0-derivative：dI_max^0/dc0 = -(rho1/c0)ln(S_c/S0)", sp.diff(Imax, c0), -rho1 / c0 * sp.log(Sc / S0))
    # 补充 S3：lambda 的偏导
    A = sp.log((S - Sbar) / Sbar)
    Bq = sp.log(Sbar / (Sc - Sbar))
    check_zero(g, "S20", "补充 S3：∂B/∂c0 = 0，∂B/∂eta = 0", sp.diff(Bq, c0) + sp.diff(Bq, eta))
    check_eq(g, "S21", "补充 S3：∂B/∂beta = -1/[(1-beta)(beta+q0(1-beta))]", sp.diff(Bq, beta),
             -1 / ((1 - beta) * (beta + q0 * (1 - beta))))
    check_eq(g, "S22", "补充 S3：∂B/∂q0 = -1/[(1-q0)(beta+q0(1-beta))]", sp.diff(Bq, q0), -1 / ((1 - q0) * (beta + q0 * (1 - beta))))
    Sf = sp.Function("Sx")
    for par, name, extra in ((c0, "c0", S / c0), (beta, "beta", S / (beta * (1 - beta)))):
        Sfun = Sf(par)
        Af = A.subs(S, Sfun)
        tgt = (sp.diff(Sfun, par) + extra.subs(S, Sfun)) / (Sfun - Sbar)
        _check_func_eq(g, f"S23{name}", f"补充 S3：∂A/∂{name} 的表达", sp.diff(Af, par) - tgt, func=Sfun)
    # 补充 S3 app:lambda 的构造（精确有理数）
    pars = {N: sp.Integer(10**6), beta: sp.Rational(1, 6), q0: sp.Rational(1, 10), gamma: sp.Rational(1, 10),
            c0: sp.Rational(20, 3), I0: sp.Integer(100)}
    ok = (sp.simplify(Sc.subs(pars) - pars[N] / 10) == 0 and sp.simplify(Sbar.subs(pars) - 3 * pars[N] / 40) == 0
          and sp.simplify((b2 / b1).subs(pars) - sp.Rational(3, 5)) == 0)
    Sst_v = pars[N] / 5
    detail = []
    signs = []
    for r in (sp.Rational(21, 20), sp.Integer(2)):
        S0v = r * Sst_v
        etav = (I0 + b2 / b1 * (S0 - S) + rho1 * sp.log(S / S0)).subs(pars).subs({S0: S0v, S: Sst_v})
        Imaxv = Imax.subs(pars).subs(S0, S0v)
        dSq = (-beta * ((S0 - S) - Sbar * sp.log(S0 / S)) / ((beta + q0 * (1 - beta)) ** 2 * rho1 * (1 / Sc - 1 / S))).subs(pars).subs({S0: S0v, S: Sst_v})
        Av, Bv = A.subs(pars).subs(S, Sst_v), Bq.subs(pars)
        dl = (Bv / (Sst_v - Sbar.subs(pars)) * dSq + Av / ((1 - q0) * (beta + q0 * (1 - beta))).subs(pars)) / (Av + Bv) ** 2
        closed = sp.Rational(40, 9) / sp.log(5) ** 2 * (sp.log(sp.Rational(5, 3)) - sp.log(3) * (sp.Rational(16, 5) * (r - 1) - sp.Rational(6, 5) * sp.log(r)))
        okr = abs(sp.N(dl - closed, 30)) < 1e-25
        okr &= bool(sp.N(etav) > pars[I0]) and bool(sp.N(Imaxv) > sp.N(etav)) and bool(S0v + pars[I0] < pars[N])
        okr &= bool(Sc.subs(pars) < 2 * Sbar.subs(pars) < Sst_v)
        ok &= okr
        signs.append(float(sp.N(dl)))
        detail.append(f"r={r}: eta={float(sp.N(etav)):.1f}, Imax={float(sp.N(Imaxv)):.1f}, dλ/dq0={float(sp.N(dl)):.4g}")
    ok &= signs[0] > 0 > signs[1]
    record(g, "S24", "补充 S3 app:lambda：构造点满足触发与拐点条件，闭式与一般式一致，两点导数一正一负", ok, "symbolic+example", "; ".join(detail))
    # 补充 S6：prop:reference-population
    sN, ssc, rN = sp.symbols("s_end s_c rhoN", positive=True)  # rhoN=rho1/N，beta2/beta1=rhoN/s_c
    th = sp.Symbol("theta", positive=True)
    Fn = th + rN / ssc * (ssc - sN) + rN * sp.log(sN / ssc) - 1 / N
    dsdN = -sp.diff(Fn, N) / sp.diff(Fn, sN)
    check_eq(g, "S25", "补充 S6 prop:reference-population：∂s_end/∂N = -1/[N²(rho1/N)(1/s_end-1/s_c)]", dsdN, -1 / (N**2 * rN * (1 / sN - 1 / ssc)))


def _check_func_eq(group, cid, desc, expr, func=None):
    """含未定函数的恒等式：把函数及其导数替换为独立符号后化简。"""
    reps = {}
    for d in expr.atoms(sp.Derivative):
        reps[d] = sp.Symbol(f"d_{abs(hash(d)) % 10**6}")
    e = expr.subs(reps)
    for fn in e.atoms(sp.Function):
        if isinstance(fn, sp.core.function.AppliedUndef):
            e = e.subs(fn, sp.Symbol(f"f_{fn.func.__name__}", positive=True))
    s = sp.simplify(e)
    if s == 0:
        record(group, cid, desc, True, "symbolic")
        return True
    ok, det = _num_check(e)
    record(group, cid, desc, ok, "numeric", det)
    return ok


# ============================================================ F 退出时瞬时释放
def group_F():
    g = "F"
    Sq2 = sp.Symbol("Sq_t2minus", positive=True)
    S_plus = Sc + xi * Sq2
    Sq_plus = (1 - xi) * Sq2
    check_zero(g, "F1", "释放前后 S+S_q 不变（只从 S_q 转到 S；I、I_q、R 连续，总人口不变）", (S_plus + Sq_plus) - (Sc + Sq2))
    Re_plus = beta * c0 * (1 - q0) * S_plus / (gamma * N)
    check_eq(g, "F2", "R_e(t2+) = 1 + xi S_q(t2-)/S_c", Re_plus, 1 + xi * Sq2 / Sc)
    Idot_plus = (beta * c0 * (1 - q0) * S_plus / N - gamma) * eta
    check_eq(g, "F3", "dI/dt(t2+) = gamma eta xi S_q(t2-)/S_c", Idot_plus, gamma * eta * xi * Sq2 / Sc)
    check_eq(g, "F4", "xi=0 时 dI/dt(t2+)=0、R_e=1（恢复常规参数、不释放，回到定理 3.5 的情形）", Idot_plus.subs(xi, 0), 0)
    # 释放前库存 S_q(t2-) 的来源：启动前 + 平台（只作说明，不进入注记）
    Spre = (1 - beta) * q0 / (beta + (1 - beta) * q0) * (S0 - Ss)
    check_eq(g, "F5", "（说明）启动前 S_q 增量 = (1-beta)q0/(beta+(1-beta)q0)·(S0-S*)；q0=0 且仅减少接触时 S_q(t2-)=S_q(0)",
             Spre, (1 - kappa0) * (S0 - Ss))


# ============================================================ G 能力约束下两种措施并用
def group_G():
    g = "G"
    # c^-(S) = max{c_min, c0 S_c/S} < c0  ⇐ c_min<c0 且 S>S_c
    # c^+(S) = min{c0, c0(1-q0)S_c/((1-q_cap)S)} > c0 S_c/S ⇐ q_cap>q0 且 S>S_c
    check_eq(g, "G1", "c0 - c0S_c/S = c0(1-S_c/S)>0（S>S_c），故 c_min<c0 ⇒ c^-(S)<c0", c0 - c0 * Sc / S, c0 * (1 - Sc / S))
    check_eq(g, "G2", "c0(1-q0)S_c/((1-q_cap)S) - c0S_c/S = c0S_c(q_cap-q0)/((1-q_cap)S)，故 q_cap>q0 ⇒ c^+(S)>c0S_c/S",
             c0 * (1 - q0) * Sc / ((1 - qcap) * S) - c0 * Sc / S, c0 * Sc * (qcap - q0) / ((1 - qcap) * S))
    check_eq(g, "G3", "c0∈[c^-,c^+] ⇔ S ≤ (1-q0)S_c/(1-q_cap)；该界 / S_c = (1-q0)/(1-q_cap) >1 ⇔ q_cap>q0",
             sp.solve(sp.Eq(c0 * (1 - q0) * Sc / ((1 - qcap) * S), c0), S)[0], (1 - q0) * Sc / (1 - qcap))
    check_eq(g, "G4", "c0S_c/S ≥ c_min ⇔ S ≤ c0S_c/c_min；该界 >S_c ⇔ c_min<c0", sp.solve(sp.Eq(c0 * Sc / S, cmin), S)[0], c0 * Sc / cmin)

    # 数值说明（证据类型 N，基准参数）：两个不等式不蕴含可行性；最小点可能落在能力边界
    base = {N: 763.0, beta: 0.155, gamma: 0.3504, c0: 10.0, q0: 0.01526}
    ev = lambda e: float(sp.N(e.subs(base)))  # noqa: E731
    Scv, Sbv = ev(Sc), ev(Sbar)
    etav = 0.05 * 763.0
    b1v, b2v = ev(b1), ev(b2)
    r1 = 0.3504 / b1v
    I0v, S0v = 1.0, 762.0
    C0v = I0v + b2v / b1v * S0v - r1 * np.log(S0v)
    zv = -1 / Scv * np.exp(-(C0v - etav) / r1)
    Sstv = float(-Scv * mp.lambertw(zv, -1).real)
    qmax = 1 - 0.3504 * 763 / (0.155 * 10 * Sstv)
    # (a) c_min<c0、q_cap>q0 但式(4.7) 不成立
    cm, qc = 0.9 * 10.0, 0.6
    feas = cm * (1 - qc) <= 10.0 * (1 - qmax)
    record(g, "G5", "（算例 N）c_min/c0=0.9、q_cap=0.6 满足 c_min<c0、q_cap>q0，但式(4.7)不成立：两个不等式不蕴含整段可行",
           not feas, "example", f"S*/S_c={Sstv / Scv:.4f}, q_max={qmax:.4f}, c_min(1-q_cap)={cm * (1 - qc):.3f} > c0(1-q_max)={10 * (1 - qmax):.3f}")
    # (b) 可行且 c_min 起作用：c_min/c0=0.9、q_cap=0.8(≥q_max)。逐状态比较端点与五次式实根
    f_expr = (((1 - c / c0) ** 2 + 2 * (1 - c0 * Sc / (c * S)) ** 2) / (c * S - c0 * Sbar)).subs(base)
    fl = sp.lambdify((S, c), f_expr, "numpy")
    quint = (c**3 / c0**2 * (c - c0) * (c + c0 - 2 * c0 * Sbar / S)
             + 2 * (c - c0 * Sc / S) * (-c**2 + 3 * c0 * Sc / S * c - 2 * c0**2 * Sbar * Sc / S**2)).subs(base)

    def argmin(Sv, lo, hi):
        poly = sp.Poly(sp.expand(quint.subs(S, Sv)), c)
        roots = [r.real for r in np.roots([float(a) for a in poly.all_coeffs()]) if abs(r.imag) < 1e-9 and lo < r.real < hi]
        cands = [lo, hi] + roots
        vals = [fl(Sv, cc) for cc in cands]
        k = int(np.argmin(vals))
        return cands[k], vals[k]

    Sswv = (3 * Scv + np.sqrt(9 * Scv**2 - 8 * Scv * Sbv)) / 2
    cm, qc = 0.9 * 10.0, 0.8
    rows = []
    hit = False
    for ratio in (1.2, 1.6, 2.0):
        Sv = ratio * Scv
        lo_u, hi_u = 10.0 * Scv / Sv, 10.0
        cu, _ = argmin(Sv, lo_u, hi_u)
        lo_c = max(cm, lo_u)
        hi_c = min(10.0, 10.0 * (1 - 0.01526) * Scv / ((1 - qc) * Sv))
        cc_, _ = argmin(Sv, lo_c, hi_c)
        qv = 1 - 10.0 * (1 - 0.01526) * Scv / (cc_ * Sv)
        rows.append(f"S/S_c={ratio}: 无约束 c*/c0={cu / 10:.4f}; 约束 c*/c0={cc_ / 10:.4f}, q*={qv:.4f}")
        hit |= abs(cc_ - cm) < 1e-12 and cc_ < 10.0 and qv > 0.01526
    record(g, "G6", "（算例 N）c_min/c0=0.9、q_cap=0.8：S<S_sw 时约束最小点落在 c=c_min 上——两种措施都强于常规，但不在约束区间内部",
           hit, "example", f"S_sw/S_c={Sswv / Scv:.4f}; " + "; ".join(rows))


# ============================================================ R 闭式代入抽查（不是 NR-3 回归）
def group_R():
    """用稿件参数代入闭式，核对稿件中的若干舍入值；同时给出退出下界占表 2 总累计感染的比例。"""
    g = "R"
    sets = {
        "基准": dict(N=763.0, beta=0.155, gamma=0.3504, c0=10.0, q0=0.01526, I0=1.0, theta=0.05,
                   ref=dict(SsSc=(4.044, 5e-4), SswSc=(2.265, 5e-4), qmax=(0.7565, 5e-5), dtq=(5.90, 5e-3), dtc=(36.26, 5e-3), lb=None),
                   totals=dict(仅减少接触=628.6, alpha05=323.4, 仅隔离=285.7, 成本最优=306.6)),
        "西安": dict(N=13163000.0, beta=0.1498, gamma=0.2953, c0=12.8872, q0=0.3230, I0=0.00100659188867187, theta=0.002,
                   ref=dict(SsSc=(4.378, 5e-4), SswSc=(2.548, 5e-4), qmax=(0.8454, 5e-5), dtq=(85.07, 5e-3), dtc=(308.79, 5e-3), lb=(1.53e6, 5e3)),
                   totals=dict(仅减少接触=3.8566e6, alpha05=2.6390e6, 仅隔离=2.3779e6, 成本最优=2.5348e6)),
    }
    for name, p in sets.items():
        Nv, bv, gv, cv, qv, I0v = (mp.mpf(p[k]) for k in ("N", "beta", "gamma", "c0", "q0", "I0"))
        etav = mp.mpf(p["theta"]) * Nv
        S0v = Nv - I0v
        Scv = gv * Nv / (bv * cv * (1 - qv))
        Sbv = (1 - bv) * gv * Nv / (bv * cv)
        b1v = cv * (bv + qv * (1 - bv)) / Nv
        b2v = bv * cv * (1 - qv) / Nv
        r1 = gv / b1v
        C0v = I0v + b2v / b1v * S0v - r1 * mp.log(S0v)
        zv = -1 / Scv * mp.exp(-(C0v - etav) / r1)
        Sst = -Scv * mp.lambertw(zv, -1).real
        Ssw = (3 * Scv + mp.sqrt(9 * Scv**2 - 8 * Scv * Sbv)) / 2
        vals = dict(SsSc=Sst / Scv, SswSc=Ssw / Scv, qmax=1 - gv * Nv / (bv * cv * Sst),
                    dtq=Nv / (cv * etav) * mp.log((Sst - Sbv) / (Scv - Sbv)),
                    dtc=Nv * (Sst - Scv) / (cv * etav * (Scv - Sbv)), lb=bv * (S0v - Scv))
        ok = True
        parts = []
        for k, ref in p["ref"].items():
            v = vals[k]
            parts.append(f"{k}={mp.nstr(v, 7)}")
            if ref is not None:  # (稿件舍入值, 半个末位)
                ok &= abs(float(v) - ref[0]) <= ref[1] * 1.0001
        record(g, f"R-{name}", f"{name}参数：S*/S_c、S_sw/S_c、q_max、Δt（仅隔离、仅减少接触）、beta(S0-S_c) 与稿件舍入值一致",
               ok, "example", "; ".join(parts))
        lbv = float(vals["lb"])
        ratios = {k: lbv / v for k, v in p["totals"].items()}
        record(g, f"R-{name}-lb", f"{name}参数：退出下界 beta(S0-S_c) 占表 2 各控制总累计新增感染（计至清零）的比例",
               True, "example", "; ".join(f"{k}:{r:.3f}" for k, r in ratios.items()))


def main():
    for grp in (group_A, group_B, group_C, group_D, group_S, group_F, group_G, group_R):
        grp()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "theory_checks.json").write_text(json.dumps(RESULTS, ensure_ascii=False, indent=1), encoding="utf-8")
    n_ok = sum(r["ok"] for r in RESULTS)
    lines = ["# NR-1 代数核对结果（`nr_audit/theory_checks.py`）", "",
             "只核对代数；不代替存在性、可测性与量词论证。example 为参数算例（证据类型 N），只说明可能性。", "",
             f"共 {len(RESULTS)} 项，通过 {n_ok} 项，未通过 {len(RESULTS) - n_ok} 项。", "",
             "| 组 | 编号 | 内容 | 方法 | 结果 | 细节 |", "|---|---|---|---|---|---|"]
    for r in RESULTS:
        det = r["detail"].replace("|", "/")
        lines.append(f"| {r['group']} | {r['id']} | {r['desc']} | {r['method']} | {'通过' if r['ok'] else '**未通过**'} | {det} |")
    (OUT / "theory_checks.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{n_ok}/{len(RESULTS)} passed")
    for r in RESULTS:
        if not r["ok"]:
            print("FAIL", r["group"], r["id"], r["desc"], r["detail"])


if __name__ == "__main__":
    main()
