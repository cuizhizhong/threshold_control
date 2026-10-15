"""第二条计算路径：完整五仓室方程（式 2.1）与累计流量的独立积分，输入按名义轨迹预先生成的
时间开环控制。阈值弧上 I 自由演化，不重置到 η，不按实时状态纠偏。

名义时钟（只用名义模型，不读完整方程的状态）：阈值弧上 dz/dτ = -(c0η/N)(x(z)z - z̄)，z(0) = z*，
按 Policy 的分段点逐段求解——显式律（x = A + B/z）用闭式，其余（成本最优控制）用 DOP853
（nominal_rtol、nominal_atol）求稠密解，段末事件 z = 段下端。控制
    c(t) = c0·x(z_nom(t - t1))，q(t) = 1 - (1-q0)/(x·z_nom(t - t1))
只是时间的函数；t1 取完整方程常规阶段的触发事件时刻，z_nom 从 Lambert W 的 z* 出发。
在名义退出时刻 t2 = t1 + Σ段时长 恢复 (c0, q0)，此后不释放隔离易感者（S_q 保持不返回）。

复制来源：analytic_tail 取自 research/return-effects bb52b96 的 r7_return/simulate.py（ω = 0 分支，
blob c088330c；与 91123ea 中 2dae861e 的 ω = 0 部分相同）。其余为新写：r7 的事件法在阈值弧上用代数
令 I ≡ η 并按状态反馈求控制，不满足本步“开环、不重置 I”的要求，未复用。开环名义时钟与分段的
思路参照 reproducibility/joint_extra/core.py 的 nominal_time 与 full_run（原文件未改动、未运行）。

状态向量（各阶段相同，阶段之间连续衔接，不重置 S_q、I_q、R）：
    y = [s, ln i, s_q, i_q, r, cI, cIq, ∫i dt, J, J_c, J_q]
    s、i、s_q、i_q、r 按 N 归一；cI = ∫β c(1-q) s i dt（进入 I），cIq = ∫β c q s i dt（进入 I_q），
    二者是独立积分的流量，不由 S0 + S_q(0) - S - S_q 定义；J、J_c、J_q 以天计（只在阈值弧上非零）。
感染者用 ln i 表示：保证 I 的正性与相对精度（西安 i0 ≈ 7.65e-11）。

事件（solve_ivp 在连续解上用 brentq 定位，求根容差由 scipy 内部设定，没有单独的事件容差参数）：
    常规阶段：ln i = ln θ 方向向上（终止）= 触发 t1；另设 s = s_c 方向向下（终止）作未触发的保护。
    阈值弧：s = s_c 方向向下（不终止），只记录实际穿越时刻，与名义 t2 对照。
    退出后：ln i = ln(1/N) 方向向下（终止）= 清零 t_end（只在退出后检测）；ln i = ln θ 方向向上
    （不终止）记录是否越过阈值。
t→∞ 由 t_end 处的 (S, I) 按定理 3.5 的首次积分解析补尾（Lambert W k = 0，brentq 交叉核对）。
"""
import math
from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp, quad
from scipy.optimize import brentq
from scipy.special import lambertw

import allocation as AL
import model as M

IS, ILI, ISQ, IIQ, IR, ICI, ICIQ, IINT, IJ, IJC, IJQ = range(11)
STATE_NAMES = ('s', 'ln_i', 'sq', 'iq', 'r', 'cI', 'cIq', 'int_i', 'J', 'Jc', 'Jq')


@dataclass
class Config:
    method: str = 'DOP853'
    rtol: float = 1e-12
    atol_scale: float = 1.0
    max_step: float = 0.5          # 天
    nominal_rtol: float = 1e-13
    nominal_atol: float = 1e-15    # z 坐标（量级 1–5）
    t_max: float = 1.0e4           # 积分上限（天）
    dense_sub: int = 8             # 诊断时每个积分步内的等分采样数


def default_atol(P, scale=1.0):
    """各分量的绝对容差（按 N 归一；J 类以天计）。scale < 1 表示收紧。
    s：1e-15；ln i：1e-12（即 I 的相对误差）；s_q、i_q、r、cI、cIq、∫i：1e-13·min(i0, 1/N)
    （远小于初始感染比例：西安约 7.7e-24，基准约 1.7e-16）；J、J_c、J_q：1e-13 d。"""
    small = 1e-13 * min(P.i0_N, 1.0 / P.N)
    a = np.array([1e-15, 1e-12, small, small, small, small, small, small, 1e-13, 1e-13, 1e-13])
    return a * scale


