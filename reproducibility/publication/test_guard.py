"""发布保护的实际只读自检；不改正式稿和已验收产物。"""
import argparse
from datetime import datetime
from pathlib import Path
import tempfile
from unittest.mock import patch
from publish_artifacts import ROOT, check_artifacts, require_hash, main
from collect_results import collect
from bootstrap import dump, sha
from publish_verified import read
from run_selection import selected_directories, SELECTION_FILE


def run(accepted_run=None, report_path=None):
    accepted_run = Path(accepted_run or ROOT / "reproducibility/runs/joint_integration_20261004/run_5").resolve()
    if not accepted_run.is_relative_to(ROOT / "reproducibility/runs"):
        raise ValueError("身份正例须是本项目的隔离运行目录。")
    report_path = Path(report_path or ROOT / "reproducibility/release_reports/20261005_sec7_v2_refinement" /
                       ("publication_guard_tests_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".json")).resolve()
    if not report_path.is_relative_to(ROOT / "reproducibility/release_reports"):
        raise ValueError("自检报告须另存项目 release_reports，不能写入运行或正式稿。")
    if report_path.exists():
        raise FileExistsError("自检报告已存在，不覆盖：" + str(report_path))
    failed_parent = ROOT / "reproducibility/runs/20261003_final"
    protected = [ROOT / "latex" / name for name in (
        "flatten_curve_analysis_cn.tex", "flatten_curve_supplement_cn.tex",
        "flatten_curve_analysis_cn.pdf", "flatten_curve_supplement_cn.pdf",
        "references.bib", "elegantpaper.cls")]
    previous = {str(path): sha(path) for path in protected}
    old_report = ROOT / "reproducibility/release_reports/publication_guard_tests.json"
    old_report_hash = sha(old_report) if old_report.is_file() else None
    errors = []
    records = []
    try:
        records = check_artifacts(accepted_run)
    except (RuntimeError, ValueError, FileNotFoundError) as error:
        errors.append({"check": "accepted_run_identity", "error": str(error)})
    wrong_hash_rejected = False
    try:
        require_hash(accepted_run / "document/latex/flatten_curve_analysis_cn.pdf", "0" * 64)
    except RuntimeError as error:
        wrong_hash_rejected = "验收后产物缺失或改变" in str(error)
    failed_repeat_rejected = False
    try:
        main(failed_parent, False)
    except RuntimeError as error:
        failed_repeat_rejected = "原双跑记录未通过" in str(error)
    untouched = all(sha(Path(path)) == digest for path, digest in previous.items())
    wrong_numeric_snapshot_rejected = False
    numeric_untouched = False
    selection_identity_verified = False
    accepted_parent = accepted_run.parent
    try:
        selected = selected_directories(accepted_parent)
        run_names = [run.name for run in selected]
        if accepted_run not in selected:
            raise RuntimeError("身份正例不属于当前显式选择的两个运行。")
        selection_identity_verified = True
        numeric_path = selected[0] / "joint_extra/compare_baseline.csv"
        if not numeric_path.is_file():
            numeric_path = selected[0] / "xian/reference.json"
        relative = numeric_path.relative_to(selected[0]).as_posix()
        numeric_digest = sha(numeric_path)
        fake_publication = {
            "passed": True, "run_directory": str(accepted_parent), "files": [],
            "accepted_run_names": run_names,
            "accepted_runs_manifest_sha256": sha(accepted_parent / SELECTION_FILE),
            "scientific_artifacts": {run.name: [{"file": relative, "sha256": "0" * 64}] for run in selected},
        }
        # 保留真实选择清单及真实通过双跑；只模拟错误发布摘要和全新的报告位置。
        # 临时位置避免既有 collection_manifest 的一次性保护提前截住摘要负例；
        # 错误摘要会在任何复制之前抛错，不能借此写入历史汇集目录。
        repeat = read(accepted_parent / "repeatability.json")
        with tempfile.TemporaryDirectory(prefix="publication_guard_numeric_fixture_") as directory:
            with patch("collect_results.report_directory", return_value=Path(directory)), \
                 patch("collect_results.read", side_effect=[fake_publication, repeat]):
                try:
                    collect(accepted_parent)
                except RuntimeError as error:
                    wrong_numeric_snapshot_rejected = "发布后未取整结果变化或越界" in str(error)
        numeric_untouched = sha(numeric_path) == numeric_digest
    except (RuntimeError, ValueError, FileNotFoundError) as error:
        errors.append({"check": "numeric_snapshot_fixture", "error": str(error)})
    historical_report_untouched = (sha(old_report) if old_report.is_file() else None) == old_report_hash
    report = {"passed": bool(records) and wrong_hash_rejected and failed_repeat_rejected and untouched,
              "actual_identity_checks": len(records), "wrong_pdf_digest_rejected": wrong_hash_rejected,
              "failed_repeat_rejected": failed_repeat_rejected, "formal_tex_unchanged": untouched,
              "wrong_numeric_snapshot_rejected": wrong_numeric_snapshot_rejected,
              "numeric_source_unchanged": numeric_untouched,
              "accepted_run": str(accepted_run),
              "selection_identity_verified": selection_identity_verified,
              "historical_report_unchanged": historical_report_untouched,
              "report_path": str(report_path), "errors": errors,
              "scope": "当前24图运行的实际只读身份正例、错误PDF摘要和历史失败双跑负例；数值负例使用真实显式选择清单及双跑记录，只模拟错误发布摘要和隔离报告位置。不改生产保护、结果或历史报告。不是科学复现或人工视觉认证。"}
    report["passed"] = bool(report["passed"] and wrong_numeric_snapshot_rejected and numeric_untouched
                            and selection_identity_verified and historical_report_untouched and not errors)
    dump(report_path, report)
    assert report["passed"], report
    print("PUBLICATION_GUARD_TESTS_PASSED")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--accepted-run", type=Path, help="已完成机器验收、登记和构建的身份正例；默认历史24图 run_5。")
    parser.add_argument("--report", type=Path, help="新的自检报告位置，已存在即拒绝；默认另存本轮带时间戳的报告。")
    args = parser.parse_args()
    run(args.accepted_run, args.report)
