"""第一条计算路径：闭式与对 S 的一维积分（无回流模型 2.1）。

复制来源：research/return-effects bb52b96 的 r7_return/endpoints.py（blob 345eb9f1，与 91123ea 相同）
的无回流部分（启动状态、分段 Simpson 与 quad 交叉核对），扩展为：一般权重与 κ、能力约束、
线性强度 J_c、J_q、启动前的 t1（写法取自 reproducibility/joint_extra/core.py 的 basics，原文件未改动）、
退出后的 S_end、清零时间与 t→∞ 补尾、各单控制的闭式（定理 3.1–3.6、4.3、式 4.14、附录 B）。

终点与约定（稿件第 2.4 节）：累计新增感染不含初始感染者；“计至清零”指各控制自身的
t_end（退出后 I 由上方降到 1）；“t→∞”按定理 3.5 的 S_∞ 解析补尾，二者是不同的量；
新增隔离易感者人数与 J、J_c、J_q 只计阈值控制期 [t1, t2]。

阈值弧上（式 4.4、4.5、5.1），z = S/S_c，x = c/c0：
    dt   = -N dz / (c0 η (x z - z̄))，                      Δt = N/(c0η) ∫_1^{z*} dz/(xz - z̄)
    J    = N/(c0η) ∫ [w_c(1-x)² + w_q(1-1/(xz))²]/(xz - z̄) dz
    J_c  = N/(c0η) ∫ (1-x)/(xz - z̄) dz，J_q = N/(c0η) ∫ (1-1/(xz))/(xz - z̄) dz
    F dt = β S_c x z/(xz - z̄) dz（总新增感染），A_q dt = (1-β) S_c (xz - (1-q0))/(xz - z̄) dz（新增隔离易感者）
恒等式（定理 4.5(iii)）：控制期感染 = β(S*-S_c) + γη(1-β)Δt，新增隔离 = (1-β)(S*-S_c-γηΔt)。
"""
import math

import numpy as np
from scipy.integrate import simpson, quad
from scipy.optimize import brentq
from scipy.special import lambertw

import allocation as AL

DEFAULT_NZ = 4001
QUAD_EPSREL = 1e-12
SEG_CLAMP_REL = 1e-12      # 在分段内求控制律时向段内收缩的相对距离（避开间断点两侧的并列）


# ---------------------------------------------------------------- 启动状态与 t1
def start_state(P):
    """常规轨迹 I(S) = I0 + κ0[(S0-S) + S_c ln(S/S0)] 首次达到 η 时的 S*（定理 3.1）。
    Lambert W 的 k = -1 分支为主结果，brentq 在 (S_c, S0) 上交叉核对。"""
    S0, Sc, I0, eta, kappa = P.S0, P.S_c, P.I0, P.eta, P.kappa0
    out = dict(S_c=Sc, kappa0=kappa)
    if not S0 > Sc:
        return dict(out, status='degenerate', reason='S0 <= S_c：I 从一开始就不增，不触发')
    I_peak = I0 + kappa * (S0 - Sc + Sc * math.log(Sc / S0))
    out['I_peak'] = I_peak
    if not (0.0 < I0 < eta < I_peak):
        reason = ('I0 >= η：不是由下方首次达到 η' if I0 >= eta else
                  'η >= I_max^0：常规轨迹不触发' if eta >= I_peak else 'I0 <= 0')
        return dict(out, status='degenerate', reason=reason)
    z0 = S0 / Sc
    A = z0 - math.log(z0) - (eta - I0) / (kappa * Sc)
    z_eta = -math.exp(-A)                       # 式 (3.1) 的 z_η
    w = lambertw(z_eta, k=-1)
    z_star = float(-w.real)
    S_star = Sc * z_star
    Ifun = lambda S: I0 + kappa * ((S0 - S) + Sc * math.log(S / S0)) - eta
    S_b = brentq(Ifun, Sc * (1.0 + 1e-14), S0, xtol=1e-13 * S0, rtol=4 * np.finfo(float).eps, maxiter=500)
    return dict(out, status='ok', z_eta=z_eta, z_star=z_star, S_star=S_star, lambertw_imag=float(w.imag),
                S_star_brentq=S_b, lambertw_vs_brentq_rel=abs(S_star - S_b) / S_star,
                residual_I=Ifun(S_star), q_max=1.0 - (1.0 - P.q0) / z_star)


