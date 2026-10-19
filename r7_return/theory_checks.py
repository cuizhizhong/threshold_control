"""R7-2 理论结果的代数核对与数值抽检（执行计划第 3 节：引理 R1、命题 R2、命题 R3、释放注记）。

SymPy 只核对代数恒等式：U 恒等式、平台上的流量下界常数 k、立即返回对照模型的常规轨迹与
Lambert W 表达、A > 1 与触发条件的等价、Δt_q 与 Δt_c 的闭式、K_q、成本被积函数与
“f 中取 S̄ = 0”的对应、x⁴h_a'(x) 的四次式及 h_a'(a)、h_a'(1)、退出附近的分担比例、
释放注记的两个公式。存在性、可测性、量词与极限论证不在此核对（见
paper/revision_notes/R7_2_return_theory.md 中的证明）。

记号：陈述用 S、c、S_c、S̄；代码中局部记 a = S_c/S、x = c/c0、u = 接触减少的分担比例、
ε = 1 - S_c/S、g(z) = z - ln z（z = S/S_c 只在 Lambert W 一段使用，与 params.py 的
第二套归一化一致）。

数值抽检用 params.py 的基准与西安两组参数（S_q(0) = 0），与执行计划第 5 节的参考值对照。

运行（仓库根目录）：
    conda run --no-capture-output -n thesis python r7_return/theory_checks.py
结果写入 r7_return/results/r7_2_theory_checks.{md,json}；任一核对不通过时退出码为 1。
"""
import json
import math
import os
import sys

import numpy as np
import sympy as sp
from scipy.integrate import quad
from scipy.optimize import brentq, minimize_scalar
from scipy.special import lambertw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import params as PR  # noqa: E402

RESULTS = []          # 每项：dict(group, name, ok, detail)


def record(group, name, ok, detail=''):
    RESULTS.append(dict(group=group, name=name, ok=bool(ok), detail=str(detail)))


def is_zero(expr):
    return sp.simplify(sp.expand(expr)) == 0


# ======================================================================
# 一、SymPy 代数核对
# ======================================================================
N, beta, gamma, dq, c0, q0, eta, omega = sp.symbols(
    'N beta gamma delta_q c_0 q_0 eta omega', positive=True)
S, Sq, I, Iq, c, q, xi = sp.symbols('S S_q I I_q c q xi', positive=True)
wc, wq = sp.symbols('w_c w_q', positive=True)
Sc = gamma * N / (beta * c0 * (1 - q0))             # 常规传播临界值 S_c
Sbar = (1 - beta) * gamma * N / (beta * c0)          # S̄（式 s1:barS）


def check_R1():
    g = 'R1 U 恒等式'
    F = beta * c * S * I / N
    dS = -c * (beta + (1 - beta) * q) * S * I / N + omega * Sq
    dSq = (1 - beta) * c * q * S * I / N - omega * Sq
    dI = beta * c * (1 - q) * S * I / N - gamma * I
    dIq = beta * c * q * S * I / N - dq * Iq
    dR = gamma * I + dq * Iq
    record(g, 'd(S+S_q)/dt = -F（任意 ω ≥ 0）', is_zero(dS + dSq + F))
    record(g, '五个仓室之和守恒（含回流模型）', is_zero(dS + dSq + dI + dIq + dR))
    # 两类感染流入之和等于 F（I_tcum 的定义）
    record(g, '进入 I 与进入 I_q 的流量之和 = F',
           is_zero(beta * c * (1 - q) * S * I / N + beta * c * q * S * I / N - F))
    # 未感染接触者进入隔离的流量 A_q = (1-β)/β · q · F ≤ (1-β)/β · F
    Aq = (1 - beta) * c * q * S * I / N
    record(g, 'A_q = (1-β)/β · q · F', is_zero(Aq - (1 - beta) / beta * q * F))
    # 立即返回对照模型：S_q ≡ 0，dS = -F，四个仓室之和守恒
    dS_ir = -F
    record(g, '立即返回对照模型：dS/dt = -F，S+I+I_q+R 守恒', is_zero(dS_ir + dI + dIq + dR))


