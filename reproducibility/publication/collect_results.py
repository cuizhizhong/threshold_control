"""汇集已发布版本的完整精度结果和验收记录；不重算、不覆盖历史目录。"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bootstrap import ROOT, dump, sha
from publish_verified import read


def collect(parent: Path) -> dict:
    parent = parent.resolve()
    if not parent.is_relative_to(ROOT / "reproducibility/runs"):
        raise RuntimeError("结果来源必须是本项目的隔离运行目录")
    publication = read(ROOT / "reproducibility/release_reports/publication_manifest.json")
    if not publication.get("passed") or Path(publication["run_directory"]).resolve() != parent:
        raise RuntimeError("该双跑版本尚未通过正式发布")
    if not read(parent / "repeatability.json").get("passed"):
        raise RuntimeError("双跑比较未通过")
    collection_manifest = ROOT / "reproducibility/release_reports/collection_manifest.json"
    if collection_manifest.exists():
        raise RuntimeError("已有结果汇集清单，不隐式覆盖：" + str(collection_manifest))
    for run_name in ("run_1", "run_2"):
        items = publication.get("scientific_artifacts", {}).get(run_name)
        if not items:
            raise RuntimeError("发布清单缺少未取整结果的摘要绑定")
        for item in items:
            source = (parent / run_name / item["file"]).resolve()
            if not source.is_relative_to(parent / run_name) or sha(source) != item["sha256"]:
                raise RuntimeError("发布后未取整结果变化或越界：" + item["file"])
    for item in publication["files"]:
        if sha(ROOT / item["file"]) != item["final_sha256"]:
            raise RuntimeError("正式交付文件在发布后发生变化：" + item["file"])
    first = parent / "run_1"
    if not read(first / "run_report.json").get("passed"):
        raise RuntimeError("科学运行未通过")
    target = ROOT / "reproducibility/results" / parent.name
    if target.exists():
        raise RuntimeError("结果汇集目录已存在，不覆盖：" + str(target))
    # 只汇集本轮派生数据；原始数据和历史缓存不复制到结果输入位置。
    files: list[tuple[Path, Path]] = []
    for module in ("xian", "population", "c0", "joint", "figure_inputs"):
        files += [(p, target / module / p.name) for p in sorted((first / module).iterdir())
                  if p.is_file() and p.suffix in {".csv", ".json", ".npz"}]
    baseline = first / "workspace/scenario1_threshold_landscape/current_run/output_csv"
    files += [(p, target / "baseline" / p.name) for p in sorted(baseline.glob("*.csv"))]
    report_root = ROOT / "reproducibility/release_reports" / parent.name
    if report_root.exists():
        raise RuntimeError("验收汇集目录已存在，不覆盖：" + str(report_root))
    for run_name in ("run_1", "run_2"):
        run = parent / run_name
        for name in ("run_report.json", "environment.json", "source_manifest.json", "stage_results.json",
                     "registry.json", "registry.md", "paper_anchor_updates.json", "manuscript_changes.json"):
            files.append((run / name, report_root / run_name / name))
        files += [(p, report_root / run_name / "validation" / p.name)
                  for p in sorted((run / "validation").glob("*.json"))]
        files.append((run / "document/build_report.json", report_root / run_name / "build_report.json"))
        files += [(p, report_root / run_name / "logs" / p.name)
                  for p in sorted((run / "logs").iterdir()) if p.is_file()]
    files.append((parent / "repeatability.json", report_root / "repeatability.json"))
    # 根目录的索引仍指向实际运行，而不是把汇集副本伪装成新的计算输入。
    for name in ("registry.json", "registry.md", "environment.json"):
        destination = ROOT / "reproducibility" / name
        if destination.exists():
            raise RuntimeError("根索引已存在，不隐式覆盖：" + str(destination))
        files.append((first / name, destination))
    if any(not source.is_file() for source, _ in files):
        raise RuntimeError("需要汇集的本轮文件缺失")
    records = []
    for source, destination in files:
        expected = sha(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        if sha(destination) != expected or sha(source) != expected:
            raise RuntimeError("复制时文件内容变化：" + str(source))
        records.append({"source": str(source.relative_to(ROOT)).replace("\\", "/"),
                        "file": str(destination.relative_to(ROOT)).replace("\\", "/"),
                        "sha256": expected, "bytes": destination.stat().st_size})
    outcome = {"passed": True, "run_directory": str(parent), "result_directory": str(target),
               "files": records, "full_precision": "CSV/JSON 的未取整 binary64 输出及原始 NPZ 数组；不认证全部尾数。",
               "results_are_inputs": False, "original_data_modified": False,
               "history_deleted": False, "git_writes": False,
               "helper_sha256": sha(Path(__file__))}
    dump(collection_manifest, outcome)
    return outcome


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-directory", type=Path, required=True)
    args = parser.parse_args()
    result = collect(args.run_directory)
    print("VERIFIED_RESULTS_COLLECTED", len(result["files"]))
