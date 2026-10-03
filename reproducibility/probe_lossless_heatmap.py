"""仅测试 fresh PNG 或 fresh native vector 的600dpi无损图像PDF形式。

不读取旧PDF作为图像源，也不修改正式绘图入口或验收容差。
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
import pymupdf
from bootstrap import dump


def emit(source: Path, output: Path, *, raster_vector=False, graphics_aa=0):
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(output)
    rect = pymupdf.Rect(0, 0, 455, 355)
    image_rect = pymupdf.Rect(1.5, 1.5, 453.5, 353.5)
    if raster_vector:
        # 原图高分辨率image输出：600dpi下禁止polygon边缘AA引出的白色接缝。
        pymupdf.TOOLS.set_aa_level(graphics_aa)
        with pymupdf.open(source) as native:
            pix = native[0].get_pixmap(dpi=600, alpha=False)
            image_bytes = pix.tobytes('png')
    else:
        image_bytes = source.read_bytes()
    with pymupdf.open() as document:
        page = document.new_page(width=rect.width, height=rect.height)
        page.insert_image(image_rect, stream=image_bytes, keep_proportion=True)
        document.save(output, deflate=True)
    return {'source':str(source),'output':str(output),'rasterized_fresh_vector':raster_vector,
            'historical_render_used':False,'raster_dpi':600 if raster_vector else None,
            'raster_aa_level':graphics_aa if raster_vector else None,
            'page_size_pt':[455,355],'uniform_image_fit':True}


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('workspace',type=Path)
    args=parser.parse_args()
    stem=args.workspace/'scenario1_threshold_landscape/current_run/figures/scenario1_heatmaps_c0_eta'
    records=[emit(stem.with_suffix('.png'),Path(str(stem)+'.pnglossless.pdf')),
             emit(Path(str(stem)+'.vector.pdf'),Path(str(stem)+'.vector600image.pdf'),raster_vector=True)]
    dump(args.workspace.parent/'lossless_heatmap_probe.json',records)
