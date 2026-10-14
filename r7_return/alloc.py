"""控制律 x(z) = c/c0（按 S_c 归一的第二套变量：z = S/S_c）。

允许区间：x ∈ [1/z, 1]（下端为仅减少接触，上端为仅隔离控制；不考虑能力约束）。
z ≤ 1 时区间退化，统一返回 x = 1（只在阈值弧之外或求解器试探点上出现）。

显式控制律：
    仅隔离       x = 1
    仅减少接触   x = 1/z
    α 族         x = α + (1-α)/z，默认 α = 0.5

成本最优控制（逐状态最小化）：在每个 z 上最小化 S 坐标下的成本密度
    无回流（ω=0）：φ0(x) = [w_c(1-x)² + w_q(1-1/(xz))²] / (x z - z̄)
    立即返回     ：φI(x) = [w_c(1-x)² + w_q(1-1/(xz))²] / (x z)
（前因子 N/(c0η) 与 N/(βc0η) 与 x 无关，不影响逐状态最小化。）

全局最小的求法（根法，两端各一套）：
- φ' 的分子是 x 的多项式。无回流时由 SymPy 导出五次多项式（φ0' 的分母 x³z²(xz-z̄)² 在
  允许区间上为正）；立即返回时用执行计划第 3 节的四次式
  x⁴ h_a'(x) = w_c x⁴ - (w_c+w_q) x² + 4 a w_q x - 3 a² w_q，a = 1/z。
- numpy.roots 求全部根。候选集 = 区间两个端点 ∪ {虚部 ≤ 1e-4·max(1,|根|) 的根的实部，
  落在 [x_lo-ε, x_hi+ε] 内的截到区间内}。候选点都是可行点，逐一计算 φ 后取最小，
  因此多收的“近似实根”只会增加可行候选、不会使结果变差；严格意义的实根个数
  （虚部 ≤ 1e-10·max(1,|根|)）另行记录，仅作诊断。
- 近似重根：彼此相距 < 1e-12 的候选合并。真正的重根处 φ' 不变号，不是局部极小；
  两个相距很近的单根之间 φ 的差是根距的三次小量，漏掉其一不改变最小值的有效数字。
- 并列最小：值在 min + 1e-15·max(1,|min|) 之内的候选视为并列，取其中 x 最大者
  （更接近仅隔离），并记录并列个数。并列只出现在零测集上，不影响积分。
不把一次局部有界搜索当作全局求解。

网格（记录中分开报告）：
- N_x：固定 z 时对控制 x 的网格，只用于交叉核对根法（grid_min）。
- N_z：状态求积与切换位置定位的网格（scan_structure、endpoints.py）。
"""
from functools import lru_cache

import numpy as np

# 根法的筛选容差（见模块说明）
IMAG_TOL_CANDIDATE = 1e-4   # 收作候选的近似实根
IMAG_TOL_STRICT = 1e-10     # 计为“实根”的诊断阈值
EDGE_TOL = 1e-12            # 区间外 ε 以内的根截到端点
DUP_TOL = 1e-12             # 合并近似重根
TIE_TOL = 1e-15             # 并列最小值的相对容差（约数个 ulp）
LABEL_TOL = 1e-13           # 判定最优点是否为端点


# ---------------- 显式控制律 ----------------
def x_bounds(z):
    """允许区间 [x_lo, x_hi] = [1/z, 1]；z ≤ 1 时退化为 [1, 1]。"""
    if z <= 1.0:
        return 1.0, 1.0
    return 1.0 / z, 1.0


def law_q_only(z):
    return 1.0


def law_c_only(z):
    return 1.0 / z if z > 1.0 else 1.0


def make_law_alpha(alpha=0.5):
    def law_alpha(z):
        return alpha + (1.0 - alpha) / z if z > 1.0 else 1.0
    law_alpha.alpha = alpha
    return law_alpha


# ---------------- 成本密度（不含前因子） ----------------
def density_noreturn(x, z, z_bar, wc, wq):
    """无回流：φ0(x) = [w_c(1-x)² + w_q(1-1/(xz))²]/(xz - z̄)。"""
    return (wc * (1.0 - x) ** 2 + wq * (1.0 - 1.0 / (x * z)) ** 2) / (x * z - z_bar)


def density_immediate(x, z, wc, wq):
    """立即返回：φI(x) = [w_c(1-x)² + w_q(1-1/(xz))²]/(xz)。"""
    return (wc * (1.0 - x) ** 2 + wq * (1.0 - 1.0 / (x * z)) ** 2) / (x * z)


