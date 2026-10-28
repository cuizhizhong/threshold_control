"""显式启动候选的完整 ODE 核验；不优化、不修改候选。

--run 评价目前已有文件；--run --watch 等待六类 best 及四级 progress 全部出现。
不同积分器、尾界目标与候选文件 SHA 均进入缓存身份，失败检查原样保留。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from evaluate import evaluate, load_params, reference, paired_threshold_status  # noqa: E402

RESULTS = ROOT / "results"
OUTPUT = RESULTS / "validation"
CASES = ("base", "xian")
OBJECTIVES = ("time", "infections", "cost")
MESHES = (20, 40, 80, 160)


def _read(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _digest(candidate):
    # 只比较实际控制与求解身份；同一候选在 progress 和 best 内的身份一致。
    text = json.dumps(candidate, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _brief(result):
    keys = ("evaluation_id", "saved_path", "archive_path", "case", "method", "rtol", "tail_tol_persons",
            "evaluation_schema", "evaluator_sha256", "numeric_status", "threshold_numeric_status",
            "first_exit_assessment",
            "duration", "J", "C_arc", "C_exit", "C_cut", "C_infinity_interval", "tail_bound_persons",
            "Sq_exit", "exit_residual_normalized", "first_Sc_exit_time", "early_first_Sc_exit",
            "platform_relative_deviation", "threshold_peak_ratio", "post_threshold_violation_relative",
            "mass_residual_normalized", "cumulative_identity_residual_normalized",
            "minimum_compartment_normalized", "platform_min_S_minus_Sc_normalized",
            "control_bound_violation", "feasible", "checks", "ode_calls", "nfev")
    return {k: result.get(k) for k in keys}


def _validate(candidate, method, tail_tol, cache, source):
    sha = _digest(candidate)
    evaluator_sha = hashlib.sha256((ROOT / "evaluate.py").read_bytes()).hexdigest()
    key = f"{sha}|{method}|1e-12|{tail_tol:.12g}|evaluator:{evaluator_sha}"
    if key in cache:
        result = _read(ROOT / cache[key]["saved_path"])
        if result is not None:
            return cache[key]
    case = candidate["case"]
    attempt = candidate.get("attempt", f"{case}_{candidate['objective']}_n{candidate['n']}")
    target = OUTPUT / f"{attempt}_{sha[:10]}_{method}_tail{tail_tol:.0e}_eval{evaluator_sha[:10]}.json"
    result = evaluate(case, candidate["duration"], candidate["lambda_values"],
                      interpolation=candidate.get("interpolation", "linear"),
                      method=method, rtol=1e-12, tail_tol=tail_tol, save_path=target)
    # 这些差异是报告值，不用来偷偷校正 duration 或终点。
    full = _read(target)
    full["candidate_identity"] = {"sha256": sha, "source": source, "attempt": attempt,
                                  "n": candidate["n"], "objective": candidate["objective"]}
    full["collocation_comparison"] = {
        "J_ODE_minus_collocation": result["J"] - candidate["J"],
        "C_interval_minus_collocation": [x - candidate["C_infinity_estimate"] for x in result["C_infinity_interval"]],
        "exit_state_N_ODE_minus_collocation": [
            result["exit_state_persons"]["S"] / load_params(case)["N"] - candidate["exit_state_N"][0],
            result["Sq_exit"] / load_params(case)["N"] - candidate["exit_state_N"][1]]}
    _dump(target, full)
    item = {"candidate_sha256": sha, "candidate_source": source, "attempt": attempt,
            "n": candidate["n"], "objective": candidate["objective"], **_brief(result),
            "collocation_comparison": full["collocation_comparison"]}
    cache[key] = item
    _dump(OUTPUT / "cache.json", cache)
    print(json.dumps({"validated": attempt, "method": method, "n": candidate["n"],
                      "J": result["J"], "C_infinity_interval": result["C_infinity_interval"],
                      "exit_residual": result["exit_residual_normalized"], "feasible": result["feasible"],
                      "false_checks": [k for k, v in result["checks"].items() if not v]}, ensure_ascii=False), flush=True)
    return item


def _method_comparison(a, b):
    ia, ib = a["C_infinity_interval"], b["C_infinity_interval"]
    return {"J_absolute_difference": abs(a["J"] - b["J"]),
            "C_cut_absolute_difference_persons": abs(a["C_cut"] - b["C_cut"]),
            "C_intervals_overlap": max(ia[0], ib[0]) <= min(ia[1], ib[1]),
            "exit_residual_difference_normalized": abs(a["exit_residual_normalized"] - b["exit_residual_normalized"]),
            "both_numerically_feasible": bool(a["feasible"] and b["feasible"]),
            "threshold_pair_status": paired_threshold_status(a["threshold_peak_ratio"], b["threshold_peak_ratio"])}


def run_available(run=False):
    cache = _read(OUTPUT / "cache.json") or {}
    summary = {"complete": False, "pending": [], "final": {}, "mesh": {},
               "scope": "完整五仓 ODE 评价；不运行优化，不改候选；尾界区间不含浮点积分误差"}
    for case in CASES:
        for objective in OBJECTIVES:
            label = f"{case}_{objective}"
            best_path = RESULTS / "collocation" / f"{label}_best.json"
            best = _read(best_path)
            if best is None:
                summary["pending"].append(str(best_path.relative_to(ROOT)))
            elif run:
                strict_tail = 1e-6 if case == "base" else 1e-3
                methods = {method: _validate(best, method, strict_tail, cache, str(best_path.relative_to(ROOT)))
                           for method in ("DOP853", "Radau")}
                summary["final"][label] = {"candidate": str(best_path.relative_to(ROOT)),
                    "candidate_sha256": _digest(best), "methods": methods,
                    "method_comparison": _method_comparison(methods["DOP853"], methods["Radau"])}
            progress_path = RESULTS / "collocation" / f"{label}_progress.json"
            progress = _read(progress_path) or []
            by_mesh = {row["n"]: row.get("best") for row in progress}
            levels = []
            for n in MESHES:
                candidate = by_mesh.get(n)
                if candidate is None:
                    summary["pending"].append(f"{progress_path.relative_to(ROOT)}:n{n}")
                elif run:
                    item = _validate(candidate, "DOP853", 1e-5 if case == "base" else 1e-3,
                                     cache, f"{progress_path.relative_to(ROOT)}:n{n}")
                    levels.append(item)
            if levels:
                changes = []
                for previous, current in zip(levels[:-1], levels[1:]):
                    changes.append({"from_n": previous["n"], "to_n": current["n"],
                        "duration_relative_change": abs(current["duration"] - previous["duration"]) / max(1.0, abs(current["duration"])),
                        "J_relative_change": abs(current["J"] - previous["J"]) / max(1.0, abs(current["J"])),
                        "C_cut_absolute_change_persons": abs(current["C_cut"] - previous["C_cut"]),
                        "C_interval_change_persons": [current["C_infinity_interval"][0] - previous["C_infinity_interval"][1],
                            current["C_infinity_interval"][1] - previous["C_infinity_interval"][0]],
                        "both_numerically_feasible": bool(previous["feasible"] and current["feasible"])})
                summary["mesh"][label] = {"levels": levels, "changes": changes}
    summary["complete"] = bool(run and not summary["pending"] and len(summary["final"]) == 6
                               and all(len(row["levels"]) == 4 for row in summary["mesh"].values()))
    if run:
        _dump(RESULTS / "final_evaluations.json", summary)
    return summary


def run_refined_infections():
    """只核验 scale10000 新文件，保留旧 best 与原六类评价。"""
    cache = _read(OUTPUT / "cache.json") or {}
    pattern = re.compile(r"^(base|xian)_infections_n160_(q_only|c_only|migrated)_\d+\.json$")
    found = {case: [] for case in CASES}
    for path in sorted((RESULTS / "collocation").glob("*infections_n160*.json")):
        match = pattern.match(path.name)
        if match:
            candidate = _read(path)
            if candidate and candidate.get("infection_objective_scale") == 10000.0:
                found[match.group(1)].append((path, candidate))
    result = {"complete": False, "protocol": "infection_scale10000_n160_independent_full_ODE",
              "old_best_untouched": True, "references": {}, "candidates": {}, "missing": []}
    for case in CASES:
        tail_tol = 1e-7 if case == "base" else 1e-5
        refs = {}
        for method in ("DOP853", "Radau"):
            path = OUTPUT / "refined_infections" / f"reference_{case}_q_only_{method}_tail{tail_tol:.0e}.json"
            existing = _read(path)
            if (existing and existing.get("parameter_sha256") == load_params(case)["source_sha256"]
                    and existing.get("tail_tol_persons") == tail_tol and existing.get("rtol") == 1e-12
                    and existing.get("evaluator_sha256") == hashlib.sha256((ROOT / "evaluate.py").read_bytes()).hexdigest()):
                refs[method] = _brief(existing)
            else:
                r = reference(case, "q_only", method=method, rtol=1e-12, tail_tol=tail_tol, save_path=path)
                refs[method] = _brief(r)
                print(json.dumps({"strict_reference": case, "method": method,
                    "C_infinity_interval": r["C_infinity_interval"], "feasible": r["feasible"]}, ensure_ascii=False), flush=True)
        result["references"][case] = {"methods": refs,
            "method_comparison": _method_comparison(refs["DOP853"], refs["Radau"])}
        kinds = set()
        for path, candidate in found[case]:
            seed = pattern.match(path.name).group(2)
            kinds.add(seed)
            item = _validate(candidate, "DOP853", tail_tol, cache, str(path.relative_to(ROOT)))
            a, b = item["C_infinity_interval"], refs["DOP853"]["C_infinity_interval"]
            item = {**item, "comparison_with_q_only": {
                "C_interval_difference_persons": [a[0] - b[1], a[1] - b[0]],
                "C_intervals_overlap": max(a[0], b[0]) <= min(a[1], b[1]),
                "duration_difference_days": item["duration"] - refs["DOP853"]["duration"],
                "J_difference": item["J"] - refs["DOP853"]["J"],
                "both_numerically_feasible": item["feasible"] and refs["DOP853"]["feasible"]}}
            result["candidates"][candidate["attempt"]] = item
        result["missing"].extend(f"{case}:{kind}" for kind in ("q_only", "c_only", "migrated") if kind not in kinds)
    result["complete"] = len(result["candidates"]) >= 6 and not result["missing"]
    _dump(RESULTS / "refined_infection_evaluations.json", result)
    return result


def _candidate_v2(candidate, path, method, tail_tol, run_id):
    source = str(path.relative_to(ROOT))
    output = OUTPUT / "v2" / run_id / f"{candidate['attempt']}_{method}.json"
    r = evaluate(candidate["case"], candidate["duration"], candidate["lambda_values"],
                 interpolation=candidate.get("interpolation", "linear"), method=method,
                 rtol=1e-12, tail_tol=tail_tol, save_path=output)
    return {**_brief(r), "candidate_identity": {"source": source,
        "raw_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "canonical_json_sha256": _digest(candidate), "attempt": candidate["attempt"]},
        "J_ODE_minus_candidate": r["J"] - candidate["J"]}


def run_acceptance_v2():
    """显式重评，不读取旧评价缓存；新旧验收回执分开保存。"""
    sha = hashlib.sha256((ROOT / "evaluate.py").read_bytes()).hexdigest()
    run_id = f"eval{sha[:10]}_{time.time_ns()}"
    result = {"complete": False, "receipt_version": "2", "run_id": run_id,
              "evaluator_sha256": sha, "representatives": {}, "method_comparisons": {},
              "missing": [], "scientific_pass_separate_from_complete": True}
    for case in CASES:
        tail_tol = 1e-7 if case == "base" else 1e-5
        for objective in OBJECTIVES:
            label = f"{case}_{objective}"
            methods = {}
            if objective == "infections":
                for method in ("DOP853", "Radau"):
                    path = OUTPUT / "v2" / run_id / f"{case}_infections_q_only_{method}.json"
                    r = reference(case, "q_only", method=method, rtol=1e-12, tail_tol=tail_tol, save_path=path)
                    methods[method] = {**_brief(r), "representative_identity": "q_only_state_feedback_first_Sc_exit",
                        "selection_note": "感染分辨率内选取仅隔离为最短代表，不宣称感染最优形态唯一"}
            else:
                path = RESULTS / "collocation" / f"{label}_best.json"
                candidate = _read(path)
                if candidate is None:
                    result["missing"].append(str(path.relative_to(ROOT)))
                    continue
                for method in ("DOP853", "Radau"):
                    methods[method] = _candidate_v2(candidate, path, method, tail_tol, run_id)
            result["representatives"][label] = methods
            result["method_comparisons"][label] = _method_comparison(methods["DOP853"], methods["Radau"])
            print(json.dumps({"v2_representative": label,
                "status": {m: x["numeric_status"] for m, x in methods.items()},
                "first_exit": {m: x["first_exit_assessment"]["status"] for m, x in methods.items()}}, ensure_ascii=False), flush=True)
            _dump(RESULTS / "final_acceptance_v2.json", result)
    result["complete"] = len(result["representatives"]) == 6 and not result["missing"]
    result["all_scientific_checks_pass"] = result["complete"] and all(
        item["feasible"] for pair in result["representatives"].values() for item in pair.values())
    _dump(RESULTS / "final_acceptance_v2.json", result)

    pattern = re.compile(r"^(base|xian)_infections_n160_(q_only|c_only|migrated)_\d+\.json$")
    refined = {"complete": False, "receipt_version": "2", "evaluator_sha256": sha,
               "run_id": run_id, "candidates": {}, "old_results_untouched": True}
    for path in sorted((RESULTS / "collocation").glob("*infections_n160*.json")):
        if pattern.match(path.name):
            candidate = _read(path)
            if candidate and candidate.get("infection_objective_scale") == 10000.0:
                case = candidate["case"]
                item = _candidate_v2(candidate, path, "DOP853", 1e-7 if case == "base" else 1e-5, run_id)
                ref = result["representatives"][f"{case}_infections"]["DOP853"]
                a, b = item["C_infinity_interval"], ref["C_infinity_interval"]
                item["comparison_with_q_only"] = {"C_intervals_overlap": max(a[0], b[0]) <= min(a[1], b[1]),
                    "C_interval_difference_persons": [a[0] - b[1], a[1] - b[0]],
                    "duration_difference_days": item["duration"] - ref["duration"]}
                refined["candidates"][candidate["attempt"]] = item
                print(json.dumps({"v2_refined": candidate["attempt"], "numeric_status": item["numeric_status"],
                    "first_exit": item["first_exit_assessment"]["status"], "feasible": item["feasible"]}, ensure_ascii=False), flush=True)
    refined["complete"] = len(refined["candidates"]) == 6
    refined["all_scientific_checks_pass"] = refined["complete"] and all(x["feasible"] for x in refined["candidates"].values())
    _dump(RESULTS / "refined_infection_evaluations_v2.json", refined)

    run_shooting_v2(result, run_id, sha)
    return result


def run_shooting_v2(result=None, run_id=None, sha=None):
    result = result or _read(RESULTS / "final_acceptance_v2.json")
    if not result or not result.get("complete"):
        raise RuntimeError("需先完成六代表 v2 评价")
    sha = sha or hashlib.sha256((ROOT / "evaluate.py").read_bytes()).hexdigest()
    run_id = run_id or f"eval{sha[:10]}_shooting_{time.time_ns()}"
    cross_path = RESULTS / "shooting_cross_n80.json"
    candidates = _read(cross_path) or []
    shooting = {"complete": False, "receipt_version": "2", "evaluator_sha256": sha,
                "run_id": run_id, "evaluations": {}, "source": str(cross_path.relative_to(ROOT)),
                "raw_file_sha256": hashlib.sha256(cross_path.read_bytes()).hexdigest() if cross_path.exists() else None}
    for case in CASES:
        matching = [x for x in candidates if x.get("case") == case and x.get("objective") == "cost"
                    and x.get("seed_label") == "cross_collocation_best" and x.get("solver_success")]
        if not matching:
            continue
        candidate = min(matching, key=lambda x: x["J"])
        full_path = None
        if "lambda_values" not in candidate:
            # 汇总表有意省略控制数组；必须回到保存了完整控制的原始attempt文件。
            originals = []
            for path in (RESULTS / "shooting_attempts").glob(f"{case}_cost_n80_cross_collocation_best_*.json"):
                original = _read(path)
                if (original and original.get("solver_success") and "lambda_values" in original
                        and abs(original["duration"] - candidate["duration"]) < 1e-9
                        and abs(original["J"] - candidate["J"]) < 1e-9):
                    originals.append((path, original))
            if not originals:
                raise RuntimeError(f"{case}: 找不到汇总候选对应的完整控制文件")
            full_path, candidate = min(originals, key=lambda pair: pair[1]["J"])
        output = OUTPUT / "v2" / run_id / f"{case}_cost_shooting_n80_DOP853.json"
        r = evaluate(case, candidate["duration"], candidate["lambda_values"], interpolation="constant",
                     method="DOP853", rtol=1e-12, tail_tol=1e-7 if case == "base" else 1e-5, save_path=output)
        main = result["representatives"][f"{case}_cost"]["DOP853"]
        shooting["evaluations"][case] = {**_brief(r), "candidate_canonical_json_sha256": _digest(candidate),
            "candidate_source": str(full_path.relative_to(ROOT)) if full_path else str(cross_path.relative_to(ROOT)),
            "candidate_raw_file_sha256": hashlib.sha256(full_path.read_bytes()).hexdigest() if full_path else None,
            "J_ODE_minus_shooting": r["J"] - candidate["J"],
            "comparison_with_main_n160": {"J_difference": r["J"] - main["J"],
                "C_interval_difference_persons": [r["C_infinity_interval"][0] - main["C_infinity_interval"][1],
                    r["C_infinity_interval"][1] - main["C_infinity_interval"][0]],
                "note": "不同控制离散化的差异单独报告，尾界不代表离散化误差"}}
        print(json.dumps({"v2_shooting": case, "numeric_status": r["numeric_status"],
                          "J": r["J"], "feasible": r["feasible"]}, ensure_ascii=False), flush=True)
    shooting["complete"] = len(shooting["evaluations"]) == 2
    shooting["all_scientific_checks_pass"] = shooting["complete"] and all(x["feasible"] for x in shooting["evaluations"].values())
    _dump(RESULTS / "shooting_validation_v2.json", shooting)
    return shooting


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="明确运行独立 ODE 评价")
    parser.add_argument("--watch", action="store_true", help="缺文件时保持等待；不把缺文件记为完成")
    parser.add_argument("--refined-infections", action="store_true", help="只评价新增 scale10000 感染候选及严格仅隔离参照")
    parser.add_argument("--acceptance-v2", action="store_true", help="修订分类后强制重评六代表、六感染候选与两条独立shooting成本")
    parser.add_argument("--shooting-v2", action="store_true", help="只接续独立shooting成本的完整ODE核验")
    parser.add_argument("--poll-seconds", type=float, default=10.0)
    args = parser.parse_args()
    if args.watch and not args.run:
        parser.error("--watch 必须同时显式给出 --run")
    if args.shooting_v2:
        if not args.run:
            parser.error("--shooting-v2 必须同时显式给出 --run")
        result = run_shooting_v2()
        print(json.dumps({"shooting_v2_complete": result["complete"],
            "all_scientific_checks_pass": result["all_scientific_checks_pass"]}, ensure_ascii=False), flush=True)
        return
    if args.acceptance_v2:
        if not args.run:
            parser.error("--acceptance-v2 必须同时显式给出 --run")
        result = run_acceptance_v2()
        print(json.dumps({"v2_complete": result["complete"],
            "all_scientific_checks_pass": result["all_scientific_checks_pass"]}, ensure_ascii=False), flush=True)
        return
    if args.refined_infections:
        if not args.run:
            parser.error("--refined-infections 必须同时显式给出 --run")
        result = run_refined_infections()
        print(json.dumps({"refined_complete": result["complete"], "candidate_count": len(result["candidates"]),
                          "missing": result["missing"]}, ensure_ascii=False), flush=True)
        return
    while True:
        result = run_available(run=args.run)
        print(json.dumps({"complete": result["complete"], "final_count": len(result["final"]),
                          "pending": result["pending"]}, ensure_ascii=False), flush=True)
        if result["complete"] or not args.watch:
            return
        time.sleep(max(1.0, args.poll_seconds))


if __name__ == "__main__":
    main()