def check_plateau_k():
    g = '有限时间退出：平台流量下界 k'
    # 平台上 I ≡ η 的平衡式：c(1-q)S = γN/β，解出 q
    q_bal = 1 - gamma * N / (beta * c * S)
    # c S - c0 S_c = c0 S_c (q - q0)/(1 - q)：q ≥ q0 ⇔ cS ≥ c0 S_c
    lhs = c * S - c0 * Sc
    rhs = c0 * Sc * (q_bal - q0) / (1 - q_bal)
    record(g, '平衡式下 cS - c0S_c = c0S_c(q-q0)/(1-q)，故 q ≥ q0 ⇔ cS ≥ c0S_c', is_zero(lhs - rhs))
    k1 = beta * c0 * Sc * eta / N
    k2 = gamma * eta / (1 - q0)
    record(g, 'k = βc0S_cη/N = γη/(1-q0)', is_zero(k1 - k2))
    # 有回流时平台上 S 的方程：c[β+(1-β)q]S = cS - c0S̄（与无回流相同），回流项另加 ωS_q
    record(g, '平衡式下 c[β+(1-β)q]S = cS - c0S̄',
           is_zero(c * (beta + (1 - beta) * q_bal) * S - (c * S - c0 * Sbar)))


def check_R3_start():
    g = 'R3 启动状态（Lambert W）'
    S0, I0 = sp.symbols('S_0 I_0', positive=True)
    # 常规轨迹（立即返回）：dI/dS = İ/Ṡ = -(1-q0)(1 - S_c/S)
    dIdS = (beta * c0 * (1 - q0) * S * I / N - gamma * I) / (-beta * c0 * S * I / N)
    record(g, '常规轨迹 dI/dS = -(1-q0)(1-S_c/S)', is_zero(dIdS + (1 - q0) * (1 - Sc / S)))
    I_of_S = I0 + (1 - q0) * ((S0 - S) + Sc * sp.log(S / S0))
    record(g, 'I(S) = I0 + (1-q0)[(S0-S) + S_c ln(S/S0)] 满足该方程',
           is_zero(sp.diff(I_of_S, S) + (1 - q0) * (1 - Sc / S)))
    Ipeak = I_of_S.subs(S, Sc)
    record(g, 'I_peak,ir = I(S_c) = I0 + (1-q0)[S0 - S_c + S_c ln(S_c/S0)]',
           is_zero(sp.expand_log(Ipeak - (I0 + (1 - q0) * (S0 - Sc + Sc * sp.log(Sc / S0))), force=True)))
    # A 与 g(z) = z - ln z
    A = (S0 - (eta - I0) / (1 - q0)) / Sc - sp.log(S0 / Sc)
    z = sp.symbols('z', positive=True)
    gz = z - sp.log(z)
    # I(S_c z) - η = (1-q0) S_c [A - g(z)]
    e1 = sp.expand_log(I_of_S.subs(S, Sc * z) - eta - (1 - q0) * Sc * (A - gz), force=True)
    record(g, 'I(S) - η = (1-q0)S_c[A - g(S/S_c)]，故 I(S) = η ⇔ S/S_c - ln(S/S_c) = A', is_zero(e1))
    # I_peak,ir - η = (1-q0) S_c (A - 1)：η < I_peak,ir ⇔ A > 1
    e2 = sp.expand_log(Ipeak - eta - (1 - q0) * Sc * (A - 1), force=True)
    record(g, 'I_peak,ir - η = (1-q0)S_c(A-1)，故 η < I_peak,ir ⇔ A > 1', is_zero(e2))
    # η - I0 = (1-q0) S_c [g(S0/S_c) - A]：η > I0 ⇔ A < g(S0/S_c)
    e3 = sp.expand_log(eta - I0 - (1 - q0) * Sc * (gz.subs(z, S0 / Sc) - A), force=True)
    record(g, 'η - I0 = (1-q0)S_c[g(S0/S_c) - A]，故 η > I0 ⇔ A < g(S0/S_c)', is_zero(e3))
    # Lambert W：若 w e^w = -e^{-A} 且 w < 0，则 z = -w 满足 z - ln z = A
    w = sp.symbols('w', negative=True)
    A_from_w = -sp.log(-w * sp.exp(w))          # 由 w e^w = -e^{-A} 解出 A
    e4 = sp.expand_log(A_from_w - (-w - sp.log(-w)), force=True)
    record(g, 'w e^w = -e^{-A}（w<0）⇒ z = -w 满足 z - ln z = A', is_zero(e4))
    # g 在 z > 1 上严格增、g(1) = 1；W_{-1} 在 (-1/e, 0) 上取值 < -1
    record(g, "g'(z) = 1 - 1/z > 0（z > 1），g(1) = 1", is_zero(sp.diff(gz, z) - (1 - 1 / z)) and gz.subs(z, 1) == 1)