# ---------------- 驻点多项式 ----------------
@lru_cache(maxsize=None)
def _noreturn_coeff_funcs():
    """用 SymPy 由 φ0 导出 φ0' 的分子（x 的五次多项式），返回系数函数（高次在前）与分母。"""
    import sympy as sp
    x, z, zb, wc, wq = sp.symbols('x z zbar w_c w_q', positive=True)
    phi = (wc * (1 - x) ** 2 + wq * (1 - 1 / (x * z)) ** 2) / (x * z - zb)
    num, den = sp.fraction(sp.together(sp.diff(phi, x)))
    poly = sp.Poly(sp.expand(num), x)
    if poly.degree() != 5:
        raise RuntimeError('φ0′ 的分子不是五次多项式')
    funcs = [sp.lambdify((z, zb, wc, wq), cf, 'math') for cf in poly.all_coeffs()]
    return funcs, str(sp.factor(den)), [str(sp.factor(cf)) for cf in poly.all_coeffs()]


def stationary_poly_noreturn(z, z_bar, wc, wq):
    """无回流驻点多项式的系数（高次在前）。"""
    funcs, _, _ = _noreturn_coeff_funcs()
    return np.array([f(z, z_bar, wc, wq) for f in funcs], dtype=float)


def stationary_poly_immediate(z, wc, wq):
    """立即返回驻点多项式 w_c x⁴ - (w_c+w_q) x² + 4 a w_q x - 3 a² w_q 的系数，a = 1/z。"""
    a = 1.0 / z
    return np.array([wc, 0.0, -(wc + wq), 4.0 * a * wq, -3.0 * a * a * wq])


def _argmin_by_roots(coeffs, x_lo, x_hi, f):
    """在 [x_lo, x_hi] 上比较两个端点与全部驻点，返回 (x*, φ(x*), 诊断)。"""
    roots = np.roots(coeffs)
    scale = np.maximum(1.0, np.abs(roots))
    n_real = int(np.sum(np.abs(roots.imag) <= IMAG_TOL_STRICT * scale))
    cand = [x_lo, x_hi]
    n_feasible = 0
    edge = EDGE_TOL * max(1.0, x_hi)
    for r, sc in zip(roots, scale):
        if abs(r.imag) <= IMAG_TOL_CANDIDATE * sc:
            xr = r.real
            if x_lo - edge <= xr <= x_hi + edge:
                cand.append(min(max(xr, x_lo), x_hi))
                n_feasible += 1
    cand = np.unique(np.array(cand))            # 已排序
    keep = [cand[0]]
    for c in cand[1:]:
        if c - keep[-1] > DUP_TOL:
            keep.append(c)
    cand = np.array(keep)
    vals = f(cand)
    vmin = float(np.min(vals))
    ties = cand[vals <= vmin + TIE_TOL * max(1.0, abs(vmin))]
    x_star = float(np.max(ties))
    if abs(x_star - x_hi) <= LABEL_TOL:
        label = 'hi'
    elif abs(x_star - x_lo) <= LABEL_TOL:
        label = 'lo'
    else:
        label = 'int'
    info = dict(n_roots=len(roots), n_real=n_real, n_feasible=n_feasible,
                n_candidates=len(cand), n_ties=len(ties), label=label)
    return x_star, float(f(np.array([x_star]))[0]), info


@lru_cache(maxsize=200000)
def argmin_noreturn(z, z_bar, wc, wq):
    """无回流（ω=0）在状态 z 上的逐状态全局最小：返回 (x*, φ0(x*), 诊断)。"""
    x_lo, x_hi = x_bounds(z)
    if x_hi - x_lo <= 0.0:
        return 1.0, float(density_noreturn(1.0, max(z, 1.0), z_bar, wc, wq)), dict(label='deg')
    coeffs = stationary_poly_noreturn(z, z_bar, wc, wq)
    return _argmin_by_roots(coeffs, x_lo, x_hi, lambda x: density_noreturn(x, z, z_bar, wc, wq))


@lru_cache(maxsize=200000)
def argmin_immediate(z, wc, wq):
    """立即返回对照模型在状态 z 上的逐状态全局最小：返回 (x*, φI(x*), 诊断)。"""
    x_lo, x_hi = x_bounds(z)
    if x_hi - x_lo <= 0.0:
        return 1.0, float(density_immediate(1.0, max(z, 1.0), wc, wq)), dict(label='deg')
    coeffs = stationary_poly_immediate(z, wc, wq)
    return _argmin_by_roots(coeffs, x_lo, x_hi, lambda x: density_immediate(x, z, wc, wq))