def t1_quadrature(P, S_star):
    """t1 = (1/β1^0)∫_{S*}^{S0} dS/(S I(S))（式 3.2）。以 loss = S0 - S = scale·(e^w - 1) 换元，
    scale = i0/(κ0 - ρ1/S0)（归一化），消去 I 很小时的对数型近奇性。"""
    s0, i0 = P.s0_N, P.i0_N
    k, rho = P.kappa0, P.rho1 / P.N
    loss_star = s0 - S_star / P.N
    ix = lambda loss: i0 + k * loss + rho * math.log1p(-loss / s0)
    scale = i0 / (k - rho / s0)
    wmax = math.log1p(loss_star / scale)

    def integrand(w):
        u = scale * math.expm1(w)
        return scale * math.exp(w) / (P.c0 * P.a * (s0 - u) * ix(u))
    val, err = quad(integrand, 0.0, wmax, epsabs=0.0, epsrel=1e-13, limit=500)
    return val, err


# ---------------------------------------------------------------- 退出后
def post_exit(P):
    """从 (S_c, η) 恢复常规后（定理 3.5）：S_end（I = 1）、S_∞、退出到清零的时间。
    Lambert W 的 k = 0 分支为主结果，brentq 交叉核对。"""
    Sc, eta, rho = P.S_c, P.eta, P.rho1
    Ipost = lambda S: eta + P.kappa0 * (Sc - S) + rho * math.log(S / Sc)   # 附录 A.2 式 (eq:s1:post-orbit)
    out = {}
    for key, level in (('S_end', 1.0), ('S_inf', 0.0)):
        w = lambertw(-math.exp(-1.0 - (eta - level) / rho), k=0)
        Sw = float(-Sc * w.real)
        Sb = brentq(lambda S: Ipost(S) - level, Sc * 1e-12, Sc * (1.0 - 1e-15), xtol=1e-14 * Sc,
                    rtol=4 * np.finfo(float).eps, maxiter=500)
        out[key] = Sw
        out[key + '_brentq'] = Sb
        out[key + '_lambertw_vs_brentq_rel'] = abs(Sw - Sb) / Sw
    tail, err = quad(lambda S: 1.0 / (P.beta1_0 * S * Ipost(S)), out['S_end'], Sc,
                     epsabs=0.0, epsrel=1e-13, limit=500)
    out.update(tail_time=tail, tail_time_err=err)
    return out


