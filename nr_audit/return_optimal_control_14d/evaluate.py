"""14 天指数回流研究的独立完整五仓室 ODE 评价器。

本模块不在导入时运行计算。平台期仍积分 log(I/N)，不把 I 固定为 eta；
不截断负仓室，不用事件偷偷修改候选 duration。所有新输出只写本研究目录。
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
import uuid
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
RESULTS = ROOT / "results"
IS, IL, ISQ, IIQ, IR, IC, IJ, IK = range(8)
OMEGA = 1.0 / 14.0
DEFAULT_TAIL = {"base": 1e-4, "xian": 0.01}
EVALUATION_SCHEMA = "2"
THRESHOLD_ROUNDOFF_RATIO = 1e-12
THRESHOLD_REVIEW_RATIO = 1e-7
EXIT_MATCH_NORMALIZED = 1e-9
_PARAMS = None
_ALLOC = None


def _source_module(name, path):
    # 冻结来源只读，连 __pycache__ 也不写回来源目录。
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        sys.modules[name] = module
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old
    return module


def _clean(value):
    if isinstance(value, dict):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [_clean(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(float(value)) else None
    return value


def _write(path, value):
    path = Path(path).resolve()
    if ROOT != path and ROOT not in path.parents:
        raise ValueError("评价结果只能写入本研究目录")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_clean(value), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _log(kind, record):
    RESULTS.mkdir(parents=True, exist_ok=True)
    row = {"kind": kind, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **record}
    with (RESULTS / "evaluation_log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_clean(row), ensure_ascii=False, separators=(",", ":")) + "\n")


def load_params(case):
    """返回固定参数及其来源身份；不计算轨迹。"""
    global _PARAMS
    if _PARAMS is None:
        _PARAMS = _source_module("return14_frozen_params", REPO / "r7_return" / "params.py")
    if case not in _PARAMS.CASES:
        raise ValueError("case 必须为 base 或 xian")
    original = _PARAMS.CASES[case]
    p = asdict(original)
    p.update(omega=OMEGA, S_c=original.S_c, sc_N=original.sc_N,
             theta=original.eta_N, z_bar=original.z_bar,
             source="r7_return/params.py",
             source_sha256=hashlib.sha256((REPO / "r7_return" / "params.py").read_bytes()).hexdigest())
    return p


def _initial(p):
    return np.array([p["S0"] / p["N"], math.log(p["I0"] / p["N"]),
                     p["Sq0"] / p["N"], p["Iq0"] / p["N"], p["R0"] / p["N"],
                     0.0, 0.0, 0.0])


def _atol(p, rtol):
    small = max(np.finfo(float).tiny, 1e-13 * min(p["I0"] / p["N"], 1.0 / p["N"]))
    factor = min(1.0, rtol / 1e-11)
    return np.array([1e-15, 1e-12, small, small, small, small, 1e-12, small]) * factor


def _rhs(p, control, active):
    def fun(t, y):
        s, li, sq, iq = y[IS], y[IL], y[ISQ], y[IIQ]
        i = math.exp(float(li))
        c, q = control(t, y)
        contacts = c * s * i
        infection = p["beta"] * contacts
        tracking = (1.0 - p["beta"]) * q * contacts
        ds = -(p["beta"] + (1.0 - p["beta"]) * q) * contacts + p["omega"] * sq
        dli = p["beta"] * c * (1.0 - q) * s - p["gamma"]
        dsq = tracking - p["omega"] * sq
        diq = p["beta"] * q * contacts - p["delta_q"] * iq
        dr = p["gamma"] * i + p["delta_q"] * iq
        # 正部来自现稿 J 的定义，不是对控制或仓室作数值截断。
        cost = (p["wc"] * max((p["c0"] - c) / p["c0"], 0.0) ** 2
                + p["wq"] * max((q - p["q0"]) / (1.0 - p["q0"]), 0.0) ** 2) if active else 0.0
        return [ds, dli, dsq, diq, dr, infection, cost, tracking]
    return fun


def _routine(p):
    return lambda t, y: (p["c0"], p["q0"])


def _state(p, y):
    n = p["N"]
    return {"S": n * y[IS], "I": n * math.exp(float(y[IL])), "S_q": n * y[ISQ],
            "I_q": n * y[IIQ], "R": n * y[IR]}


def _solve(p, fun, interval, y, method, rtol, stats, events=None, max_step=2.0):
    try:
        sol = solve_ivp(fun, interval, y, method=method, rtol=rtol, atol=_atol(p, rtol),
                        max_step=max_step, dense_output=True, events=events)
    except Exception as exc:
        _log("ode_exception", {"case": p["name"], "interval": interval, "method": method,
             "exception": repr(exc), "completed_calls_in_failed_invocation": len(stats), "failed_ode_calls": 1})
        raise
    stats.append({"t_start": interval[0], "t_stop": float(sol.t[-1]), "method": method,
                  "nfev": sol.nfev, "njev": sol.njev, "nlu": sol.nlu,
                  "steps": len(sol.t) - 1, "success": sol.success, "message": sol.message})
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol


def prepare_start(case, method="DOP853", rtol=1e-12, use_cache=True):
    """完整常规方程积分到首次 I=eta；不重置触发状态。"""
    p = load_params(case)
    cache = RESULTS / "starts" / f"{case}_{method}_{rtol:.0e}.json"
    if use_cache and cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        if data.get("parameter_sha256") == p["source_sha256"] and data.get("omega") == OMEGA:
            _log("start_cache_hit", {"case": case, "ode_calls": 0, "path": str(cache.relative_to(ROOT))})
            return data
    stats = []
    event = lambda t, y: y[IL] - math.log(p["theta"])
    event.terminal, event.direction = True, 1
    sol = _solve(p, _rhs(p, _routine(p), False), (0.0, 1e4), _initial(p), method, rtol, stats,
                 events=event, max_step=1.0)
    if len(sol.t_events[0]) != 1:
        raise RuntimeError("常规轨迹未首次触及 eta")
    y = sol.y[:, -1]
    result = {"case": case, "omega": OMEGA, "t1": float(sol.t[-1]), "s": y[IS], "sq": y[ISQ],
              "theta": p["theta"], "sc_N": p["sc_N"], "y": y,
              "state_persons": _state(p, y), "C_start": p["N"] * y[IC],
              "trigger_relative_residual": math.expm1(float(y[IL]) - math.log(p["theta"])),
              "parameter_sha256": p["source_sha256"], "method": method, "rtol": rtol,
              "ode_calls": len(stats), "integration_stats": stats}
    result = _clean(result)
    _write(cache, result)
    _log("prepare_start", {"case": case, "ode_calls": len(stats), "nfev": sum(x["nfev"] for x in stats)})
    return result


def _sample_segments(segments, per_segment=9):
    tt, yy = [], []
    for a, b, sol in segments:
        times = np.unique(np.r_[sol.t, np.linspace(a, b, per_segment)])
        values = sol.sol(times)
        if tt and abs(times[0] - tt[-1]) < 1e-11:
            times, values = times[1:], values[:, 1:]
        tt.extend(times.tolist())
        yy.extend(values.T.tolist())
    return np.asarray(tt), np.asarray(yy).T


def _classify_threshold(peak_ratio, roundoff_tol=THRESHOLD_ROUNDOFF_RATIO):
    """正超限不是允许的模型松弛；只把舍入量级单独标为数值边界。"""
    excess = float(peak_ratio) - 1.0
    if excess <= 0.0:
        return "satisfied"
    if excess <= roundoff_tol:
        return "boundary_roundoff"
    if excess <= THRESHOLD_REVIEW_RATIO:
        return "undetermined"
    return "violated"


def paired_threshold_status(first_ratio, second_ratio, roundoff_tol=THRESHOLD_ROUNDOFF_RATIO):
    """两种积分器稳定同向的小正超限也记 violated，不因小于1e-7而通过。"""
    da, db = float(first_ratio) - 1.0, float(second_ratio) - 1.0
    spread = abs(da - db)
    error_budget = max(roundoff_tol, 5.0 * spread)
    if min(da, db) > error_budget:
        status = "violated"
    elif max(da, db) <= 0.0:
        status = "satisfied"
    elif max(da, db) <= roundoff_tol:
        status = "boundary_roundoff"
    else:
        status = "undetermined"
    return {"status": status, "method_spread_ratio": spread, "numerical_error_budget_ratio": error_budget,
            "note": "经验数值误差预算，非区间算术认证；正偏差不作为模型阈值松弛"}


def _find_roots(segments, p, control=None, derivative=None, return_details=False):
    roots, contacts, extrema = [], [], []
    for a, b, sol in segments:
        grid = np.unique(np.r_[sol.t, np.linspace(a, b, max(17, len(sol.t) * 3))])
        vals = sol.sol(grid)[IS] - p["sc_N"]
        if derivative is not None:
            slope = lambda t: float(derivative(t, sol.sol(t)))
        elif control is not None:
            complete_rhs = _rhs(p, control, True)
            slope = lambda t: float(complete_rhs(t, sol.sol(t))[IS])
        else:
            slope = None
        for j in range(len(grid) - 1):
            if vals[j] == 0:
                roots.append(float(grid[j]))
                contacts.append({"time": float(grid[j]), "kind": "sampled_zero", "residual": float(vals[j])})
            if vals[j] * vals[j + 1] < 0:
                root = float(brentq(lambda t: sol.sol(t)[IS] - p["sc_N"], grid[j], grid[j + 1], xtol=1e-12))
                roots.append(root)
                contacts.append({"time": root, "kind": "sign_change", "residual": float(sol.sol(root)[IS] - p["sc_N"])})
        # 只查状态符号变化会漏掉切触。另定位每段 Sdot=0，并检查局部极小与临界值。
        if slope is not None:
            derivatives = np.array([slope(float(t)) for t in grid])
            critical = []
            for j in range(len(grid) - 1):
                if derivatives[j] == 0.0:
                    critical.append(float(grid[j]))
                elif derivatives[j] * derivatives[j + 1] < 0.0:
                    critical.append(float(brentq(slope, grid[j], grid[j + 1], xtol=1e-12)))
            for point in critical:
                gap = float(sol.sol(point)[IS] - p["sc_N"])
                eps = min(max((b - a) * 1e-5, 1e-8), (b - a) * 0.1)
                left, right = max(a, point - eps), min(b, point + eps)
                is_min = slope(left) <= 0.0 and slope(right) >= 0.0
                extrema.append({"time": point, "S_minus_Sc_normalized": gap, "is_local_minimum": bool(is_min)})
                if abs(gap) <= 5e-14:
                    roots.append(point)
                    contacts.append({"time": point, "kind": "stationary_contact_roundoff", "residual": gap})
        if abs(vals[-1]) <= 5e-14:
            roots.append(float(grid[-1]))
            contacts.append({"time": float(grid[-1]), "kind": "endpoint_roundoff", "residual": float(vals[-1])})
    unique = []
    for t in sorted(roots):
        if not unique or abs(t - unique[-1]) > 1e-7 * (1.0 + abs(t)):
            unique.append(t)
    details = {"roots": unique, "contacts": contacts, "stationary_points": extrema,
               "search_note": "ODE步长网格、状态变号根及Sdot变号根；不构成区间算术完备性证明"}
    return details if return_details else unique


def _first_exit_assessment(t2, duration, terminal_residual, root_details,
                           terminal_tol=EXIT_MATCH_NORMALIZED):
    roots = root_details["roots"]
    time_tol = max(1e-8, duration * 1e-10)
    prior = [t for t in roots if t < t2 - time_tol]
    if prior:
        return {"time": prior[0], "status": "prior_root", "early": True,
                "time_tolerance_days": time_tol, "terminal_within_tolerance": abs(terminal_residual) <= terminal_tol}
    if roots:
        return {"time": roots[0], "status": "root_at_terminal_roundoff", "early": False,
                "time_tolerance_days": time_tol, "terminal_within_tolerance": abs(terminal_residual) <= terminal_tol}
    if abs(terminal_residual) <= terminal_tol:
        return {"time": t2, "status": "terminal_within_tolerance", "early": False,
                "time_tolerance_days": time_tol, "terminal_within_tolerance": True,
                "note": "终端在状态容差内，未定位到严格变号根；此t2为数值端点身份，非精确事件证书"}
    return {"time": None, "status": "not_matched", "early": None,
            "time_tolerance_days": time_tol, "terminal_within_tolerance": False}


def _tail_bound(p, y):
    u = y[IS] + y[ISQ]
    if u >= p["sc_N"]:
        return math.inf
    return p["N"] * p["beta"] * p["c0"] * u * math.exp(float(y[IL])) / (p["gamma"] * (1.0 - u / p["sc_N"]))


def _post(p, yexit, t2, method, rtol, tail_tol, stats):
    def finish(t, y):
        u = y[IS] + y[ISQ]
        return (tail_tol / p["N"]) * p["gamma"] * (1.0 - u / p["sc_N"]) - p["beta"] * p["c0"] * u * math.exp(float(y[IL]))
    finish.terminal, finish.direction = True, 1
    sc = lambda t, y: y[IS] - p["sc_N"]
    sc.terminal, sc.direction = False, 0
    # 常规阶段 I 的所有极值与 S=Sc 的全部根重合；均保存，而非只取极大。
    if _tail_bound(p, yexit) <= tail_tol:
        return [], yexit, t2, {"tail_reached": True, "Sc_events": []}
    segments = []
    y, a, window = np.array(yexit, copy=True), float(t2), 2000.0
    events = []
    while a < t2 + 1e5:
        b = min(t2 + 1e5, a + window)
        sol = _solve(p, _rhs(p, _routine(p), False), (a, b), y, method, rtol, stats,
                     events=[finish, sc], max_step=2.0)
        end = float(sol.t[-1])
        segments.append((a, end, sol))
        events.extend(float(t) for t in sol.t_events[1])
        y = sol.y[:, -1]
        if len(sol.t_events[0]):
            return segments, y, end, {"tail_reached": True, "Sc_events": events}
        a, window = end, min(window * 2.0, 20000.0)
    return segments, y, a, {"tail_reached": False, "Sc_events": events}


def _finalize(case, start, segments, control, duration, method, rtol, tail_tol, stats,
              evaluation_id, save_path, metadata):
    p = load_params(case)
    t1 = start["t1"]
    t2 = t1 + duration
    ystart = np.asarray(start["y"], dtype=float)
    yexit = segments[-1][2].y[:, -1]
    pt, py = _sample_segments(segments)
    controls = np.array([control(float(t), py[:, j]) for j, t in enumerate(pt)])
    root_details = _find_roots(segments, p, control=control, return_details=True)
    roots = root_details["roots"]
    residual = float(yexit[IS] - p["sc_N"])
    exit_assessment = _first_exit_assessment(t2, duration, residual, root_details)
    first_exit = exit_assessment["time"]
    earlier = exit_assessment["early"]
    post, ytail, tend, postinfo = _post(p, yexit, t2, method, rtol, tail_tol, stats)
    if post:
        qt, qy = _sample_segments(post, 129)
        tt = np.r_[pt, qt[1:]]
        yy = np.column_stack([py, qy[:, 1:]])
    else:
        qt, qy, tt, yy = np.array([t2]), yexit[:, None], pt, py
    peak_candidates = [(float(t1), float(ystart[IL])), (float(t2), float(yexit[IL])), (float(tend), float(ytail[IL]))]
    peak_candidates.extend((float(pt[j]), float(py[IL, j])) for j in range(len(pt)))
    peak_candidates.extend((float(qt[j]), float(qy[IL, j])) for j in range(len(qt)))
    for a, b, sol in post:
        for rt in postinfo["Sc_events"]:
            if a - 1e-9 <= rt <= b + 1e-9:
                peak_candidates.append((rt, float(sol.sol(rt)[IL])))
    peak_time, peak_log = max(peak_candidates, key=lambda pair: pair[1])
    platform_dev = float(np.max(np.abs(np.expm1(py[IL] - math.log(p["theta"])))))
    peak_ratio = math.exp(peak_log - math.log(p["theta"]))
    five = np.vstack([yy[IS], np.exp(yy[IL]), yy[ISQ], yy[IIQ], yy[IR]])
    mass = float(np.max(np.abs(np.sum(five, axis=0) - 1.0)))
    cumulative = float(np.max(np.abs(yy[IC] - (p["S0"] / p["N"] + p["Sq0"] / p["N"] - yy[IS] - yy[ISQ]))))
    min_comp = float(np.min(five))
    min_platform_s_gap = min([float(np.min(py[IS] - p["sc_N"]))]
                             + [x["S_minus_Sc_normalized"] for x in root_details["stationary_points"]])
    control_violation = float(max(np.max(controls[:, 0] - p["c0"]), np.max(-controls[:, 0]),
                                  np.max(p["q0"] - controls[:, 1]), np.max(controls[:, 1] - 1.0), 0.0))
    tail = _tail_bound(p, ytail)
    ccut = float(p["N"] * ytail[IC])
    threshold_status = _classify_threshold(peak_ratio)
    checks = {"exit_match": abs(residual) <= EXIT_MATCH_NORMALIZED,
              "first_exit_matched": exit_assessment["status"] != "not_matched",
              "no_early_exit": earlier is False,
              "platform": platform_dev <= 1e-7,
              "post_threshold": threshold_status in ("satisfied", "boundary_roundoff"),
              "nonnegative": min_comp >= -1e-12, "mass": mass <= 1e-9,
              "cumulative_identity": cumulative <= 1e-9, "control_bounds": control_violation <= 1e-8,
              "platform_domain": min_platform_s_gap >= -1e-9,
              "tail_reached": postinfo["tail_reached"]}
    if all(checks.values()):
        numeric_status = threshold_status
    elif threshold_status in ("undetermined", "violated"):
        numeric_status = threshold_status
    else:
        numeric_status = "infeasible"
    result = {"evaluation_id": evaluation_id, "case": case, "omega": OMEGA,
              "evaluation_schema": EVALUATION_SCHEMA,
              "evaluator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "method": method, "rtol": rtol, "tail_tol_persons": tail_tol,
              "duration": duration, "t1": t1, "t2": t2, "T_tail": tend,
              "J": float(yexit[IJ] - ystart[IJ]), "C_arc": float(p["N"] * (yexit[IC] - ystart[IC])),
              "C_exit": float(p["N"] * yexit[IC]), "C_cut": ccut,
              "C_infinity_interval": [ccut, ccut + tail], "tail_bound_persons": tail,
              "interval_note": "基于数值终点状态的解析尾界，不含浮点积分误差；不是区间算术认证",
              "start_state_persons": _state(p, ystart), "exit_state_persons": _state(p, yexit),
              "tail_state_persons": _state(p, ytail), "Sq_exit": float(p["N"] * yexit[ISQ]),
              "exit_residual_normalized": residual,
              "first_Sc_exit_time": first_exit, "early_first_Sc_exit": earlier,
              "first_exit_assessment": exit_assessment,
              "platform_Sc_roots": roots, "platform_Sc_root_search": root_details,
              "post_Sc_roots": postinfo["Sc_events"],
              "platform_relative_deviation": platform_dev, "threshold_peak_ratio": peak_ratio,
              "threshold_peak_time": peak_time, "post_threshold_violation_relative": max(peak_ratio - 1.0, 0.0),
              "threshold_numeric_status": threshold_status, "numeric_status": numeric_status,
              "threshold_roundoff_ratio": THRESHOLD_ROUNDOFF_RATIO,
              "threshold_note": "1e-12是舍入误差分类预算，不是允许提高eta；boundary_roundoff非严格数学认证",
              "mass_residual_normalized": mass, "cumulative_identity_residual_normalized": cumulative,
              "minimum_compartment_normalized": min_comp, "control_bound_violation": control_violation,
              "platform_min_S_minus_Sc_normalized": min_platform_s_gap,
              "five_compartments_integrated": True, "I_not_fixed": True, "no_compartment_clipping": True,
              "checks": checks, "feasible": all(checks.values()),
              "parameter_sha256": p["source_sha256"], "ode_calls": len(stats),
              "nfev": sum(x["nfev"] for x in stats), "integration_stats": stats,
              "trajectory": {"t_platform": pt, "states_platform": py.T,
                             "c_platform": controls[:, 0], "q_platform": controls[:, 1],
                             "t_post": qt, "states_post": qy.T}, **metadata}
    target = Path(save_path) if save_path else RESULTS / "evaluations" / f"{evaluation_id}.json"
    if not target.is_absolute():
        target = ROOT / target
    archive = RESULTS / "evaluations" / f"{evaluation_id}.json"
    result["saved_path"] = str(target.resolve().relative_to(ROOT))
    result["archive_path"] = str(archive.relative_to(ROOT))
    result = _clean(result)
    # 显式给定的输出可以是 latest；每次实际评价另留唯一回执，保留失败和重复核验。
    if archive.resolve() != target.resolve():
        _write(archive, result)
    _write(target, result)
    _log(metadata.get("kind", "evaluate"), {"evaluation_id": evaluation_id, "case": case,
          "ode_calls": len(stats), "nfev": result["nfev"], "feasible": result["feasible"],
          "saved_path": result["saved_path"]})
    return result


def evaluate(case, duration, lambda_values, interpolation="linear", method="DOP853",
             rtol=1e-12, tail_tol=None, save_path=None):
    """按给定 duration 完整积分；不以退出事件替换 duration。

    linear: lambda_values 是均匀 tau 节点值；constant/piecewise_constant:
    lambda_values 是等长 tau 区间值，每段独立启动完整 ODE 积分。
    """
    p = load_params(case)
    values = np.asarray(lambda_values, dtype=float)
    if values.ndim != 1 or len(values) < 1 or not np.all(np.isfinite(values)):
        raise ValueError("lambda_values 必须是非空有限一维序列")
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("duration 必须为正有限数")
    if np.min(values) < -1e-10 or np.max(values) > 1.0 + 1e-10:
        raise ValueError("lambda_values 不在 [0,1] 数值容差内；评价器不作截断")
    if interpolation not in ("linear", "constant", "piecewise_constant"):
        raise ValueError("interpolation 必须为 linear/constant/piecewise_constant")
    start = prepare_start(case, method=method, rtol=rtol)
    t1 = start["t1"]
    if interpolation == "linear":
        knots = np.linspace(0.0, 1.0, max(len(values), 2))
        vv = values if len(values) > 1 else np.repeat(values, 2)
        lamfun = lambda tau: float(np.interp(tau, knots, vv))
    else:
        knots = np.linspace(0.0, 1.0, len(values) + 1)
        lamfun = lambda tau: float(values[min(max(int(math.floor(tau * len(values))), 0), len(values) - 1)])
    def control(t, y):
        lam = lamfun((t - t1) / duration)
        c_lower = p["c0"] * p["sc_N"] / y[IS]
        c = c_lower + lam * (p["c0"] - c_lower)
        q = 1.0 - p["gamma"] / (p["beta"] * c * y[IS])
        return c, q
    stats, segments = [], []
    y = np.asarray(start["y"], dtype=float)
    for index in range(len(knots) - 1):
        a, b = t1 + duration * knots[index], t1 + duration * knots[index + 1]
        # 常值段取该段本身的 lambda，避免右端取到下一段导致求解器跨跳变。
        if interpolation != "linear":
            lam = float(values[index])
            def seg_control(t, yy, lam=lam):
                low = p["c0"] * p["sc_N"] / yy[IS]
                cc = low + lam * (p["c0"] - low)
                return cc, 1.0 - p["gamma"] / (p["beta"] * cc * yy[IS])
        else:
            seg_control = control
        sol = _solve(p, _rhs(p, seg_control, True), (a, b), y, method, rtol, stats,
                     max_step=min(2.0, b - a))
        y = sol.y[:, -1]
        segments.append((a, b, sol))
    eid = f"{case}_{uuid.uuid4().hex[:12]}"
    return _finalize(case, start, segments, control, duration, method, rtol,
                     DEFAULT_TAIL[case] if tail_tol is None else tail_tol, stats, eid, save_path,
                     {"kind": "evaluate", "interpolation": interpolation, "lambda_values": values})


def reference(case, kind, n_samples=161, method="DOP853", rtol=1e-12, tail_tol=None, save_path=None):
    """完整 ODE 的仅隔离、仅接触或无回流最优反馈迁移参照。"""
    global _ALLOC
    p = load_params(case)
    aliases = {"isolation": "q_only", "contact": "c_only", "migration": "opt_noreturn"}
    kind = aliases.get(kind, kind)
    if kind not in ("q_only", "c_only", "opt_noreturn"):
        raise ValueError("未知参照控制")
    if kind == "opt_noreturn" and _ALLOC is None:
        _ALLOC = _source_module("return14_frozen_alloc", REPO / "r7_return" / "alloc.py")
    start = prepare_start(case, method=method, rtol=rtol)
    def control(t, y):
        z = y[IS] / p["sc_N"]
        if kind == "q_only":
            x = 1.0
        elif kind == "c_only":
            x = 1.0 / z
        else:
            x = _ALLOC.argmin_noreturn(z, p["z_bar"], p["wc"], p["wq"])[0]
        c = p["c0"] * x
        return c, 1.0 - p["gamma"] / (p["beta"] * c * y[IS])
    stop = lambda t, y: y[IS] - p["sc_N"]
    stop.terminal, stop.direction = True, -1
    stats = []
    sol = _solve(p, _rhs(p, control, True), (start["t1"], start["t1"] + 1e4),
                 np.asarray(start["y"], dtype=float), method, rtol, stats, events=stop, max_step=1.0)
    if not len(sol.t_events[0]):
        raise RuntimeError("参照控制未在时限内退出")
    end = float(sol.t[-1])
    duration = end - start["t1"]
    times = np.linspace(start["t1"], end, n_samples)
    states = sol.sol(times)
    lam = []
    for j, t in enumerate(times):
        c, _ = control(t, states[:, j])
        low = p["c0"] * p["sc_N"] / states[IS, j]
        gap = p["c0"] - low
        lam.append((c - low) / gap if abs(gap) > 1e-10 else
                   (1.0 if kind == "q_only" else (lam[-1] if kind == "opt_noreturn" and lam else 0.0)))
    eid = f"reference_{case}_{kind}_{uuid.uuid4().hex[:8]}"
    target = save_path if save_path else RESULTS / "references" / f"{case}_{kind}.json"
    return _finalize(case, start, [(start["t1"], end, sol)], control, duration, method, rtol,
                     DEFAULT_TAIL[case] if tail_tol is None else tail_tol, stats, eid, target,
                     {"kind": "reference", "reference_kind": kind, "lambda_samples": lam,
                      "lambda_values": lam, "interpolation": "linear", "n_samples": n_samples})


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--references", action="store_true", help="明确运行六条14天参照轨迹")
    args = parser.parse_args()
    if not args.references:
        parser.print_help()
        return
    summaries = []
    for case in ("base", "xian"):
        for kind in ("q_only", "c_only", "opt_noreturn"):
            r = reference(case, kind)
            item = {key: r[key] for key in ("case", "reference_kind", "duration", "J", "C_infinity_interval",
                    "threshold_peak_ratio", "exit_residual_normalized", "feasible", "ode_calls")}
            print(json.dumps(item, ensure_ascii=False), flush=True)
            summaries.append(item)
    _write(RESULTS / "references" / "summary.json", summaries)


if __name__ == "__main__":
    _main()