def check_R3_arc():
    g = 'R3 阈值弧：时长、感染、K_q、成本'
    S1, S2 = sp.symbols('S_1 S_2', positive=True)        # 积分区间 [S_c, S*_ir]，用一般端点核对
    q_bal = 1 - gamma * N / (beta * c * S)
    # 立即返回：Ṡ = -βcSη/N；dt = N dS/(βη c S)（正向时长）
    dt_dS_ir = N / (beta * eta * c * S)
    Sb = sp.symbols('Sbar', nonnegative=True)           # 无回流被积函数中的 S̄ 作为独立符号
    dt_dS_0 = N / (eta * (c * S - c0 * Sb))             # 无回流：Ṡ = -(η/N)(cS - c0S̄)
    record(g, '时长被积函数：立即返回 = (1/β)·[无回流被积函数中取 S̄=0]',
           is_zero(dt_dS_ir - dt_dS_0.subs(Sb, 0) / beta))
    # 无回流被积函数在原模型中的 S̄ 取值：c0S̄ = (1-β)γN/β > 0，不能取 0（S̄=0 只是对应）
    record(g, '原模型中 S̄/S_c = (1-β)(1-q0) ∈ (0,1)（0<β<1、0≤q0<1）',
           is_zero(Sbar / Sc - (1 - beta) * (1 - q0)))
    # 仅隔离 c = c0 与仅减少接触 c = c0 S_c/S 的闭式
    dtq = sp.integrate(dt_dS_ir.subs(c, c0), (S, S1, S2))
    record(g, 'Δt_q = N/(βηc0) ln(S*_ir/S_c)', is_zero(sp.expand_log(dtq - N / (beta * eta * c0) * sp.log(S2 / S1), force=True)))
    dtc = sp.integrate(dt_dS_ir.subs(c, c0 * S1 / S), (S, S1, S2))
    record(g, 'Δt_c = N(S*_ir-S_c)/(βηc0S_c)', is_zero(dtc - N * (S2 - S1) / (beta * eta * c0 * S1)))
    # 被积函数随 c 严格减：∂/∂c [1/(cS)] < 0
    record(g, '∂/∂c[N/(βηcS)] = -N/(βηc²S) < 0', is_zero(sp.diff(dt_dS_ir, c) + N / (beta * eta * c ** 2 * S)))
    # 感染：F dt = βcSη/N · dt = dS，控制期累计感染 = S*_ir - S_c
    F_dt = (beta * c * S * eta / N) * dt_dS_ir
    record(g, '平台上 F·dt/dS = 1，控制期累计感染 = S*_ir - S_c', is_zero(F_dt - 1))
    # K_q：(1-β)cqSη/N · dt = (1-β)/β · q dS，且 q = 1 - γN/(βcS)
    Kq_dens = (1 - beta) * c * q_bal * S * eta / N * dt_dS_ir
    record(g, 'K_q 被积函数 = (1-β)/β·[1 - γη·N/(βηcS)]，积分得 (1-β)/β[S*_ir-S_c-γηΔt_ir]',
           is_zero(Kq_dens - (1 - beta) / beta * (1 - gamma * eta * dt_dS_ir)))
    # 仅减少接触（q ≡ q0）时 K_q = (1-β)/β q0 (S*_ir-S_c)，与恒等式一致
    Kq_c = (1 - beta) / beta * (S2 - S1 - gamma * eta * dtc)
    record(g, '仅减少接触：(1-β)/β[S*_ir-S_c-γηΔt_c] = (1-β)/β·q0·(S*_ir-S_c)',
           is_zero((Kq_c - (1 - beta) / beta * q0 * (S2 - S1)).subs(S1, Sc)))
    # 归一化隔离强度在立即返回模型中仍为 1 - c0S_c/(cS)
    record(g, '(q-q0)/(1-q0) = 1 - c0S_c/(cS)（平衡式下）',
           is_zero((q_bal - q0) / (1 - q0) - (1 - c0 * Sc / (c * S))))
    # 成本：J 的时间被积函数 × dt/dS = (N/(βη))·f|_{S̄=0}
    n_cost = wc * (1 - c / c0) ** 2 + wq * ((q_bal - q0) / (1 - q0)) ** 2
    f0 = (wc * (1 - c / c0) ** 2 + wq * (1 - c0 * Sc / (c * S)) ** 2) / (c * S)   # f 中取 S̄=0
    record(g, 'J 的被积函数 = (N/(βη))·f(S,c)|_{S̄=0}', is_zero(n_cost * dt_dS_ir - N / (beta * eta) * f0))


