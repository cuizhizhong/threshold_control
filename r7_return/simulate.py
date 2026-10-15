"""事件法正式计算：常规 → 阈值弧 → 退出后（按 N 归一的第一套变量）。

状态向量（各阶段相同，阶段之间连续衔接，不重置）：
    y = [s_N, logi_N, sq_N, iq_N, r_N, cinf_N, J, kq_N]
    s_N = S/N，logi_N = ln(I/N)，sq_N = S_q/N，iq_N = I_q/N，r_N = R/N，
    cinf_N = 累计新增感染/N（∫F dt，独立积分的状态，不由 U(0)-U 定义），
    J      = 二次干预强度成本 ∫(w_c u_c² + w_q u_q²) dt（天），
    kq_N   = 未感染接触者累计追踪人次/N（∫A_q dt；ω=0 时即新增隔离易感者人数）。
感染者用 ln I 表示：保证 I 的正性与相对精度（西安 i0 ≈ 7.65e-11），求解误差不会造成假的零感染。

阶段：
1. 常规（c0, q0）：事件“I 由下方首次达到 η”（ln i - ln θ = 0，方向向上，终止）。
   I0 ≥ η 等退化情形单列分支。ω = 0 与立即返回时另设“S 由上方到达 S_c 而未触发”事件：
   此后 S 单调下降、I 单调下降，策略不再触发。
2. 阈值弧：I ≡ η 由代数给出（ln i 取 ln θ，导数为 0），其余状态照常推进；
   c = c0·x(S/S_c)，q = 1 - γN/(βcS)。事件“S 由上方首次达到 S_c”（方向向下，终止）即退出 t2。
   进入阈值弧时 ln i 取代数值 ln θ，触发事件处的偏差作为事件残差报告。
3. 退出后：永久取 (c0, q0)。可选在 t2 释放比例 ξ 的隔离易感者（S += ξS_q，S_q -= ξS_q）。
   终止按模型分支：
   - ω = 0 与立即返回：清零事件 I = 1 只在本阶段、方向向下时触发；t→∞ 值按首次积分
     I + κ(S - S_c ln S) = 常数解析补尾（ω=0 时 κ = β(1-q0)/(β+(1-β)q0)，定理 3.5 的 S_∞）。
   - ω > 0：U < S_c 后用执行计划第 5 节的尾部误差上界
       B(T) = β c0 U(T) I(T) / (N γ [1 - U(T)/S_c])，
     积分到 B ≤ ε_tail（默认 1e-6·U(0)）为止（事件，方向向上，终止），输出
     “最终规模估计 = 终止时累计感染 + [0, B]”；到积分上限仍未满足的记为“未到达”。
     不把 I < 1 当作尾部感染为零。
   - ω > 0 且 Config.return_endpoint = 'first_below_one'（R7-3 起正式结果采用）：退出后 I 首次
     由上方降到 1 时截断（方向向下的终止事件），假设此时传播结束；截断值不是 t→∞ 的估计，
     命题 R2 的下界只针对不截断的 t→∞ 累计感染。
   退出后峰值：İ = 0 的非终止事件（İ/I = βc0(1-q0)s - γ 由正变负为极大、由负变正为极小）
   定位内部极值，与端点 t2、终止时刻比较；t2 处本来就有 İ = 0，紧邻 t2 的伪事件剔除，
   不作终止条件。另记 I = 1 的上、下穿越，“越过阈值”与“I 降到 1 以下后再回升”分开记录。

积分：solve_ivp（默认 Radau，rtol = 1e-11），各分量 atol 显式设置（见 default_atol），
max_step 默认 1 d。solve_ivp 没有单独的事件容差：收敛检查同时收紧 rtol、atol 并减小 max_step。
事件时刻由 solve_ivp 在连续解上用 brentq 求根（求根容差为 4·机器精度，scipy 内部设定）。
"""
import math
from dataclasses import dataclass, field

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.special import lambertw

import alloc as AL
import model as M

IS, ILI, ISQ, IIQ, IR, ICF, IJ, IKQ = range(8)
STATE_NAMES = ('s_N', 'logi_N', 'sq_N', 'iq_N', 'r_N', 'cinf_N', 'J', 'kq_N')

