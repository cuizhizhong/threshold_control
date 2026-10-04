"""独立的发布前产物回核，不修改已冻结的科学复现入口。"""
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bootstrap import ROOT, dump, sha
from compare_runs import compare
from publish_verified import publish, read


def require_hash(path: Path, expected: str) -> dict:
    if not path.is_file() or sha(path) != expected:
        raise RuntimeError("验收后产物缺失或改变：" + str(path))
    return {"file": str(path), "sha256": expected, "passed": True}


def check_artifacts(run: Path) -> list[dict]:
    records = []
    build = read(run / "document/build_report.json")
    registry = read(run / "registry.json")
    initial = read(run / "validation/source_integrity_initial.json")
    release = ROOT / "joint_control/threshold_control_reproducible_release_20261002"
    records.append(require_hash(release / "MANIFEST_SHA256.json", initial["frozen_manifest_sha256"]))
    for item in initial["frozen_release"]:
        records.append(require_hash(release / item["file"], item["expected_sha256"]))
    for stem, info in build["documents"].items():
        records.append(require_hash(run / "document/latex" / (stem + ".pdf"), info["pdf_sha256"]))
    for item in registry["documents"]:
        records.append(require_hash(run / "document/latex" / Path(item["source"]).name, item["sha256"]))
    for name in ("references.bib", "elegantpaper.cls"):
        records.append(require_hash(run / "document/latex" / name, initial["source_input_hashes"]["latex/" + name]))
    generated = read(run / "validation/figure_generation.json")
    if not generated.get("passed") or len(generated["figures"]) != 20:
        raise RuntimeError("图件生成记录不完整")
    seen = set()
    for item in generated["figures"]:
        source = Path(item["file"]).resolve()
        if not source.is_relative_to(run / "figures"):
            raise RuntimeError("图件记录指向其他运行")
        relative = source.relative_to(run / "figures")
        seen.add(relative)
        records.append(require_hash(source, item["file_sha256"]))
        records.append(require_hash(run / "document/latex/figures" / relative, item["file_sha256"]))
    if seen != {p.relative_to(run / "figures") for p in (run / "figures").rglob("*.pdf")}:
        raise RuntimeError("图件清单和当前目录不同")
    return records


def scientific_artifacts(run: Path) -> list[dict]:
    """发布时绑定未取整结果；汇集阶段不能接受事后变化的 CSV/JSON/NPZ。"""
    files = []
    for module in ("xian", "population", "c0", "joint", "figure_inputs"):
        files += [p for p in (run / module).iterdir()
                  if p.is_file() and p.suffix in {".csv", ".json", ".npz"}]
    files += list((run / "workspace/scenario1_threshold_landscape/current_run/output_csv").glob("*.csv"))
    return [{"file": p.relative_to(run).as_posix(), "sha256": sha(p)} for p in sorted(files)]


