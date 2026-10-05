"""冻结量纲门槛下的候选、时间开环、计数与收敛检查。"""
from __future__ import annotations

import numpy as np
if __package__:
    from . import core
else:
    import core

A = core.ACCEPTANCE


def quadrature_checks(state):
    errors = {"duration_days": float(state["quad_duration_estimate"]),
              "cost_days": float(state["quad_cost_estimate"]),
              "count_persons": float(state["quadrature_count_estimate"])}
    passed = (errors["duration_days"] <= A["time_absolute_days"] and
              errors["cost_days"] <= A["cost_absolute_days"] and
              errors["count_persons"] <= min(A["count_absolute_persons"], A["identity_absolute_persons"]))
    return {"passed": bool(passed), "order_differences": errors,
            "orders": state["quadrature_order_values"], "estimate_is_rigorous": False}


def policy_checks(policy, state, time):
    p, e = policy.p, policy.entry
    diffs = {"duration_days": abs(state["duration_state"]-time["duration_time"]),
             "cost_days": abs(state["J_state"]-time["J_time"]),
             "clearance_time_days": abs(state["t_end_state"]-time["t_end"]),
             "cumulative_persons": abs(state["total_infections_state"]-time["total_infections_to_clearance"]),
             "plateau_infections_identity_persons": abs(state["plateau_infections_state"]-time["plateau_infections_time"]),
             "plateau_Sq_identity_persons": abs(state["Sq_increment_plateau_state"]-time["Sq_increment_plateau"])}
    checked_quad = quadrature_checks(state)
    checks = {"state_quadrature": checked_quad["passed"],
              "duration": diffs["duration_days"] <= A["time_absolute_days"],
              "cost": diffs["cost_days"] <= A["cost_absolute_days"],
              "clearance_time": diffs["clearance_time_days"] <= A["time_absolute_days"],
              "cumulative": diffs["cumulative_persons"] <= A["count_absolute_persons"],
              "infection_identity": diffs["plateau_infections_identity_persons"] <= A["identity_absolute_persons"],
              "Sq_identity": diffs["plateau_Sq_identity_persons"] <= A["identity_absolute_persons"],
              "platform": time["plateau_abs_error"] <= A["plateau_absolute_persons"],
              "whole_trajectory_I_bound": time["I_threshold_excess"] <= A["plateau_absolute_persons"],
              "mass": time["mass_absolute_error"] <= A["mass_absolute_persons"],
              "nonnegative": time["minimum_compartment"] >= A["minimum_compartment_persons"],
              "exit_S": abs(time["exit_S_error"]) <= A["count_absolute_persons"],
              "exit_I": abs(time["exit_I_error"]) <= A["plateau_absolute_persons"],
              "clearance_event": abs(time["clearance_I_error"]) <= A["clearance_absolute_persons"] and time["clearance_direction"] < 0,
              "entry_time": abs(time["entry_time_error"]) <= A["time_absolute_days"],
              "entry_state": abs(time["entry_S_error"]) <= A["count_absolute_persons"],
              "c_bounds": time["c_min"] >= policy.cmin-A["control_c_absolute"] and time["c_max"] <= p.c0+A["control_c_absolute"],
              "q_bounds": time["q_min"] >= p.q0-A["control_q_absolute"] and time["q_max"] <= (policy.qcap if policy.qcap is not None else 1.)+A["control_q_absolute"],
              "peak_search": time["peak_search_change"] <= A["peak_search_value_absolute_persons"],
              "I_peak_search": time["I_peak_search_change"] <= A["peak_search_value_absolute_persons"]}
    return {"passed": bool(all(checks.values())), "checks": {k: bool(v) for k, v in checks.items()},
            "absolute_method_differences": diffs, "root_residual_max": policy.diagnostics.get("maximum_root_residual", 0.),
            "observation_interval": time["observation_interval"],
            "state_quadrature": checked_quad,
            "precision_scope": "数值稠密解/分段开环/求积阶数及两档收敛；不认证根完整性、一般全局最优或无限时域峰值"}


