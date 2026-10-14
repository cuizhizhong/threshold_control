"""两端模型的阈值弧：启动状态与 S 坐标求积（按 S_c 归一的第二套变量 z = S/S_c）。

两端（执行计划第 3 节）：
- 无回流（ω = 0，稿件式 (2.1)）：
    启动状态由常规轨迹的首次积分给出，κ0 = β(1-q0)/(β+(1-β)q0)；
    阈值弧上 dt = -N dz / (c0 η (x z - z̄))，
    Δt = N/(c0 η) ∫_1^{z*} dz/(x z - z̄)，
    J  = N/(c0 η) ∫_1^{z*} [w_c(1-x)² + w_q(1-1/(xz))²]/(x z - z̄) dz，
    控制期累计感染（恒等式）= β(S*-S_c) + (1-β)γηΔt，
    新增隔离易感者（恒等式）= (1-β)(S*-S_c-γηΔt)。
- 立即返回对照模型（S_q ≡ 0）：
    常规轨迹 I(S) = I0 + (1-q0)(S0-S) + (1-q0)S_c ln(S/S0)，κ = 1-q0；
    阈值弧上 dt = -N dz / (β c0 η x z)，
    Δt = N/(β c0 η) ∫_1^{z*_∞} dz/(x z)，
    J  = N/(β c0 η) ∫_1^{z*_∞} [w_c(1-x)² + w_q(1-1/(xz))²]/(x z) dz，
    控制期累计感染 = S*_∞ - S_c（所有控制相同），
    未感染接触者累计追踪人次 K_q = (1-β)/β [S*_∞ - S_c - γηΔt]。
所有积分都写成从 1 到 z* 的正时长定积分（不带负号）。

启动状态：z - ln z = A，z* = -S_c W_{-1}(-e^{-A}) / S_c（scipy.special.lambertw，k = -1），
并用 brentq 在 (S_c, S0) 上解 I(S) = η 交叉核对。触发条件 0 < I0 < η < I_peak 不满足时
走退化分支，不调用 Lambert W。

求积（主结果）：N_z 点网格上的复合 Simpson，在结构变化点（alloc.scan_structure 定位的
切换位置）与陡峭点处分段；另用 scipy.integrate.quad（同样分段，epsabs=0, epsrel=1e-12）
作交叉核对，两者之差随结果一并返回。
"""
import math

import numpy as np
from scipy.integrate import simpson, quad
from scipy.optimize import brentq
from scipy.special import lambertw

import alloc as AL

DEFAULT_NZ = 4001


# ---------------- 启动状态 ----------------
def kappa_noreturn(P):
    """无回流常规轨迹 dI/dS = -κ0 (1 - S_c/S)，κ0 = β(1-q0)/(β+(1-β)q0)。"""
    return P.beta * (1.0 - P.q0) / (P.beta + (1.0 - P.beta) * P.q0)


def kappa_immediate(P):
    """立即返回常规轨迹 dI/dS = -(1-q0)(1 - S_c/S)。"""
    return 1.0 - P.q0


def _start_state(P, kappa):
    """常规轨迹 I(S) = I0 + κ[(S0-S) + S_c ln(S/S0)] 首次达到 η 时的 S*（两端共用的代数）。"""
    S0, Sc, I0, eta = P.S0, P.S_c, P.I0, P.eta
    out = dict(kappa=kappa, S_c=Sc)
    if not S0 > Sc:
        out.update(status='degenerate', reason='S0 <= S_c：常规轨迹从一开始 I 就不增，不触发')
        return out
    I_peak = I0 + kappa * (S0 - Sc + Sc * math.log(Sc / S0))
    out['I_peak'] = I_peak
    if not (0.0 < I0 < eta < I_peak):
        if I0 >= eta:
            reason = 'I0 >= η：不是“由下方首次达到 η”，单列退化分支'
        elif eta >= I_peak:
            reason = 'η >= I_peak：常规轨迹不触发（η = I_peak 为恰好触峰）'
        else:
            reason = 'I0 <= 0'
        out.update(status='degenerate', reason=reason)
        return out
    z0 = S0 / Sc
    A = z0 - math.log(z0) - (eta - I0) / (kappa * Sc)
    out['A'] = A
    if not A > 1.0:      # 触发条件满足时必有 A > 1；此处只作防御
        out.update(status='degenerate', reason=f'A = {A} <= 1')
        return out
    w = lambertw(-math.exp(-A), k=-1)
    z_star = float(-w.real)
    S_star = Sc * z_star
    Ifun = lambda S: I0 + kappa * ((S0 - S) + Sc * math.log(S / S0)) - eta
    S_star_brentq = brentq(Ifun, Sc * (1.0 + 1e-14), S0, xtol=1e-12 * S0, rtol=4 * np.finfo(float).eps,
                           maxiter=500)
    out.update(status='ok', z_star=z_star, S_star=S_star, lambertw_imag=float(w.imag),
               S_star_brentq=S_star_brentq,
               lambertw_vs_brentq_rel=abs(S_star - S_star_brentq) / S_star,
               residual_I=Ifun(S_star))
    return out