E_ABS_TOL = 1e-8          # e = max I/η - 1 的绝对判据（越过 / 未越过 / 数值上未确定）
T2_EVENT_GUARD = 1e-9     # 剔除紧邻 t2 的 İ=0 伪事件：t - t2 ≤ 1e-9·(1+t2)


def default_atol(P, scale=1.0):
    """各分量的绝对容差（按 N 归一）。scale < 1 表示收紧。
    - s_N：1e-15；r_N：同下面的小量；
    - logi_N：1e-12（ln I 的绝对误差即 I 的相对误差）；
    - sq_N、iq_N、r_N、cinf_N、kq_N：1e-13·min(i0_N, 1/N)，远小于初始感染比例
      （西安约 7.7e-24，基准约 1.7e-16）；
    - J：1e-12（天）。"""
    small = 1e-13 * min(P.i0_N, 1.0 / P.N)
    a = np.array([1e-15, 1e-12, small, small, small, small, 1e-12, small])
    return a * scale


@dataclass
class Config:
    method: str = 'Radau'
    rtol: float = 1e-11
    atol_scale: float = 1.0
    max_step: float = 1.0
    t_max: float = 1.0e5            # 积分上限（天）
    eps_tail_rel: float = 1e-6      # ε_tail = eps_tail_rel·U(0)
    # ω > 0 的终止规则：'tail'（尾部误差上界 ≤ ε_tail，t→∞ 的区间估计）或
    # 'first_below_one'（退出后 I 首次由上方降到 1 时截断，假设此时传播结束；
    # 与 Zhou 等 2024 Remark 3.1 及第 3–7 章清零时间 t_end 的约定相同）
    return_endpoint: str = 'tail'
    e_tol: float = E_ABS_TOL
    keep_solutions: bool = False


def _event(fun, terminal, direction):
    fun.terminal = terminal
    fun.direction = direction
    return fun


class _Runner:
    def __init__(self, P, law, omega, model, wc, wq, cfg):
        if model not in ('return', 'immediate'):
            raise ValueError(model)
        if model == 'immediate' and P.Sq0 != 0.0:
            raise ValueError('立即返回对照模型要求 S_q(0) = 0')
        self.P, self.law, self.omega, self.model = P, law, omega, model
        self.wc = P.wc if wc is None else wc
        self.wq = P.wq if wq is None else wq
        self.cfg = cfg
        self.atol = default_atol(P, cfg.atol_scale)
        self.l_eta = math.log(P.eta_N)
        self.l_one = math.log(1.0 / P.N)
        self.sols = []
        self.phases = []

    # ---------- 右端 ----------
    def _derivs(self, s, i, sq, iq, r, c, q):
        P = self.P
        if self.model == 'return':
            ds, di, dsq, diq, dr = M.rhs_return(s, i, sq, iq, r, c, q, P, self.omega)
        else:
            ds, di, diq, dr = M.rhs_immediate(s, i, iq, r, c, q, P)
            dsq = 0.0
        _, F, Aq = M.flows_N(s, i, c, q, P)
        return ds, dsq, diq, dr, F, Aq

    def rhs_routine(self, t, y):
        P = self.P
        i = math.exp(y[ILI])
        ds, dsq, diq, dr, F, Aq = self._derivs(y[IS], i, y[ISQ], y[IIQ], y[IR], P.c0, P.q0)
        return [ds, M.log_growth_rate(y[IS], P.c0, P.q0, P), dsq, diq, dr, F, 0.0, Aq]

    def control_plateau(self, s):
        z = s / self.P.sc_N
        x = self.law(z)
        c, q = M.plateau_control(z, x, self.P)
        return z, x, c, q

    def rhs_plateau(self, t, y):
        P = self.P
        z, x, c, q = self.control_plateau(y[IS])
        ds, dsq, diq, dr, F, Aq = self._derivs(y[IS], P.eta_N, y[ISQ], y[IIQ], y[IR], c, q)
        return [ds, 0.0, dsq, diq, dr, F, M.cost_rate(x, z, P, self.wc, self.wq), Aq]

    # ---------- 积分 ----------
    def solve(self, fun, t0, y0, events, label):
        cfg = self.cfg
        self.phases.append(label)
        sol = solve_ivp(fun, (t0, cfg.t_max), y0, method=cfg.method, rtol=cfg.rtol,
                        atol=self.atol, max_step=cfg.max_step, events=events, dense_output=True)
        if sol.status == -1:
            raise RuntimeError(f'solve_ivp 失败：{sol.message}')
        self.sols.append(sol)
        return sol

    def u_N(self, y):
        return y[IS] + y[ISQ] if self.model == 'return' else y[IS]