def convergence(first, second, *, time=False):
    keys = ["duration_time", "J_time", "total_infections_to_clearance", "t_end", "peak_I_plus_Iq", "max_I_to_clearance"] if time else ["duration_state", "J_state", "total_infections_state", "t_end_state"]
    differences = {k: float(abs(first[k]-second[k])) for k in keys}
    checks = {k: d <= (A["peak_search_value_absolute_persons"] if k in ("peak_I_plus_Iq", "max_I_to_clearance") else A["count_absolute_persons"] if "infections" in k else A["cost_absolute_days"] if k.startswith("J") else A["time_absolute_days"]) for k, d in differences.items()}
    quad = {} if time else {"first": quadrature_checks(first), "second": quadrature_checks(second)}
    return {"passed": bool(all(checks.values()) and all(row["passed"] for row in quad.values())), "absolute_change": differences,
            "quadrature": quad,
            "display_stability_four_decimals": {k: format(first[k], ".4f") == format(second[k], ".4f") for k in keys if not "infections" in k},
            "note": "数值容差通过不自动证明取整分界；显示小数另外核对"}


def candidate_checks(policy, states=17):
    grid_states = np.unique(np.r_[np.linspace(policy.p.Sc, policy.entry["Sstar"], states)[1:],
                                 policy.p.Sc/(1-np.asarray(A["near_exit_z"]))])
    grid_states = grid_states[grid_states <= policy.entry["Sstar"]]
    rows = [core.grid_check(float(S), policy.p, policy.wc, policy.wq, policy.kappa,
                           policy.cmin, policy.qcap, nx=A["settings"]["independent_grid_nodes"]) for S in grid_states]
    profile = []
    for S in grid_states:
        exact = core.candidates(float(S), policy.p, policy.wc, policy.wq, policy.kappa, policy.cmin, policy.qcap)
        selected_x = policy.x(float(S))
        selected_value = core.objective(selected_x, S, policy.p, policy.wc, policy.wq, policy.kappa)
        exact_value = core.objective(exact["x"], S, policy.p, policy.wc, policy.wq, policy.kappa)
        gap = abs(selected_value-exact_value)
        profile.append({"S": float(S), "profile_x": selected_x, "candidate_x": exact["x"],
                        "objective_difference": float(gap),
                        "passed": bool(gap <= A["independent_grid_objective_relative"]*max(1., abs(exact_value))),
                        "scope": "实际允许份额插值与逐点候选的代表状态对照"})
    limits = []
    if policy.kappa == 0 and policy.cmin == 0 and policy.qcap is None:
        limit = policy.wq/(policy.wc+policy.wq)
        for z in A["near_exit_z"]:
            S = policy.p.Sc/(1-z)
            if S <= policy.entry["Sstar"]:
                row = core.candidates(S, policy.p, policy.wc, policy.wq)
                error = abs(row["y"]-limit)
                limits.append({"z_requested": z, "z_actual": 1-policy.p.Sc/S, "S": S,
                               "selected_y": row["y"], "limit": limit, "absolute_error": error,
                               "tested_against_limit": z <= A["near_exit_share_test_max_z"],
                               "passed": bool(z > A["near_exit_share_test_max_z"] or error <= A["near_exit_share_absolute"]),
                               "source": "非退化状态实际求根，未填充Sc端点"})
    recs = policy.diagnostics.get("representative_candidates", [])
    residuals = [r.get("original_derivative_residual", 0.) for row in recs for r in row["records"] if r["branch"] == "interior"]
    original_max = max(residuals, default=0.)
    coordinate = []
    for S in grid_states:
        if 1-policy.p.Sc/S >= 1e-4:
            x = core.candidates(S, policy.p, policy.wc, policy.wq, policy.kappa, policy.cmin, policy.qcap, force_coordinate="x")
            y = core.candidates(S, policy.p, policy.wc, policy.wq, policy.kappa, policy.cmin, policy.qcap, force_coordinate="y")
            gap = abs(x["x"]-y["x"])
            objgap = abs(x.get("objective", 0.)-y.get("objective", 0.))
            tie = x["near_tie_count"] > 1 or y["near_tie_count"] > 1
            coordinate.append({"S": float(S), "x_difference": gap, "objective_difference": objgap,
                               "near_tie": tie, "passed": bool(gap <= A["coordinate_x_absolute"] or (tie and objgap < 1e-8))})
    return {"passed": bool(all(r["passed"] for r in rows+limits+coordinate+profile) and original_max <= A["root_normalized_residual"]),
            "independent_grid": rows, "near_exit_share": limits,
            "coordinate_cross_check": coordinate,
            "actual_profile_candidate_comparison": profile,
            "maximum_original_derivative_residual": original_max, **policy.diagnostics}