def main(parent: Path, check_only: bool) -> None:
    parent = parent.resolve()
    if not parent.is_relative_to(ROOT / "reproducibility/runs"):
        raise RuntimeError("发布目录越界")
    if not read(parent / "repeatability.json").get("passed"):
        raise RuntimeError("原双跑记录未通过，拒绝发布")
    first, second = parent / "run_1", parent / "run_2"
    versions = [read(run / "validation/source_integrity_initial.json") for run in (first, second)]
    for key in ("runner_source_hashes", "static_art_assets", "raw_inputs", "source_input_hashes", "frozen_manifest_sha256"):
        if versions[0][key] != versions[1][key]:
            raise RuntimeError("两轮版本或输入不一致：" + key)
    records = check_artifacts(first) + check_artifacts(second)
    review = read(first / "validation/manual_review_root.json")
    build = read(first / "document/build_report.json")
    if not review.get("passed") or review.get("failures"):
        raise RuntimeError("人工审阅未通过")
    if review["main_pdf_sha256"] != sha(first / "document/latex/flatten_curve_analysis_cn.pdf") or review["supplement_pdf_sha256"] != sha(first / "document/latex/flatten_curve_supplement_cn.pdf"):
        raise RuntimeError("实际产物不是已审阅的 PDF")
    agent_path = first / "validation/manual_review_agent.json"
    if agent_path.is_file():
        agent = read(agent_path)
        if (agent.get("status") != "review_completed" or
            agent.get("main_pdf_sha256") != review["main_pdf_sha256"] or
            agent.get("supplement_pdf_sha256") != review["supplement_pdf_sha256"] or
            any(item.get("blocking_issue") for item in agent.get("findings_by_page", []))):
            raise RuntimeError("独立人工审阅记录未绑定当前 PDF 或存在阻断问题")
    for stem, key in (("flatten_curve_analysis_cn", "main_contact_pages_viewed"),
                      ("flatten_curve_supplement_cn", "supplement_contact_pages_viewed")):
        if set(review[key]) != set(range(1, build["documents"][stem]["page_count"] + 1)):
            raise RuntimeError("人工整篇页面核查覆盖不完整")
    report_dir = ROOT / "reproducibility/release_reports"
    report_dir.mkdir(exist_ok=True)
    comparison = compare(first, second, report_dir / "repeatability_publication_preflight.json")
    if not comparison["passed"]:
        raise RuntimeError("发布前严格重比较未通过")
    science = {"run_1": scientific_artifacts(first), "run_2": scientific_artifacts(second)}
    dump(report_dir / "artifact_preflight.json", {
        "passed": True, "files": records, "publication_helper_sha256": sha(Path(__file__)),
        "scientific_artifacts": science,
        "scientific_runner_changed": False, "manual_pdf_identity_verified": True,
        "all_pages_reviewed": True, "strict_comparison_repeated": True,
        "scope": "发布前实际产物身份核查；独立于科学双跑，不能替代数值和证明审查。"})
    if check_only:
        print("ARTIFACT_PREFLIGHT_PASSED_NO_PUBLICATION")
        return
    targets = [ROOT / "latex" / name for name in ("flatten_curve_analysis_cn.tex", "flatten_curve_supplement_cn.tex", "flatten_curve_analysis_cn.pdf", "flatten_curve_supplement_cn.pdf", "references.bib", "elegantpaper.cls")]
    targets += [ROOT / "latex/figures" / p.relative_to(first / "figures") for p in (first / "figures").rglob("*.pdf")]
    previous = {str(p): sha(p) if p.is_file() else None for p in targets}
    backups = set((ROOT / "reproducibility/backups").glob("before_verified_publication_*"))
    try:
        result = publish(parent)
        for run_name, items in science.items():
            for item in items:
                require_hash(parent / run_name / item["file"], item["sha256"])
    except Exception as error:
        changed = [p for p, old in previous.items() if (sha(Path(p)) if Path(p).is_file() else None) != old]
        new_backups = set((ROOT / "reproducibility/backups").glob("before_verified_publication_*")) - backups
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        failure = {
            "passed": False, "error": str(error), "partial_publication": bool(changed),
            "changed_targets": changed, "recoverable_backups": [str(p) for p in new_backups],
            "run_directory": str(parent),
            "note": "不自动回滚或删除文件；需检查备份和部分更新状态，不可宣称发布完成。"}
        dump(report_dir / ("publication_failure_" + stamp + ".json"), failure)
        if (report_dir / "publication_manifest.json").is_file():
            dump(report_dir / ("partial_publication_manifest_" + stamp + ".json"),
                 read(report_dir / "publication_manifest.json"))
        dump(report_dir / "publication_manifest.json", failure)
        raise
    result["artifact_preflight"] = "artifact_preflight.json"
    result["scientific_artifacts"] = science
    result["publication_helper_sha256"] = sha(Path(__file__)); result["publication_is_one_shot"] = True
    dump(report_dir / "publication_manifest.json", result)
    print("VERIFIED_ARTIFACTS_PUBLISHED_FORMAL_BUILD_PASSED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    main(args.run_directory, args.check_only)
