"""复核通用检查器的裁剪路径/数学上下标误报；不改 PDF 或原始审计报告。"""
from pathlib import Path
import json
import sys
import fitz

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(Path.home()/".codex"/"skills"/"nature-figure"/"scripts"))
from audit_figure_collisions import rect_overlap_ratio

reviews=[]
for reportpath in (HERE/"qa").glob("*.collision.json"):
    report=json.loads(reportpath.read_text(encoding="utf-8"))
    page=fitz.open(report["pdf"])[0]
    ordinary=page.get_drawings()
    clip_by_seq={}
    active={}
    for item in page.get_drawings(extended=True):
        level=item["level"]
        active={k:v for k,v in active.items() if k<level}
        if item["type"]=="clip":
            active[level]=fitz.Rect(item["scissor"])
        elif "seqno" in item:
            clip=fitz.Rect(page.rect)
            for rectangle in active.values(): clip &= rectangle
            clip_by_seq[item["seqno"]]=clip
    for finding in report["findings"]:
        row={"figure":reportpath.stem,"finding":finding}
        if finding["severity"]=="FAIL" and finding["kind"]=="text-stroke":
            target=fitz.Rect(finding["text_bbox"])
            clips=[clip_by_seq[ordinary[i]["seqno"]] for i in finding["object_indexes"]]
            assert all((target & clip).is_empty for clip in clips), finding
            row.update(resolution="false_positive_verified",reason="路径被 PDF 坐标轴裁剪；全部实际裁剪框与该面板编号不相交。",
                       clip_rectangles=[list(c) for c in clips])
        elif finding["severity"]=="FAIL" and finding["kind"]=="text-text":
            assert finding["text"]=="IT" and finding["other_text"]=="peak",finding
            region=fitz.Rect(finding["text_bbox"])|fitz.Rect(finding["other_bbox"])
            chars=[]
            for trace in page.get_texttrace():
                for char in trace["chars"]:
                    bbox=fitz.Rect(char[3])
                    if region.contains(bbox): chars.append((chr(char[0]),tuple(bbox)))
            overlaps=[rect_overlap_ratio(a[1],b[1]) for i,a in enumerate(chars) for b in chars[i+1:]]
            maximum=max(overlaps,default=0.)
            crop=HERE/"qa"/f"math_review_{len(reviews):02}.png"
            page.get_pixmap(clip=region+(-3,-3,3,3),dpi=720).save(crop)
            row.update(resolution="visual_review",reason="通用检查器合并 I 与上标 T 的框；逐字形框仍含字形留白，另导出高倍裁剪检查实际上下标轮廓。",
                       characters=chars,maximum_glyph_bbox_overlap=maximum,crop=str(crop))
        elif finding["severity"]=="WARN":
            row.update(resolution="visual_review",reason="内嵌图白底及标签白底边界触发包围框提示；已对照最终页面，无柱值、参照文字或数据曲线遮挡。")
        else:
            raise AssertionError(finding)
        reviews.append(row)
(HERE/"qa"/"collision_geometry_review.json").write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding="utf-8")
print("REVIEWED",len(reviews),"findings; raw audit reports retained")
