"""含回流的 SIQR 模型与立即返回对照模型（按 N 归一的第一套变量）。

执行计划第 3 节的模型（ω ≥ 0；ω = 0 即稿件式 (2.1)）：
    Ṡ   = -c[β+(1-β)q] S I/N + ω S_q
    Ṡ_q =  (1-β) c q S I/N   - ω S_q
    İ   =  β c (1-q) S I/N   - γ I
    İ_q =  β c q S I/N       - δ_q I_q
    Ṙ   =  γ I + δ_q I_q
两边除以 N 得到 s_N = S/N 等变量的方程（形式不变，只把 S I/N 换成 s_N i_N）。

立即返回对照模型单独实现，不用 ω = inf 的数值近似代替：
    S_q ≡ 0（要求 S_q(0) = 0），Ṡ = -β c S I/N，I、I_q、R 的方程不变，总人口守恒。

流量记号（按 N 归一）：
    contact = c s_N i_N              接触流量
    F_N     = β · contact            总新增感染流量 F/N（进入 I 与 I_q 之和）
    Aq_N    = (1-β) q · contact      未感染接触者被追踪隔离的流量（进入 S_q 或立即返回）
总易感者 U = S + S_q 满足 U̇ = -F（引理 R1）。
"""


def flows_N(s_N, i_N, c, q, P):
    """返回 (contact, F_N, Aq_N)。"""
    contact = c * s_N * i_N
    return contact, P.beta * contact, (1.0 - P.beta) * q * contact


def log_growth_rate(s_N, c, q, P):
    """İ/I = βc(1-q)s_N - γ（两种模型相同）。"""
    return P.beta * c * (1.0 - q) * s_N - P.gamma


def rhs_return(s_N, i_N, sq_N, iq_N, r_N, c, q, P, omega):
    """含回流模型的右端，返回 (ṡ, i̇, ṡ_q, i̇_q, ṙ)（按 N 归一）。"""
    contact, F_N, Aq_N = flows_N(s_N, i_N, c, q, P)
    ds = -(P.beta + (1.0 - P.beta) * q) * contact + omega * sq_N
    di = P.beta * (1.0 - q) * contact - P.gamma * i_N
    dsq = Aq_N - omega * sq_N
    diq = P.beta * q * contact - P.delta_q * iq_N
    dr = P.gamma * i_N + P.delta_q * iq_N
    return ds, di, dsq, diq, dr


def rhs_immediate(s_N, i_N, iq_N, r_N, c, q, P):
    """立即返回对照模型的右端，返回 (ṡ, i̇, i̇_q, ṙ)；S_q ≡ 0 不是状态。"""
    contact, F_N, Aq_N = flows_N(s_N, i_N, c, q, P)
    ds = -P.beta * contact
    di = P.beta * (1.0 - q) * contact - P.gamma * i_N
    diq = P.beta * q * contact - P.delta_q * iq_N
    dr = P.gamma * i_N + P.delta_q * iq_N
    return ds, di, diq, dr


def plateau_control(z, x, P):
    """阈值弧上的控制：c = c0 x，q = 1 - γN/(βcS) = 1 - (1-q0)/(x z)（z = S/S_c）。"""
    return P.c0 * x, 1.0 - (1.0 - P.q0) / (x * z)


def cost_rate(x, z, P, wc=None, wq=None):
    """二次干预强度成本的被积函数 w_c u_c² + w_q u_q²，u_c = 1-x，u_q = 1 - 1/(x z)。"""
    wc = P.wc if wc is None else wc
    wq = P.wq if wq is None else wq
    return wc * (1.0 - x) ** 2 + wq * (1.0 - 1.0 / (x * z)) ** 2