def check_R3_cost():
    g = 'R3 成本结构（h_a）'
    a, x, u, eps = sp.symbols('a x u epsilon', positive=True)
    h = (wc * (1 - x) ** 2 + wq * (1 - a / x) ** 2) / x
    quartic = wc * x ** 4 - (wc + wq) * x ** 2 + 4 * a * wq * x - 3 * a ** 2 * wq
    record(g, "x⁴h_a'(x) = w_c x⁴ - (w_c+w_q)x² + 4a w_q x - 3a² w_q", is_zero(x ** 4 * sp.diff(h, x) - quartic))
    ha_a = sp.simplify(sp.diff(h, x).subs(x, a))
    record(g, "h_a'(a) = w_c(1 - a⁻²)", is_zero(ha_a - wc * (1 - a ** -2)))
    ha_1 = sp.simplify(sp.diff(h, x).subs(x, 1))
    record(g, "h_a'(1) = w_q(1-a)(3a-1)", is_zero(ha_1 - wq * (1 - a) * (3 * a - 1)))
    # f|_{S̄=0}(S, c0 x) = h_a(x)/(c0 S)，a = S_c/S
    Ssym = sp.symbols('S', positive=True)
    f0 = (wc * (1 - c / c0) ** 2 + wq * (1 - c0 * Sc / (c * Ssym)) ** 2) / (c * Ssym)
    e = f0.subs(c, c0 * x) - h.subs(a, Sc / Ssym) / (c0 * Ssym)
    record(g, 'f(S,c0x)|_{S̄=0} = h_a(x)/(c0S)，a = S_c/S', is_zero(e))
    # 五次驻点式（式 joint:stationary）在 S̄ = 0 处 = c·c0²·x⁴h_a'(x)
    Sb = sp.symbols('Sbar', nonnegative=True)
    Scs = sp.symbols('S_c', positive=True)
    quintic = (wc * c ** 3 / c0 ** 2 * (c - c0) * (c + c0 - 2 * c0 * Sb / Ssym)
               + wq * (c - c0 * Scs / Ssym) * (-c ** 2 + 3 * c0 * Scs / Ssym * c - 2 * c0 ** 2 * Sb * Scs / Ssym ** 2))
    e5 = quintic.subs(Sb, 0) - c * c0 ** 2 * quartic.subs({x: c / c0, a: Scs / Ssym})
    record(g, '式 (joint:stationary) 中取 S̄=0 等于 c·c0²·[x⁴h_a\'(x)]（x=c/c0），c=0 不在允许区间',
           is_zero(e5))
    # 五次式本身：对 f（含 S̄）求导乘 c³(cS-c0S̄)²/S 后等于式 (joint:stationary)
    fS = (wc * (1 - c / c0) ** 2 + wq * (1 - c0 * Scs / (c * Ssym)) ** 2) / (c * Ssym - c0 * Sb)
    e6 = sp.diff(fS, c) * c ** 3 * (c * Ssym - c0 * Sb) ** 2 / Ssym - quintic
    record(g, '附录 A.7：∂f/∂c · c³(cS-c0S̄)²/S = 式 (joint:stationary)（S̄ ≥ 0 一般成立）', is_zero(e6))
    # 命题 5.3 右端点二次式在 S̄=0 处的根为 0 与 3S_c；S_sw 中取 S̄=0 即 3S_c
    Ssw = (3 * Scs + sp.sqrt(9 * Scs ** 2 - 8 * Scs * Sb)) / 2
    record(g, 'S_sw 中取 S̄=0 等于 3S_c', is_zero(Ssw.subs(Sb, 0) - 3 * Scs))
    quad_r = Ssym ** 2 - 3 * Scs * Ssym + 2 * Scs * Sb
    record(g, '右端点二次式 S² - 3S_cS + 2S_cS̄ 在 S̄=0 处 = S(S-3S_c)', is_zero(quad_r.subs(Sb, 0) - Ssym * (Ssym - 3 * Scs)))
    # 附录 A.8 左、右端点的符号量（含 S̄），核对与 h_a'(a)、h_a'(1) 在 S̄=0 处一致
    nfun = wc * (1 - c / c0) ** 2 + wq * (1 - c0 * Scs / (c * Ssym)) ** 2
    G = sp.diff(nfun, c) * (c * Ssym - c0 * Sb) - Ssym * nfun
    left = G.subs(c, c0 * Scs / Ssym)
    left_paper = -2 * wc * (1 - Scs / Ssym) * (Scs - Sb) - Ssym * wc * (1 - Scs / Ssym) ** 2
    record(g, '附录 A.8 左端点量 = -2w_c(1-S_c/S)(S_c-S̄) - Sw_c(1-S_c/S)²', is_zero(left - left_paper))
    right = G.subs(c, c0)
    right_paper = -wq / Ssym * (1 - Scs / Ssym) * (Ssym ** 2 - 3 * Scs * Ssym + 2 * Scs * Sb)
    record(g, '附录 A.8 右端点量 = -(w_q/S)(1-S_c/S)(S²-3S_cS+2S_cS̄)', is_zero(right - right_paper))
    # 退出附近：x = 1 - εu，a = 1 - ε，四次式按 ε 展开
    ser = sp.expand(quartic.subs({x: 1 - eps * u, a: 1 - eps}))
    c0_term = ser.coeff(eps, 0)
    c1_term = sp.factor(ser.coeff(eps, 1))
    record(g, '四次式在 (x,a) = (1-εu, 1-ε) 处：ε⁰ 项为 0', is_zero(c0_term))
    u_star = sp.solve(sp.Eq(c1_term, 0), u)
    record(g, 'ε¹ 项为 2[w_q - (w_c+w_q)u]，零点 u = w_q/(w_c+w_q)',
           is_zero(c1_term - 2 * (wq - (wc + wq) * u)) and len(u_star) == 1
           and is_zero(u_star[0] - wq / (wc + wq)), f'u* = {u_star}')
    # 极限函数：f|_{S̄=0}(S, c0(1-εu))/ε² 中 S = S_c/(1-ε)，ε→0 时 → [w_c u² + w_q(1-u)²]/(c0S_c)
    Sexpr = Scs / (1 - eps)
    lim_f = (wc * (eps * u) ** 2 + wq * (1 - c0 * Scs / (c0 * (1 - eps * u) * Sexpr)) ** 2) / (c0 * (1 - eps * u) * Sexpr) / eps ** 2
    G0 = (wc * u ** 2 + wq * (1 - u) ** 2) / (c0 * Scs)
    record(g, 'f/ε² → [w_c u² + w_q(1-u)²]/(c0S_c)（ε→0）', is_zero(sp.limit(lim_f, eps, 0) - G0))
    uG = sp.solve(sp.diff(G0, u), u)
    record(g, '极限函数的唯一最小点 u = w_q/(w_c+w_q)（严格凸）',
           len(uG) == 1 and is_zero(uG[0] - wq / (wc + wq)) and sp.simplify(sp.diff(G0, u, 2)) != 0)
    # 两种归一化强度：接触 εu，隔离 ε(1-u)/(1-εu)；比值 → u/(1-u) = w_q/w_c
    ratio = (eps * u) / (eps * (1 - u) / (1 - eps * u))
    record(g, '强度之比 → w_q/w_c', is_zero(sp.limit(ratio, eps, 0).subs(u, wq / (wc + wq)) - wq / wc))
    qshare = sp.limit((1 - u) / (1 - eps * u), eps, 0).subs(u, wq / (wc + wq))
    record(g, '隔离强度/(1-S_c/S) → w_c/(w_c+w_q)', is_zero(qshare - wc / (wc + wq)))
    # 默认权重下 a = 1/(2√2) 时 x = 1/√2 是四次式的三重根（R7-1 记录第 2 条：c_c* 不光滑）
    P = quartic.subs({wc: 1, wq: 2, a: 1 / (2 * sp.sqrt(2))})
    x0 = 1 / sp.sqrt(2)
    vals = [sp.simplify(sp.diff(P, x, k).subs(x, x0)) for k in range(4)]
    record(g, '默认权重：a = 1/(2√2)（S = 2√2 S_c）时 x = 1/√2 为三重根',
           vals[0] == 0 and vals[1] == 0 and vals[2] == 0 and vals[3] != 0, f'P, P\', P\'\', P\'\'\' = {vals}')


