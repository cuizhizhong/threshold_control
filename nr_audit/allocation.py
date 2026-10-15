"""控制律 x(z) = c/c0 与逐状态最小化（按 S_c 归一的第二套变量：z = S/S_c）。

复制来源：research/return-effects bb52b96 的 r7_return/alloc.py（blob 034e6207，与 91123ea 相同），
只保留无回流部分，并扩展为：一般正权重 w_c、w_q；时长乘子 κ（注记 5.5，J + κΔt）；
能力约束下的允许区间（式 4.8）；接近退出时的缩放坐标 y（写法取自
reproducibility/joint_extra/core.py 的 candidates，原文件未改动）；候选根的牛顿修正、残差与
重根诊断；带局部加密的 N_x 网格核对。删去立即返回对照模型的部分。

允许区间（式 4.6–4.8；z ≤ 1 时退化为 {1}）：
    x_lo(z) = max{1/z, c_min/c0}，x_hi(z) = min{1, h/z}，h = (1-q0)/(1-q_cap)。
不考虑能力约束时 x_lo = 1/z（仅减少接触）、x_hi = 1（仅隔离控制）。区间为空（式 4.7 不成立）
时报错，不截断。

成本最优控制：在每个 z 上最小化 S 坐标下的被积函数（定理 5.1，前因子 N/(c0η) 与 x 无关）
    φ(x) = [w_c(1-x)² + w_q(1-1/(xz))² + κ] / (x z - z̄)，z̄ = (1-β)(1-q0)。
φ′ 的分子乘以正数后是 x 的五次多项式（r = 1/z，b = z̄/z，高次在前）：
    [w_c, -2b w_c, w_c(2b-1) - w_q - κ, 4r w_q, -r(3r+2b) w_q, 2br² w_q]，
κ = 0 时与稿件式 (5.4) 相差正因子 c0³（tests/test_allocation.py 用 SymPy 核对）。
接近退出（ζ = 1 - 1/z < ZETA_SCALED）时改用 x = 1 - ζy，y ∈ [(1-x_hi)/ζ, (1-x_lo)/ζ]，
在 y 上比较同一组候选（缩放后的五次式由 numpy 多项式运算构造，避免 1-x 的相消）。

候选与选择：
- 两个端点，加上 numpy.roots 中虚部 ≤ IMAG_TOL_CANDIDATE·max(1,|根|) 的根的实部（落在区间外
  EDGE_TOL·区间宽度以内的截到端点）。候选都是可行点，逐一计算目标值，所以多收的近似实根
  只会增加候选，不会使结果变差。每个候选根先做至多 8 步牛顿修正（只在不离开区间时采用）。
- 严格实根（虚部 ≤ IMAG_TOL_STRICT·max(1,|根|)）另计个数；区间内两两距离小于
  DOUBLE_ROOT_GAP·区间宽度的根记为“近重根”。重根处 φ′ 不变号，不是局部极小；近重根的
  两个单根之间 φ 的差是根距的三次小量，漏掉其一不改变最小值的有效数字。
- 相距小于 DUP_TOL·区间宽度的候选合并（保留端点）。
- 选目标值严格最小者；完全相等时取 x 较大者（更接近仅隔离）。另记录值在
  min + NEAR_TIE_REL·max(|min|, 候选值极差) 以内的候选个数（近并列，只作诊断；并列只出现在零测集上，
  定理 5.1 中任一可测选择都是最优控制，不对选择作平滑）。
网格只作交叉核对（grid_check），不作为求解方法。
"""
import math
from functools import lru_cache

import numpy as np
from numpy.polynomial import Polynomial