def _fired(sol, k):
    """终止事件 k 是否在本段末尾触发。"""
    return sol.status == 1 and len(sol.t_events[k]) > 0 and sol.t_events[k][-1] == sol.t[-1]


def analytic_tail(P, model, S, I, C):
    """ω = 0 或立即返回、常规控制下由 (S, I, 累计感染 C) 补到 t→∞（人）。
    首次积分 I + κ(S - S_c ln S) = 常数，z∞ - ln z∞ = I/(κS_c) + z - ln z，z∞ < 1；
    t→∞ 新增感染 = λ_F (S - S_∞)，λ_F = F/(-Ṡ)（ω=0：β/(β+(1-β)q0)；立即返回：1）。"""
    if model == 'return':
        kappa = P.beta * (1 - P.q0) / (P.beta + (1 - P.beta) * P.q0)
        lamF = P.beta / (P.beta + (1 - P.beta) * P.q0)
    else:
        kappa, lamF = 1 - P.q0, 1.0
    Sc = P.S_c
    zT = S / Sc
    B = I / (kappa * Sc) + zT - math.log(zT)
    z_inf = float(-lambertw(-math.exp(-B), 0).real)
    g = lambda z: z - math.log(z) - B
    z_inf_b = brentq(g, 1e-300, 1.0 - 1e-15, xtol=1e-16, rtol=4 * np.finfo(float).eps) if B > 1 else float('nan')
    S_inf = Sc * z_inf
    return dict(S_inf=S_inf, C_inf=C + lamF * (S - S_inf), increment=lamF * (S - S_inf),
                lambertw_vs_brentq_rel=abs(z_inf - z_inf_b) / z_inf)