def _ev(fun, terminal, direction):
    fun.terminal = terminal
    fun.direction = direction
    return fun


# ---------------------------------------------------------------- 名义时钟
class NominalSegment:
    """阈值弧的一段：z 从 z_hi 降到 z_lo，τ ∈ [0, duration]。"""

    def __init__(self, pol, lo, hi, cfg):
        P = pol.P
        self.lo, self.hi = lo, hi
        k = P.c0 * P.eta / P.N
        lf = pol.linear_form(lo, hi)
        self.linear = lf
        if lf is not None:
            A, B = lf
            if A > 0.0:
                z_eq = (P.z_bar - B) / A
                self.duration = math.log((hi - z_eq) / (lo - z_eq)) / (k * A)
                self._z = lambda tau, z_eq=z_eq, A=A: z_eq + (hi - z_eq) * np.exp(-k * A * np.asarray(tau))
            else:
                rate = k * (B - P.z_bar)
                self.duration = (hi - lo) / rate
                self._z = lambda tau, rate=rate: hi - rate * np.asarray(tau)
            self.method = 'closed_form'
        else:
            est = quad(lambda z: 1.0 / (k * (pol.x_on(z, lo, hi) * z - P.z_bar)), lo, hi,
                       epsabs=0.0, epsrel=1e-13, limit=500)[0]
            ev = _ev(lambda t, y: y[0] - lo, True, -1)
            sol = solve_ivp(lambda t, y: [-k * (pol.x_on(y[0], lo, hi) * y[0] - P.z_bar)], (0.0, 1.5 * est + 1.0),
                            [hi], method='DOP853', rtol=cfg.nominal_rtol, atol=cfg.nominal_atol,
                            max_step=max(est / 200.0, 1e-6), events=ev, dense_output=True)
            if sol.status != 1 or not len(sol.t_events[0]):
                raise RuntimeError('名义时钟未到达段下端')
            self.duration = float(sol.t_events[0][0])
            self.duration_quad = est
            self._sol = sol
            self._z = lambda tau: sol.sol(np.asarray(tau))[0]
            self.method = 'DOP853'
        self.pol = pol

    def z(self, tau):
        tau = np.clip(tau, 0.0, self.duration)
        return np.clip(self._z(tau), self.lo, self.hi)

    def control(self, tau):
        """名义控制 (c, q, z_nom, x)。"""
        P = self.pol.P
        zn = float(self.z(tau))
        x = self.pol.x_on(zn, self.lo, self.hi)
        c, q = M.plateau_control(zn, x, P)
        return c, q, zn, x


def nominal_clock(pol, cfg):
    """自 z* 到 1 的名义分段（时间顺序：z 从大到小）。"""
    segs = [NominalSegment(pol, lo, hi, cfg) for lo, hi in reversed(pol.segments())]
    return segs


# ---------------------------------------------------------------- 完整方程
class _Runner:
    def __init__(self, pol, cfg):
        self.pol, self.P, self.cfg = pol, pol.P, cfg
        self.atol = default_atol(pol.P, cfg.atol_scale)
        self.phases = []      # (label, sol, control(t)->(c,q), t_start, t_stop)

    def rhs(self, control):
        P, wc, wq = self.P, self.pol.wc, self.pol.wq

        def f(t, y):
            c, q = control(t)
            s, i = y[IS], math.exp(y[ILI])
            ds, di, dsq, diq, dr = M.rhs_N(s, i, y[ISQ], y[IIQ], y[IR], c, q, P)
            _, into_I, into_Iq, _ = M.flows_N(s, i, c, q, P)
            uc, uq = M.intensities(c, q, P)
            return [ds, M.log_growth_rate(s, c, q, P), dsq, diq, dr, into_I, into_Iq, i,
                    M.cost_rate(uc, uq, wc, wq), uc, uq]
        return f

    def solve(self, label, control, t0, t1, y0, events=None):
        cfg = self.cfg
        sol = solve_ivp(self.rhs(control), (t0, t1), y0, method=cfg.method, rtol=cfg.rtol, atol=self.atol,
                        max_step=cfg.max_step, events=events, dense_output=True)
        if sol.status == -1:
            raise RuntimeError(f'solve_ivp 失败：{sol.message}')
        self.phases.append((label, sol, control, float(sol.t[0]), float(sol.t[-1])))
        return sol


