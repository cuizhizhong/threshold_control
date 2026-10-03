"""发布保护的实际只读自检；不改正式稿和已验收产物。"""
from pathlib import Path
from unittest.mock import patch
from publish_artifacts import ROOT, check_artifacts, require_hash, main
from collect_results import collect
from bootstrap import dump, sha


def run():
    failed_parent = ROOT / "reproducibility/runs/20261003_final"
    previous = sha(ROOT / "latex/flatten_curve_analysis_cn.tex")
    records = check_artifacts((failed_parent / "run_1").resolve())
    wrong_hash_rejected = False
    try:
        require_hash(failed_parent / "run_1/document/latex/flatten_curve_analysis_cn.pdf", "0" * 64)
    except RuntimeError as error:
        wrong_hash_rejected = "验收后产物缺失或改变" in str(error)
    failed_repeat_rejected = False
    try:
        main(failed_parent, False)
    except RuntimeError as error:
        failed_repeat_rejected = "原双跑记录未通过" in str(error)
    untouched = previous == sha(ROOT / "latex/flatten_curve_analysis_cn.tex")
    numeric_path = failed_parent / "run_1/xian/reference.json"
    numeric_digest = sha(numeric_path)
    fake_publication = {"passed": True, "run_directory": str(failed_parent), "files": [],
                        "scientific_artifacts": {"run_1": [{"file": "xian/reference.json", "sha256": "0" * 64}],
                                                 "run_2": [{"file": "xian/reference.json", "sha256": "0" * 64}]}}
    wrong_numeric_snapshot_rejected = False
    with patch("collect_results.read", side_effect=[fake_publication, {"passed": True}]):
        try:
            collect(failed_parent)
        except RuntimeError as error:
            wrong_numeric_snapshot_rejected = "发布后未取整结果变化或越界" in str(error)
    numeric_untouched = sha(numeric_path) == numeric_digest
    report = {"passed": bool(records) and wrong_hash_rejected and failed_repeat_rejected and untouched,
              "actual_identity_checks": len(records), "wrong_pdf_digest_rejected": wrong_hash_rejected,
              "failed_repeat_rejected": failed_repeat_rejected, "formal_tex_unchanged": untouched,
              "wrong_numeric_snapshot_rejected": wrong_numeric_snapshot_rejected,
              "numeric_source_unchanged": numeric_untouched,
              "scope": "实际只读身份正例、错误PDF摘要和失败双跑负例；数值摘要负例仅模拟发布记录，不改结果。不是科学复现或人工视觉认证。"}
    report["passed"] = report["passed"] and wrong_numeric_snapshot_rejected and numeric_untouched
    dump(ROOT / "reproducibility/release_reports/publication_guard_tests.json", report)
    assert report["passed"], report
    print("PUBLICATION_GUARD_TESTS_PASSED")


if __name__ == "__main__":
    run()