def run(P, law, omega=0.0, model='return', xi=0.0, wc=None, wq=None, cfg=None, alpha=0.5):
    """一条完整轨迹。
    P：params.Params；law：控制律名称（见 alloc.get_law）或可调用对象 x(z)；
    omega：回流率 ω（model='return'；ω=0 即稿件式 (2.1)）；model：'return' 或 'immediate'；
    xi：在 t2 释放的隔离易感者比例 ξ ∈ [0, 1]（只用于 model='return'）。
    返回 dict（人数以人计、时间以天计；JSON 可存）。"""
    cfg = cfg or Config()
    if isinstance(law, str):
        law_name = law
        law = AL.get_law(law, P, wc, wq, alpha)
    else:
        law_name = getattr(law, 'kind', getattr(law, '__name__', 'callable'))
    if model == 'immediate' and xi:
        raise ValueError('立即返回对照模型没有隔离易感者库存，不能释放')
    R = _Runner(P, law, omega, model, wc, wq, cfg)
    N, eta = P.N, P.eta
    out = dict(case=P.name, model=model, omega=omega, law=law_name, xi=xi,
               settings=dict(method=cfg.method, rtol=cfg.rtol, atol=R.atol.tolist(),
                             max_step=cfg.max_step, t_max=cfg.t_max, eps_tail_rel=cfg.eps_tail_rel,
                             e_tol=cfg.e_tol, return_endpoint=cfg.return_endpoint,
                             event_root_tol='scipy brentq, xtol=rtol=4·eps'))
    y0 = np.array([P.s0_N, math.log(P.i0_N), P.Sq0 / N, P.Iq0 / N, P.R0 / N, 0.0, 0.0, 0.0])
    U0_N = P.U0 / N
    t = 0.0

    # ---------------- 1. 常规阶段 ----------------
    triggered = False
    if P.I0 > eta:
        out.update(status='degenerate_I0_above_eta')
        return _finish(out, R, P, U0_N)
    if P.I0 == eta:
        if P.s0_N > P.sc_N:
            triggered, t1, y1 = True, 0.0, y0.copy()
            out['trigger_event_rel'] = 0.0
        else:
            out['note'] = 'I0 = η 且 S0 ≤ S_c：不触发'
    elif model == 'immediate' or omega == 0.0:
        if P.s0_N <= P.sc_N:
            out['note'] = 'S0 ≤ S_c：I 从一开始不增，不触发'
            y_post, t_post = y0, 0.0
        else:
            ev_trig = _event(lambda t, y: y[ILI] - R.l_eta, True, 1)
            ev_peak = _event(lambda t, y: y[IS] - P.sc_N, True, -1)
            sol = R.solve(R.rhs_routine, 0.0, y0, [ev_trig, ev_peak], 'routine')
            if _fired(sol, 0):
                triggered, t1, y1 = True, float(sol.t_events[0][-1]), sol.y_events[0][-1].copy()
            else:
                out['note'] = 'S 到达 S_c 时 I 仍低于 η：不触发'
                y_post, t_post = sol.y[:, -1].copy(), float(sol.t[-1])
                if sol.status == 0:
                    out.update(status='not_reached')
                    return _finish(out, R, P, U0_N)
    else:
        ev_trig = _event(lambda t, y: y[ILI] - R.l_eta, True, 1)
        sol = R.solve(R.rhs_routine, 0.0, y0, [ev_trig, _tail_event(R, U0_N)], 'routine')
        if _fired(sol, 0):
            triggered, t1, y1 = True, float(sol.t_events[0][-1]), sol.y_events[0][-1].copy()
        elif _fired(sol, 1):
            out.update(status='not_triggered', termination='tail')
            return _finish_tail(out, R, P, sol.y[:, -1], float(sol.t[-1]), U0_N)
        else:
            out.update(status='not_reached')
            return _finish(out, R, P, U0_N)

    if not triggered:
        out.update(status='not_triggered', t1=None, t2=None)
        return _post(out, R, P, y_post, t_post, U0_N, t_exit=None)

    # ---------------- 2. 阈值弧 ----------------
    out['trigger_event_rel'] = abs(math.expm1(y1[ILI] - R.l_eta))
    y1[ILI] = R.l_eta                    # 阈值弧上 I ≡ η（代数），其余状态连续衔接
    out.update(t1=t1, S_star=y1[IS] * N, Sq_t1=y1[ISQ] * N, C_t1=y1[ICF] * N, Kq_t1=y1[IKQ] * N)
    ev_exit = _event(lambda t, y: y[IS] - P.sc_N, True, -1)
    sol = R.solve(R.rhs_plateau, t1, y1, [ev_exit], 'plateau')
    if not _fired(sol, 0):
        out.update(status='not_reached', note='到积分上限仍未退出阈值弧')
        return _finish(out, R, P, U0_N)
    t2, y2 = float(sol.t_events[0][-1]), sol.y_events[0][-1].copy()
    out['exit_event_rel'] = abs(y2[IS] / P.sc_N - 1.0)
    xs, qs = [], []
    for yy in sol.y.T:
        z, x, c, q = R.control_plateau(yy[IS])
        xs.append(x)
        qs.append(q)
    out.update(t2=t2, dt=t2 - t1, J=y2[IJ], C_t2=y2[ICF] * N, Kq_t2=y2[IKQ] * N, Sq_t2=y2[ISQ] * N,
               arc_infections=(y2[ICF] - y1[ICF]) * N, arc_Kq=(y2[IKQ] - y1[IKQ]) * N,
               plateau_x_min=min(xs), plateau_x_max=max(xs), plateau_q_min=min(qs), plateau_q_max=max(qs))
    if model == 'return' and omega == 0.0:
        out['arc_infections_identity'] = (P.beta * (out['S_star'] - P.S_c)
                                          + (1 - P.beta) * P.gamma * eta * out['dt'])
        out['arc_Sq_new_identity'] = (1 - P.beta) * (out['S_star'] - P.S_c - P.gamma * eta * out['dt'])
    elif model == 'immediate':
        out['arc_infections_identity'] = out['S_star'] - P.S_c
        out['arc_Kq_identity'] = (1 - P.beta) / P.beta * (out['S_star'] - P.S_c - P.gamma * eta * out['dt'])
    # 释放（ω=0 的注记：R_e(t2+) = 1 + ξS_q(t2)/S_c）
    out['Sq_t2_over_Sc'] = y2[ISQ] / P.sc_N
    if xi:
        moved = xi * y2[ISQ]
        y2[IS] += moved
        y2[ISQ] -= moved
        out['Re_after_release'] = y2[IS] / P.sc_N
    out['status'] = 'ok'
    return _post(out, R, P, y2, t2, U0_N, t_exit=t2)