def analytic_tail(P, S, I, C):
    """常规控制、无回流下由 (S, I, 累计感染 C) 补到 t→∞（人）。首次积分 I + κ0(S - S_c ln S) = 常数，
    z∞ - ln z∞ = I/(κ0 S_c) + z - ln z，z∞ < 1；t→∞ 新增感染 = λ_F(S - S_∞)。"""
    Sc = P.S_c
    zT = S / Sc
    B = I / (P.kappa0 * Sc) + zT - math.log(zT)
    z_inf = float(-lambertw(-math.exp(-B), 0).real)
    z_inf_b = brentq(lambda z: z - math.log(z) - B, 1e-300, 1.0 - 1e-15, xtol=1e-16,
                     rtol=4 * np.finfo(float).eps) if B > 1 else float('nan')
    S_inf = Sc * z_inf
    return dict(S_inf=S_inf, C_inf=C + P.lamF * (S - S_inf), increment=P.lamF * (S - S_inf),
                lambertw_vs_brentq_rel=abs(z_inf - z_inf_b) / z_inf)


def run(pol, cfg=None, c_scale=1.0):
    """一条完整轨迹（开环）。pol：state_integrals.Policy。返回 dict（人数以人计、时间以天计）。
    c_scale ≠ 1 只用于检验开环性（tests/test_simulate.py）：阈值弧上的接触率乘以该因子、隔离比例不变，
    I 应当偏离 η——若实现中把 I 重置到 η，偏离就不会出现。"""
    cfg = cfg or Config()
    P = pol.P
    R = _Runner(pol, cfg)
    N, eta = P.N, P.eta
    l_eta, l_one = math.log(P.eta_N), math.log(1.0 / N)
    routine = lambda t: (P.c0, P.q0)
    out = dict(case=P.name, law=pol.name, weights=[pol.wc, pol.wq], kappa=pol.kappa, c_scale=c_scale,
               capacity=None if pol.cap is None else dict(c_min=pol.cap.c_min, q_cap=pol.cap.q_cap),
               settings=dict(method=cfg.method, rtol=cfg.rtol, atol=R.atol.tolist(), max_step=cfg.max_step,
                             nominal_rtol=cfg.nominal_rtol, nominal_atol=cfg.nominal_atol, t_max=cfg.t_max,
                             event_root='scipy solve_ivp 内部 brentq（无单独事件容差参数）'))
    y0 = np.array([P.s0_N, math.log(P.i0_N), P.Sq0 / N, P.Iq0 / N, P.R0 / N, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    # 1. 常规阶段
    ev_trig = _ev(lambda t, y: y[ILI] - l_eta, True, 1)
    ev_guard = _ev(lambda t, y: y[IS] - P.sc_N, True, -1)
    sol = R.solve('routine', routine, 0.0, cfg.t_max, y0, [ev_trig, ev_guard])
    if not len(sol.t_events[0]):
        raise RuntimeError('常规阶段未触发')
    t1, y1 = float(sol.t_events[0][0]), sol.y_events[0][0].copy()
    out.update(t1=t1, S_t1=y1[IS] * N, I_t1=math.exp(y1[ILI]) * N, n_trigger_events=len(sol.t_events[0]),
               trigger_dlnI=M.log_growth_rate(y1[IS], P.c0, P.q0, P))

    # 2. 阈值弧（开环）
    segs = nominal_clock(pol, cfg)
    y, t = y1, t1
    seg_rec, exit_cross = [], []
    for sg in segs:
        if c_scale == 1.0:
            ctrl = (lambda tt, sg=sg, ts=t: sg.control(tt - ts)[:2])
        else:
            ctrl = (lambda tt, sg=sg, ts=t: (lambda c, q: (c * c_scale, q))(*sg.control(tt - ts)[:2]))
        ev_exit = _ev(lambda tt, yy: yy[IS] - P.sc_N, False, -1)
        sl = R.solve('plateau', ctrl, t, t + sg.duration, y, [ev_exit])
        exit_cross += [float(v) for v in sl.t_events[0]]
        seg_rec.append(dict(z_hi=sg.hi, z_lo=sg.lo, t_start=t, duration=sg.duration, method=sg.method,
                            duration_quad=getattr(sg, 'duration_quad', None), linear_form=sg.linear))
        sg.t_start = t
        y, t = sl.y[:, -1].copy(), t + sg.duration
    t2, y2 = t, y
    out.update(t2=t2, dt=t2 - t1, segments=seg_rec, S_t2=y2[IS] * N, I_t2=math.exp(y2[ILI]) * N,
               exit_S_error=(y2[IS] - P.sc_N) * N, exit_I_error=(math.exp(y2[ILI]) - P.eta_N) * N,
               exit_actual_crossings=exit_cross,
               J=y2[IJ] - y1[IJ], Jc=y2[IJC] - y1[IJC], Jq=y2[IJQ] - y1[IJQ],
               arc_infections=(y2[ICI] + y2[ICIQ] - y1[ICI] - y1[ICIQ]) * N,
               arc_into_I=(y2[ICI] - y1[ICI]) * N,
               arc_Sq_new=(y2[ISQ] - y1[ISQ]) * N,
               Sq_t1=y1[ISQ] * N, Sq_t2=y2[ISQ] * N, Iq_t2=y2[IIQ] * N)
    S_star = pol.start['S_star']
    out['arc_infections_identity'] = P.beta * (S_star - P.S_c) + P.gamma * eta * (1 - P.beta) * out['dt']
    out['arc_Sq_new_identity'] = (1 - P.beta) * (S_star - P.S_c - P.gamma * eta * out['dt'])

    # 3. 退出后（永久常规，不释放）
    ev_clear = _ev(lambda tt, yy: yy[ILI] - l_one, True, -1)
    ev_over = _ev(lambda tt, yy: yy[ILI] - l_eta, False, 1)
    sl = R.solve('post', routine, t2, cfg.t_max, y2, [ev_clear, ev_over])
    if not len(sl.t_events[0]):
        raise RuntimeError('退出后未清零')
    t_end, ye = float(sl.t_events[0][0]), sl.y_events[0][0]
    I_end = math.exp(ye[ILI]) * N
    C_end = (ye[ICI] + ye[ICIQ]) * N
    tail = analytic_tail(P, ye[IS] * N, I_end, C_end)
    out.update(t_end=t_end, clearance_I_error=I_end - 1.0, n_clearance_events=len(sl.t_events[0]),
               clearance_dlnI=M.log_growth_rate(ye[IS], P.c0, P.q0, P),
               post_upcross_eta=[float(v) for v in sl.t_events[1]],
               total_infections_to_clearance=C_end, cI_end=ye[ICI] * N, cIq_end=ye[ICIQ] * N,
               S_end=ye[IS] * N, Sq_end=ye[ISQ] * N, Iq_end=ye[IIQ] * N, R_end=ye[IR] * N,
               total_infections_inf=tail['C_inf'], S_inf=tail['S_inf'], tail_increment=tail['increment'],
               tail_lambertw_vs_brentq_rel=tail['lambertw_vs_brentq_rel'])
    out.update(_diagnostics(R, pol, segs, t1, t2, t_end))
    out['n_steps'] = int(sum(len(ph[1].t) for ph in R.phases))
    out['_runner'] = R
    return out


# ---------------------------------------------------------------- 诊断
def _samples(sol, t_a, t_b, sub):
    ts = sol.t[(sol.t >= t_a) & (sol.t <= t_b)]
    ts = np.unique(np.r_[t_a, ts, t_b])
    fine = [np.linspace(a, b, sub + 1)[:-1] for a, b in zip(ts[:-1], ts[1:])]
    tt = np.unique(np.r_[np.concatenate(fine) if fine else [], t_b])
    return tt, sol.sol(tt)


def _diagnostics(R, pol, segs, t1, t2, t_end):
    P, cfg = R.P, R.cfg
    N, eta = P.N, P.eta
    s0q0 = P.s0_N + P.Sq0 / N
    mass = ident = icum = sqid = 0.0
    min_comp = math.inf
    plateau_dev = 0.0
    feas = dict(c_below_lo=0.0, c_above_hi=0.0, q_below_q0=0.0, q_above_cap=0.0, balance=0.0,
                c_above_c0=0.0)
    q_cap = 1.0 if pol.cap is None else pol.cap.q_cap
    peak_tot = dict(value=-math.inf)
    peak_I = dict(value=-math.inf)
    seg_iter = iter(segs)
    for label, sol, control, ta, tb in R.phases:
        if label == 'post':
            tb = min(tb, t_end)
        tt, Y = _samples(sol, ta, tb, cfg.dense_sub)
        i = np.exp(Y[ILI])
        comp = np.vstack([Y[IS], i, Y[ISQ], Y[IIQ], Y[IR]])
        mass = max(mass, float(np.max(np.abs(comp.sum(axis=0) - 1.0))) * N)
        min_comp = min(min_comp, float(np.min(comp)) * N)
        ident = max(ident, float(np.max(np.abs(Y[ICI] + Y[ICIQ] - (s0q0 - Y[IS] - Y[ISQ])))) / s0q0)
        icum = max(icum, float(np.max(np.abs(Y[ICI] - (i - P.i0_N + P.gamma * Y[IINT])))) / s0q0)
        sqid = max(sqid, float(np.max(np.abs(Y[ISQ] - P.Sq0 / N - (1 - P.beta) / P.beta * Y[ICIQ]))) / s0q0)
        if label == 'plateau':
            sg = next(seg_iter)
            plateau_dev = max(plateau_dev, float(np.max(np.abs(i * N - eta))))
            for t in tt:
                c, q, zn, x = sg.control(t - sg.t_start)
                xl, xh, _, _ = AL.x_bounds_raw(zn, pol.x_min, pol.h)
                feas['c_below_lo'] = max(feas['c_below_lo'], (P.c0 * xl - c) / P.c0)
                feas['c_above_hi'] = max(feas['c_above_hi'], (c - P.c0 * xh) / P.c0)
                feas['c_above_c0'] = max(feas['c_above_c0'], (c - P.c0) / P.c0)
                feas['q_below_q0'] = max(feas['q_below_q0'], P.q0 - q)
                feas['q_above_cap'] = max(feas['q_above_cap'], q - q_cap)
                feas['balance'] = max(feas['balance'], abs(P.beta * c * (1 - q) * zn * P.sc_N / P.gamma - 1.0))
        # 现存感染 I + I_q 与 I 的峰值：采样最大值，再在导数变号处用 brentq 加密
        for kind, rec in (('tot', peak_tot), ('I', peak_I)):
            v = (i + Y[IIQ]) if kind == 'tot' else i
            k = int(np.argmax(v))
            cands = [(float(v[k]), float(tt[k]))]

            def deriv(t, sol=sol, control=control, kind=kind):
                y = sol.sol(t)
                c, q = control(t)
                s, ii = y[IS], math.exp(y[ILI])
                if kind == 'tot':
                    return P.beta * c * s * ii - P.gamma * ii - P.delta_q * y[IIQ]
                return P.beta * c * (1 - q) * s * ii - P.gamma * ii
            if label != 'plateau' or kind == 'tot':
                dv = np.array([deriv(t) for t in tt])
                for a, b, ga, gb in zip(tt[:-1], tt[1:], dv[:-1], dv[1:]):
                    if ga > 0 >= gb:
                        tr = brentq(deriv, a, b, xtol=1e-12, rtol=1e-14)
                        y = sol.sol(tr)
                        val = math.exp(y[ILI]) + (y[IIQ] if kind == 'tot' else 0.0)
                        cands.append((float(val), float(tr)))
            val, tm = max(cands)
            if val > rec['value']:
                rec.update(value=val, t=tm, phase=label)
    return dict(mass_residual_persons=mass, min_compartment_persons=min_comp,
                identity_residual_rel=ident, Icum_identity_residual_rel=icum, Sq_identity_residual_rel=sqid,
                plateau_abs_dev=plateau_dev, plateau_rel_dev=plateau_dev / eta,
                feasibility=feas,
                peak_I_plus_Iq=peak_tot['value'] * N, t_peak_I_plus_Iq=peak_tot['t'],
                peak_I_plus_Iq_phase=peak_tot['phase'], peak_I_plus_Iq_over_eta=peak_tot['value'] * N / eta,
                max_I=peak_I['value'] * N, t_max_I=peak_I['t'], max_I_over_eta_minus_1=peak_I['value'] * N / eta - 1.0)
