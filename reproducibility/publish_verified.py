"""人工页面核查后发布指定双跑产物；不提交 Git，不删除历史材料。"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import shutil
import subprocess

import pymupdf

from bootstrap import ROOT, dump, sha


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def metadata_only(first: Path, second: Path) -> bool:
    """只有完整图形几何、字体流、文本、图像及渲染都相同时才复用旧 PDF。"""
    if not first.is_file():
        return False
    with pymupdf.open(first) as a, pymupdf.open(second) as b:
        if len(a) != len(b):
            return False
        for x, y in zip(a, b):
            if x.rect != y.rect or x.get_drawings() != y.get_drawings():
                return False
            if x.get_text("rawdict") != y.get_text("rawdict"):
                return False
            fonts_a = sorted((v[1:6], a.extract_font(v[0])[3]) for v in x.get_fonts())
            fonts_b = sorted((v[1:6], b.extract_font(v[0])[3]) for v in y.get_fonts())
            if fonts_a != fonts_b:
                return False
            if x.get_pixmap(dpi=120, alpha=False).samples != y.get_pixmap(dpi=120, alpha=False).samples:
                return False
        return True


def compare_documents(formal: Path, checked: Path) -> dict:
    pages = []
    with pymupdf.open(formal) as a, pymupdf.open(checked) as b:
        if len(a) != len(b):
            raise RuntimeError("正式 PDF 页数与已审阅产物不一致")
        for i, (x, y) in enumerate(zip(a, b)):
            render_same = (x.rect == y.rect and
                           x.get_pixmap(dpi=120, alpha=False).samples ==
                           y.get_pixmap(dpi=120, alpha=False).samples)
            text_same = x.get_text() == y.get_text()
            pages.append({"page": i + 1, "render_exact_120dpi": render_same,
                          "text_exact": text_same})
    if not all(p["render_exact_120dpi"] and p["text_exact"] for p in pages):
        raise RuntimeError("正式重编译 PDF 与已审阅页不一致，需要重新人工核查")
    return {"passed": True, "page_count": len(pages), "pages": pages,
            "metadata_ignored": True, "pdf_sha256": sha(formal)}


def publish(parent: Path) -> dict:
    parent = parent.resolve()
    if not parent.is_relative_to(ROOT / "reproducibility/runs"):
        raise RuntimeError("只允许发布本工程隔离运行目录内的结果")
    first, second = parent / "run_1", parent / "run_2"
    repeat = read(parent / "repeatability.json")
    reports = [read(p / "run_report.json") for p in (first, second)]
    if not repeat.get("passed") or not all(r.get("passed") for r in reports):
        raise RuntimeError("双空目录复现尚未通过，拒绝发布")
    review = read(first / "validation/manual_review_root.json")
    if not review.get("passed"):
        raise RuntimeError("缺少实际页面核查记录")
    build = read(first / "document/build_report.json")
    reviewed_hashes = {
        "flatten_curve_analysis_cn": review["main_pdf_sha256"],
        "flatten_curve_supplement_cn": review["supplement_pdf_sha256"],
    }
    for stem, info in build["documents"].items():
        if reviewed_hashes[stem] != info["pdf_sha256"]:
            raise RuntimeError("人工审阅的 PDF 不是本轮编译产物")
    agent_path = first / "validation/manual_review_agent.json"
    if agent_path.is_file():
        agent = read(agent_path)
        if any(x.get("blocking_issue") for x in agent.get("findings_by_page", [])):
            raise RuntimeError("存在未解决的独立页面审阅问题")

    # 发布前再次核对科学源码及原始输入，不使用旧生成缓存作为新的依据。
    initial = read(first / "validation/source_integrity_initial.json")
    for relative, expected in initial["source_input_hashes"].items():
        if sha(ROOT / relative) != expected:
            raise RuntimeError("验收后原始来源变化：" + relative)
    for relative, expected in initial["runner_source_hashes"].items():
        if sha(ROOT / relative) != expected:
            raise RuntimeError("验收后复现源码变化：" + relative)
    for relative, expected in initial["static_art_assets"].items():
        if sha(ROOT / relative) != expected:
            raise RuntimeError("验收后可编辑图源变化：" + relative)
    release = ROOT / "ai/threshold_control_reproducible_release_20261002"
    manifest = read(release / "MANIFEST_SHA256.json")
    if any(sha(release / p) != v["sha256"] for p, v in manifest["files"].items()):
        raise RuntimeError("冻结交付包变化")

    names = ("flatten_curve_analysis_cn.tex", "flatten_curve_supplement_cn.tex",
             "flatten_curve_analysis_cn.pdf", "flatten_curve_supplement_cn.pdf",
             "references.bib", "elegantpaper.cls")
    for name in names[:2]:
        if (first / "document/latex" / name).read_bytes() != (second / "document/latex" / name).read_bytes():
            raise RuntimeError("两轮正文源文件不一致：" + name)
    sources = [(first / "document/latex" / name, ROOT / "latex" / name) for name in names]
    figures = sorted((first / "figures").rglob("*.pdf"))
    if len(figures) != 20:
        raise RuntimeError("发布图件必须恰为 20 幅")
    sources += [(p, ROOT / "latex/figures" / p.relative_to(first / "figures")) for p in figures]
    for source, target in sources:
        if not source.is_file() or not target.resolve().is_relative_to(ROOT / "latex"):
            raise RuntimeError("发布目标越界或缺失：" + str(target))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / "reproducibility/backups" / ("before_verified_publication_" + stamp)
    backup.mkdir(parents=True, exist_ok=False)
    records = []
    for source, target in sources:
        relative = target.relative_to(ROOT)
        old = sha(target) if target.is_file() else None
        if target.is_file():
            saved = backup / target.relative_to(ROOT / "latex")
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
        unchanged = old == sha(source)
        metadata_reuse = target.suffix == ".pdf" and target.is_relative_to(ROOT / "latex/figures") and metadata_only(target, source)
        if not unchanged and not metadata_reuse:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        records.append({"file": relative.as_posix(), "old_sha256": old,
                        "verified_source_sha256": sha(source), "published_sha256": sha(target),
                        "action": "unchanged" if unchanged else ("metadata_only_reused" if metadata_reuse else "updated")})

    # 用正式目录的工程入口真实编译，而不是仅复制已编译 PDF。
    publication = ROOT / "reproducibility/release_reports"
    publication.mkdir(exist_ok=True)
    with (publication / "formal_build_stdout.log").open("w", encoding="utf-8") as log:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                        str(ROOT / "latex/build_paper.ps1")], cwd=ROOT,
                       stdout=log, stderr=subprocess.STDOUT, check=True, timeout=900)
    fatal = r"undefined|Missing character|Overfull|Float too large|multiply defined|^!|(?:LaTeX|Package \S+) Error:"
    logs, documents = {}, {}
    for stem in ("flatten_curve_analysis_cn", "flatten_curve_supplement_cn"):
        txt = (ROOT / "latex" / (stem + ".log")).read_text(encoding="utf-8", errors="replace")
        hits = [line for line in txt.splitlines() if re.search(fatal, line, re.I)]
        warnings = [line for line in txt.splitlines() if "Warning" in line or "Underfull" in line]
        logs[stem] = {"failures": hits, "warnings": warnings}
        if hits:
            raise RuntimeError("正式目录编译核查失败：" + str(hits[:5]))
        documents[stem] = compare_documents(ROOT / "latex" / (stem + ".pdf"), first / "document/latex" / (stem + ".pdf"))
    blg = (ROOT / "latex/flatten_curve_analysis_cn.blg").read_text(encoding="utf-8", errors="replace")
    biber_warnings = [line for line in blg.splitlines() if re.search(r"WARN|ERROR", line)]
    if biber_warnings:
        raise RuntimeError("正式文献核查失败：" + str(biber_warnings))
    formal_text = (ROOT / "latex/flatten_curve_analysis_cn.tex").read_text(encoding="utf-8")
    if formal_text.count("\\printbibliography") != 1:
        raise RuntimeError("正式稿参考文献必须且只能打印一次")
    bbl = (ROOT / "latex/flatten_curve_analysis_cn.bbl").read_text(encoding="utf-8")
    printed = sorted(set(re.findall(r"\\entry\{([^}]+)\}", bbl)))
    if printed != build["printed_bibliography_keys"]:
        raise RuntimeError("正式稿与验收稿参考文献不一致")
    changed_targets = {r["file"] for r in records}
    protected = {rel: sha(ROOT / rel) == expected for rel, expected in initial["source_input_hashes"].items()
                 if Path(rel).as_posix() not in changed_targets}
    if not all(protected.values()):
        raise RuntimeError("发布影响了无关原始来源")
    for item in records:
        item["final_sha256"] = sha(ROOT / item["file"])
    result = {"passed": True, "formal_files_published": True, "run_directory": str(parent),
              "backup": str(backup), "files": records, "documents": documents,
              "formal_compile": "SI XeLaTeX x2; main XeLaTeX -> Biber -> XeLaTeX x2",
              "logs": logs, "biber_warnings": biber_warnings,
              "printed_reference_count": len(printed), "main_bibliography_print_count": 1,
              "frozen_files_checked": len(manifest["files"]), "unrelated_inputs_preserved": protected,
              "scope": "本研究版本的计算、图表和排版验收；不认证一般理论证明或临床阈值。",
              "git_writes": False, "original_data_deleted": False, "historical_files_deleted": False}
    dump(publication / "publication_manifest.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-directory", type=Path, required=True)
    args = parser.parse_args()
    try:
        outcome = publish(args.run_directory)
        print(json.dumps({"passed": outcome["passed"], "formal_files_published": True}, ensure_ascii=False))
    except Exception as error:
        dump(ROOT / "reproducibility/release_reports/publication_failure.json",
             {"passed": False, "error": str(error), "run_directory": str(args.run_directory),
              "time": datetime.now().isoformat(timespec="seconds"),
              "note": "检查备份及正式文件状态；本记录不标记发布完成。"})
        raise