IMAG_TOL_CANDIDATE = 1e-4
IMAG_TOL_STRICT = 1e-10
EDGE_TOL = 1e-10          # 相对区间宽度
DUP_TOL = 1e-12           # 相对区间宽度
DOUBLE_ROOT_GAP = 1e-6    # 相对区间宽度
NEAR_TIE_REL = 1e-10
DEG_TOL = 1e-14           # 区间宽度不超过它（绝对，x 坐标）视为退化
FEAS_TOL = 1e-12          # x_lo 超过 x_hi 不到 FEAS_TOL·x_hi 视为相等（等号可行）
ZETA_SCALED = 1e-4        # ζ = 1-1/z 小于它时用缩放坐标 y
NEWTON_STEPS = 8


class Infeasible(ValueError):
    """能力约束下某状态的允许区间为空。"""


# ---------------------------------------------------------------- 允许区间
def cap_factors(P, cap):
    """能力约束换成 (x_min, h)：x ≥ x_min = c_min/c0，x ≤ h/z，h = (1-q0)/(1-q_cap)。
    不考虑能力约束时返回 (0, inf)。"""
    if cap is None:
        return 0.0, math.inf
    cap.check(P)
    return cap.c_min / P.c0, (1.0 - P.q0) / (1.0 - cap.q_cap)


def x_bounds_raw(z, x_min=0.0, h=math.inf):
    """允许区间 [x_lo, x_hi] 及两端的类型。
    lo_kind ∈ {'contact_only'（=1/z）, 'cmin'}，hi_kind ∈ {'c0'（=1）, 'qcap'（=h/z）}。"""
    if z <= 1.0:
        return 1.0, 1.0, 'deg', 'deg'
    lo, lo_kind = 1.0 / z, 'contact_only'
    if x_min > lo:
        lo, lo_kind = x_min, 'cmin'
    hi, hi_kind = 1.0, 'c0'
    if h / z < hi:
        hi, hi_kind = h / z, 'qcap'
    if lo > hi:
        if lo - hi <= FEAS_TOL * hi:
            lo = hi
        else:
            raise Infeasible(f'z = {z}: x_lo = {lo} > x_hi = {hi}')
    return lo, hi, lo_kind, hi_kind


def x_bounds(z, P=None, cap=None):
    lo, hi, _, _ = x_bounds_raw(z, *cap_factors(P, cap)) if cap is not None else x_bounds_raw(z)
    return lo, hi


def geometric_kinks(P, cap, z_star):
    """能力区间端点的折点（区间端点由 max/min 切换处），只取 (1, z*) 内的。"""
    if cap is None:
        return []
    x_min, h = cap_factors(P, cap)
    out = []
    if x_min > 0.0 and 1.0 < 1.0 / x_min < z_star:
        out.append(1.0 / x_min)          # 1/z = x_min：x_lo 由 1/z 切到 c_min/c0
    if 1.0 < h < z_star:
        out.append(h)                     # h/z = 1：x_hi 由 h/z 切到 1
    return sorted(out)


# ---------------------------------------------------------------- 显式控制律
def law_q_only(z):
    return 1.0


def law_c_only(z):
    return 1.0 / z if z > 1.0 else 1.0


def make_law_alpha(alpha):
    def law(z):
        return alpha + (1.0 - alpha) / z if z > 1.0 else 1.0
    law.alpha = alpha
    return law


# ---------------------------------------------------------------- 目标函数
def objective_x(x, z, z_bar, wc, wq, kappa=0.0):
    """φ(x) = [w_c(1-x)² + w_q(1-1/(xz))² + κ]/(xz - z̄)（不含前因子 N/(c0η)）。"""
    return (wc * (1.0 - x) ** 2 + wq * (1.0 - 1.0 / (x * z)) ** 2 + kappa) / (x * z - z_bar)


def objective_y(y, z, z_bar, wc, wq, kappa=0.0):
    """同一目标在缩放坐标 x = 1 - ζy 下的值（ζ = 1 - 1/z），避免 1-x 与 1-1/(xz) 的相消。"""
    zeta = 1.0 - 1.0 / z
    u = 1.0 - zeta * y
    return (zeta * zeta * (wc * y * y + wq * (1.0 - y) ** 2 / (u * u)) + kappa) / (u * z - z_bar)