def make_law_opt_noreturn(P, wc=None, wq=None):
    """ω=0 的成本最优控制律 x(z)。在其他 ω 下实施即“无回流最优律迁移”：
    任何所需的 z（包括有回流时超过无回流 S* 的状态）都按 ω=0 的逐状态最小化直接计算，
    不插值、不外推。"""
    wc = P.wc if wc is None else wc
    wq = P.wq if wq is None else wq
    z_bar = P.z_bar

    def law(z):
        return argmin_noreturn(float(z), z_bar, wc, wq)[0]
    law.kind = 'opt_noreturn'
    return law


def make_law_opt_immediate(P, wc=None, wq=None):
    """立即返回对照模型自身的成本最优控制律 x(z)。"""
    wc = P.wc if wc is None else wc
    wq = P.wq if wq is None else wq

    def law(z):
        return argmin_immediate(float(z), wc, wq)[0]
    law.kind = 'opt_immediate'
    return law


def get_law(name, P, wc=None, wq=None, alpha=0.5):
    """按名称取控制律：'q_only'、'c_only'、'alpha'、'opt_noreturn'（ω>0 时即迁移律）、'opt_immediate'。"""
    if name == 'q_only':
        return law_q_only
    if name == 'c_only':
        return law_c_only
    if name == 'alpha':
        return make_law_alpha(alpha)
    if name in ('opt_noreturn', 'migrated'):
        return make_law_opt_noreturn(P, wc, wq)
    if name == 'opt_immediate':
        return make_law_opt_immediate(P, wc, wq)
    raise ValueError(name)


# ---------------- N_x 网格交叉核对 ----------------
def grid_min(density, z, N_x):
    """固定 z，在 N_x 个等距点上取 density(x) 的最小值（只用于核对根法）。"""
    x_lo, x_hi = x_bounds(z)
    xs = np.linspace(x_lo, x_hi, N_x)
    v = density(xs)
    k = int(np.argmin(v))
    return float(xs[k]), float(v[k])


# ---------------- N_z 网格上的结构扫描与切换位置定位 ----------------
JUMP_CLASSIFY_TOL = 1e-6    # 加密到 |Δz| ≤ 1e-14·z 后，x 两侧之差超过它才算间断


