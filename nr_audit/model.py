"""无回流 SIQR 模型（稿件式 2.1）的右端、流量与阈值弧上的控制（按 N 归一的第一套变量）。

复制来源：research/return-effects bb52b96 的 r7_return/model.py（blob 810bf85c，与 91123ea 相同），
只保留 ω = 0 的部分：删去回流项 ωS_q 与立即返回对照模型；成本被积函数改为稿件式 (2.13)
的 (·)_+ 形式，并增加线性强度 u_c、u_q（式 2.12）。

    Ṡ   = -c[β+(1-β)q] S I/N
    İ   =  β c (1-q) S I/N - γ I
    Ṡ_q =  (1-β) c q S I/N
    İ_q =  β c q S I/N     - δ_q I_q
    Ṙ   =  γ I + δ_q I_q
两边除以 N 后形式不变，只把 S I/N 换成 s_N i_N。

流量（按 N 归一）：
    contact = c s_N i_N          接触流量
    into_I  = β(1-q)·contact     进入 I 的新增感染（I_cum 的被积函数）
    into_Iq = βq·contact         进入 I_q 的新增感染（I_qcum 的被积函数）
    into_Sq = (1-β)q·contact     未感染接触者被隔离（S_q 的流入）
总新增感染 F = into_I + into_Iq = β·contact，满足 d(S+S_q)/dt = -F。
"""


def flows_N(s_N, i_N, c, q, P):
    """返回 (contact, into_I, into_Iq, into_Sq)。"""
    contact = c * s_N * i_N
    return (contact, P.beta * (1.0 - q) * contact, P.beta * q * contact,
            (1.0 - P.beta) * q * contact)


def rhs_N(s_N, i_N, sq_N, iq_N, r_N, c, q, P):
    """式 (2.1) 的右端，返回 (ṡ, i̇, ṡ_q, i̇_q, ṙ)（按 N 归一）。"""
    contact, into_I, into_Iq, into_Sq = flows_N(s_N, i_N, c, q, P)
    ds = -(P.beta + (1.0 - P.beta) * q) * contact
    di = into_I - P.gamma * i_N
    dsq = into_Sq
    diq = into_Iq - P.delta_q * iq_N
    dr = P.gamma * i_N + P.delta_q * iq_N
    return ds, di, dsq, diq, dr


def log_growth_rate(s_N, c, q, P):
    """İ/I = βc(1-q)s_N - γ。"""
    return P.beta * c * (1.0 - q) * s_N - P.gamma


def plateau_control(z, x, P):
    """阈值弧上的控制：c = c0 x，q = 1 - γN/(βcS) = 1 - (1-q0)/(x z)（z = S/S_c，式 4.3）。"""
    return P.c0 * x, 1.0 - (1.0 - P.q0) / (x * z)


def intensities(c, q, P):
    """归一化强度 u_c = (c0-c)_+/c0、u_q = (q-q0)_+/(1-q0)（式 2.12、2.13）。"""
    return max(0.0, (P.c0 - c) / P.c0), max(0.0, (q - P.q0) / (1.0 - P.q0))


def cost_rate(u_c, u_q, wc, wq):
    """二次干预强度成本的被积函数 w_c u_c² + w_q u_q²（式 2.13）。"""
    return wc * u_c * u_c + wq * u_q * u_q