# ---------------------------------------------------------------- 控制律与分段
class Policy:
    """阈值弧上的一个控制律 x(z)，连同其分段点（结构变化点与能力折点）。
    name ∈ {'q_only','c_only','alpha','opt','cap_upper','cap_lower'}；cap 为 params.Capacity 或 None；
    wc、wq 为成本权重（'opt' 的优化目标与 J 的计算都用它）；kappa 为时长乘子（只用于 'opt'）。"""

    def __init__(self, P, name, cap=None, wc=None, wq=None, kappa=0.0, alpha=0.5, N_z=DEFAULT_NZ):
        self.P, self.name, self.cap, self.alpha, self.kappa = P, name, cap, alpha, float(kappa)
        self.wc = P.wc if wc is None else float(wc)
        self.wq = P.wq if wq is None else float(wq)
        self.start = start_state(P)
        if self.start['status'] != 'ok':
            raise ValueError(f"不触发：{self.start['reason']}")
        self.z_star = self.start['z_star']
        self.x_min, self.h = AL.cap_factors(P, cap)
        AL.x_bounds_raw(self.z_star, self.x_min, self.h)        # 式 (4.7) 不成立时抛出 Infeasible
        self.law = AL.get_law(name, P, cap, self.wc, self.wq, self.kappa, alpha)
        self.kinks = AL.geometric_kinks(P, cap, self.z_star)
        self.structure = None
        breaks = list(self.kinks)
        if name == 'opt':
            zb, wc_, wq_, ka = P.z_bar, self.wc, self.wq, self.kappa
            xm, hh = self.x_min, self.h

            def poly_at_end(z, end):
                lo, hi, _, _ = AL.x_bounds_raw(z, xm, hh)
                return float(np.polyval(AL.stationary_poly_x(z, zb, wc_, wq_, ka), hi if end == 'hi' else lo))
            self.structure = AL.scan_structure(self.law.full, 1.0, self.z_star, N_z, poly_at_end, self.kinks)
            breaks += [b['z'] for b in self.structure['breakpoints']]
            breaks += list(self.structure['steep_points'])
            # 间断点与陡峭点两侧用分级网格（可能是立方根型尖点；连续切换与能力折点不必）
            self.graded = [b['z'] for b in self.structure['breakpoints'] if not b['continuous']]
            self.graded += list(self.structure['steep_points'])
        else:
            self._check_explicit_feasible(N_z)
            self.graded = []
        self.breaks = sorted(b for b in set(breaks) if 1.0 < b < self.z_star)
        self.nodes = [1.0] + self.breaks + [self.z_star]

    def _check_explicit_feasible(self, N_z):
        """显式律须落在允许区间内（能力约束下仅隔离、仅减少接触或 α 族可能不可行）。"""
        zz = np.linspace(1.0, self.z_star, min(N_z, 2001))[1:]
        for z in zz:
            lo, hi, _, _ = AL.x_bounds_raw(float(z), self.x_min, self.h)
            x = self.law(float(z))
            if x < lo * (1 - 1e-13) or x > hi * (1 + 1e-13):
                raise AL.Infeasible(f'{self.name} 在 z = {z} 处 x = {x} 不在 [{lo}, {hi}] 内')

    def segments(self):
        """[(z_lo, z_hi)]，自低到高。"""
        return list(zip(self.nodes[:-1], self.nodes[1:]))

    def x_on(self, z, lo, hi):
        """在分段 (lo, hi) 内求 x(z)。成本最优控制律先把 z 收缩到段内 SEG_CLAMP_REL·hi 以内
        （保证间断两侧取本段的分支），再把所得 x 投影到 z 处的允许区间（收缩造成的偏差约 1e-12，
        投影保证控制严格满足界限）。显式律直接求值。"""
        z = float(z)
        if self.name != 'opt':
            return self.law(z)
        if z <= 1.0:
            return 1.0                       # 退出状态 S = S_c：允许区间退化为 {c0}
        d = SEG_CLAMP_REL * hi
        zc = min(max(z, lo + d), hi - d) if hi - lo > 2 * d else 0.5 * (lo + hi)
        x = self.law(zc)
        if z > 1.0:
            xl, xh, _, _ = AL.x_bounds_raw(z, self.x_min, self.h)
            x = min(max(x, xl), xh)
        return x

    def x(self, z):
        """全局求值（不分段）；z ≤ 1 时退化为 1。"""
        return self.law(float(z))

    def linear_form(self, lo, hi):
        return AL.linear_form(self.name, self.P, self.cap, lo, hi, self.alpha)


# ---------------------------------------------------------------- 分段 Simpson 与 quad
ADAPT_TOL = 1e-12          # 每片 Richardson 误差估计 |S_n - S_{n/2}|/15 的相对判据
ADAPT_MAX_DEPTH = 10       # 每片至多对半细分 10 层