def stationary_poly_x(z, z_bar, wc, wq, kappa=0.0):
    """φ′ 分子（乘以正数 x³z(xz-z̄)²/z² 后）的系数，高次在前。"""
    r, b = 1.0 / z, z_bar / z
    return np.array([wc, -2.0 * b * wc, wc * (2.0 * b - 1.0) - wq - kappa,
                     4.0 * r * wq, -r * (3.0 * r + 2.0 * b) * wq, 2.0 * b * r * r * wq])


def stationary_poly_y(z, z_bar, wc, wq, kappa=0.0):
    """缩放坐标下 dφ/dy 分子（乘以正数）的系数，高次在前。
    Q(y) = ζ{w_c[2y u³(u-b) + ζy²u³] + w_q[-2r(1-y)(u-b) + ζ(1-y)²u]} + κu³，u = 1-ζy。"""
    r, b = 1.0 / z, z_bar / z
    zeta = 1.0 - r
    Y = Polynomial([0.0, 1.0])
    u = Polynomial([1.0, -zeta])
    poly = zeta * (wc * (2.0 * Y * u ** 3 * (u - b) + zeta * Y ** 2 * u ** 3)
                   + wq * (-2.0 * r * (1.0 - Y) * (u - b) + zeta * (1.0 - Y) ** 2 * u)) + kappa * u ** 3
    coef = poly.coef[::-1]
    return np.trim_zeros(coef, 'f') if np.any(coef) else coef


# ---------------------------------------------------------------- 根法
def _polish(p, dp, v, lo, hi):
    for _ in range(NEWTON_STEPS):
        d = dp(v)
        if d == 0.0 or not np.isfinite(d):
            break
        step = p(v) / d
        nv = v - step
        if not (lo <= nv <= hi):
            break
        if abs(step) <= 1e-16 * max(1.0, abs(v)):
            v = nv
            break
        v = nv
    return v


def _argmin_on(coeffs, v_lo, v_hi, f, prefer_high=True):
    """在 [v_lo, v_hi]（所用坐标）上比较两个端点与全部近似实驻点，返回 (v*, f(v*), 诊断)。
    f 为向量化的目标函数；coeffs 为驻点多项式系数（高次在前）；目标值完全相等时
    prefer_high=True 取坐标较大者（x 坐标即更接近仅隔离；y 坐标传 False）。"""
    width = v_hi - v_lo
    coeffs = np.asarray(coeffs, dtype=float)
    scale = float(np.max(np.abs(coeffs))) if coeffs.size else 0.0
    cand = [(v_lo, 'lo'), (v_hi, 'hi')]
    n_roots = n_real = n_in = 0
    real_in = []
    max_res = 0.0
    if scale > 0.0 and coeffs.size > 1:
        c = coeffs / scale
        p = np.poly1d(c)
        dp = p.deriv()
        roots = np.roots(c)
        n_roots = len(roots)
        mag = np.maximum(1.0, np.abs(roots))
        n_real = int(np.sum(np.abs(roots.imag) <= IMAG_TOL_STRICT * mag))
        edge = EDGE_TOL * width
        for rt, m in zip(roots, mag):
            if abs(rt.imag) > IMAG_TOL_CANDIDATE * m:
                continue
            v = rt.real
            if not (v_lo - edge <= v <= v_hi + edge):
                continue
            v = min(max(v, v_lo), v_hi)
            v = _polish(p, dp, v, v_lo, v_hi)
            n_in += 1
            real_in.append(v)
            den = float(np.sum(np.abs(c) * np.abs(v) ** np.arange(len(c) - 1, -1, -1)))
            max_res = max(max_res, abs(float(p(v))) / max(den, 1e-300))
            cand.append((v, 'root'))
    # 合并近似重复（保留端点）
    cand.sort(key=lambda a: a[0])
    keep = []
    for v, k in cand:
        if keep and v - keep[-1][0] <= DUP_TOL * max(width, 1e-300):
            if keep[-1][1] == 'root' and k != 'root':
                keep[-1] = (v, k)
            continue
        keep.append((v, k))
    vs = np.array([v for v, _ in keep])
    vals = np.asarray(f(vs), dtype=float)
    vmin = float(np.min(vals))
    idx = [j for j in range(len(vs)) if vals[j] == vmin]
    jbest = idx[-1] if prefer_high else idx[0]
    # 近并列的容差相对于 max(|min|, 候选值的极差)：最小值接近 0 时仍有意义
    near = int(np.sum(vals <= vmin + NEAR_TIE_REL * max(abs(vmin), float(np.max(vals)) - vmin, 1e-300)))
    real_in.sort()
    gaps = np.diff(real_in) if len(real_in) > 1 else np.array([])
    min_gap = float(np.min(gaps)) / width if gaps.size and width > 0 else None
    info = dict(n_roots=n_roots, n_real=n_real, n_in_interval=n_in, n_candidates=len(vs),
                near_ties=near, kind=keep[jbest][1], max_root_residual=max_res,
                min_root_gap_rel=min_gap,
                near_double_root=bool(min_gap is not None and min_gap < DOUBLE_ROOT_GAP),
                candidates=[(float(v), k, float(val)) for (v, k), val in zip(keep, vals)])
    return float(vs[jbest]), vmin, info