def _tail_event(R, U0_N):
    """尾部误差上界事件：g = ε_N γ (1 - u/s_c) - β c0 u i ≥ 0 ⇔ U < S_c 且 B ≤ ε_tail。"""
    P = R.P
    eps_N = R.cfg.eps_tail_rel * U0_N

    def g(t, y):
        u = R.u_N(y)
        return eps_N * P.gamma * (1.0 - u / P.sc_N) - P.beta * P.c0 * u * math.exp(y[ILI])
    return _event(g, True, 1)


def _post(out, R, P, y, t, U0_N, t_exit):
    """退出后（或未触发时）的常规阶段与终止。"""
    N, eta = P.N, P.eta
    growth = lambda t, y: M.log_growth_rate(y[IS], P.c0, P.q0, P)
    ev_max = _event(lambda t, y: growth(t, y), False, -1)      # I 的极大
    ev_min = _event(lambda t, y: growth(t, y), False, 1)       # I 的极小
    ev_one_up = _event(lambda t, y: y[ILI] - R.l_one, False, 1)
    exact_tail = (R.model == 'immediate' or R.omega == 0.0)
    if R.cfg.return_endpoint not in ('tail', 'first_below_one'):
        raise ValueError(R.cfg.return_endpoint)
    trunc = (not exact_tail) and R.cfg.return_endpoint == 'first_below_one'
    if exact_tail or trunc:
        ev_one_down = _event(lambda t, y: y[ILI] - R.l_one, y[ILI] > R.l_one, -1)
        events = [ev_max, ev_min, ev_one_up, ev_one_down]
    else:
        ev_one_down = _event(lambda t, y: y[ILI] - R.l_one, False, -1)
        events = [ev_max, ev_min, ev_one_up, ev_one_down, _tail_event(R, U0_N)]
    if exact_tail and not y[ILI] > R.l_one:
        sol = None          # I ≤ 1 且之后单调下降：直接解析补尾
        yT, T = y, t
    else:
        sol = R.solve(R.rhs_routine, t, y, events, 'post')
        yT, T = sol.y[:, -1], float(sol.t[-1])
    # 终止
    if sol is None:
        out['termination'] = 'analytic_tail_at_start'
    elif exact_tail:
        out['termination'] = 'clearance' if _fired(sol, 3) else 'not_reached'
        if _fired(sol, 3):
            out['clearance_event_abs'] = abs(N * math.exp(yT[ILI]) - 1.0)
    elif trunc:
        out['termination'] = 'first_below_one' if _fired(sol, 3) else 'not_reached'
        if _fired(sol, 3):
            out['clearance_event_abs'] = abs(N * math.exp(yT[ILI]) - 1.0)
            out['t_end'] = T
            out['C_t_end'] = yT[ICF] * N
    else:
        out['termination'] = 'tail' if _fired(sol, 4) else 'not_reached'
    out['T_term'] = T
    out['C_term'] = yT[ICF] * N
    out['J_total'] = yT[IJ]
    out['Kq_term'] = yT[IKQ] * N
    out['U_term'] = R.u_N(yT) * N
    out['S_term'] = yT[IS] * N
    out['I_term'] = N * math.exp(yT[ILI])
    if exact_tail:
        tail = analytic_tail(P, R.model, yT[IS] * N, N * math.exp(yT[ILI]), yT[ICF] * N)
        out.update(C_inf=tail['C_inf'], S_inf=tail['S_inf'], tail_increment=tail['increment'],
                   tail_lambertw_vs_brentq_rel=tail['lambertw_vs_brentq_rel'],
                   final_reliable=out['termination'] != 'not_reached')
        if out['termination'] == 'clearance':
            out['t_end'] = T
            out['C_t_end'] = out['C_term']
    else:
        U, I = R.u_N(yT) * N, N * math.exp(yT[ILI])
        if U < P.S_c:
            B = P.beta * P.c0 * U * I / (N * P.gamma * (1.0 - U / P.S_c))
        else:
            B = float('inf')
        if trunc:
            # 截断终点不是 t→∞ 的估计：只记录截断时 U 是否已低于 S_c（否则此后确定性模型中还有感染）
            out['U_below_Sc_at_end'] = bool(U < P.S_c)
            out['final_reliable'] = False
        else:
            out['tail_bound'] = B
            out['eps_tail'] = R.cfg.eps_tail_rel * P.U0
            out['final_reliable'] = out['termination'] == 'tail'
            out['final_estimate_lo'] = out['C_term']
            out['final_estimate_hi'] = out['C_term'] + B if out['final_reliable'] else None
    out['L_bound'] = P.L_bound
    if not exact_tail:
        out['excess_over_L_rel'] = (out['C_term'] - P.L_bound) / P.L_bound

    # 退出后峰值与回升
    if sol is not None and t_exit is not None:
        guard = T2_EVENT_GUARD * (1.0 + t_exit)
        tm = [(float(tt), N * math.exp(yy[ILI])) for tt, yy in zip(sol.t_events[0], sol.y_events[0])
              if tt - t_exit > guard]
        tn = [float(tt) for tt in sol.t_events[1] if tt - t_exit > guard]
        down = [float(tt) for tt in sol.t_events[3]]
        up = [float(tt) for tt in sol.t_events[2]]
        n_guarded = sum(1 for tt in list(sol.t_events[0]) + list(sol.t_events[1]) if tt - t_exit <= guard)
        e_int = max((I / eta - 1.0 for _, I in tm), default=-math.inf)
        e_end = out['I_term'] / eta - 1.0
        e = max(0.0, e_int, e_end)      # 端点 t2 处 I = η
        if e_int > R.cfg.e_tol or e_end > R.cfg.e_tol:
            crossing = 'crossed'
        elif (e_int < -R.cfg.e_tol or not tm) and e_end < -R.cfg.e_tol:
            crossing = 'not_crossed'
        else:
            crossing = 'undetermined'
        t_below = down[0] if down else None
        if t_below is not None:          # 首次 I < 1 时的累计感染（旧实现的终止口径，只作对照）
            out['C_below_one'] = float(sol.sol(t_below)[ICF]) * N
        regrow = t_below is not None and any(tt > t_below for tt in tn)
        peaks_after = [I for tt, I in tm if t_below is not None and tt > t_below]
        out.update(post_interior_max=[dict(t=tt, I=I) for tt, I in tm], post_interior_min_t=tn,
                   n_guarded_events=n_guarded, e=e, e_interior=e_int if tm else None, e_end=e_end,
                   crossing=crossing, below_one_time=t_below,
                   regrowth_after_below_one=regrow,
                   regrowth_peak_I=max(peaks_after) if peaks_after else None,
                   recrossed_one=t_below is not None and any(tt > t_below for tt in up),
                   max_I_after_exit=eta * (1.0 + e))
    return _finish(out, R, P, U0_N)


