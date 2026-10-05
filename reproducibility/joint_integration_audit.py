"""联合控制整合的旧资产保护、差异和版本记录；不运行科学计算。"""
from __future__ import annotations

import argparse
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                               allow_nan=False) + "\n", encoding="utf-8")


def section9(text: str) -> str:
    marker = r"\label{sec:dominance}"
    if text.count(marker) != 1:
        raise ValueError("第9节标签必须唯一")
    start = text.rfind(r"\section", 0, text.index(marker))
    end = text.find(r"\section", text.index(marker))
    return text[start:end]


def tables(text: str) -> dict:
    blocks = re.findall(r"\\begin\{table\}\[.*?\].*?\\end\{table\}", text, re.S)
    result = {}
    for block in blocks:
        labels = re.findall(r"\\label\{([^}]+)\}", block)
        if not labels:
            raise ValueError("表环境必须有标签；既有别名标签完整保留")
        result[labels[0]] = block
    return result


def record(root: Path, out: Path, backup: Path) -> None:
    backup = backup.resolve()
    if out.exists():
        raise FileExistsError(out)
    main = root / "latex/flatten_curve_analysis_cn.tex"
    supplement = root / "latex/flatten_curve_supplement_cn.tex"
    # 并行编辑开始后也以已保存的修改前版本建立基线。
    main_before = backup / main.relative_to(root)
    supplement_before = backup / supplement.relative_to(root)
    text = main_before.read_text(encoding="utf-8")
    immutable = [root / "latex/references.bib", root / "latex/elegantpaper.cls", supplement]
    for folder in ["joint_control/threshold_control_reproducible_release_20261002",
                   "真实数据", "reproducibility/results", "reproducibility/release_reports"]:
        immutable.extend(p for p in (root / folder).rglob("*") if p.is_file())
    images = []
    for name in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", text):
        path = root / "latex" / name
        candidates = [path, path.with_suffix(".pdf"),
                      root / "latex/figures" / name,
                      (root / "latex/figures" / name).with_suffix(".pdf"),
                      root / "latex/table" / name]
        path = next((p for p in candidates if p.exists()), candidates[0])
        if not path.exists():
            raise FileNotFoundError(path)
        images.append(path)
    if len(images) != 20 or len(set(images)) != 20:
        raise ValueError(f"本轮旧图基线不是20幅独立图件: {len(images)}")
    immutable.extend(images)
    for path in images:
        target = backup / path.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    all_tables = {"main": tables(text), "supplement": tables(supplement_before.read_text(encoding="utf-8"))}
    if sum(map(len, all_tables.values())) != 7:
        raise ValueError("本轮原有表格基线必须为7张")
    git = subprocess.run(["git", "status", "--porcelain=v1"], cwd=root,
                         text=True, encoding="utf-8", capture_output=True)
    save(out, {
        "baseline_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "inventory_git_status": git.stdout, "git_status_stderr": git.stderr,
        "backup": str(backup.relative_to(root)),
        "main_sha256": sha(main_before), "main_text": text,
        "section9": section9(text), "original_tables": all_tables,
        "original_figures": [str(p.relative_to(root)).replace("\\", "/") for p in images],
        "protected": [{"path": str(p.relative_to(root)).replace("\\", "/"),
                       "size": p.stat().st_size, "sha256": sha(p)}
                      for p in sorted(set(immutable))],
        "scope": "旧图、表、冻结来源、原始数据及既有验收保护；不是科学复算验收"
    })


def verify(root: Path, baseline: Path, out: Path) -> bool:
    old = json.loads(baseline.read_text(encoding="utf-8"))
    failures = []
    for item in old["protected"]:
        path = root / item["path"]
        if not path.exists() or sha(path) != item["sha256"]:
            failures.append({"kind": "immutable_changed", "path": item["path"]})
    text = (root / "latex/flatten_curve_analysis_cn.tex").read_text(encoding="utf-8")
    new_tables = {"main": tables(text), "supplement": tables((root / "latex/flatten_curve_supplement_cn.tex").read_text(encoding="utf-8"))}
    for document, blocks in old["original_tables"].items():
        for label, block in blocks.items():
            if new_tables[document].get(label) != block:
                failures.append({"kind": "original_table_changed", "label": label})
    if section9(text) != old["section9"]:
        failures.append({"kind": "section9_changed"})
    # 新命题允许插入；已有编号公式及证明必须逐个保留，不按顺移后的序号匹配。
    counts = {}
    for environment in ("equation", "align", "proof"):
        pattern = r"\\begin\{" + environment + r"\}(.*?)\\end\{" + environment + r"\}"
        before = Counter(re.findall(pattern, old["main_text"], re.S))
        after = Counter(re.findall(pattern, text, re.S))
        missing = before-after
        counts[environment] = {"before": sum(before.values()), "after": sum(after.values()),
                               "original_blocks_preserved": not missing}
        if missing:
            failures.append({"kind": "original_math_block_changed", "environment": environment,
                             "missing_count": sum(missing.values())})
    diff = "".join(difflib.unified_diff(old["main_text"].splitlines(keepends=True),
                                      text.splitlines(keepends=True),
                                      fromfile="before/flatten_curve_analysis_cn.tex",
                                      tofile="after/flatten_curve_analysis_cn.tex"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".patch").write_text(diff, encoding="utf-8")
    save(out, {"passed": not failures, "failures": failures,
               "protected_file_count": len(old["protected"]),
               "original_figure_count": len(old["original_figures"]),
               "original_table_count": sum(map(len, old["original_tables"].values())),
               "original_math_blocks": counts,
               "section9_unchanged": section9(text) == old["section9"],
               "scientific_rerun": False})
    return not failures


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["record", "verify"])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--backup", type=Path)
    args = parser.parse_args()
    if args.mode == "record":
        record(args.root.resolve(), args.baseline, args.backup)
    else:
        raise SystemExit(0 if verify(args.root.resolve(), args.baseline, args.out) else 1)