def check_release():
    g = '释放注记（ω = 0）'
    SqT = sp.symbols('S_q2', positive=True)
    S_plus = Sc + xi * SqT
    Re = beta * c0 * (1 - q0) * S_plus / (gamma * N)
    record(g, 'R_e(t2+) = 1 + ξS_q(t2)/S_c', is_zero(Re - (1 + xi * SqT / Sc)))
    dI = beta * c0 * (1 - q0) * S_plus * eta / N - gamma * eta
    record(g, 'İ(t2+) = γη ξ S_q(t2)/S_c', is_zero(dI - gamma * eta * xi * SqT / Sc))


# ======================================================================
# 二、两组参数的数值抽检
# ======================================================================
REF = {   # 执行计划第 5 节参考值
    'base': dict(S_c=175.160, S_star_inf=712.512, dt_q=18.104, dt_c=39.584, infections=537.35,
                 C0_qonly=286.590, L=586.840, Sq2_over_Sc=2.215, Re=3.22),
    'xian': dict(S_c=2.97413e6, S_star_inf=1.31127e7, dt_q=384.26, dt_c=882.91, infections=1.01386e7,
                 C0_qonly=2.37795e6, L=1.01889e7, Sq2_over_Sc=2.714, Re=3.71),
}


def rel(a, b):
    return abs(a - b) / abs(b)


