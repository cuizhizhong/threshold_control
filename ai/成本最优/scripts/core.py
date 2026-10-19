"""成本最优控制（不考虑能力约束）的逐状态精确求解与结构分析。
记号：U=S/S_c，u=cS/(c0 S_c)=(1-q0)/(1-q) in [1,U]，b=Sbar/S_c，r=w_q/w_c。
每个状态的候选 = 端点 {1, U} + 五次驻点方程在 (1,U) 内的全部实根（与论文定理 5.1 相同的有限比较）。"""
import numpy as np
import sympy as sp
from scipy.optimize import brentq

# ---------- 五次驻点多项式的系数（符号推导一次，之后数值求根） ----------
_u, _U, _b, _r = sp.symbols('u U b r')
_poly = sp.Poly(sp.expand((-2*(_U-_u)*_u**3 + 2*_r*_U**2*(_u-1))*(_u-_b)
                          - (_U-_u)**2*_u**3 - _r*_U**2*_u*(_u-1)**2), _u)
_coef_funcs = [sp.lambdify((_U, _b, _r), c, 'numpy') for c in _poly.all_coeffs()]
assert _poly.degree() == 5

def G(u, U, b, r):
    return ((1 - u/U)**2 + r*(1 - 1/u)**2) / (u - b)

def stationary_roots(U, b, r, tol=1e-12):
    c = [float(f(U, b, r)) for f in _coef_funcs]
    rt = np.roots(c)
    rt = rt[np.abs(rt.imag) < 1e-9].real
    return np.sort(rt[(rt > 1 + tol) & (rt < U - tol)])

def candidates(U, b, r):
    return np.concatenate([[1.0, U], stationary_roots(U, b, r)])

def argmin_exact(U, b, r):
    cand = candidates(U, b, r)
    vals = G(cand, U, b, r)
    i = int(np.argmin(vals))
    return cand[i], vals[i], cand, vals

# ---------- 闭式量 ----------
def Usw(b):  return (3 + np.sqrt(9 - 8*b)) / 2
def rhat(b): s = np.sqrt(9 - 8*b); return ((3 + s)/(1 + s))**2
def rinf(b): return 27.0 / (9 - 8*b)                    # 分支断开阈值（u=3/2 处 C(u)=u）
def rloc(b):                                            # S_sw 处二阶（局部）阈值
    Us = Usw(b); return 2*Us*(Us - b)/((Us - 1)*(2*Us - 3))

def C_of(u, b, r): return r*(u - 1)*(3*u - u**2 - 2*b)/u**2
def vs_of(u, b, r):
    C = C_of(u, b, r); D = (u - b)**2 - (u - 2*b)*C
    return C/((u - b) + np.sqrt(np.maximum(D, 0)))
def Us_branch(u, b, r):
    """内部驻点曲线 U_s(u)=u/(1-v_s(u))；C(u)>=u 处无内部驻点，返回 nan。"""
    C = C_of(u, b, r); v = vs_of(u, b, r)
    out = u/(1 - v)
    return np.where(C < u, out, np.nan)

def Pfold(u, b, r):
    X = u**3 - 6*u**2 + 6*u + 2*b*(3*u - 4)
    return (r*X + u**3)**2 - 4*r*b**2*u**2*(2*u - 3)