def phase_cell_check(row, S, p, wq):
    lo, hi = core.bounds(S, p)
    violation = max(0., lo-row["x"], row["x"]-hi)
    root_residual = max((r["root_residual"] for r in row["records"]), default=0.)
    derivative_residual = max((r.get("original_derivative_residual", 0.) for r in row["records"]), default=0.)
    values = [r["value"] for r in row["records"]]
    selected = core.objective(row["x"], S, p, 1., wq)
    gap = abs(selected-min(values)) if values else 0.
    passed = (violation*p.c0 <= A["control_c_absolute"] and
              root_residual <= A["root_normalized_residual"] and derivative_residual <= A["root_normalized_residual"] and
              gap <= A["independent_grid_objective_relative"]*max(1., abs(selected)))
    return {"passed": bool(passed), "root_residual": root_residual, "original_derivative_residual": derivative_residual,
            "interval_violation": violation, "candidate_objective_gap": gap}


def phase_switch_check(record, p, wq, bracket):
    S = record["S"]
    all_rows = core.candidates(S, p, 1., wq)
    values = [core.objective(record[k], S, p, 1., wq) for k in ("x_low_S", "x_high_S")]
    gap = abs(values[0]-values[1])
    min_gap = abs(min(values)-min(r["value"] for r in all_rows["records"]))
    # 在原相图单元中加密定位同一全球上端点交接，而非另取理论阈值代替。
    refined_states = np.linspace(*bracket, 17)
    refined_rows = [core.candidates(float(v), p, 1., wq) for v in refined_states]
    pairs = [(j-1, j) for j in range(1, len(refined_rows))
             if refined_rows[j-1]["branch"] != "upper" and refined_rows[j]["branch"] == "upper"]
    if not pairs:
        return {"passed": False, "reason": "加密单元未识别同一上端点交接", "S": S, "r": wq}
    a, b = min(pairs, key=lambda ab: abs(.5*(refined_states[ab[0]]+refined_states[ab[1]])-S))
    refined = core._locate_switch(p, refined_states[a], refined_states[b], refined_rows[a], refined_rows[b], 1., wq, 0., 0., None)
    change = abs(S-refined["S"])
    tol = max(A["switch_absolute_S"], A["switch_relative_S"]*p.Sc)
    bounds_ok = all(core.bounds(S, p)[0]-1e-12 <= record[k] <= 1.+1e-12 for k in ("x_low_S", "x_high_S"))
    value_ok = max(gap, min_gap) <= A["independent_grid_objective_relative"]*max(1., abs(min(values)))
    left_branch, right_branch = refined_rows[a]["branch"], refined_rows[b]["branch"]
    return {"passed": bool(bounds_ok and value_ok and change <= tol),
            "S": S, "r": wq, "refined_S": refined["S"], "state_change": change,
            "state_tolerance": tol, "left_branch": left_branch, "right_branch": right_branch,
            "objective_cross_gap": gap, "global_candidate_gap": min_gap, "bounds_passed": bounds_ok,
            "scope": "原单元17点加密后重定位；有限数值核查，不是严格区间认证"}


def pair_identities(rows, p):
    anchor = rows[0]
    checks = []
    for row in rows[1:]:
        duration = row["duration_time"]-anchor["duration_time"]
        e1 = (row["t_end"]-anchor["t_end"])-duration
        e2 = (row["total_infections_to_clearance"]-anchor["total_infections_to_clearance"])-p.gamma*p.eta*(1-p.beta)*duration
        checks.append({"strategy": row["strategy"], "clearance_difference_error_days": abs(e1),
                       "infection_difference_error_persons": abs(e2),
                       "passed": bool(abs(e1) <= A["time_absolute_days"] and abs(e2) <= A["count_absolute_persons"])})
    return {"passed": bool(all(c["passed"] for c in checks)), "rows": checks}
