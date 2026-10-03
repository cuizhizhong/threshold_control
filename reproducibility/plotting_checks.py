"""项目自包含绘图核查，不依赖用户目录或外部技能。

仅检查主面板几何及科学对象；图形最终可读性仍需实际 PDF 页面复核。
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


def scientific_fingerprint(figure) -> list:
    """记录曲线/散点/柱图数据与视觉编码，不把排版位置当数值数据。"""
    records = []
    for main in figure.axes:
        for ax in [main, *main.child_axes]:
            rows = []
            for line in ax.lines:
                values = np.asarray(line.get_xydata())
                rows.append({"kind": "line", "data_sha256": hashlib.sha256(values.tobytes()).hexdigest(),
                             "shape": list(values.shape), "color": str(line.get_color()),
                             "width": line.get_linewidth(), "style": line.get_linestyle(),
                             "marker": line.get_marker(), "marker_size": line.get_markersize(),
                             "alpha": line.get_alpha()})
            for collection in ax.collections:
                rows.append({"kind": "collection", "offsets_sha256": hashlib.sha256(
                    np.asarray(collection.get_offsets()).tobytes()).hexdigest(),
                    "paths": [hashlib.sha256(p.vertices.tobytes()).hexdigest() for p in collection.get_paths()],
                    "facecolors": np.asarray(collection.get_facecolors()).tolist(),
                    "edgecolors": np.asarray(collection.get_edgecolors()).tolist()})
            for patch in ax.patches:
                rows.append({"kind": "patch", "path": patch.get_path().vertices.tolist(),
                             "facecolor": patch.get_facecolor(), "edgecolor": patch.get_edgecolor(),
                             "height": getattr(patch, "get_height", lambda: None)()})
            records.append(rows)
    return records


def require_matplotlib_panel_alignment(figure, json_out=None, tolerance_pt=1.5,
                                      gutter_tolerance_pt=1.5, strict=True):
    """检查同一 GridSpec 跨度的宽高偏差及同列/同行边缘。

    通栏面板、内嵌小图及色标不与半栏主面板混比；无 GridSpec 的手排轴
    只报告实测位置；显式 height_ratios/width_ratios 按已声明的比例检验，
    不误判合法的不等高面板。返回/保存实测尺寸，不宣称完成视觉审阅。
    """
    figure.canvas.draw()
    width_pt, height_pt = figure.get_size_inches() * 72
    axes = []
    for ax in figure.axes:
        if ax.get_label() == "<colorbar>" or not ax.get_visible():
            continue
        box = ax.get_position()
        spec = ax.get_subplotspec() if hasattr(ax, "get_subplotspec") else None
        key = None
        if spec is not None:
            key = (id(spec.get_gridspec()), spec.rowspan.stop - spec.rowspan.start,
                   spec.colspan.stop - spec.colspan.start)
        declared = spec.get_position(figure) if spec is not None else box
        axes.append({"bounds": np.array([box.x0 * width_pt, box.y0 * height_pt,
                                         box.width * width_pt, box.height * height_pt]),
                     "declared_bounds": np.array([declared.x0 * width_pt, declared.y0 * height_pt,
                                                  declared.width * width_pt, declared.height * height_pt]),
                     "key": key,
                     "rows": tuple(spec.rowspan) if spec is not None else None,
                     "cols": tuple(spec.colspan) if spec is not None else None})
    failures, comparisons = [], []
    for i, first in enumerate(axes):
        for j in range(i + 1, len(axes)):
            second = axes[j]
            if first["key"] is None or first["key"] != second["key"]:
                continue
            # 比较实际长度相对 GridSpec 声明长度的偏差，兼容明确指定的高度比例。
            deviation_first = first["bounds"][2:] - first["declared_bounds"][2:]
            deviation_second = second["bounds"][2:] - second["declared_bounds"][2:]
            error = np.abs(deviation_first - deviation_second)
            comparisons.append({"panels": [i, j], "width_error_pt": float(error[0]),
                                "height_error_pt": float(error[1])})
            if np.max(error) > tolerance_pt:
                failures.append(f"panels {i}/{j}: width/height mismatch {error.tolist()} pt")
            for field, coordinate in [("rows", 1), ("cols", 0)]:
                if first[field] == second[field]:
                    edge_error = abs(first["bounds"][coordinate] - second["bounds"][coordinate])
                    if edge_error > tolerance_pt:
                        failures.append(f"panels {i}/{j}: {field} edge mismatch {edge_error} pt")
    report = {"status": "pass" if not failures else "fail", "axes_count": len(axes),
              "figure_size_pt": [float(width_pt), float(height_pt)],
              "bounds_pt": [a["bounds"].tolist() for a in axes], "comparisons": comparisons,
              "declared_bounds_pt": [a["declared_bounds"].tolist() for a in axes],
              "tolerance_pt": tolerance_pt, "failures": failures,
              "limitations": "Geometry only; not a visual legibility or collision certification."}
    if json_out is not None:
        path = Path(json_out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if strict and failures:
        raise RuntimeError("; ".join(failures))
    return report


def audit_pdf(path: Path) -> dict:
    import pymupdf
    with pymupdf.open(path) as doc:
        if len(doc) != 1:
            raise ValueError(f"Figure must have one page: {path}")
        page = doc[0]
        sizes, clipped = [], []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("text", "").strip():
                        sizes.append(float(span["size"]))
                        box = pymupdf.Rect(span["bbox"])
                        if not (page.rect + (-1, -1, 1, 1)).contains(box):
                            clipped.append(span["text"])
        raster = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False)
        return {"file": str(path), "size_pt": [page.rect.width, page.rect.height],
                "minimum_span_font_pt": min(sizes) if sizes else None,
                "drawing_objects": len(page.get_drawings()), "images": len(page.get_images()),
                "text": page.get_text(), "outside_page_text": clipped,
                "render_sha256_108dpi": hashlib.sha256(raster.samples).hexdigest(),
                "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "visual_review": "not_performed_by_this_function"}