def _pieces(lo, hi, a, b, N_z, graded):
    """把分段 (lo, hi) 化成若干求积片 (z(u), dz/du, n)，u ∈ [0, 1]：按长度分配约 N_z 个点（每片 4m+1 个、
    至少 101 个）；与 graded 中的点（间断或陡峭点）相邻的一端用分级网格 z = 端点 ± L u³，把 |z - z_c|^{1/3}
    型的奇性化为 u 的光滑函数；两端都需分级时先对半分。"""
    gl = any(abs(lo - g) <= 1e-12 * g for g in graded)
    gh = any(abs(hi - g) <= 1e-12 * g for g in graded)
    halves = [(lo, 0.5 * (lo + hi), True, False), (0.5 * (lo + hi), hi, False, True)] if gl and gh else [(lo, hi, gl, gh)]
    out = []
    for l_, h_, sl, sh in halves:
        n = max(101, int(round(N_z * (h_ - l_) / (b - a))))
        n = 4 * ((n - 1 + 3) // 4) + 1
        L = h_ - l_
        if sl:
            zf, jf = (lambda u, l_=l_, L=L: l_ + L * u ** 3), (lambda u, L=L: 3.0 * L * u ** 2)
        elif sh:
            zf, jf = (lambda u, h_=h_, L=L: h_ - L * u ** 3), (lambda u, L=L: 3.0 * L * u ** 2)
        else:
            zf, jf = (lambda u, l_=l_, L=L: l_ + L * u), (lambda u, L=L: L * np.ones_like(u))
        out.append((zf, jf, n))
    return out


def _simpson_adaptive(fvals, zf, jf, n, u0=0.0, u1=1.0, depth=0, stats=None):
    """在 u ∈ [u0, u1] 上用 n 点复合 Simpson 积分 fvals(z) 的各分量 × dz/du；以隔点（n/2）的 Simpson 估计误差
    |S_n - S_{n/2}|/15，'time' 或 'cost' 分量超过 ADAPT_TOL·|S_n| 时对半细分（至多 ADAPT_MAX_DEPTH 层）。
    返回 (各分量积分, 误差估计)。"""
    uu = np.linspace(u0, u1, n)
    zz = zf(uu)
    vals = fvals(zz)
    jac = jf(uu)
    fine = {k: simpson(v * jac, x=uu) for k, v in vals.items()}
    coarse = {k: simpson((v * jac)[::2], x=uu[::2]) for k, v in vals.items()}
    err = {k: abs(fine[k] - coarse[k]) / 15.0 for k in fine}
    bad = any(err[k] > ADAPT_TOL * abs(fine[k]) + 1e-300 for k in ('time', 'cost'))
    if bad and depth < ADAPT_MAX_DEPTH:
        stats['splits'] += 1
        m = 0.5 * (u0 + u1)
        a1, e1 = _simpson_adaptive(fvals, zf, jf, n, u0, m, depth + 1, stats)
        a2, e2 = _simpson_adaptive(fvals, zf, jf, n, m, u1, depth + 1, stats)
        return {k: a1[k] + a2[k] for k in a1}, {k: e1[k] + e2[k] for k in e1}
    if bad:
        stats['unresolved'] += 1
    stats['evals'] += n
    return fine, err


def _densities(x, z, P, wc, wq):
    d = x * z - P.z_bar
    xz = x * z
    return dict(time=1.0 / d,
                cost=(wc * (1.0 - x) ** 2 + wq * (1.0 - 1.0 / xz) ** 2) / d,
                Jc=(1.0 - x) / d,
                Jq=(1.0 - 1.0 / xz) / d,
                inf=xz / d,
                sq=(xz - (1.0 - P.q0)) / d)


def arc_integrals(pol, N_z=DEFAULT_NZ, with_quad=True):
    """阈值弧的 S 坐标求积（主结果：分段复合 Simpson，分段点为 pol.nodes，每片按 Richardson 误差估计自适应
    对半细分；交叉核对：分段 quad）。"""
    P = pol.P
    pref = P.N / (P.c0 * P.eta)
    a, b = 1.0, pol.z_star
    keys = ('time', 'cost', 'Jc', 'Jq', 'inf', 'sq')
    tot = {k: 0.0 for k in keys}
    x_min_seen, x_max_seen, feas_viol = math.inf, -math.inf, 0.0
    stats = dict(splits=0, unresolved=0, evals=0)
    err_tot = {k: 0.0 for k in keys}
    for lo, hi in pol.segments():
        def fvals(zz, lo=lo, hi=hi):
            nonlocal x_min_seen, x_max_seen, feas_viol
            xx = np.array([pol.x_on(z, lo, hi) for z in zz])
            for z, x in zip(zz, xx):
                if z > 1.0:
                    xl, xh, _, _ = AL.x_bounds_raw(float(z), pol.x_min, pol.h)
                    feas_viol = max(feas_viol, xl - x, x - xh)
            x_min_seen, x_max_seen = min(x_min_seen, xx.min()), max(x_max_seen, xx.max())
            return _densities(xx, zz, P, pol.wc, pol.wq)
        for zf, jf, n in _pieces(lo, hi, a, b, N_z, pol.graded):
            val, err = _simpson_adaptive(fvals, zf, jf, n, stats=stats)
            for k in keys:
                tot[k] += val[k]
                err_tot[k] += err[k]
    dt = pref * tot['time']
    S_star, Sc = pol.start['S_star'], P.S_c
    out = dict(law=pol.name, N_z=N_z, S_star=S_star, z_star=pol.z_star, S_c=Sc, nodes=list(pol.nodes),
               dt=dt, J=pref * tot['cost'], Jc=pref * tot['Jc'], Jq=pref * tot['Jq'],
               inf_flux=P.beta * Sc * tot['inf'], sq_flux=(1.0 - P.beta) * Sc * tot['sq'],
               inf_identity=P.beta * (S_star - Sc) + P.gamma * P.eta * (1.0 - P.beta) * dt,
               sq_identity=(1.0 - P.beta) * (S_star - Sc - P.gamma * P.eta * dt),
               into_I=P.gamma * P.eta * dt,
               x_min=float(x_min_seen), x_max=float(x_max_seen), c_min=P.c0 * float(x_min_seen),
               q_max=1.0 - (1.0 - P.q0) / (pol.x(pol.z_star * (1 - 1e-15)) * pol.z_star),
               feasibility_violation=float(feas_viol),
               structure=None if pol.structure is None else dict(
                   breakpoints=pol.structure['breakpoints'], steep_points=pol.structure['steep_points'],
                   n_brackets=pol.structure['n_brackets']),
               kinks=list(pol.kinks), weights=(pol.wc, pol.wq), kappa=pol.kappa,
               simpson=dict(stats, err_dt=pref * err_tot['time'], err_J=pref * err_tot['cost']))
    if with_quad:
        qt = {}
        for k in ('time', 'cost'):
            v_tot, e_tot = 0.0, 0.0
            for lo, hi in pol.segments():
                fun = lambda z, lo=lo, hi=hi, k=k: float(_densities(
                    np.array([pol.x_on(z, lo, hi)]), np.array([z]), P, pol.wc, pol.wq)[k][0])
                v, e = quad(fun, lo, hi, epsabs=0.0, epsrel=QUAD_EPSREL, limit=500)
                v_tot += v
                e_tot += e
            qt[k] = (pref * v_tot, pref * e_tot)
        out.update(dt_quad=qt['time'][0], dt_quad_err=qt['time'][1], J_quad=qt['cost'][0], J_quad_err=qt['cost'][1])
    return out


# ---------------------------------------------------------------- 全过程（状态路径）
def state_path(pol, N_z=DEFAULT_NZ, with_quad=True):
    """第一条路径的全过程指标：t1（式 3.2）、阈值弧积分、退出后 S_end 与清零时间（定理 3.5）、
    计至清零与 t→∞ 的总累计新增感染（定理 3.6 的三段写法：前后两段 λ_F·ΔS，λ_F = β/(β+(1-β)q0)）。"""
    P = pol.P
    arc = arc_integrals(pol, N_z, with_quad)
    t1, t1_err = t1_quadrature(P, arc['S_star'])
    post = post_exit(P)
    lam = P.lamF
    pre_inf = lam * (P.S0 - arc['S_star'])
    out = dict(arc, t1=t1, t1_quad_err=t1_err, t2=t1 + arc['dt'], t_end=t1 + arc['dt'] + post['tail_time'],
               tail_time=post['tail_time'], S_end=post['S_end'], S_inf=post['S_inf'],
               post=post, pre_infections=pre_inf,
               total_infections_to_clearance=pre_inf + arc['inf_identity'] + lam * (P.S_c - post['S_end']),
               total_infections_inf=pre_inf + arc['inf_identity'] + lam * (P.S_c - post['S_inf']),
               Sq_t1=P.Sq0 + (1.0 - P.beta) * P.q0 / P.a * (P.S0 - arc['S_star']))
    return out


# ---------------------------------------------------------------- 单控制与显式族的闭式
def closed_forms(P, alpha=0.5, wc=None, wq=None):
    """现稿中的闭式（只依赖 S*、S_c、S̄ 与 S_end/S_∞），供回归核对。"""
    wc = P.wc if wc is None else wc
    wq = P.wq if wq is None else wq
    st = start_state(P)
    post = post_exit(P)
    Ss, Sc, Sb = st['S_star'], P.S_c, P.S_bar
    pref = P.N / (P.c0 * P.eta)
    lam = P.lamF
    dt_q = pref * math.log((Ss - Sb) / (Sc - Sb))                               # 式 (3.6)
    dt_c = pref * (Ss - Sc) / (Sc - Sb)                                          # 式 (4.14) 右端
    dt_a = pref / alpha * math.log1p(alpha * (Ss - Sc) / (Sc - Sb))              # 式 (4.11)
    arc_inf_q = P.beta * (Ss - Sc + Sb * math.log((Ss - Sb) / (Sc - Sb)))        # 定理 3.6 第二项
    out = dict(S_star=Ss, q_max=1.0 - P.gamma * P.N / (P.beta * P.c0 * Ss),      # 式 (3.10)
               dt_q_only=dt_q, dt_c_only=dt_c, dt_alpha=dt_a, alpha=alpha,
               Itcum_q_only_to_clearance=lam * (P.S0 - Ss + Sc - post['S_end']) + arc_inf_q,   # 式 (3.18)
               Itcum_q_only_inf=lam * (P.S0 - Ss + Sc - post['S_inf']) + arc_inf_q,
               arc_inf_q_only=arc_inf_q,
               # 附录 B：仅隔离控制（u_c = 0，u_q = 1 - S_c/S）
               Jq_q_only=pref * (Sc / Sb * math.log(Ss / Sc) + (1.0 - Sc / Sb) * math.log((Ss - Sb) / (Sc - Sb))),
               J_q_only=wq * pref * (Sc * (2 * Sb - Sc) / Sb ** 2 * math.log(Ss / Sc)
                                     + Sc ** 2 / Sb * (1.0 / Ss - 1.0 / Sc)
                                     + (1.0 - Sc / Sb) ** 2 * math.log((Ss - Sb) / (Sc - Sb))),
               # 附录 B：仅减少接触（u_c = 1 - S_c/S，u_q = 0）
               J_c_only=wc * P.N / (P.c0 * P.eta * (Sc - Sb)) * (Ss - Sc ** 2 / Ss - 2 * Sc * math.log(Ss / Sc)),
               Jc_c_only=P.N / (P.c0 * P.eta * (Sc - Sb)) * (Ss - Sc - Sc * math.log(Ss / Sc)),
               S_end=post['S_end'], S_inf=post['S_inf'])
    return out


def q_only_S_of_t(P, tau):
    """仅隔离控制阈值弧上 S(t1+τ) = S̄ + (S*-S̄)e^{-c0ητ/N}（式 3.5）。"""
    Ss = start_state(P)['S_star']
    return P.S_bar + (Ss - P.S_bar) * np.exp(-P.c0 * P.eta * np.asarray(tau) / P.N)


def q_only_q_of_t(P, tau):
    """仅隔离控制的 q_c(t1+τ)（式 3.8 第一种写法）。"""
    Ss = start_state(P)['S_star']
    A = P.beta * P.c0 * Ss / (P.gamma * P.N) + P.beta - 1.0
    return 1.0 - 1.0 / (A * np.exp(-P.c0 * P.eta * np.asarray(tau) / P.N) + 1.0 - P.beta)
