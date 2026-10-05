"""规定感染平台类的数值候选比较、分段时间开环及完整 SIQR 核查。

冻结来源和历史输出只读。计算坐标 S/Sc 不改写论文 s=S/N；实根枚举
是浮点计算，不是严格区间根隔离。完整 ODE 控制只访问预先计算的名义
时间解，绝不访问实际积分状态以重新调节控制。
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from numpy.polynomial import Polynomial
from scipy.integrate import quad, solve_ivp
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq, minimize_scalar

ROOT = Path(__file__).resolve().parents[2]
BASELINE_JSON = "joint_control/threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json"
XIAN_REFERENCE = "reproducibility/results/20261003_release_final/xian/reference.json"
ACCEPTANCE = json.loads((Path(__file__).parent / "acceptance.json").read_text(encoding="utf-8"))
X = Polynomial([0.0, 1.0])


@dataclass(frozen=True)
class Params:
    N: float
    S0: float
    I0: float
    beta: float
    gamma: float
    delta_q: float
    c0: float
    q0: float
    eta: float
    wc: float = 1.0
    wq: float = 2.0
    Sq0: float = 0.0
    Iq0: float = 0.0
    R0: float = 0.0

    @property
    def Sc(self):
        return self.gamma*self.N/(self.beta*self.c0*(1-self.q0))

    @property
    def Sbar(self):
        return (1-self.beta)*self.gamma*self.N/(self.beta*self.c0)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_inputs(root=ROOT, baseline_path=None, xian_reference=None):
    root = Path(root).resolve()
    bp = Path(baseline_path or root/BASELINE_JSON).resolve()
    xp = Path(xian_reference or root/XIAN_REFERENCE).resolve()
    base = json.loads(bp.read_text(encoding="utf-8"))
    ref = json.loads(xp.read_text(encoding="utf-8"))
    b = dict(base["parameters"])
    b.update(base.get("other_initial_states", {}))
    px = dict(ref["parameters"])
    px.update(I0=ref["I0_abs"], S0=px["N"]-ref["I0_abs"], eta=.002*px["N"],
              Sq0=0.0, Iq0=0.0, R0=ref.get("fit", {}).get("R0_initial", 0.0), wc=1.0, wq=2.0)
    cases = {"baseline": Params(**b), "xian": Params(**px)}
    for p in cases.values():
        validate_inputs(p)
    return cases, ref, {"baseline": {"path": str(bp), "sha256": sha(bp)},
                        "xian_reference": {"path": str(xp), "sha256": sha(xp)}}


def validate_inputs(p):
    vals = asdict(p)
    if not all(np.isfinite(v) for v in vals.values()):
        raise ValueError("参数或初值不是有限数")
    if not (p.N > 0 and p.c0 > 0 and 0 < p.beta <= 1 and p.gamma > 0 and p.delta_q > 0
            and 0 <= p.q0 < 1 and p.wc > 0 and p.wq > 0):
        raise ValueError("参数未满足本文正性与比例假设")
    if min(p.S0, p.I0, p.Sq0, p.Iq0, p.R0) < 0 or p.I0 <= 0:
        raise ValueError("初值非法")
    if abs(p.S0+p.I0+p.Sq0+p.Iq0+p.R0-p.N) > ACCEPTANCE["mass_absolute_persons"]:
        raise ValueError("初始总人口不守恒")
    if not p.S0 > p.Sc > p.Sbar or p.eta <= 1 or p.I0 >= p.eta:
        raise ValueError("需要 Sc<S0、I0<eta 及 eta>1 的严格触发/下降清零算例")


def basics(p):
    """归一化稳定首次积分；不重新拟合，也不读取取整正文参数。"""
    a = p.beta+p.q0*(1-p.beta)
    k = p.beta*(1-p.q0)/a
    rho = p.gamma/(p.c0*a)
    s0, i0, sc, sb = p.S0/p.N, p.I0/p.N, p.Sc/p.N, p.Sbar/p.N
    theta = p.eta/p.N
    def ix(loss):
        return i0+k*loss+rho*np.log1p(-loss/s0)
    peak = float(ix(s0-sc))*p.N
    if not p.I0 < p.eta < peak:
        raise ValueError("阈值不是常规轨道上的严格上升触发")
    loss = brentq(lambda z: ix(z)-theta, 0., s0-sc, xtol=1e-15, rtol=1e-14)
    ss = s0-loss
    scale = i0/(k-rho/s0)
    zmax = math.log1p(loss/scale)
    def before(z):
        u = scale*math.expm1(z)
        return scale*math.exp(z)/(p.c0*a*(s0-u)*ix(u))
    t1 = quad(before, 0., zmax, epsabs=2e-10, epsrel=2e-11, limit=500)[0]
    def tail_i(s):
        return theta+k*(sc-s)+rho*math.log(s/sc)
    se = brentq(lambda s: tail_i(s)-1/p.N, sc*1e-10, sc*(1-1e-14), xtol=1e-15, rtol=1e-14)
    tail = quad(lambda s: 1/(p.c0*a*s*tail_i(s)), se, sc, epsabs=2e-9, epsrel=2e-10, limit=500)[0]
    return {"Sc": p.Sc, "Sbar": p.Sbar, "Sstar": ss*p.N, "t1": t1,
            "S_end": se*p.N, "tail": tail, "routine_peak": peak,
            "pre_tail_new_infections": p.N*p.beta/a*(loss+sc-se)}


def bounds(S, p, cmin=0., qcap=None):
    if cmin < 0 or cmin > p.c0 or (qcap is not None and not p.q0 <= qcap < 1):
        raise ValueError("能力参数非法")
    r = p.Sc/S
    lo = max(r, cmin/p.c0)
    hi = min(1., (1-p.q0)*r/(1-qcap)) if qcap is not None else 1.
    if lo > hi + 1e-12:
        raise ValueError("能力限制下允许区间为空")
    return lo, hi


def capacity_classification(p, entry, cmin, qcap):
    x = p.Sc/entry["Sstar"]
    single_q = qcap >= 1-(1-p.q0)*x
    single_c = cmin <= p.c0*x
    feasible = cmin*(1-qcap) <= p.c0*(1-p.q0)*x + 1e-13*p.c0
    return {"classification": "single_feasible" if feasible and (single_q or single_c)
            else "joint_required" if feasible else "infeasible_at_trigger",
            "quarantine_only_feasible": bool(single_q), "contact_only_feasible": bool(single_c),
            "joint_feasible": bool(feasible)}


def objective(x, S, p, wc=None, wq=None, kappa=0.):
    wc, wq = p.wc if wc is None else wc, p.wq if wq is None else wq
    r, b = p.Sc/S, p.Sbar/S
    return (wc*(1-x)**2+wq*(1-r/x)**2+kappa)/(x-b)


def candidates(S, p, wc=None, wq=None, kappa=0., cmin=0., qcap=None, force_coordinate=None):
    """比较端点及数值实驻点。κ改变驻点多项式，而非只改候选值。"""
    wc, wq = p.wc if wc is None else float(wc), p.wq if wq is None else float(wq)
    if wc <= 0 or wq <= 0 or not np.isfinite(kappa):
        raise ValueError("成本权重或乘子非法")
    if S < p.Sc*(1-1e-13):
        raise ValueError("状态低于平台退出状态")
    if S <= p.Sc:
        return {"x": 1., "y": None, "branch": "degenerate", "records": [],
                "near_tie_count": 1, "root_residual": 0., "coordinate": "endpoint"}
    r, b = p.Sc/S, p.Sbar/S
    z = 1-r
    lo, hi = bounds(S, p, cmin, qcap)
    shrinking = z < 1e-4 if force_coordinate is None else force_coordinate == "y"
    if hi-lo <= 1e-14:
        x = .5*(lo+hi)
        return {"x": x, "y": (1-x)/z, "branch": "degenerate", "records": [],
                "near_tie_count": 1, "root_residual": 0., "coordinate": "endpoint"}
    if shrinking:
        yl, yh = max(0., (1-hi)/z), min(1., (1-lo)/z)
        u = Polynomial([1., -z])
        poly0 = (wc*(2*X*u**3*(u-b)+z*X**2*u**3)
                 +wq*(-2*r*(1-X)*(u-b)+z*(1-X)**2*u))
        poly = z*poly0+kappa*u**3
        endpoints = [(yl, "upper"), (yh, "lower")]
        to_x = lambda v: 1-z*v
        def value(v):
            uval = 1-z*v
            return (z*z*(wc*v*v+wq*(1-v)**2/uval**2)+kappa)/(uval-b)
        imaginary_tol = 1e-9
        vl, vh = yl, yh
    else:
        # 逐系数写出同一五次式，避免相图百万次调用中的对象乘法开销。
        poly = Polynomial([2*b*r*r*wq, -r*(3*r+2*b)*wq, 4*r*wq,
                           wc*(2*b-1)-wq-kappa, -2*b*wc, wc])
        endpoints = [(lo, "lower"), (hi, "upper")]
        to_x = lambda v: v
        value = lambda v: objective(v, S, p, wc, wq, kappa)
        imaginary_tol = 1e-8
        vl, vh = lo, hi
    scale = max(float(np.max(np.abs(poly.coef))), 1e-300)
    poly = poly/scale
    records = [{"coordinate": float(v), "x": float(to_x(v)), "value": float(value(v)),
                "branch": branch, "root_residual": 0.} for v, branch in endpoints]
    for record in records:
        deriv = float(poly(record["coordinate"]))
        coordinate_is_left = abs(record["coordinate"]-vl) <= 1e-12
        record["local_minimum"] = None if abs(deriv) <= 1e-10 else bool(deriv > 0 if coordinate_is_left else deriv < 0)
        record["local_test"] = "原导数单侧符号；近零不分类"
    roots = []
    for rr in poly.roots():
        if abs(rr.imag) <= imaginary_tol*(1+abs(rr.real)) and vl-1e-10 <= rr.real <= vh+1e-10:
            v = float(np.clip(rr.real, vl, vh))
            if all(abs(v-a) > 1e-10 for a in roots):
                roots.append(v)
    for j, v in enumerate(sorted(roots)):
        den = max(sum(abs(a)*abs(v)**k for k, a in enumerate(poly.coef)), 1e-300)
        residual = float(abs(poly(v))/den)
        # 清分母后的根还须回代原分式导数的代数等价分子；不接受伪根。
        if residual > ACCEPTANCE["root_normalized_residual"]:
            raise ArithmeticError("驻点根残差超限")
        if min(abs(v-vl), abs(v-vh)) <= 1e-10:
            continue
        if shrinking:
            uval = 1-z*v
            H = wc*v*v+wq*(1-v)**2/uval**2
            Hp = 2*wc*v-2*wq*r*(1-v)/uval**3
            n, dn = z*z*H+kappa, z*z*Hp
            first, second = dn*(uval-b), z*n
            raw_original_residual = abs(first+second)/max(abs(first)+abs(second), 1e-300)
            # 原导数分子按两种成本分项稳定分组；避免 Hp 的 O(z) 消减
            # 又被近退出相对尺度放大为虚假的残差。没有用poly(v)替代。
            parts = [z*wc*(2*v*(uval-b)+z*v*v),
                     z*wq*(-2*r*(1-v)*(uval-b)/uval**3+z*(1-v)**2/uval**2), kappa]
            original_residual = abs(sum(parts))/max(sum(abs(t) for t in parts), 1e-300)
        else:
            xx = to_x(v)
            n = wc*(1-xx)**2+wq*(1-r/xx)**2+kappa
            dn = 2*wc*(xx-1)+2*wq*r*(xx-r)/xx**3
            first, second = dn*(xx-b), n
            original_residual = abs(first-second)/max(abs(first)+abs(second), 1e-300)
        records.append({"coordinate": v, "x": float(to_x(v)), "value": float(value(v)),
                        "branch": "interior", "root_id": j, "root_residual": residual,
                        "local_minimum": None if abs(float(poly.deriv()(v))) <= 1e-10 else bool(poly.deriv()(v) > 0),
                        "local_test": "原目标在驻点的二阶符号；正分母清除后等价导数，近零不分类",
                        "original_derivative_residual": float(original_residual),
                        "raw_cancellation_sensitive_derivative_residual": float(raw_original_residual) if shrinking else float(original_residual)})
    best = min(records, key=lambda a: (a["value"], a["x"]))
    gap = ACCEPTANCE["near_tie_objective_relative"]*max(1., abs(best["value"]))
    return {"x": best["x"], "y": float(best["coordinate"]) if shrinking else float((1-best["x"])/z),
            "branch": best["branch"], "records": records,
            "near_tie_count": sum(a["value"]-best["value"] <= gap for a in records),
            "root_residual": max(a["root_residual"] for a in records),
            "coordinate": "scaled_y" if shrinking else "x", "objective": best["value"]}


def grid_check(S, p, wc=1., wq=2., kappa=0., cmin=0., qcap=None, nx=4001):
    """独立细网格及每个局部极小区间加密，非单次全区间bounded。"""
    exact = candidates(S, p, wc, wq, kappa, cmin, qcap)
    lo, hi = bounds(S, p, cmin, qcap)
    z, r, b = 1-p.Sc/S, p.Sc/S, p.Sbar/S
    if z <= 0 or hi-lo < 1e-14:
        return {"S": S, "passed": True, "objective_gap": 0., "x_gap": 0., "local_minima": 1}
    yl, yh = (1-hi)/z, (1-lo)/z
    yy = np.linspace(yl, yh, nx)
    def f(y):
        u = 1-z*y
        return (z*z*(wc*y*y+wq*(1-y)**2/u**2)+kappa)/(u-b)
    vals = f(yy)
    loc = np.flatnonzero((vals[1:-1] <= vals[:-2]) & (vals[1:-1] <= vals[2:]))+1
    choices = [(float(vals[0]), yy[0]), (float(vals[-1]), yy[-1])]
    for j in loc:
        opt = minimize_scalar(f, bounds=(yy[j-1], yy[j+1]), method="bounded", options={"xatol": 1e-13})
        choices.append((float(opt.fun), float(opt.x)))
    val, gy = min(choices)
    exval = f(exact["y"])
    gap = float(abs(val-exval))
    return {"S": float(S), "kappa": float(kappa), "weight_ratio": float(wq/wc),
            "objective_gap": gap, "x_gap": float(abs(1-z*gy-exact["x"])),
            "local_minima": int(len(loc)+(vals[0] < vals[1])+(vals[-1] < vals[-2])),
            "candidate_count": len(exact["records"]), "near_tie_count": exact["near_tie_count"],
            "passed": bool(gap < ACCEPTANCE["independent_grid_objective_relative"]*max(1., abs(val)))}


class Policy:
    def __init__(self, p, entry, name, state, x, *, wc=1., wq=2., kappa=0., cmin=0., qcap=None, switches=None, diagnostics=None):
        self.p, self.entry, self.name = p, entry, name
        self.wc, self.wq, self.kappa = wc, wq, kappa
        self.cmin, self.qcap = cmin, qcap
        self.state, self.values = np.asarray(state), np.asarray(x)
        self.switches = switches or []
        self.diagnostics = diagnostics or {}
        cuts = [p.Sc]+[v["S"] for v in self.switches]+[entry["Sstar"]]
        # λ的上下边界含max/min折角，必须在构造插值之前分段，不只是求积时分段。
        if cmin > 0:
            cuts.append(p.c0*p.Sc/cmin)
        if qcap is not None:
            cuts.append((1-p.q0)*p.Sc/(1-qcap))
        cuts = sorted(set(v for v in cuts if p.Sc <= v <= entry["Sstar"]))
        self.pieces = []
        for left, right in zip(cuts, cuts[1:]):
            xx = self.state[(self.state > left) & (self.state < right)]
            xx = np.r_[left, xx, right]
            if name in ("contact_only", "quarantine_only", "alpha_0.5") or name.startswith("alpha_"):
                vv = self._explicit(xx)
            elif name in ("capacity_lower", "capacity_upper"):
                vv = np.asarray([bounds(s, p, cmin, qcap)[0 if name == "capacity_lower" else 1] for s in xx])
            else:
                vv = np.interp(xx, self.state, self.values)
                # 几何折点未必在原采样节点上；用该S的实际候选，不跨折角线性插值端点。
                for index in (0, -1):
                    vv[index] = candidates(float(xx[index]), p, wc, wq, kappa, cmin, qcap)["x"]
                for switch in self.switches:
                    if abs(left-switch["S"]) < 1e-7:
                        vv[0] = switch["x_high_S"]
                    if abs(right-switch["S"]) < 1e-7:
                        vv[-1] = switch["x_low_S"]
            endpoint_branch = None
            if name == "minimum_cost":
                bb = np.asarray([bounds(float(S), p, cmin, qcap) for S in xx])
                if np.max(abs(vv-bb[:, 0])) <= 1e-10:
                    endpoint_branch = "lower"
                elif np.max(abs(vv-bb[:, 1])) <= 1e-10:
                    endpoint_branch = "upper"
            bb = np.asarray([bounds(float(S), p, cmin, qcap) for S in xx])
            width = bb[:, 1]-bb[:, 0]
            fraction = np.divide(vv-bb[:, 0], width, out=np.zeros_like(vv), where=width > 1e-14)
            if name == "minimum_cost":
                for j, S in enumerate(xx):
                    z = 1-p.Sc/S
                    if 0 < z < 1e-4 and width[j] > 0:
                        # 使用实际缩放根而非1-x的消减结果构造可行份额。
                        selected = candidates(float(S), p, wc, wq, kappa, cmin, qcap, force_coordinate="y")
                        yl, yh = (1-bb[j, 1])/z, (1-bb[j, 0])/z
                        fraction[j] = (yh-selected["y"])/(yh-yl)
            valid = np.flatnonzero(width > 1e-14)
            for j in np.flatnonzero(width <= 1e-14):
                fraction[j] = fraction[valid[np.argmin(abs(valid-j))]] if len(valid) else 0.
            if np.any(fraction < -1e-8) or np.any(fraction > 1+1e-8):
                bad = np.flatnonzero((fraction < -1e-8) | (fraction > 1+1e-8))
                raise ArithmeticError(f"候选分段数据的允许区间份额非法: kappa={kappa}, "
                                      f"S={xx[bad].tolist()}, fraction={fraction[bad].tolist()}")
            fraction = np.clip(fraction, 0., 1.)
            self.pieces.append({"lo": float(left), "hi": float(right), "interpolator": PchipInterpolator(xx, vv), "nodes": xx,
                                "fraction_interpolator": PchipInterpolator(xx, fraction), "endpoint_branch": endpoint_branch})

    def _explicit(self, S):
        if self.name == "contact_only":
            return self.p.Sc/S
        if self.name == "quarantine_only":
            return np.ones_like(S)
        alpha = float(self.name.removeprefix("alpha_"))
        return alpha+(1-alpha)*self.p.Sc/S

    def x(self, S, side="low"):
        S = float(np.clip(S, self.p.Sc, self.entry["Sstar"]))
        if self.name in ("contact_only", "quarantine_only") or self.name.startswith("alpha_"):
            return float(self._explicit(S))
        if self.name.startswith("capacity_"):
            return bounds(S, self.p, self.cmin, self.qcap)[0 if self.name == "capacity_lower" else 1]
        if S == self.p.Sc:
            return 1.
        for part in self.pieces:
            if S <= part["hi"]:
                return self.local_x(S, part)
        raise ArithmeticError("控制状态不在定义区间")

    def local_x(self, S, part):
        S = float(np.clip(S, part["lo"], part["hi"]))
        if self.name in ("contact_only", "quarantine_only") or self.name.startswith("alpha_") or self.name.startswith("capacity_"):
            return self.x(S)
        if part.get("endpoint_branch"):
            return bounds(S, self.p, self.cmin, self.qcap)[0 if part["endpoint_branch"] == "lower" else 1]
        lo, hi = bounds(S, self.p, self.cmin, self.qcap)
        fraction = float(part["fraction_interpolator"](S))
        if fraction < -1e-10 or fraction > 1+1e-10:
            raise ArithmeticError("分段可行份额插值越出[0,1]")
        return lo+(hi-lo)*float(np.clip(fraction, 0., 1.))


def _locate_switch(p, left, right, a, b, wc, wq, kappa, cmin, qcap):
    ax, bx = a["x"], b["x"]
    tol = max(ACCEPTANCE["switch_absolute_S"], ACCEPTANCE["switch_relative_S"]*p.Sc)
    endpoint = a["branch"] if a["branch"] in ("lower", "upper") else b["branch"] if b["branch"] in ("lower", "upper") else None
    # 连续的端点驻点合并以端点导数=0定位，不能以已合并候选的零目标差定位。
    if endpoint is not None and abs(ax-bx) < .025:
        def endpoint_derivative(S):
            r, bb = p.Sc/S, p.Sbar/S
            lo, hi = bounds(S, p, cmin, qcap)
            x = lo if endpoint == "lower" else hi
            n = wc*(1-x)**2+wq*(1-r/x)**2+kappa
            dn = 2*wc*(x-1)+2*wq*r*(x-r)/x**3
            return dn*(x-bb)-n
        dl, dr = endpoint_derivative(left), endpoint_derivative(right)
        if dl*dr <= 0 and dl != dr:
            state = brentq(endpoint_derivative, left, right, xtol=tol, rtol=1e-14)
            l, rr = max(left, state-tol*4), min(right, state+tol*4)
            # 左右样本属于不同S，不能复制其x至精确分段端点：凸边界会因此被跨越。
            at_state = bounds(state, p, cmin, qcap)[0 if endpoint == "lower" else 1]
            return {"S": float(state), "S_interval": [float(l), float(rr)],
                    "x_low_S": float(at_state), "x_high_S": float(at_state),
                    "jump": False, "method": "端点原导数零点；连续合并而非目标同值区间"}
    def pair(S):
        rec = candidates(S, p, wc, wq, kappa, cmin, qcap)["records"]
        ra = min(rec, key=lambda z: abs(z["x"]-ax))
        rb = min(rec, key=lambda z: abs(z["x"]-bx))
        return ra, rb
    def diff(S):
        u, v = pair(S)
        if u is v:
            # 第二驻点尚未出现时，最近分支映射可能都落在同一根；其0差不是交叉。
            return np.nan
        return u["value"]-v["value"]
    dl, dr = diff(left), diff(right)
    state = None
    if np.isfinite(dl) and np.isfinite(dr) and dl*dr <= 0 and dl != dr:
        try:
            state = brentq(diff, left, right, xtol=tol, rtol=1e-14)
        except ValueError:
            # 括号内有候选分支缺失时，回到实际全局选中分支定位，不能制造假目标差。
            state = None
    if state is not None:
        l, r = max(left, state-tol*4), min(right, state+tol*4)
    else:
        l, r = left, right
        for _ in range(60):
            if r-l <= tol:
                break
            mid = (l+r)/2
            m = candidates(mid, p, wc, wq, kappa, cmin, qcap)
            if abs(m["x"]-ax) < abs(m["x"]-bx):
                l = mid
            else:
                r = mid
        state = (l+r)/2
    low_near = candidates(l, p, wc, wq, kappa, cmin, qcap)["x"]
    high_near = candidates(r, p, wc, wq, kappa, cmin, qcap)["x"]
    at_state = candidates(state, p, wc, wq, kappa, cmin, qcap)["records"]
    low = min(at_state, key=lambda row: abs(row["x"]-low_near))["x"]
    high = min(at_state, key=lambda row: abs(row["x"]-high_near))["x"]
    return {"S": float(state), "S_interval": [float(l), float(r)], "x_low_S": low,
            "x_high_S": high, "jump": bool(abs(high-low) > 1e-5),
            "method": "不同候选目标值交叉/缺分支时选中分支二分；同一根零差不作交叉"}


def build_profile(p, entry=None, name="minimum_cost", *, wc=None, wq=None, kappa=0., cmin=0., qcap=None, ns=8001):
    entry = basics(p) if entry is None else entry
    wc, wq = p.wc if wc is None else wc, p.wq if wq is None else wq
    # 退出附近补对数点，不用 Sc 的 0/0 理论值来验证份额。
    states = np.unique(np.r_[np.linspace(p.Sc, entry["Sstar"], ns), p.Sc/(1-np.asarray(ACCEPTANCE["near_exit_z"]))])
    states = states[(states >= p.Sc) & (states <= entry["Sstar"])]
    if name in ("contact_only", "quarantine_only") or name.startswith("alpha_"):
        x = np.ones_like(states) if name == "quarantine_only" else p.Sc/states if name == "contact_only" else float(name[6:])+(1-float(name[6:]))*p.Sc/states
        return Policy(p, entry, name, states, x, wc=wc, wq=wq, kappa=kappa, cmin=cmin, qcap=qcap)
    if name.startswith("capacity_"):
        x = [bounds(S, p, cmin, qcap)[0 if name == "capacity_lower" else 1] for S in states]
        return Policy(p, entry, name, states, x, wc=wc, wq=wq, kappa=kappa, cmin=cmin, qcap=qcap)
    rows = [candidates(float(S), p, wc, wq, kappa, cmin, qcap) for S in states]
    switches = []
    for j in range(2, len(states)):
        a, b = rows[j-1], rows[j]
        if a["branch"] == "degenerate" or b["branch"] == "degenerate":
            # 能力等号仅使启动点的允许区间坍缩，不是两个不同候选分支的交叉。
            continue
        # 连续端点交接也分段；内部根排序改变不独自当作跳变。
        if a["branch"] != b["branch"] or abs(a["x"]-b["x"]) > .025:
            sw = _locate_switch(p, states[j-1], states[j], a, b, wc, wq, kappa, cmin, qcap)
            if not switches or abs(sw["S"]-switches[-1]["S"]) > 1e-7:
                switches.append(sw)
    diag_indices = np.unique(np.r_[np.linspace(1, len(states)-1, 17, dtype=int),
                                    np.flatnonzero(1-p.Sc/states <= 1e-4)])
    diagnostics = {"maximum_root_residual": max(r["root_residual"] for r in rows),
                   "near_tie_states": [{"S": float(states[j]), **rows[j]} for j in diag_indices if rows[j]["near_tie_count"] > 1],
                   "representative_candidates": [{"S": float(states[j]), **rows[j]} for j in diag_indices],
                   "switches": switches, "state_nodes": len(states)}
    return Policy(p, entry, name, states, [r["x"] for r in rows], wc=wc, wq=wq, kappa=kappa,
                  cmin=cmin, qcap=qcap, switches=switches, diagnostics=diagnostics)


def _geometry_cuts(policy, part):
    """能力区间max/min的解析折点；与优化候选分支交接是不同对象。"""
    p = policy.p
    cuts = [part["lo"], part["hi"]]
    if policy.qcap is not None:
        cuts.append((1-p.q0)*p.Sc/(1-policy.qcap))
    if policy.cmin > 0:
        cuts.append(p.c0*p.Sc/policy.cmin)
    return np.unique([v for v in cuts if part["lo"] <= v <= part["hi"]])


def _vector_local_x(policy, part, S):
    """同一允许份额插值的向量求值，不另求根或截断无约束最优值。"""
    p, S = policy.p, np.asarray(S)
    low = np.maximum(p.Sc/S, policy.cmin/p.c0)
    high = np.ones_like(S) if policy.qcap is None else np.minimum(1., (1-p.q0)*p.Sc/((1-policy.qcap)*S))
    if policy.name == "contact_only":
        return p.Sc/S
    if policy.name == "quarantine_only":
        return np.ones_like(S)
    if policy.name.startswith("alpha_"):
        a = float(policy.name[6:])
        return a+(1-a)*p.Sc/S
    branch = part.get("endpoint_branch")
    if branch == "lower" or policy.name == "capacity_lower":
        return low
    if branch == "upper" or policy.name == "capacity_upper":
        return high
    fraction = part["fraction_interpolator"](S)
    if np.any(fraction < -1e-10) or np.any(fraction > 1+1e-10):
        raise ArithmeticError("逐段求积的允许份额越界")
    return low+(high-low)*np.clip(fraction, 0., 1.)


def _gauss_segment(policy, part, order):
    # 每个真实PCHIP多项式区间独立取Gauss点，避免全局quad漏掉窄区间。
    interior = part["nodes"][(part["nodes"] > part["lo"]) & (part["nodes"] < part["hi"])]
    nodes = np.unique(np.r_[part["lo"], part["hi"], interior])
    nodes = np.unique(np.r_[nodes, _geometry_cuts(policy, part)])/policy.p.Sc
    abscissa, weights = np.polynomial.legendre.leggauss(order)
    middle, half = (nodes[:-1]+nodes[1:])/2, np.diff(nodes)/2
    scaled = middle[:, None]+half[:, None]*abscissa
    x = _vector_local_x(policy, part, scaled*policy.p.Sc)
    density = 1/(x*scaled-policy.p.Sbar/policy.p.Sc)
    cost = (policy.wc*(1-x)**2+policy.wq*(1-1/(x*scaled))**2)*density
    pref = policy.p.N/(policy.p.eta*policy.p.c0)
    return np.asarray([np.sum(half[:, None]*weights*density),
                       np.sum(half[:, None]*weights*cost)])*pref


def evaluate_policy(policy, eps=1e-9):
    """显式分段Gauss阶数核查；eps保留接口，仅记录，非严格误差保证。"""
    if not np.isfinite(eps) or eps <= 0:
        raise ValueError("求积精度请求必须为正")
    p, e = policy.p, policy.entry
    orders = ACCEPTANCE["quadrature"]["gauss_orders"]
    values = {order: np.sum([_gauss_segment(policy, part, order) for part in policy.pieces], axis=0)
              for order in orders}
    duration, cost = values[orders[-1]]
    differences = np.asarray([abs(values[b]-values[a]) for a, b in zip(orders[:-1], orders[1:])])
    derr, jerr = np.max(differences, axis=0)
    inf = p.beta*(e["Sstar"]-p.Sc)+p.gamma*p.eta*(1-p.beta)*duration
    sq = (1-p.beta)*(e["Sstar"]-p.Sc-p.gamma*p.eta*duration)
    vals = np.asarray([policy.x(v) for v in policy.state])
    qq = 1-(1-p.q0)*p.Sc/(vals*policy.state)
    return {"duration_state": duration, "J_state": cost, "duration": duration, "J": cost,
            "t_end_state": e["t1"]+duration+e["tail"],
            "plateau_infections_state": inf, "Sq_increment_plateau_state": sq,
            "total_infections_state": e["pre_tail_new_infections"]+inf,
            "quad_duration_estimate": derr, "quad_cost_estimate": jerr,
            "quadrature_method": "逐PCHIP区间及能力几何折点Gauss-Legendre",
            "quadrature_order_values": {str(order): {"duration_days": float(v[0]), "cost_days": float(v[1])} for order, v in values.items()},
            "quadrature_requested_eps": eps,
            "quadrature_count_estimate": p.gamma*p.eta*(1-p.beta)*derr,
            "q_max": float(np.max(qq)), "c_min": float(np.min(p.c0*vals)),
            "quad_error_is_rigorous_bound": False}


def rhs(p, controls):
    """前9项为人口比例；其后三项为J、J_c、J_q。"""
    def fun(t, y):
        s, i, sq, iq, rr = y[:5]
        c, q = controls(t)
        force = c*s*i
        fc, fq, fs = p.beta*(1-q)*force, p.beta*q*force, (1-p.beta)*q*force
        uc, uq = max(0., 1-c/p.c0), max(0., (q-p.q0)/(1-p.q0))
        return [-fc-fq-fs, fc-p.gamma*i, fs, fq-p.delta_q*iq,
                p.gamma*i+p.delta_q*iq, fc+fq, fc, fq, fs,
                p.wc*uc*uc+p.wq*uq*uq, uc, uq]
    return fun


def _integrate(p, controls, start, stop, initial, *, event=None, tight=False):
    settings = ACCEPTANCE["ode"]
    atol = np.asarray(settings["fine_atol"])*(settings["tight_atol_multiplier"] if tight else 1.)
    sol = solve_ivp(rhs(p, controls), (start, stop), initial, dense_output=True, events=event,
                    method="DOP853", rtol=settings["tight_rtol"] if tight else settings["fine_rtol"],
                    atol=atol, max_step=settings["tight_max_step"] if tight else settings["fine_max_step"])
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol


def common_entry(p, entry, tight=False):
    initial = np.zeros(12)
    initial[:5] = np.asarray([p.S0, p.I0, p.Sq0, p.Iq0, p.R0])/p.N
    def trigger(t, y):
        return y[1]-p.eta/p.N
    trigger.terminal, trigger.direction = True, 1
    pre = _integrate(p, lambda t: (p.c0, p.q0), 0., 2*entry["t1"]+10., initial, event=trigger, tight=tight)
    if len(pre.t_events[0]) != 1:
        raise RuntimeError("未找到第一次上升感染阈值事件")
    return pre, float(pre.t_events[0][0]), pre.y_events[0][0]


def nominal_time(policy, t1, tight=False):
    """名义解析端点/局部稠密解；在能力折点分段，绝不实际事件纠偏。"""
    p = policy.p
    now = t1
    segments = []
    settings = ACCEPTANCE["nominal"]
    parts = []
    for original in reversed(policy.pieces):
        cuts = _geometry_cuts(policy, original)
        parts.extend(dict(original, lo=float(lo), hi=float(hi))
                     for lo, hi in reversed(list(zip(cuts[:-1], cuts[1:]))))
    for part in parts:
        lo, hi = part["lo"]/p.N, part["hi"]/p.N
        factor = p.eta*p.c0/p.N
        alpha = offset = None
        branch = part.get("endpoint_branch")
        if policy.name == "contact_only":
            alpha, offset = 0., p.Sc/p.N
        elif policy.name == "quarantine_only":
            alpha, offset = 1., 0.
        elif policy.name.startswith("alpha_"):
            alpha = float(policy.name[6:])
            offset = (1-alpha)*p.Sc/p.N
        elif branch == "upper" or policy.name == "capacity_upper":
            if policy.qcap is None or part["hi"] <= (1-p.q0)*p.Sc/(1-policy.qcap):
                alpha, offset = 1., 0.
            else:
                alpha, offset = 0., (1-p.q0)*p.Sc/((1-policy.qcap)*p.N)
        elif branch == "lower" or policy.name == "capacity_lower":
            if policy.cmin == 0 or part["hi"] <= p.c0*p.Sc/policy.cmin:
                alpha, offset = 0., p.Sc/p.N
            else:
                alpha, offset = policy.cmin/p.c0, 0.
        if alpha is not None:
            if alpha == 0:
                rate = factor*(offset-p.Sbar/p.N)
                duration = (hi-lo)/rate
                trajectory = lambda dt, hi=hi, rate=rate: hi-rate*np.asarray(dt)
            else:
                equilibrium = (p.Sbar/p.N-offset)/alpha
                rate = factor*alpha
                duration = np.log1p((hi-lo)/(lo-equilibrium))/rate
                trajectory = lambda dt, hi=hi, eq=equilibrium, rate=rate: hi+(hi-eq)*np.expm1(-rate*np.asarray(dt))
            sol = SimpleNamespace(sol=lambda dt, trajectory=trajectory: np.asarray([trajectory(dt)]),
                                  nominal_method="解析线性/指数名义时钟")
        else:
            def nominal_rhs(t, y):
                S = float(np.clip(y[0]*p.N, part["lo"], part["hi"]))
                return [-factor*(policy.local_x(S, part)*y[0]-p.Sbar/p.N)]
            def exit_(t, y):
                return y[0]-lo
            exit_.terminal, exit_.direction = True, -1
            estimate = _gauss_segment(policy, part, ACCEPTANCE["quadrature"]["gauss_orders"][-1])[0]
            sol = solve_ivp(nominal_rhs, (0., max(.01, estimate*1.1)), [hi], method="DOP853",
                            rtol=settings["tight_rtol"] if tight else settings["fine_rtol"],
                            atol=settings["tight_atol"] if tight else settings["fine_atol"],
                            dense_output=True, events=exit_, max_step=max(estimate/settings["step_divisor"], settings["minimum_step"]))
            if not sol.success or not len(sol.t_events[0]):
                raise RuntimeError("分段名义轨迹未到达出口")
            duration = float(sol.t_events[0][0])
            sol.nominal_method = "局部时间归一化DOP853名义稠密解"
        stop = now+duration
        sol.nominal_S_bounds = [part["lo"], part["hi"]]
        def control(t, fixed=sol, piece=part, start=now):
            S = float(np.clip(fixed.sol(t-start)[0]*p.N, piece["lo"], piece["hi"]))
            # piece 自己的左右极限插值；不跨跳变使用全局曲线。
            x = policy.local_x(S, piece)
            c = p.c0*x
            q = 1-(1-p.q0)*p.Sc/(x*S)
            return c, q
        segments.append((now, stop, sol, control))
        now = stop
    return segments


def _peak(stages, p, subdivisions=2, kind="total"):
    candidates_ = []
    for phase, start, stop, sol, controls in stages:
        nodes = np.unique(np.r_[np.linspace(start, stop, 401), sol.t,
                                  np.concatenate([np.linspace(a, b, subdivisions+1) for a, b in zip(sol.t[:-1], sol.t[1:])])])
        def deriv(t):
            y = sol.sol(t)
            c, q = controls(t)
            return p.beta*c*(1-q)*y[0]*y[1]-p.gamma*y[1] if kind == "I" else p.beta*c*y[0]*y[1]-p.gamma*y[1]-p.delta_q*y[3]
        values = np.asarray([deriv(float(t)) for t in nodes])
        population = sol.sol(nodes)[1] if kind == "I" else sol.sol(nodes)[1]+sol.sol(nodes)[3]
        roots = [start, stop, float(nodes[int(np.argmax(population))])]
        for a, b, ga, gb in zip(nodes[:-1], nodes[1:], values[:-1], values[1:]):
            if ga*gb < 0:
                roots.append(brentq(deriv, a, b, xtol=ACCEPTANCE["peak_time_xtol"], rtol=1e-14))
        for t in roots:
            y = sol.sol(t)
            candidates_.append({"t": float(t), "value": float((y[1] if kind == "I" else y[1]+y[3])*p.N), "phase": phase})
    peak = max(candidates_, key=lambda a: a["value"])
    if kind == "I":
        return {"max_I_to_clearance": peak["value"], "t_max_I_to_clearance": peak["t"],
                "I_threshold_excess": max(0., peak["value"]-p.eta), "I_peak_candidates": candidates_}
    return {"peak_I_plus_Iq": peak["value"], "t_peak_I_plus_Iq": peak["t"],
            "peak_candidates": candidates_, "observation_interval": [stages[0][1], stages[-1][2]]}


def full_run(policy, *, tight=False, cached_entry=None, trace_points=1201):
    p, entry = replace(policy.p, wc=policy.wc, wq=policy.wq), policy.entry
    pre, t1, y1 = common_entry(p, entry, tight) if cached_entry is None else cached_entry
    nominal = nominal_time(policy, t1, tight)
    regular = lambda t: (p.c0, p.q0)
    stages = [("before", 0., t1, pre, regular)]
    actual = y1.copy()
    for start, stop, nom, controls in nominal:
        mid = _integrate(p, controls, start, stop, actual, tight=tight)
        actual = mid.y[:, -1]
        stages.append(("control", start, stop, mid, controls))
    t2 = nominal[-1][1]
    y2 = actual.copy()
    def clear(t, y):
        return y[1]-1/p.N
    clear.terminal, clear.direction = True, -1
    post = _integrate(p, regular, t2, t2+2*entry["tail"]+10., actual, event=clear, tight=tight)
    if len(post.t_events[0]) != 1:
        raise RuntimeError("未找到恢复常规后的下降清零事件")
    tend, final = float(post.t_events[0][0]), post.y_events[0][0]
    stages.append(("after", t2, tend, post, regular))
    records = []
    mass = drift = 0.
    minimum = float("inf")
    cmin, cmax, qmin, qmax = float("inf"), 0., float("inf"), 0.
    for j, (phase, start, stop, sol, controls) in enumerate(stages):
        tt = np.unique(np.r_[np.linspace(start, stop, trace_points), sol.t])
        yy = sol.sol(tt)
        mass = max(mass, float(np.max(abs(yy[:5].sum(axis=0)-1))*p.N))
        minimum = min(minimum, float(np.min(yy[:5])*p.N))
        if phase == "control":
            drift = max(drift, float(np.max(abs(yy[1]*p.N-p.eta))))
        for t, y in zip(tt, yy.T):
            c, q = controls(float(t))
            cmin, cmax, qmin, qmax = min(cmin, c), max(cmax, c), min(qmin, q), max(qmax, q)
            records.append({"strategy": policy.name, "phase": phase, "segment": j, "t": float(t),
                            **{k: float(y[i]*p.N) for i, k in enumerate(["S", "I", "Sq", "Iq", "R", "Ctotal", "Cc", "Cq", "Csq"])},
                            "J": float(y[9]), "J_c": float(y[10]), "J_q": float(y[11]), "c": c, "q": q})
    peak = _peak(stages, p)
    peak_fine = _peak(stages, p, subdivisions=4)
    peak_I = _peak(stages, p, kind="I")
    peak_I_fine = _peak(stages, p, subdivisions=4, kind="I")
    vals = {"t1": t1, "t2": t2, "t_end": tend, "duration_time": t2-t1,
            "J_time": float(final[9]), "total_infections_to_clearance": float(final[5]*p.N),
            "plateau_infections_time": float((y2[5]-y1[5])*p.N),
            "Sq_increment_plateau": float((y2[2]-y1[2])*p.N),
            "q_max": qmax, "c_min": cmin, "c_max": cmax, "q_min": qmin,
            "plateau_abs_error": drift, "plateau_relative_error": drift/p.eta,
            "mass_absolute_error": mass, "minimum_compartment": minimum,
            "exit_S_error": float(y2[0]*p.N-p.Sc), "exit_I_error": float(y2[1]*p.N-p.eta),
            "clearance_I_error": float(final[1]*p.N-1),
            "entry_time_error": float(t1-entry["t1"]), "entry_S_error": float(y1[0]*p.N-entry["Sstar"]),
            "clearance_direction": float(rhs(p, regular)(tend, final)[1]*p.N),
            "peak_search_change": abs(peak["peak_I_plus_Iq"]-peak_fine["peak_I_plus_Iq"]),
            "I_peak_search_change": abs(peak_I["max_I_to_clearance"]-peak_I_fine["max_I_to_clearance"]),
            **peak_I_fine,
            **peak_fine, "peak_I_plus_Iq_over_eta": peak_fine["peak_I_plus_Iq"]/p.eta,
            "nominal_segment_times": [[a, b] for a, b, _, _ in nominal],
            "nominal_segment_methods": [{"interval": [a, b], "S_bounds": sol.nominal_S_bounds,
                                         "method": sol.nominal_method} for a, b, sol, _ in nominal],
            "control_implementation": "预先名义分段稠密时间解；完整ODE仅访问固定时间函数；不按实际S纠偏"}
    return vals, records