def start_state_noreturn(P):
    """无回流（ω = 0）的启动状态 S*。"""
    out = _start_state(P, kappa_noreturn(P))
    out['model'] = 'noreturn'
    return out


def start_state_immediate(P):
    """立即返回对照模型的启动状态 S*_∞；先检查 R3 的触发条件 0 < I0 < η < I_peak,ir。"""
    out = _start_state(P, kappa_immediate(P))
    out['model'] = 'immediate'
    if 'I_peak' in out:
        out['I_peak_ir'] = out['I_peak']
    return out


# ---------------- 分段 Simpson ----------------
def _piecewise_simpson(f, a, b, cuts, N_z, steep=()):
    """在 [a, b] 上以 cuts ∪ steep 分段，按长度分配约 N_z 个点（每段奇数个、至少 101 个）。
    与陡峭点（x(z) 导数无界，立方根型）相邻的一端用分级网格 z = 端点 ± L u³，
    把 |z - z_c|^{1/3} 型的奇性化为 u 的光滑函数后再用 Simpson；两端都陡峭的段先对半分。"""
    steep = [s for s in steep if a < s < b]
    pts = sorted(set([a, b] + [c for c in cuts if a < c < b] + steep))
    pieces = []
    for lo, hi in zip(pts[:-1], pts[1:]):
        sl = any(abs(lo - s) <= 1e-12 * s for s in steep)
        sh = any(abs(hi - s) <= 1e-12 * s for s in steep)
        if sl and sh:
            m = 0.5 * (lo + hi)
            pieces += [(lo, m, True, False), (m, hi, False, True)]
        else:
            pieces.append((lo, hi, sl, sh))
    total = 0.0
    for lo, hi, sl, sh in pieces:
        n = max(101, int(round(N_z * (hi - lo) / (b - a))))
        if n % 2 == 0:
            n += 1
        L = hi - lo
        if sl or sh:
            u = np.linspace(0.0, 1.0, n)
            zz = lo + L * u ** 3 if sl else hi - L * u ** 3
            total += simpson(f(zz) * 3.0 * L * u ** 2, x=u)
        else:
            zz = np.linspace(lo, hi, n)
            total += simpson(f(zz), x=zz)
    return total


def _piecewise_quad(f1, a, b, cuts):
    pts = [a] + sorted(c for c in cuts if a < c < b) + [b]
    total, err = 0.0, 0.0
    for lo, hi in zip(pts[:-1], pts[1:]):
        v, e = quad(f1, lo, hi, epsabs=0.0, epsrel=1e-12, limit=500)
        total += v
        err += e
    return total, err


def _law_and_structure(law_name, P, model, z_star, N_z, wc, wq, alpha):
    """取控制律；成本最优控制律另在 N_z 网格上定位结构变化点与陡峭点。"""
    law = AL.get_law(law_name, P, wc, wq, alpha)
    cuts, steep, structure = [], [], None
    if law_name in ('opt_noreturn', 'opt_immediate'):
        if law_name == 'opt_noreturn':
            fn = lambda z: AL.argmin_noreturn(z, P.z_bar, wc, wq)
            pf = lambda z: AL.stationary_poly_noreturn(z, P.z_bar, wc, wq)
        else:
            fn = lambda z: AL.argmin_immediate(z, wc, wq)
            pf = lambda z: AL.stationary_poly_immediate(z, wc, wq)
        structure = AL.scan_structure(fn, 1.0, z_star, N_z, poly_fn=pf)
        cuts = [b['z'] for b in structure['breakpoints']]
        steep = list(structure['steep_points'])
    return law, cuts, steep, structure


def _vec(law):
    return np.vectorize(lambda z: law(float(z)), otypes=[float])