@lru_cache(maxsize=400000)
def argmin_state(z, z_bar, wc, wq, kappa=0.0, x_min=0.0, h=math.inf, coordinate='auto'):
    """状态 z 上的逐状态全局最小（定理 5.1 的有限比较）。
    返回 (x*, φ(x*), 诊断)；诊断中 label ∈ {'hi','lo','int','deg'}，lo_kind/hi_kind 见 x_bounds_raw，
    y = (1-x*)/(1-1/z) 为接触率降幅占仅减少接触降幅的比例（图 7 的颜色）。"""
    lo, hi, lo_kind, hi_kind = x_bounds_raw(z, x_min, h)
    base = dict(lo_kind=lo_kind, hi_kind=hi_kind, x_lo=lo, x_hi=hi)
    if hi - lo <= DEG_TOL:
        x = 0.5 * (lo + hi)
        val = float(objective_x(x, max(z, 1.0), z_bar, wc, wq, kappa)) if z > 1.0 else 0.0
        return x, val, dict(base, label='deg', coordinate='x', kind='deg', y=None, near_ties=1)
    zeta = 1.0 - 1.0 / z
    use_y = (coordinate == 'y') or (coordinate == 'auto' and zeta < ZETA_SCALED)
    if use_y:
        y_lo, y_hi = (1.0 - hi) / zeta, (1.0 - lo) / zeta
        coeffs = stationary_poly_y(z, z_bar, wc, wq, kappa)
        f = lambda y: objective_y(y, z, z_bar, wc, wq, kappa)
        y, val, info = _argmin_on(coeffs, y_lo, y_hi, f, prefer_high=False)
        x = 1.0 - zeta * y
        # 坐标 y 的 'lo' 端是 x_hi
        kind = {'lo': 'hi', 'hi': 'lo'}.get(info['kind'], info['kind'])
    else:
        coeffs = stationary_poly_x(z, z_bar, wc, wq, kappa)
        f = lambda xx: objective_x(xx, z, z_bar, wc, wq, kappa)
        x, val, info = _argmin_on(coeffs, lo, hi, f)
        y = (1.0 - x) / zeta
        kind = info['kind']
    label = {'hi': 'hi', 'lo': 'lo', 'root': 'int'}[kind]
    info = dict(info, **base, label=label, coordinate='y' if use_y else 'x', y=y)
    return x, val, info