def scan_structure(argmin_fn, z_a, z_b, N_z, poly_fn=None):
    """在 [z_a, z_b] 的 N_z 点网格上记录 x(z) 与最优点类型（'lo'/'int'/'hi'），
    找出类型改变或 x 变化过快的括区，再逐个加密，返回结构变化点。

    - 类型改变且 x 连续（内部驻点移到端点）：在括区内对“φ′ 的分子在该端点的值”
      用 brentq 求根（该点处驻点恰在端点）；无变号时退回按类型二分。
    - x 变化过快（相邻网格差 > max(1e-3, 50·中位数)）：按“更接近左侧还是右侧的 x”
      二分到 |Δz| ≤ 1e-14·z；两侧 x 之差仍 > JUMP_CLASSIFY_TOL 才记为间断，
      否则只是陡峭的连续变化，不记为结构变化点。
    argmin_fn(z) -> (x*, φ*, 诊断)；poly_fn(z) -> 驻点多项式系数。
    返回 dict(z, x, label, breakpoints=[{z, kind, continuous, x_left, x_right, ...}], n_brackets)。"""
    zg = np.linspace(z_a, z_b, N_z)
    res = [argmin_fn(float(z)) for z in zg]
    xg = np.array([r[0] for r in res])
    lab = [r[2].get('label', 'deg') for r in res]
    dx = np.abs(np.diff(xg))
    jump_tol = max(1e-3, 50.0 * float(np.median(dx)) if len(dx) else 0.0)
    brackets = []
    for k in range(len(zg) - 1):
        if lab[k] == 'deg' or lab[k + 1] == 'deg':
            continue
        if lab[k] != lab[k + 1]:
            brackets.append((float(zg[k]), float(zg[k + 1]), 'label'))
        elif dx[k] > jump_tol:
            brackets.append((float(zg[k]), float(zg[k + 1]), 'jump'))

    def bisect(za, zb, kind):
        xa, _, ia = argmin_fn(za)
        la = ia.get('label')
        xb = argmin_fn(zb)[0]
        lo, hi = za, zb
        while hi - lo > 1e-14 * hi:
            m = 0.5 * (lo + hi)
            if m <= lo or m >= hi:
                break
            xm, _, im = argmin_fn(m)
            left = (im.get('label') == la) if kind == 'label' else (abs(xm - xa) < abs(xm - xb))
            if left:
                lo = m
            else:
                hi = m
        return lo, hi

    bps = []
    steep = []      # 陡峭但连续的区段：每段取 Δx 最大的括区二分后的位置，只作求积分段点
    run = []
    for k, (za, zb, kind) in enumerate(brackets):
        if kind == 'jump':
            if run and abs(run[-1][1] - za) > 1e-15 * zb:
                steep.append(max(run, key=lambda b: abs(argmin_fn(b[1])[0] - argmin_fn(b[0])[0])))
                run = []
            run.append((za, zb))
    if run:
        steep.append(max(run, key=lambda b: abs(argmin_fn(b[1])[0] - argmin_fn(b[0])[0])))

    def zoom(lo, hi):
        """把括区反复十等分，保留 |Δx| 最大的子区间，直到宽度 ≤ 1e-13·z：
        收敛到 x(z) 导数无界的点（如立方根型尖点）。"""
        while hi - lo > 1e-13 * hi:
            zz = np.linspace(lo, hi, 11)
            xs = np.array([argmin_fn(float(z))[0] for z in zz])
            k = int(np.argmax(np.abs(np.diff(xs))))
            lo, hi = float(zz[k]), float(zz[k + 1])
        return 0.5 * (lo + hi)
    steep_points = [zoom(a, b) for a, b in steep]
    for za, zb, kind in brackets:
        xa, _, ia = argmin_fn(za)
        xb, _, ib = argmin_fn(zb)
        la, lb = ia.get('label'), ib.get('label')
        method = 'bisect'
        zloc = None
        if kind == 'label' and poly_fn is not None and 'int' in (la, lb):
            end = la if la != 'int' else lb
            x_end = (lambda z: 1.0) if end == 'hi' else (lambda z: 1.0 / z)
            g = lambda z: float(np.polyval(poly_fn(z), x_end(z)))
            # 并列规则使类型标签在真实切换点前约 1e-7 处就翻转，网格括区可能恰好错过变号；
            # 先用原括区，不变号时向两侧各扩一格再试。求得的点须两侧 x 连续才采用，否则退回二分
            h = zb - za
            for lo_, hi_ in ((za, zb), (max(z_a, za - h), min(z_b, zb + h))):
                if g(lo_) * g(hi_) < 0:
                    from scipy.optimize import brentq
                    zc = brentq(g, lo_, hi_, xtol=1e-15, rtol=1e-15)
                    xl, xr = argmin_fn(zc * (1 - 1e-12))[0], argmin_fn(zc * (1 + 1e-12))[0]
                    if abs(xr - xl) <= JUMP_CLASSIFY_TOL:
                        zloc, method = zc, 'brentq_endpoint_stationary'
                    break
        if zloc is None:
            lo, hi = bisect(za, zb, kind)
            zloc = 0.5 * (lo + hi)
            x_left, x_right = argmin_fn(lo)[0], argmin_fn(hi)[0]
        else:
            x_left, x_right = argmin_fn(zloc * (1 - 1e-12))[0], argmin_fn(zloc * (1 + 1e-12))[0]
        continuous = abs(x_right - x_left) <= JUMP_CLASSIFY_TOL
        if kind == 'jump' and continuous:
            continue          # 陡峭但连续，不是结构变化点
        bps.append(dict(z=zloc, kind=kind, method=method, continuous=continuous,
                        label_left=la, label_right=lb, x_left=x_left, x_right=x_right))
    # 结构变化点之外的陡峭点（如立即返回、默认权重下 z = 2√2 处驻点多项式的三重根）
    steep_points = [zs for zs in steep_points
                    if all(abs(zs - b['z']) > 1e-9 * zs for b in bps)]
    return dict(z=zg, x=xg, label=lab, breakpoints=bps, steep_points=steep_points,
                n_brackets=len(brackets))


def terminal_share(x, z):
    """接触减少的分担比例 (1 - c/c0)/(1 - S_c/S) = (1-x)/(1-1/z)。"""
    return (1.0 - x) / (1.0 - 1.0 / z)


def z_sw_noreturn_formula(z_bar):
    """命题 5.3 的 S_sw/S_c = (3 + √(9 - 8 z̄))/2（局部性质的分界）。"""
    return 0.5 * (3.0 + np.sqrt(9.0 - 8.0 * z_bar))