# ---------------- 阈值弧（两端各一套） ----------------
def arc_noreturn(P, law_name, N_z=DEFAULT_NZ, wc=None, wq=None, alpha=0.5, with_quad=True):
    """无回流（ω = 0）阈值弧的 S 坐标求积。"""
    wc = P.wc if wc is None else wc
    wq = P.wq if wq is None else wq
    st = start_state_noreturn(P)
    if st['status'] != 'ok':
        return dict(status=st['status'], start=st, model='noreturn', law=law_name)
    z_star, z_bar = st['z_star'], P.z_bar
    law, cuts, steep, structure = _law_and_structure(law_name, P, 'noreturn', z_star, N_z, wc, wq, alpha)
    xv = _vec(law)
    pref = P.N / (P.c0 * P.eta)                       # Δt、J 的前因子 N/(c0 η)

    def dens(z, kind):
        x = xv(z)
        d = x * z - z_bar
        if kind == 'time':
            return 1.0 / d
        if kind == 'cost':
            return (wc * (1 - x) ** 2 + wq * (1 - 1 / (x * z)) ** 2) / d
        if kind == 'inf':                              # F dt = β S_c x z/(xz - z̄) dz
            return x * z / d
        if kind == 'sq':                               # A_q dt = (1-β) S_c x z q/(xz - z̄) dz
            q = 1 - (1 - P.q0) / (x * z)
            return x * z * q / d
        raise ValueError(kind)

    integ = {k: _piecewise_simpson(lambda z, k=k: dens(z, k), 1.0, z_star, cuts, N_z, steep)
             for k in ('time', 'cost', 'inf', 'sq')}
    dt = pref * integ['time']
    J = pref * integ['cost']
    Sc, S_star = P.S_c, st['S_star']
    out = dict(status='ok', model='noreturn', law=law_name, N_z=N_z, start=st,
               S_star=S_star, z_star=z_star, S_c=Sc, dt=dt, J=J,
               infections_identity=P.beta * (S_star - Sc) + (1 - P.beta) * P.gamma * P.eta * dt,
               infections_quad=P.beta * Sc * integ['inf'],
               Sq_new_identity=(1 - P.beta) * (S_star - Sc - P.gamma * P.eta * dt),
               Sq_new_quad=(1 - P.beta) * Sc * integ['sq'],
               cuts=cuts, steep_points=steep, structure=_structure_summary(structure))
    if with_quad:
        tq, te = _piecewise_quad(lambda z: float(dens(np.array([z]), 'time')[0]), 1.0, z_star, cuts + steep)
        cq, ce = _piecewise_quad(lambda z: float(dens(np.array([z]), 'cost')[0]), 1.0, z_star, cuts + steep)
        out.update(dt_quad=pref * tq, J_quad=pref * cq, dt_quad_err=pref * te, J_quad_err=pref * ce)
    return out


def arc_immediate(P, law_name, N_z=DEFAULT_NZ, wc=None, wq=None, alpha=0.5, with_quad=True):
    """立即返回对照模型阈值弧的 S 坐标求积。"""
    wc = P.wc if wc is None else wc
    wq = P.wq if wq is None else wq
    if P.Sq0 != 0.0:
        raise ValueError('立即返回对照模型要求 S_q(0) = 0')
    st = start_state_immediate(P)
    if st['status'] != 'ok':
        return dict(status=st['status'], start=st, model='immediate', law=law_name)
    z_star = st['z_star']
    law, cuts, steep, structure = _law_and_structure(law_name, P, 'immediate', z_star, N_z, wc, wq, alpha)
    xv = _vec(law)
    pref = P.N / (P.beta * P.c0 * P.eta)              # 前因子 N/(β c0 η)

    def dens(z, kind):
        x = xv(z)
        if kind == 'time':
            return 1.0 / (x * z)
        if kind == 'cost':
            return (wc * (1 - x) ** 2 + wq * (1 - 1 / (x * z)) ** 2) / (x * z)
        if kind == 'q':                                # K_q = (1-β)/β S_c ∫ q dz
            return 1 - (1 - P.q0) / (x * z)
        raise ValueError(kind)

    integ = {k: _piecewise_simpson(lambda z, k=k: dens(z, k), 1.0, z_star, cuts, N_z, steep)
             for k in ('time', 'cost', 'q')}
    dt = pref * integ['time']
    J = pref * integ['cost']
    Sc, S_star = P.S_c, st['S_star']
    out = dict(status='ok', model='immediate', law=law_name, N_z=N_z, start=st,
               S_star=S_star, z_star=z_star, S_c=Sc, dt=dt, J=J,
               infections=S_star - Sc,
               Kq_identity=(1 - P.beta) / P.beta * (S_star - Sc - P.gamma * P.eta * dt),
               Kq_quad=(1 - P.beta) / P.beta * Sc * integ['q'],
               dt_closed_q_only=pref * math.log(z_star),
               dt_closed_c_only=pref * (z_star - 1.0),
               cuts=cuts, steep_points=steep, structure=_structure_summary(structure))
    if with_quad:
        tq, te = _piecewise_quad(lambda z: float(dens(np.array([z]), 'time')[0]), 1.0, z_star, cuts + steep)
        cq, ce = _piecewise_quad(lambda z: float(dens(np.array([z]), 'cost')[0]), 1.0, z_star, cuts + steep)
        out.update(dt_quad=pref * tq, J_quad=pref * cq, dt_quad_err=pref * te, J_quad_err=pref * ce)
    return out


def _structure_summary(structure):
    if structure is None:
        return None
    return dict(breakpoints=structure['breakpoints'], steep_points=structure['steep_points'],
                n_brackets=structure['n_brackets'])


def arc(model, P, law_name, **kw):
    """model ∈ {'noreturn', 'immediate'}。"""
    return arc_noreturn(P, law_name, **kw) if model == 'noreturn' else arc_immediate(P, law_name, **kw)