def numeric_case(P):
    g = f'数值抽检：{P.name}'
    out = {}
    Sc_, Sb_, N_, b_, g_, c0_, q0_, eta_ = P.S_c, P.S_bar, P.N, P.beta, P.gamma, P.c0, P.q0, P.eta
    S0_, I0_ = P.S0, P.I0
    ref = REF[P.name]
    out.update(S_c=Sc_, S_bar=Sb_, U0=P.U0, L=P.L_bound)
    record(g, 'S_c 与参考值（相对差 < 1e-5）', rel(Sc_, ref['S_c']) < 1e-5, f'{Sc_:.10g}')
    # ---- 立即返回：触发条件、A、S*_ir ----
    z0 = S0_ / Sc_
    Ipeak = I0_ + (1 - q0_) * (S0_ - Sc_ + Sc_ * math.log(Sc_ / S0_))
    A = (S0_ - (eta_ - I0_) / (1 - q0_)) / Sc_ - math.log(S0_ / Sc_)
    out.update(I_peak_ir=Ipeak, A=A)
    record(g, '触发条件 0 < I0 < η < I_peak,ir 且 S0 > S_c', 0 < I0_ < eta_ < Ipeak and S0_ > Sc_,
           f'I0 = {I0_:.6g}, η = {eta_:.6g}, I_peak,ir = {Ipeak:.10g}')
    record(g, 'A > 1，且 I_peak,ir - η = (1-q0)S_c(A-1)',
           A > 1 and rel(Ipeak - eta_, (1 - q0_) * Sc_ * (A - 1)) < 1e-10, f'A = {A:.12g}')
    w = lambertw(-math.exp(-A), k=-1)
    S_inf = -Sc_ * w.real
    Ifun = lambda s: I0_ + (1 - q0_) * ((S0_ - s) + Sc_ * math.log(s / S0_)) - eta_
    S_inf_b = brentq(Ifun, Sc_ * (1 + 1e-14), S0_, xtol=1e-13 * S0_, rtol=4 * np.finfo(float).eps)
    out.update(S_star_inf=S_inf, S_star_inf_brentq=S_inf_b)
    record(g, 'S*_ir = -S_c W_{-1}(-e^{-A}) 与 brentq 一致（< 1e-12）',
           rel(S_inf, S_inf_b) < 1e-12 and abs(w.imag) < 1e-12 and Sc_ < S_inf < S0_, f'{S_inf:.12g}')
    record(g, 'S*_ir 与参考值（< 1e-5）', rel(S_inf, ref['S_star_inf']) < 1e-5)
    # ---- Δt_q、Δt_c 闭式与求积 ----
    pref = N_ / (b_ * eta_)
    dtq = N_ / (b_ * eta_ * c0_) * math.log(S_inf / Sc_)
    dtc = N_ * (S_inf - Sc_) / (b_ * eta_ * c0_ * Sc_)
    dtq_quad = pref * quad(lambda s: 1 / (c0_ * s), Sc_, S_inf, epsabs=0, epsrel=1e-13)[0]
    dtc_quad = pref * quad(lambda s: 1 / (c0_ * Sc_), Sc_, S_inf, epsabs=0, epsrel=1e-13)[0]
    out.update(dt_q=dtq, dt_c=dtc)
    record(g, 'Δt_q 闭式 = 求积（< 1e-10），与参考值（< 1e-4）',
           rel(dtq, dtq_quad) < 1e-10 and rel(dtq, ref['dt_q']) < 1e-4, f'{dtq:.10g}')
    record(g, 'Δt_c 闭式 = 求积（< 1e-10），与参考值（< 1e-4）',
           rel(dtc, dtc_quad) < 1e-10 and rel(dtc, ref['dt_c']) < 1e-4, f'{dtc:.10g}')
    record(g, 'Δt_q < Δt_c', dtq < dtc)
    # ---- 控制期感染与 K_q ----
    inf = S_inf - Sc_
    out['infections_ir'] = inf
    record(g, '控制期累计感染 S*_ir - S_c 与参考值（< 1e-5）', rel(inf, ref['infections']) < 1e-5, f'{inf:.10g}')
    Kq = lambda dt: (1 - b_) / b_ * (S_inf - Sc_ - g_ * eta_ * dt)
    Kq_q, Kq_c = Kq(dtq), Kq(dtc)
    # 直接求积：K_q = (1-β)/β ∫ q dS，q = 1 - γN/(βcS)
    Kq_q_quad = (1 - b_) / b_ * quad(lambda s: 1 - g_ * N_ / (b_ * c0_ * s), Sc_, S_inf, epsabs=0, epsrel=1e-13)[0]
    Kq_c_direct = (1 - b_) / b_ * q0_ * (S_inf - Sc_)
    out.update(Kq_q=Kq_q, Kq_c=Kq_c)
    record(g, 'K_q 恒等式 = 直接求积（仅隔离）与 q0 公式（仅减少接触）（< 1e-10）',
           rel(Kq_q, Kq_q_quad) < 1e-10 and rel(Kq_c, Kq_c_direct) < 1e-10,
           f'K_q：仅隔离 {Kq_q:.8g}，仅减少接触 {Kq_c:.8g}')
    record(g, 'K_q 与 Δt 反序：K_q(仅隔离) > K_q(仅减少接触)', Kq_q > Kq_c)
    # ---- k ----
    k1 = b_ * c0_ * Sc_ * eta_ / N_
    k2 = g_ * eta_ / (1 - q0_)
    out['k'] = k1
    record(g, 'k = βc0S_cη/N = γη/(1-q0)', rel(k1, k2) < 1e-13, f'k = {k1:.10g} 人/d')
    # ---- h_a 的四次式与有限差分；端点导数符号 ----
    wc_, wq_ = P.wc, P.wq
    hfun = lambda x, a: (wc_ * (1 - x) ** 2 + wq_ * (1 - a / x) ** 2) / x
    quart = lambda x, a: wc_ * x ** 4 - (wc_ + wq_) * x ** 2 + 4 * a * wq_ * x - 3 * a ** 2 * wq_
    zs = np.linspace(1.05, S_inf / Sc_, 25)
    max_fd = 0.0
    for zz in zs:
        a_ = 1 / zz
        for x_ in np.linspace(a_ + 1e-3, 1 - 1e-3, 7):
            hstep = 1e-6
            fd = (hfun(x_ + hstep, a_) - hfun(x_ - hstep, a_)) / (2 * hstep)
            max_fd = max(max_fd, abs(fd - quart(x_, a_) / x_ ** 4) / max(1.0, abs(fd)))
    record(g, "x⁴h_a'(x) 与 h_a 的中心差分一致（相对 < 1e-7）", max_fd < 1e-7, f'max = {max_fd:.2e}')
    ok_left = all(quart(1 / zz, 1 / zz) < 0 for zz in zs)
    sgn_right = [(zz, np.sign(quart(1.0, 1 / zz))) for zz in zs]
    ok_right = all((s < 0) == (zz > 3) for zz, s in sgn_right if abs(zz - 3) > 1e-9)
    record(g, "抽样 S∈(S_c,S*_ir]：h_a'(a) < 0；h_a'(1) 在 S>3S_c 时 < 0、S<3S_c 时 > 0", ok_left and ok_right)
    # ---- 退出附近的分担比例（数值最小化） ----
    shares = {}
    for (wcv, wqv) in [(1.0, 2.0), (1.0, 1.0), (3.0, 1.0)]:
        res = []
        for e_ in [1e-2, 1e-3, 1e-4]:
            a_ = 1 - e_
            h2 = lambda x: (wcv * (1 - x) ** 2 + wqv * (1 - a_ / x) ** 2) / x
            m = minimize_scalar(h2, bounds=(a_, 1.0), method='bounded', options=dict(xatol=1e-14))
            res.append((1 - m.x) / e_)        # 接触减少的分担比例 (1-c/c0)/(1-S_c/S)
        shares[f'{wcv:g},{wqv:g}'] = res
    ok_share = all(abs(v[-1] - wqv / (wcv + wqv)) < 2e-3
                   for (k, v), (wcv, wqv) in zip(shares.items(), [(1.0, 2.0), (1.0, 1.0), (3.0, 1.0)]))
    record(g, '退出附近分担比例 → w_q/(w_c+w_q)（ε = 1e-2, 1e-3, 1e-4；三组权重）', ok_share,
           '; '.join(f'(w_c,w_q)=({k}): ' + ', '.join(f'{v:.5f}' for v in vals) for k, vals in shares.items()))
    out['terminal_shares'] = shares
    # ---- 无回流仅隔离控制 t→∞ 的累计感染（定理 3.5、3.6）与 L：推论 cor:return:right-discontinuity 的前提抽检 ----
    kappa0 = b_ * (1 - q0_) / (b_ + (1 - b_) * q0_)          # β2/β1
    kprime = b_ / (b_ + q0_ * (1 - b_))
    I0fun = lambda s: I0_ + kappa0 * ((S0_ - s) + Sc_ * math.log(s / S0_)) - eta_
    S_star0 = brentq(I0fun, Sc_ * (1 + 1e-14), S0_, xtol=1e-13 * S0_, rtol=4 * np.finfo(float).eps)
    S_inf_post = float(-Sc_ * lambertw(-math.exp(-1 - eta_ / (kappa0 * Sc_)), k=0).real)
    C_q = (kprime * (S0_ - S_star0 + Sc_ - S_inf_post)
           + b_ * (S_star0 - Sc_ + Sb_ * math.log((S_star0 - Sb_) / (Sc_ - Sb_))))
    dt0_q = N_ / (c0_ * eta_) * math.log((S_star0 - Sb_) / (Sc_ - Sb_))
    dt0_c = N_ * (S_star0 - Sc_) / (c0_ * eta_ * (Sc_ - Sb_))
    al = 0.5
    dt0_a = N_ / (c0_ * eta_ * al) * math.log(1 + al * (S_star0 - Sc_) / (Sc_ - Sb_))
    C_of = lambda dt: C_q + g_ * eta_ * (1 - b_) * (dt - dt0_q)   # 推论 joint:whole-epidemic（t→∞）
    Cs = dict(q_only=C_q, alpha=C_of(dt0_a), c_only=C_of(dt0_c))
    try:   # 成本最优控制的 Δt 用 R7-1 的求积（只读调用）
        import endpoints as EP
        dt0_opt = EP.arc_noreturn(P, 'opt_noreturn', with_quad=False)['dt']
        Cs['opt'] = C_of(dt0_opt)
    except Exception as exc:   # pragma: no cover
        Cs['opt'] = float('nan')
        record(g, '成本最优控制 Δt（R7-1 求积）', False, repr(exc))
    out.update(S_star_noreturn=S_star0, S_inf_noreturn=S_inf_post, C0=Cs)
    record(g, '无回流仅隔离 t→∞ 累计感染与参考值（< 1e-5）', rel(C_q, ref['C0_qonly']) < 1e-5, f'{C_q:.10g}')
    record(g, 'L = U(0) - S_c 与参考值（< 1e-5）', rel(P.L_bound, ref['L']) < 1e-5, f'{P.L_bound:.10g}')
    premise = {k: (v < P.L_bound) for k, v in Cs.items()}
    out['premise_C0_lt_L'] = premise
    record(g, '推论 cor:return:right-discontinuity 的前提 C_π(0) < L 的抽检（只报告，不判通过与否）', True,
           '; '.join(f'{k}: C(0) = {v:.8g}，{"满足" if premise[k] else "不满足"}' for k, v in Cs.items()))
    # ---- 释放注记：仅隔离控制 S_q(t2)/S_c 的解析值（S_q(0)=0） ----
    dSq_pre = (1 - b_) * q0_ / (b_ + (1 - b_) * q0_) * (S0_ - S_star0)
    dSq_plat = (1 - b_) * (S_star0 - Sc_ - g_ * eta_ * dt0_q)
    Sq2 = P.Sq0 + dSq_pre + dSq_plat
    out.update(Sq2_over_Sc=Sq2 / Sc_, Re_release=1 + Sq2 / Sc_)
    record(g, '仅隔离控制 S_q(t2)/S_c 与 ξ=1 的 R_e(t2+)（解析，与计划数值 < 1e-3）',
           rel(Sq2 / Sc_, ref['Sq2_over_Sc']) < 1e-3 and rel(1 + Sq2 / Sc_, ref['Re']) < 2e-3,
           f'S_q(t2)/S_c = {Sq2 / Sc_:.7f}，R_e = {1 + Sq2 / Sc_:.7f}')
    return out