def make_law_opt(P, cap=None, wc=None, wq=None, kappa=0.0):
    """成本最优控制律 x(z)（J + κΔt 的逐状态最小化；κ = 0 即定理 5.1）。"""
    wc = P.wc if wc is None else float(wc)
    wq = P.wq if wq is None else float(wq)
    if not (wc > 0 and wq > 0 and math.isfinite(kappa)):
        raise ValueError('权重须为正、κ 须有限')
    x_min, h = cap_factors(P, cap)
    z_bar = P.z_bar

    def law(z):
        return argmin_state(float(z), z_bar, wc, wq, float(kappa), x_min, h)[0]

    def full(z):
        return argmin_state(float(z), z_bar, wc, wq, float(kappa), x_min, h)
    law.kind = 'opt'
    law.full = full
    law.weights = (wc, wq)
    law.kappa = kappa
    return law


def make_law_cap(P, cap, side):
    """能力约束下最快（side='upper'，c⁺）与最慢（side='lower'，c⁻）的控制律（推论 4.6）。"""
    x_min, h = cap_factors(P, cap)

    def law(z):
        lo, hi, _, _ = x_bounds_raw(float(z), x_min, h)
        return hi if side == 'upper' else lo
    law.kind = 'cap_' + side
    return law


def get_law(name, P, cap=None, wc=None, wq=None, kappa=0.0, alpha=0.5):
    """'q_only'、'c_only'、'alpha'、'opt'、'cap_upper'、'cap_lower'。"""
    if name == 'q_only':
        return law_q_only
    if name == 'c_only':
        return law_c_only
    if name == 'alpha':
        return make_law_alpha(alpha)
    if name == 'opt':
        return make_law_opt(P, cap, wc, wq, kappa)
    if name in ('cap_upper', 'cap_lower'):
        if cap is None:
            raise ValueError('cap_upper/cap_lower 需要能力约束')
        return make_law_cap(P, cap, name[4:])
    raise ValueError(name)


def linear_form(name, P, cap, z_lo, z_hi, alpha=0.5):
    """显式律在区间 (z_lo, z_hi) 上若可写成 x = A + B/z，返回 (A, B)；否则返回 None。
    用于名义时钟的闭式（x z - z̄ = A z + B - z̄ 为 z 的线性函数）。"""
    if name == 'q_only':
        return 1.0, 0.0
    if name == 'c_only':
        return 0.0, 1.0
    if name == 'alpha':
        return alpha, 1.0 - alpha
    if name in ('cap_upper', 'cap_lower'):
        x_min, h = cap_factors(P, cap)
        zm = 0.5 * (z_lo + z_hi)
        _, _, lo_kind, hi_kind = x_bounds_raw(zm, x_min, h)
        if name == 'cap_upper':
            return (1.0, 0.0) if hi_kind == 'c0' else (0.0, h)
        return (0.0, 1.0) if lo_kind == 'contact_only' else (x_min, 0.0)
    return None


# ---------------------------------------------------------------- N_x 网格核对
def grid_check(z, z_bar, wc, wq, kappa=0.0, x_min=0.0, h=math.inf, N_x=4001):
    """固定 z，在 N_x 个等距点上计算目标值，并对网格上的每个局部极小在相邻两格内用
    有界一维搜索加密；与根法的目标值比较。只作交叉核对。
    返回 dict(gap_rel = (根法值 - 网格值)/max(|网格值|, tiny)，正数表示网格更低（根法漏解），
    x_gap，n_local_min_grid)。"""
    from scipy.optimize import minimize_scalar
    x_star, v_star, info = argmin_state(float(z), z_bar, wc, wq, kappa, x_min, h)
    lo, hi = info['x_lo'], info['x_hi']
    if info['label'] == 'deg':
        return dict(z=z, gap_rel=0.0, x_gap=0.0, n_local_min_grid=1, N_x=N_x, coordinate='x')
    zeta = 1.0 - 1.0 / z
    if info['coordinate'] == 'y':
        a, b = (1.0 - hi) / zeta, (1.0 - lo) / zeta
        f = lambda v: objective_y(v, z, z_bar, wc, wq, kappa)
        to_x = lambda v: 1.0 - zeta * v
    else:
        a, b = lo, hi
        f = lambda v: objective_x(v, z, z_bar, wc, wq, kappa)
        to_x = lambda v: v
    vv = np.linspace(a, b, N_x)
    fv = f(vv)
    loc = [j for j in range(1, N_x - 1) if fv[j] <= fv[j - 1] and fv[j] <= fv[j + 1]]
    best = [(float(fv[0]), float(vv[0])), (float(fv[-1]), float(vv[-1]))]
    for j in loc:
        res = minimize_scalar(lambda v: float(f(np.array([v]))[0]), bounds=(vv[j - 1], vv[j + 1]),
                              method='bounded', options=dict(xatol=1e-14 * max(1.0, abs(vv[j]))))
        best.append((float(res.fun), float(res.x)))
        best.append((float(fv[j]), float(vv[j])))
    g_val, g_v = min(best)
    gap = (v_star - g_val) / max(abs(g_val), 1e-300)
    return dict(z=float(z), N_x=N_x, coordinate=info['coordinate'], value_roots=v_star, value_grid=g_val,
                gap_rel=float(gap), x_gap=float(abs(to_x(g_v) - x_star)),
                n_local_min_grid=len(loc) + int(fv[0] < fv[1]) + int(fv[-1] < fv[-2]))


