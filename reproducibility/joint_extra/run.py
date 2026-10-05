"""新增联合控制 A-D 核查入口；默认只在全新结果目录计算，不发布论文。

python -B reproducibility/joint_extra/run.py --out <new-directory> --mode compute
公开 run(output_dir, root, baseline_path=None, xian_reference=None, tasks=None)。
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import datetime as dt
import csv
import json
from pathlib import Path
import platform
import subprocess
import sys
import traceback
import warnings

import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if __package__:
    from . import core
    from . import validation as V
else:
    import core
    import validation as V

STRATEGIES = ["contact_only", "alpha_0.5", "quarantine_only", "minimum_cost"]
CAPACITY_POINTS = {"baseline": {"u_max": .5, "q_cap": .6}, "xian": {"u_max": .5, "q_cap": .75}}
ORIGINAL_KAPPA = np.unique(np.r_[-np.logspace(2, -4, 70), 0., np.logspace(-4, 2, 70), np.linspace(-1.5, .2, 171)])
KAPPA_REFINEMENT = np.array([k / 500 for k in range(-300, -99)], dtype=float)
KAPPA_DUPLICATE_TOLERANCE = 1e-12


def refined_kappa_grid():
    """保留旧浮点值，仅加入与全部已保留值相差超过容差的新点。"""
    retained = list(ORIGINAL_KAPPA)
    for candidate in KAPPA_REFINEMENT:
        if all(abs(candidate - old) > KAPPA_DUPLICATE_TOLERANCE for old in retained):
            retained.append(float(candidate))
    return np.array(sorted(retained), dtype=float)


KAPPA = refined_kappa_grid()
R_GRID = np.logspace(-1, np.log10(20.), core.ACCEPTANCE["settings"]["phase_weight_nodes"])


def clean(obj):
    if isinstance(obj, dict):
        return {str(k): clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return clean(obj.tolist())
    if isinstance(obj, (float, np.floating)):
        return float(obj) if np.isfinite(obj) else None
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj


def write_json(path, obj):
    Path(path).write_text(json.dumps(clean(obj), ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def write_csv(path, rows):
    if not rows:
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with Path(path).open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: format(v, ".17g") if isinstance(v, (float, np.floating)) else v for k, v in row.items()})


def _numeric_metrics(state, time):
    # 大型候选/峰诊断另存JSON，不混入CSV数值列。
    row = {k: v for k, v in {**state, **time}.items() if isinstance(v, (int, float, bool))}
    row.update(duration=state["duration_state"], J=state["J_state"],
               duration_quadrature=state["duration_state"], J_quadrature=state["J_state"],
               total_infections=time["total_infections_to_clearance"], plateau_new_Sq=time["Sq_increment_plateau"],
               conservation_infections=state["plateau_infections_state"], conservation_Sq=state["Sq_increment_plateau_state"])
    return row


def _evaluate(case, p, e, name, out, *, ns=None, wc=1., wq=2., kappa=0., cmin=0., qcap=None, cache=None, tighten=True):
    ns = ns or core.ACCEPTANCE["settings"]["state_nodes"]
    policy = core.build_profile(p, e, name, ns=ns, wc=wc, wq=wq, kappa=kappa, cmin=cmin, qcap=qcap)
    state = core.evaluate_policy(policy)
    timed, trace = core.full_run(policy, cached_entry=(cache or {}).get("fine"))
    checked = V.policy_checks(policy, state, timed)
    diag = V.candidate_checks(policy) if name == "minimum_cost" else {"passed": True, "scope": "显式端点/指定α，不是最低J候选"}
    checked["candidate_checks_passed"] = diag["passed"]
    checked["passed"] = bool(checked["passed"] and diag["passed"])
    if tighten:
        tight, _ = core.full_run(policy, tight=True, cached_entry=(cache or {}).get("tight"), trace_points=401)
        conv_time = V.convergence(timed, tight, time=True)
        ns2 = core.ACCEPTANCE["settings"]["refined_state_nodes"] if ns == core.ACCEPTANCE["settings"]["state_nodes"] else 2*ns-1
        finer = core.build_profile(p, e, name, ns=ns2, wc=wc, wq=wq, kappa=kappa, cmin=cmin, qcap=qcap)
        fine_state = core.evaluate_policy(finer)
        conv_state = V.convergence(state, fine_state)
        checked["convergence"] = {"time": conv_time, "state": conv_state}
        checked["passed"] = bool(checked["passed"] and conv_time["passed"] and conv_state["passed"])
    row = {"case": case, "strategy": name, **_numeric_metrics(state, timed), "passed": checked["passed"]}
    return row, trace, {"validation": checked, "candidate_checks": diag,
                        "state_diagnostics": state, "time_diagnostics": timed}, policy


def _cache(cases, entries):
    return {case: {level: core.common_entry(p, entries[case], level == "tight") for level in ("fine", "tight")}
            for case, p in cases.items()}


def task_A(cases, entries, ref, out, cache):
    reports, tables, derived = {}, {}, {}
    for case, p in cases.items():
        print("JOINT_EXTRA_A", case, flush=True)
        rows, traces, checks = [], [], {}
        for name in STRATEGIES:
            print("STRATEGY", case, name, flush=True)
            row, tr, report, _ = _evaluate(case, p, entries[case], name, out, cache=cache[case])
            rows.append(row)
            traces.extend(tr)
            checks[name] = report
        pair = V.pair_identities(rows, p)
        reports[case] = {"passed": bool(all(r["passed"] for r in rows) and pair["passed"]),
                         "strategies": checks, "pair_identities": pair}
        tables[case] = rows
        write_csv(out/f"compare_{case}.csv", rows)
        write_csv(out/f"trajectories_{case}.csv", traces)
        by = {r["strategy"]: r for r in rows}
        low, iso = by["minimum_cost"], by["quarantine_only"]
        derived[case] = {"minimum_vs_quarantine": {
            "cost_change_pct": 100*(low["J_state"]/iso["J_state"]-1),
            "duration_change_pct": 100*(low["duration_state"]/iso["duration_state"]-1),
            "total_infections_change_pct": 100*(low["total_infections_to_clearance"]/iso["total_infections_to_clearance"]-1),
            "Sq_change_pct": 100*(low["Sq_increment_plateau"]/iso["Sq_increment_plateau"]-1)}, "strategies": by}
    write_json(out/"TDINN_external_reference.json", {
        "scope": "既有正式参照，不重新积分，不属于共同阈值控制类",
        "I_peak_T": ref["I_peak_T"], "J_T": ref["J_T"], "Itcum_T": ref["Itcum_T"], "t_end_T": ref["t_end_T"],
        "peak_I_plus_Iq": None, "t1": None, "t2": None,
        "missing_metrics": "reference没有现存感染总峰值，本轮留空而非重新计算"})
    write_json(out/"candidate_checks_A.json", reports)
    return {"passed": bool(all(r["passed"] for r in reports.values())), "cases": reports}, derived


def capacity_edge_checks(p, e):
    B = (1-p.q0)*p.Sc/e["Sstar"]
    qm = 1-B
    points = [
        ("both_single", 0., (1+qm)/2, "single_feasible"),
        ("joint_equality", .5*p.c0, 1-B/.5, "joint_required"),
        ("outside", .5*p.c0, 1-B/.5-1e-6, "infeasible_at_trigger"),
        ("only_contact", 0., p.q0, "single_feasible"),
        ("only_quarantine", p.c0, (1+qm)/2, "single_feasible"),
        ("fully_no_extra", p.c0, p.q0, "infeasible_at_trigger")]
    rows = []
    for name, cm, qc, expected in points:
        got = core.capacity_classification(p, e, cm, qc)
        rows.append({"name": name, "cmin": cm, "qcap": qc, **got, "expected": expected,
                     "passed": got["classification"] == expected})
    return {"passed": all(r["passed"] for r in rows), "rows": rows,
            "unconstrained": core.candidates(e["Sstar"], p)["x"],
            "degenerate_exit": core.candidates(p.Sc, p)["x"]}


def task_B(cases, entries, out, cache, derived):
    cap, reports = {}, {}
    for case, p in cases.items():
        print("JOINT_EXTRA_B", case, flush=True)
        e = entries[case]
        pt = {**CAPACITY_POINTS[case], "c_min": .5*p.c0}
        cls = core.capacity_classification(p, e, pt["c_min"], pt["q_cap"])
        if cls["classification"] != "joint_required":
            raise ArithmeticError("指定代表点不属于必须联合区域")
        row, trace, checked, pol = _evaluate(case, p, e, "minimum_cost", out, cmin=pt["c_min"], qcap=pt["q_cap"], cache=cache[case])
        boundaries = {}
        for name in ("capacity_lower", "capacity_upper"):
            rr, _, cc, _ = _evaluate(case, p, e, name, out, cmin=pt["c_min"], qcap=pt["q_cap"], cache=cache[case], tighten=False)
            boundaries[name] = {"metrics": rr, "validation": cc["validation"]}
        times_ok = (boundaries["capacity_upper"]["metrics"]["duration_state"]-V.A["time_absolute_days"]
                    <= row["duration_state"] <= boundaries["capacity_lower"]["metrics"]["duration_state"]+V.A["time_absolute_days"])
        un = core.evaluate_policy(core.build_profile(p, e, ns=V.A["settings"]["state_nodes"]))
        increase = row["J_state"]-un["J_state"]
        edges = capacity_edge_checks(p, e)
        equality_point = next(v for v in edges["rows"] if v["name"] == "joint_equality")
        eq_row, eq_trace, eq_checked, _ = _evaluate(case, p, e, "minimum_cost", out,
            cmin=equality_point["cmin"], qcap=equality_point["qcap"], cache=cache[case])
        write_csv(out/f"capacity_equality_traj_{case}.csv", eq_trace)
        passed = bool(checked["validation"]["passed"] and all(v["validation"]["passed"] for v in boundaries.values())
                      and times_ok and increase >= -V.A["cost_absolute_days"] and edges["passed"] and eq_checked["validation"]["passed"])
        B = (1-p.q0)*p.Sc/e["Sstar"]
        sst = e["Sstar"]/p.Sc
        cap[case] = {"q0": p.q0, "s_star": sst, "q_required_quarantine_only": 1-B,
                     "u_required_contact_only": 1-1/sst, "joint_feasibility_bound": B,
                     "point": pt, "plot_viewport": {"post_exit_days": 1.0}, **cls, "metrics": row, **row, "cost_increase_vs_unconstrained": increase,
                     "passed": passed}
        u, q = np.linspace(0., .999, V.A["settings"]["phase_capacity_nodes"]), np.linspace(p.q0, .999, V.A["settings"]["phase_capacity_nodes"])
        U, Q = np.meshgrid(u, q)
        single = (Q >= 1-B) | (U >= 1-1/sst)
        joint = (1-U)*(1-Q) <= B
        region = np.where(joint, np.where(single, 2, 1), 0).astype(np.int8)
        boundary_u = np.linspace(0., .999, 1201)
        boundary_q = 1-B/(1-boundary_u)
        ok = (boundary_q >= p.q0) & (boundary_q < 1.)
        np.savez_compressed(out/f"capacity_{case}.npz", u=u, q=q, region=region,
                            boundary_u=boundary_u[ok], boundary_q=boundary_q[ok],
                            quarantine_line=np.array([1-B]), contact_line=np.array([1-1/sst]))
        write_csv(out/f"capacity_traj_{case}.csv", trace)
        reports[case] = {"passed": passed, "minimum_cost": checked, "allowed_boundaries": boundaries,
                         "time_bounds_passed": times_ok, "cost_increase": increase, "edge_cases": edges,
                         "joint_equality": {"parameters": equality_point, "metrics": eq_row, **eq_checked}}
    write_json(out/"capacity.json", cap)
    write_json(out/"candidate_checks_B.json", reports)
    return {"passed": all(v["passed"] for v in reports.values()), "cases": reports}, cap


def task_C(cases, entries, out, cache):
    summary, reports = {}, {}
    for case, p in cases.items():
        print("JOINT_EXTRA_C", case, flush=True)
        e = entries[case]
        s = np.linspace(1., e["Sstar"]/p.Sc, V.A["settings"]["phase_state_nodes"])
        shape = (len(R_GRID), len(s))
        yy, classes, ties = np.full(shape, np.nan), np.full(shape, 3, dtype=np.int8), np.zeros(shape, dtype=np.int16)
        cell_passed = np.zeros(shape, dtype=bool)
        residuals, deriv_residuals, objective_gaps, interval_violations = (np.full(shape, np.nan) for _ in range(4))
        switch, multi_lo, multi_hi, switch_records, switch_checks = [], [], [], [], []
        for j, r in enumerate(R_GRID):
            if j % 40 == 0:
                print("PHASE_ROW", case, j, len(R_GRID), flush=True)
            rows = [core.candidates(float(v*p.Sc), p, 1., float(r)) for v in s]
            for k, rec in enumerate(rows[1:], 1):
                yy[j, k] = rec["y"]
                classes[j, k] = 1 if rec["branch"] == "upper" else 2 if rec["branch"] == "lower" else 0
                ties[j, k] = rec["near_tie_count"]
                cell = V.phase_cell_check(rec, float(s[k]*p.Sc), p, float(r))
                cell_passed[j, k] = cell["passed"]
                residuals[j, k] = cell["root_residual"]
                deriv_residuals[j, k] = cell["original_derivative_residual"]
                objective_gaps[j, k] = cell["candidate_objective_gap"]
                interval_violations[j, k] = cell["interval_violation"]
            indices = np.flatnonzero(classes[j] == 1)
            sw = np.nan
            if len(indices):
                k = int(indices[0])
                if k > 1:
                    sr = core._locate_switch(p, s[k-1]*p.Sc, s[k]*p.Sc, rows[k-1], rows[k], 1., float(r), 0., 0., None)
                    sw = sr["S"]/p.Sc
                    switch_records.append({"r": float(r), **sr})
                    switch_checks.append(V.phase_switch_check(sr, p, float(r), (s[k-1]*p.Sc, s[k]*p.Sc)))
                else:
                    sw = float(s[k])
            switch.append(sw)
            multi = [k for k, rec in enumerate(rows[1:], 1) if sum(v.get("local_minimum") is True for v in rec["records"]) > 1]
            multi_lo.append(float(s[min(multi)]) if multi else np.nan)
            multi_hi.append(float(s[max(multi)]) if multi else np.nan)
        local = (3+np.sqrt(9-8*p.Sbar/p.Sc))/2
        np.savez_compressed(out/f"phase_{case}.npz", s=s, r=R_GRID, y=yy, classification=classes,
                            near_tie_count=ties, switch=np.asarray(switch),
                            cell_passed=cell_passed, root_residual=residuals,
                            original_derivative_residual=deriv_residuals, candidate_objective_gap=objective_gaps,
                            interval_violation=interval_violations,
                            two_minima_lo=np.asarray(multi_lo), two_minima_hi=np.asarray(multi_hi))
        weight_checks = {}
        for r in (.1, .5, 1., 2., 5., 20.):
            row, _, checked, _ = _evaluate(case, p, e, "minimum_cost", out, wq=r, cache=cache[case])
            weight_checks[str(r)] = {"metrics": row, **checked}
        # 有限参数点的局部端点判据回代；等号不强行分类。
        local_check = []
        for r in (.1, .5, 1., 2., 5., 20.):
            for sc_ratio in (1.01, max(1.02, local-.01), min(e["Sstar"]/p.Sc, local+.01), e["Sstar"]/p.Sc):
                S, x = sc_ratio*p.Sc, 1.
                rr, b = p.Sc/S, p.Sbar/S
                derivative_hi = (2*r*rr*(x-rr))*(x-b)-r*(1-rr)**2
                local_check.append({"r": r, "S_over_Sc": sc_ratio, "upper_derivative": derivative_hi,
                                    "passed": bool((derivative_hi < 0) == (sc_ratio > local))})
        grid_checked = {"passed": bool(np.all(cell_passed[:, 1:])), "nondegenerate_cells": int(cell_passed[:, 1:].size),
            "failed_cells": np.argwhere(~cell_passed[:, 1:]).tolist(),
            "maximum_root_residual": float(np.nanmax(residuals)),
            "maximum_original_derivative_residual": float(np.nanmax(deriv_residuals)),
            "maximum_candidate_objective_gap": float(np.nanmax(objective_gaps)),
            "maximum_interval_violation": float(np.nanmax(interval_violations)),
            "Sc_masked_not_validated": True, "scope": "所有实际计算相图单元的候选/残差/区间核查；独立网格仍限代表状态"}
        passed = bool(all(v["validation"]["passed"] for v in weight_checks.values()) and all(x["passed"] for x in local_check)
                      and grid_checked["passed"] and all(v["passed"] for v in switch_checks))
        summary[case] = {"s_sw": local, "S_sw": local*p.Sc, "s_star": e["Sstar"]/p.Sc, "sbar": p.Sbar/p.Sc,
                         "default_ratio": 2., "Sc_endpoint_share_filled": False,
                         "classification_codes": {"0": "interior", "1": "upper/quarantine_only", "2": "lower/contact_only", "3": "degenerate/masked"},
                         "local_threshold_not_global_for_all_r": True, "passed": passed,
                         "switches": switch_records}
        reports[case] = {"passed": passed, "weights": weight_checks, "local_endpoint_checks": local_check,
                         "all_phase_cells": grid_checked, "switch_location_checks": switch_checks,
                         "near_tie_cells": int(np.sum(ties > 1)), "scope": "有限r/S数值候选，不是全参数解析分类"}
    write_json(out/"phase.json", summary)
    write_json(out/"candidate_checks_C.json", reports)
    return {"passed": all(r["passed"] for r in reports.values()), "cases": reports}, summary


def task_D(cases, entries, out, cache):
    p, e = cases["baseline"], entries["baseline"]
    print("JOINT_EXTRA_D", "baseline", flush=True)
    rows, checks = [], []
    for j, kappa in enumerate(KAPPA):
        if j % 40 == 0:
            print("KAPPA", j, len(KAPPA), flush=True)
        try:
            coarse = core.build_profile(p, e, kappa=float(kappa), ns=V.A["settings"]["frontier_state_nodes"])
            state = core.evaluate_policy(coarse)
            refined = core.build_profile(p, e, kappa=float(kappa), ns=V.A["settings"]["frontier_refined_state_nodes"])
            fine = core.evaluate_policy(refined)
            conv = V.convergence(state, fine)
            diag = V.candidate_checks(refined, states=5)
        except Exception as error:
            failed = {"kappa": float(kappa), "passed": False, "status": "failed_exception",
                      "error": str(error), "traceback": traceback.format_exc()}
            checks.append(failed)
            rows.append({"kappa": float(kappa), "duration": None, "J": None, "passed": False,
                         "status": "failed_exception", "duration_gap_before": True, "connection_group": -1})
            write_csv(out/"frontier_baseline_checkpoint.csv", rows)
            write_json(out/"candidate_checks_D_checkpoint.json", {"scan": checks, "completed": j+1,
                "failed_point": failed, "passed": False, "note": "阶段失败记录不替代全任务验收"})
            # 保留失败点并继续检查既定扫描范围；该点始终令D不通过。
            continue
        passed = bool(conv["passed"] and diag["passed"])
        rows.append({"kappa": float(kappa), "duration": fine["duration_state"], "J": fine["J_state"],
                     "plateau_infections": fine["plateau_infections_state"], "plateau_new_Sq": fine["Sq_increment_plateau_state"],
                     "branch_jump": any(v["jump"] for v in refined.switches), "passed": passed,
                     "status": "passed_numeric_support" if passed else "failed", "duration_gap_before": False, "connection_group": 0})
        checks.append({"kappa": float(kappa), "convergence": conv, "candidates": diag})
        if j % 40 == 0 or not passed:
            write_csv(out/"frontier_baseline_checkpoint.csv", rows)
            write_json(out/"candidate_checks_D_checkpoint.json", {"scan": checks, "completed": j+1,
                "passed": False, "note": "阶段检查点，尚未完成全任务验收；失败点不剔除"})
    monotone = all(rows[j]["duration"] is not None and rows[j+1]["duration"] is not None and
                   rows[j+1]["duration"] <= rows[j]["duration"]+V.A["time_absolute_days"] for j in range(len(rows)-1))
    # 邻点大间距只作待核查缺口，连线保守中断；不宣称可达集存在已证明的空洞。
    delta = np.abs(np.diff([r["duration"] if r["duration"] is not None else np.nan for r in rows]))
    finite = delta[np.isfinite(delta) & (delta > V.A["time_absolute_days"])]
    median = np.median(finite) if len(finite) else 0.
    group = 0
    for j in range(1, len(rows)):
        gap = bool(not rows[j-1]["passed"] or not rows[j]["passed"] or
                   not np.isfinite(delta[j-1]) or delta[j-1] > max(.5, 10*median))
        if gap:
            group += 1
        rows[j]["duration_gap_before"], rows[j]["connection_group"] = gap, group
    arows = []
    for alpha in np.linspace(0., 1., 41):
        pol = core.build_profile(p, e, name=f"alpha_{alpha:.17g}", ns=4001)
        state = core.evaluate_policy(pol)
        arows.append({"alpha": float(alpha), "duration": state["duration_state"], "J": state["J_state"],
                      "plateau_infections": state["plateau_infections_state"], "plateau_new_Sq": state["Sq_increment_plateau_state"]})
    representatives = {}
    write_csv(out/"frontier_baseline.csv", rows)
    write_json(out/"candidate_checks_D_checkpoint.json", {"scan": checks, "completed": len(KAPPA),
        "passed": False, "note": "扫描完成；完整ODE代表点尚在核查，失败点不剔除"})
    for k in (-1., 0., .01, 1.):
        row, _, checked, _ = _evaluate("baseline", p, e, "minimum_cost", out, kappa=k, cache=cache["baseline"])
        representatives[str(k)] = {"metrics": row, **checked}
    passed = bool(all(r["passed"] for r in rows) and monotone and all(v["validation"]["passed"] for v in representatives.values()))
    write_csv(out/"frontier_baseline.csv", rows)
    write_csv(out/"alpha_family_baseline.csv", arows)
    write_json(out/"candidate_checks_D.json", {"scan": checks, "time_representatives": representatives})
    report = {"passed": passed, "scan_points": len(rows), "kappa_duration_nonincreasing": monotone,
              "representatives": representatives, "failed_points": [r["kappa"] for r in rows if not r["passed"]],
              "curve_connection_policy": "扫描支持点；明显邻点时间间距保守断线，不证明全可达集连续或缺口不存在",
              "sufficient_optimality_scope": "取得匹配实际时长的乘子解时，κ>=0支持时长上限，κ<=0支持时长下限；不认证整个前沿完备"}
    return report, {"passed": passed, "minimum_cost_point": next(r for r in rows if r["kappa"] == 0),
                    "scan_points": len(rows), "supported_scan_points": sum(r["passed"] for r in rows),
                    "representatives": {k: v["metrics"] for k, v in representatives.items()},
                    "comparison_with_alpha_at_same_time_proved": False}


def _plot(out, textwidth_bp=None):
    path = HERE/"figures.py"
    if not path.exists():
        raise FileNotFoundError("绘图层尚未建立")
    if textwidth_bp is None:
        man = json.loads((out/"input_manifest.json").read_text(encoding="utf-8"))
        textwidth_bp = man.get("publication", {}).get("textwidth_bp")
    if textwidth_bp is None or not np.isfinite(textwidth_bp) or textwidth_bp <= 0:
        raise ValueError("绘图需显式传入实测 --textwidth-bp，或计算manifest已有同版本实测宽度")
    subprocess.run([sys.executable, "-B", str(path), "--res", str(out), "--out", str(out/"figures"),
                    "--textwidth-bp", format(textwidth_bp, ".17g")], check=True)


def run(output_dir, root=core.ROOT, baseline_path=None, xian_reference=None, tasks=None, mode="compute", textwidth_bp=None):
    out, root = Path(output_dir).resolve(), Path(root).resolve()
    tasks = list(dict.fromkeys(tasks or ["A", "B", "C", "D"]))
    if not set(tasks) <= {"A", "B", "C", "D"}:
        raise ValueError("任务仅允许A/B/C/D")
    if mode == "plot":
        _plot(out, textwidth_bp)
        return json.loads((out/"validation.json").read_text(encoding="utf-8"))
    if mode == "verify":
        saved = json.loads((out/"validation.json").read_text(encoding="utf-8"))
        man = json.loads((out/"input_manifest.json").read_text(encoding="utf-8"))
        unchanged = all(core.sha(HERE/name) == value for name, value in man["calculation_source_hashes"].items())
        result = {"passed": bool(unchanged and saved["passed"]), "source_hashes_unchanged": unchanged,
                  "scope": "既有本轮结果静态核查，不重新执行科学计算", "tasks": saved["tasks"]}
        write_json(out/("verification_"+dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f")+".json"), result)
        return result
    if mode not in ("compute", "all"):
        raise ValueError("未知运行模式")
    if mode == "all" and textwidth_bp is None:
        raise ValueError("all模式须指定当前模板实测 --textwidth-bp；不得固定旧模板宽度")
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("计算输出必须为空，不覆盖已有结果："+str(out))
    for forbidden in (root/"latex", root/"ai", root/"joint_control"):
        if out == forbidden or forbidden in out.parents:
            raise ValueError("结果不能写入论文、讨论来源或冻结包")
    out.mkdir(parents=True, exist_ok=True)
    cases, ref, sources = core.load_inputs(root, baseline_path, xian_reference)
    entries = {case: core.basics(p) for case, p in cases.items()}
    source_hashes = {name: core.sha(HERE/name) for name in ("core.py", "run.py", "validation.py", "acceptance.json")}
    manifest = {"schema": "joint-extra-v2", "created": dt.datetime.now().isoformat(), "root": str(root),
                "inputs": sources, "cases": {case: {"parameters": asdict(p), "derived": entries[case]} for case, p in cases.items()},
                "acceptance": core.ACCEPTANCE, "calculation_source_hashes": source_hashes,
                "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
                "tasks_requested": tasks, "settings": {"capacity_points": CAPACITY_POINTS, "r_grid": R_GRID,
                                                        "kappa_grid": KAPPA, "weights": [1., 2.],
                                                        "kappa_grid_construction": {
                                                            "original_grid": ORIGINAL_KAPPA,
                                                            "refinement_grid": KAPPA_REFINEMENT,
                                                            "original_count": len(ORIGINAL_KAPPA),
                                                            "refinement_count": len(KAPPA_REFINEMENT),
                                                            "final_count": len(KAPPA),
                                                            "refinement_interval": [-.6, -.2],
                                                            "refinement_step": .002,
                                                            "duplicate_absolute_tolerance": KAPPA_DUPLICATE_TOLERANCE,
                                                            "retention_rule": "按绝对差去除近重复，优先保留原310点的完整浮点值"}},
                "publication": {"textwidth_bp": textwidth_bp, "source": "调用者本轮同版本TeX实测；不作为科学参数"},
                "xian_input_scope": "继承指定已验收reference完整拟合初值与TDINN参照；本轮不fit、不重新积分TDINN"}
    write_json(out/"input_manifest.json", manifest)
    # 冻结门槛另存，不在观察结果后调松。
    write_json(out/"acceptance.json", core.ACCEPTANCE)
    cache = _cache(cases, entries)
    report = {"passed": False, "status": "running", "tasks": {}, "scientific_rerun_scope": "仅本轮新增A-D模块；无MATLAB旧图重算或西安重新拟合"}
    derived = {"cases": {}, "scope": "统一未取整指标派生，不把不同成本/医疗资源指标百分比相减"}
    functions = {"A": lambda: task_A(cases, entries, ref, out, cache),
                 "B": lambda: task_B(cases, entries, out, cache, derived),
                 "C": lambda: task_C(cases, entries, out, cache),
                 "D": lambda: task_D(cases, entries, out, cache)}
    caught_warnings = []
    for name in tasks:
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                task, summary = functions[name]()
            caught_warnings.extend({"task": name, "message": str(w.message), "category": w.category.__name__} for w in caught)
            report["tasks"][name] = {"status": "passed" if task["passed"] else "failed", **task}
            if name == "A":
                derived["cases"] = summary
            else:
                derived[{"B": "capacity", "C": "phase", "D": "duration_cost"}[name]] = summary
        except Exception as exc:
            report["tasks"][name] = {"passed": False, "status": "failed", "error": str(exc), "traceback": traceback.format_exc()}
            print("TASK_FAILED", name, repr(exc), flush=True)
        write_json(out/"validation.json", report)
        write_json(out/"derived_summary.json", derived)
    for name in ("A", "B", "C", "D"):
        report["tasks"].setdefault(name, {"passed": False, "status": "not_executed"})
    successes = [v["passed"] for v in report["tasks"].values() if v["status"] != "not_executed"]
    report["passed"] = bool(successes and all(successes))
    report["status"] = "passed" if report["passed"] else "partial" if any(successes) else "failed"
    report["warnings"] = caught_warnings
    report["precision_scope"] = "数值候选/根残差/独立网格/两档开环核查，非严格根隔离、数学全域证明或临床验证"
    write_json(out/"validation.json", report)
    write_json(out/"derived_summary.json", derived)
    write_json(out/"candidate_checks.json", {name: f"candidate_checks_{name}.json" for name in tasks if (out/f"candidate_checks_{name}.json").exists()})
    write_json(out/"convergence.json", {"scope": "各任务候选检查JSON内的state/time/convergence字段", "tasks": {
        name: f"candidate_checks_{name}.json" for name in tasks if (out/f"candidate_checks_{name}.json").exists()}})
    if mode == "all" and any(report["tasks"][name]["passed"] for name in tasks):
        _plot(out, textwidth_bp)
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=core.ROOT)
    ap.add_argument("--baseline", type=Path)
    ap.add_argument("--xian-reference", type=Path)
    ap.add_argument("--out", "--output-dir", type=Path)
    ap.add_argument("--mode", choices=("compute", "plot", "verify", "all"), default="compute")
    ap.add_argument("--tasks", default="A,B,C,D")
    ap.add_argument("--textwidth-bp", type=float, help="plot/all需要当前稿件实测textwidth，不沿用硬编码旧尺寸")
    args = ap.parse_args()
    out = args.out or args.root/"reproducibility/results"/("joint_extra_v2_"+dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    result = run(out, args.root, args.baseline, args.xian_reference, [v.strip().upper() for v in args.tasks.split(",")], args.mode, args.textwidth_bp)
    print(json.dumps({"passed": result["passed"], "status": result.get("status"), "out": str(out)}, ensure_ascii=False), flush=True)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