def _finish_tail(out, R, P, yT, T, U0_N):
    N = P.N
    U, I = R.u_N(yT) * N, N * math.exp(yT[ILI])
    B = P.beta * P.c0 * U * I / (N * P.gamma * (1.0 - U / P.S_c)) if U < P.S_c else float('inf')
    out.update(T_term=T, C_term=yT[ICF] * N, tail_bound=B, final_reliable=True,
               final_estimate_lo=yT[ICF] * N, final_estimate_hi=yT[ICF] * N + B)
    return _finish(out, R, P, U0_N)


def _finish(out, R, P, U0_N):
    """恒等式与质量残差（在所有求解步上）；转成可存 JSON 的类型。"""
    res_id, res_mass = 0.0, 0.0
    for sol in R.sols:
        Y = sol.y
        u = Y[IS] + Y[ISQ] if R.model == 'return' else Y[IS]
        res_id = max(res_id, float(np.max(np.abs(Y[ICF] - (U0_N - u))) / U0_N))
        i = np.exp(Y[ILI])
        mass = Y[IS] + i + Y[ISQ] + Y[IIQ] + Y[IR] - 1.0
        res_mass = max(res_mass, float(np.max(np.abs(mass))))
    out['identity_residual_rel'] = res_id      # |cinf - (U(0)-U)|/U(0) 的最大值
    out['mass_residual_abs'] = res_mass        # |s+i+s_q+i_q+r-1| 的最大值（按 N 归一）
    out['n_steps'] = int(sum(len(s.t) for s in R.sols))
    out['phases'] = list(R.phases)
    if R.cfg.keep_solutions:
        out['_sols'] = R.sols
    return {k: _plain(v) for k, v in out.items()}


def _plain(v):
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, dict):
        return {k: _plain(w) for k, w in v.items()}
    if isinstance(v, (list, tuple)):
        return [_plain(w) for w in v]
    return v