# ---------------------------------------------------------------- N_z 网格上的结构扫描
JUMP_CLASSIFY_TOL = 1e-6    # 加密到 |Δz| ≤ 1e-14·z 后，两侧 x 之差超过它才算间断


ANOMALY_FLOOR = 1e-10      # 二阶差分异常的绝对下限（x 坐标）
ANOMALY_FACTOR = 1000.0    # 二阶差分超过其邻域中位数的这一倍数记为异常


def scan_structure(full_fn, z_a, z_b, N_z, poly_at_end=None, kinks=()):
    """在 [z_a, z_b] 的 N_z 点网格上记录 x(z) 与最优点类型（'lo'/'int'/'hi'），找出类型改变或
    x 变化异常的括区并逐个加密，返回结构变化点与陡峭点（复制自 r7 的 scan_structure 并作推广）。

    括区：(a) 相邻网格点的类型不同；(b) 类型相同但 x 的增量异常——二阶差分
    |Δx_k - (Δx_{k-1}+Δx_{k+1})/2| 是局部最大且超过 ANOMALY_FACTOR·邻域（k±10，去掉 k±2）中位数 + ANOMALY_FLOOR
    （同类型内部分支之间的小跳变、陡峭但连续的区段）；或 |Δx| > 1e-3 且超过邻域 |Δx| 中位数的 5 倍。
    - (a) 且 x 连续（内部驻点移到端点）：对“驻点多项式在该端点的值”用 brentq 求根；
      无变号或括区跨能力折点时退回二分。
    - 其余：按“更接近左侧还是右侧的 x”二分到 |Δz| ≤ 1e-14·z；两侧 x 之差 > JUMP_CLASSIFY_TOL 记为
      间断（结构变化点），否则是陡峭但连续的变化：把括区反复十等分、保留 |Δx| 最大的子区间，
      收敛到斜率最大处，记为陡峭点（只作求积分段点，并在其两侧用分级网格）。
    full_fn(z) -> (x*, φ*, 诊断)；poly_at_end(z, end) -> 驻点多项式在端点 end ∈ {'hi','lo'} 处的值。
    返回 dict(z, x, label, breakpoints=[{z, kind, method, continuous, x_left, x_right, label_left,
    label_right}], steep_points, n_brackets)。x_left 指 z 较小一侧（时间上较晚）。"""
    from scipy.optimize import brentq
    zg = np.linspace(z_a, z_b, N_z)
    res = [full_fn(float(z)) for z in zg]
    xg = np.array([r[0] for r in res])
    lab = [r[2]['label'] for r in res]
    dxs = np.diff(xg)
    dx = np.abs(dxs)
    anom = np.zeros_like(dx)
    if len(dx) > 2:
        anom[1:-1] = np.abs(dxs[1:-1] - 0.5 * (dxs[:-2] + dxs[2:]))
    nb = len(dx)
    valid = [k for k in range(nb) if lab[k] != 'deg' and lab[k + 1] != 'deg']
    label_br = {k for k in valid if lab[k] != lab[k + 1]}
    h_grid = zg[1] - zg[0] if N_z > 1 else 1.0
    kink_br = {k for k in range(nb) for kk in kinks if zg[k] - 2 * h_grid <= kk <= zg[k + 1] + 2 * h_grid}
    brackets = []
    for k in valid:
        if k in label_br:
            brackets.append((float(zg[k]), float(zg[k + 1]), 'label'))
            continue
        # 与类型改变、能力折点、退化端点相邻的括区不作异常判断（那里本来就有折角）
        if any(abs(k - j) <= 1 for j in label_br) or k in kink_br or k <= 1 or k >= nb - 1:
            continue
        # 异常：二阶差分远大于其邻域（去掉 k±2 后 k±10 范围内的中位数）——跳变或宽度小于网格的陡峭区；
        # 已被网格分辨的光滑变化，其二阶差分随 k 缓慢变化，不会被选中
        win = [j for j in range(max(1, k - 10), min(nb - 1, k + 11)) if abs(j - k) > 2]
        ref = float(np.median(anom[win])) if win else 0.0
        dref = float(np.median(dx[win])) if win else 0.0
        is_anom = (dx[k] > 1e-3 and dx[k] > 5.0 * dref) or (
            anom[k] > ANOMALY_FACTOR * ref + ANOMALY_FLOOR and anom[k] >= anom[k - 1] and anom[k] >= anom[k + 1])
        if is_anom:
            brackets.append((float(zg[k]), float(zg[k + 1]), 'jump'))
    # 退出附近（第一个网格格子之内）另用对数网格 z - z_a = h·10^{-12…0} 只查类型改变：
    # 例如 κ > 0 时 x 在 ζ = O(κ) 处由内部解切到仅隔离，可能落在第一个格子里
    if N_z > 1:
        zl = z_a + (zg[1] - z_a) * np.logspace(-12.0, 0.0, 49)
        ll = [full_fn(float(z))[2]['label'] for z in zl]
        for k in range(len(zl) - 1):
            if 'deg' not in (ll[k], ll[k + 1]) and ll[k] != ll[k + 1]:
                brackets.append((float(zl[k]), float(zl[k + 1]), 'label'))
        brackets.sort(key=lambda b: b[0])

    def bisect(za, zb):
        xa = full_fn(za)[0]
        xb = full_fn(zb)[0]
        lo, hi = za, zb
        while hi - lo > 1e-14 * hi:
            m = 0.5 * (lo + hi)
            if m <= lo or m >= hi:
                break
            xm = full_fn(m)[0]
            if abs(xm - xa) <= abs(xm - xb):
                lo = m
            else:
                hi = m
        return lo, hi

    def zoom(lo, hi):
        while hi - lo > 1e-13 * hi:
            zz = np.linspace(lo, hi, 11)
            xs = np.array([full_fn(float(z))[0] for z in zz])
            k_ = int(np.argmax(np.abs(np.diff(xs))))
            lo, hi = float(zz[k_]), float(zz[k_ + 1])
        return 0.5 * (lo + hi)

    # 相邻（相隔不超过两格）的异常括区并成一组：每组只保留 |Δx| 最大的括区，组的范围留给 zoom
    grouped, run = [], []
    for br in brackets:
        if br[2] != 'jump':
            grouped.append((br[0], br[1], 'label', br[0], br[1]))
            continue
        if run and br[0] - run[-1][1] > 2.5 * (zg[1] - zg[0]):
            best = max(run, key=lambda b: abs(full_fn(b[1])[0] - full_fn(b[0])[0]))
            grouped.append((best[0], best[1], 'jump', run[0][0], run[-1][1]))
            run = []
        run.append(br)
    if run:
        best = max(run, key=lambda b: abs(full_fn(b[1])[0] - full_fn(b[0])[0]))
        grouped.append((best[0], best[1], 'jump', run[0][0], run[-1][1]))

    bps, steep = [], []
    for za, zb, kind, run_lo, run_hi in grouped:
        la, lb = full_fn(za)[2]['label'], full_fn(zb)[2]['label']
        zloc, method = None, 'bisect'
        crosses_kink = any(za < k_ < zb for k_ in kinks)
        if kind == 'label' and poly_at_end is not None and 'int' in (la, lb) and not crosses_kink:
            end = la if la != 'int' else lb
            g = lambda z: poly_at_end(z, end)
            h_ = zb - za
            for lo_, hi_ in ((za, zb), (max(z_a, za - h_), min(z_b, zb + h_))):
                if any(lo_ < k_ < hi_ for k_ in kinks):
                    continue
                if g(lo_) * g(hi_) < 0:
                    zc = brentq(g, lo_, hi_, xtol=1e-15, rtol=1e-15)
                    xl, xr = full_fn(zc * (1 - 1e-12))[0], full_fn(zc * (1 + 1e-12))[0]
                    # 还须确认该点的选择就是这个端点：否则（例如端点驻点处两侧都已选内部解，真正的切换是别处的
                    # 跳变）不能把它当作连续切换，退回二分
                    xc, _, ic = full_fn(zc)
                    x_end = ic['x_hi'] if end == 'hi' else ic['x_lo']
                    if abs(xr - xl) <= JUMP_CLASSIFY_TOL and abs(xc - x_end) <= JUMP_CLASSIFY_TOL:
                        zloc, method = zc, 'brentq_endpoint_stationary'
                    break
        if zloc is None:
            lo, hi = bisect(za, zb)
            zloc = 0.5 * (lo + hi)
            x_left, x_right = full_fn(lo)[0], full_fn(hi)[0]
            l_left, l_right = full_fn(lo)[2]['label'], full_fn(hi)[2]['label']
        else:
            x_left, x_right = full_fn(zloc * (1 - 1e-12))[0], full_fn(zloc * (1 + 1e-12))[0]
            # 类型在 ±1e-6 处读取：紧邻连续切换点时内部极小与端点的目标值之差是 Δx 的二次小量，会被舍入淹没
            l_left, l_right = full_fn(zloc * (1 - 1e-6))[2]["label"], full_fn(zloc * (1 + 1e-6))[2]["label"]
        continuous = abs(x_right - x_left) <= JUMP_CLASSIFY_TOL
        if kind == 'jump' and continuous:
            steep.append(zoom(run_lo, run_hi))
            continue
        bps.append(dict(z=float(zloc), kind=kind, method=method, continuous=bool(continuous),
                        label_left=l_left, label_right=l_right, x_left=float(x_left), x_right=float(x_right)))
    # 合并落在同一位置的括区（相邻括区可能收敛到同一点）
    merged = []
    for b in sorted(bps, key=lambda b: b['z']):
        if merged and abs(b['z'] - merged[-1]['z']) <= 1e-11 * b['z']:
            continue
        merged.append(b)
    steep_m = []
    for s in sorted(steep):
        if all(abs(s - b['z']) > 1e-9 * s for b in merged) and (not steep_m or abs(s - steep_m[-1]) > 1e-9 * s):
            steep_m.append(float(s))
    return dict(z=zg, x=xg, label=lab, breakpoints=merged, steep_points=steep_m, n_brackets=len(brackets), n_groups=len(grouped))


def terminal_share(x, z):
    """接触减少的分担比例 y = (1 - c/c0)/(1 - S_c/S) = (1-x)/(1-1/z)。"""
    return (1.0 - x) / (1.0 - 1.0 / z)


def z_sw_formula(z_bar):
    """命题 5.3 的 S_sw/S_c = (3 + √(9 - 8 z̄))/2（局部性质的分界）。"""
    return 0.5 * (3.0 + math.sqrt(9.0 - 8.0 * z_bar))