def rA(b, n=20001):
    """尖点阈值：P(u,b,r)=0 关于 r 的最小正根在 u in (1,U_sw) 上的最小值。"""
    us = np.linspace(1, Usw(b), n)[1:-1]
    X = us**3 - 6*us**2 + 6*us + 2*b*(3*us - 4)
    A = X**2; B = 2*X*us**3 - 4*b**2*us**2*(2*us - 3); C = us**6
    disc = B*B - 4*A*C
    best = np.inf; ubest = np.nan
    ok = (A > 0) & (disc >= 0)
    for sgn in (-1, 1):
        rt = np.where(ok, (-B + sgn*np.sqrt(np.where(ok, disc, 0)))/(2*np.where(ok, A, 1)), np.inf)
        rt = np.where(rt > 0, rt, np.inf)
        i = int(np.argmin(rt))
        if rt[i] < best: best, ubest = rt[i], us[i]
    # 局部细化
    from scipy.optimize import minimize_scalar
    def f(uu):
        X = uu**3 - 6*uu**2 + 6*uu + 2*b*(3*uu - 4)
        A = X**2; B = 2*X*uu**3 - 4*b**2*uu**2*(2*uu - 3); C = uu**6
        d = B*B - 4*A*C
        if d < 0: return 1e9
        rts = [(-B - np.sqrt(d))/(2*A), (-B + np.sqrt(d))/(2*A)]
        rts = [x for x in rts if x > 0]
        return min(rts) if rts else 1e9
    h = (Usw(b) - 1)/n*5
    res = minimize_scalar(f, bounds=(max(1, ubest - h), min(Usw(b), ubest + h)), method='bounded',
                          options={'xatol': 1e-13})
    return (res.fun, res.x) if res.fun < best else (best, ubest)

def rg(U, b):
    """仅隔离与内部点相切等值时的 r（U>=U_sw）。接触点满足三次方程。"""
    lo = 2*U/(2*U - 1)
    # (U-1)^2 u^3 - 2(U-b)[(2U-1)u^2 - U(U+1)u + U^2] = 0
    c = [(U - 1)**2, -2*(U - b)*(2*U - 1), 2*(U - b)*U*(U + 1), -2*(U - b)*U**2]
    rt = np.roots(c); rt = rt[np.abs(rt.imag) < 1e-10].real
    rt = rt[(rt > lo) & (rt < U)]
    if rt.size == 0: return np.nan, np.nan
    rv = rt**3/((2*U - 1)*rt - 2*U)
    i = int(np.argmin(rv))
    return rv[i], rt[i]

def Uglob(r, b):
    """仅隔离段的起点 U_glob(r)：r<=rhat 时为 U_sw，否则解 rg(U,b)=r。"""
    if r <= rhat(b): return Usw(b), np.nan
    f = lambda U: rg(U, b)[0] - r
    hi = max(b + r*(1 - b), Usw(b)) * 1.5 + 1
    while f(hi) < 0: hi *= 2
    U0 = brentq(f, Usw(b)*(1 + 1e-12), hi, xtol=1e-13)
    return U0, rg(U0, b)[1]

# ---------- 跳跃检测与精确定位 ----------
def newton_track(u0, U, b, r):
    """从 u0 出发在状态 U 上找最近的驻点（用于跟踪局部最小分支）。"""
    rts = stationary_roots(U, b, r)
    cand = np.concatenate([rts, [U]]) if U >= Usw(b) - 1e-12 else rts
    if cand.size == 0: return np.nan
    return cand[np.argmin(np.abs(cand - u0))]

def scan(b, r, Umax, n=4000):
    Ug = 1 + (Umax - 1)*np.linspace(0, 1, n + 1)[1:]
    us = np.array([argmin_exact(U, b, r)[0] for U in Ug])
    return Ug, us

def locate_jumps(b, r, Umax, n=4000, jump_tol=None):
    Ug, us = scan(b, r, Umax, n)
    h = Ug[1] - Ug[0]
    jt = jump_tol if jump_tol else 50*h
    jumps = []
    for k in range(len(Ug) - 1):
        if abs(us[k + 1] - us[k]) > jt:
            UL, UR = Ug[k], Ug[k + 1]
            uL, uR = us[k], us[k + 1]
            # 二分：判断全局最小更接近左分支还是右分支
            for _ in range(60):
                Um = 0.5*(UL + UR)
                um = argmin_exact(Um, b, r)[0]
                if abs(um - uL) < abs(um - uR): UL, uL = Um, um
                else: UR, uR = Um, um
            if abs(uR - uL) > 1e-6:          # 二分后两侧仍分离才是真跳跃（陡峭的连续段会收拢）
                jumps.append(dict(U=0.5*(UL + UR), u_left=uL, u_right=uR,
                                  x_left=uL/UL, x_right=uR/UR))
    return Ug, us, jumps