# ======================================================================
def main():
    check_R1()
    check_plateau_k()
    check_R3_start()
    check_R3_arc()
    check_R3_cost()
    check_release()
    numbers = {name: numeric_case(P) for name, P in PR.CASES.items()}

    n_fail = sum(not r['ok'] for r in RESULTS)
    lines = ['# R7-2 理论核对（`r7_return/theory_checks.py` 自动生成）', '',
             'SymPy 只核对代数；存在性、可测性与量词论证见 `paper/revision_notes/R7_2_return_theory.md`。', '',
             f'共 {len(RESULTS)} 项，未通过 {n_fail} 项。', '',
             '| 组 | 核对项 | 结果 | 说明 |', '|---|---|---|---|']
    for r in RESULTS:
        lines.append(f"| {r['group']} | {r['name']} | {'通过' if r['ok'] else '**未通过**'} | {r['detail']} |")
    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
    with open(os.path.join(HERE, 'results', 'r7_2_theory_checks.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')
    with open(os.path.join(HERE, 'results', 'r7_2_theory_checks.json'), 'w', encoding='utf-8') as fh:
        json.dump(dict(checks=RESULTS, numbers=numbers), fh, ensure_ascii=False, indent=1,
                  default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    for r in RESULTS:
        print(('PASS ' if r['ok'] else 'FAIL ') + f"[{r['group']}] {r['name']}  {r['detail']}")
    print(f'\n{len(RESULTS)} 项，未通过 {n_fail} 项')
    return 1 if n_fail else 0


if __name__ == '__main__':
    sys.exit(main())
