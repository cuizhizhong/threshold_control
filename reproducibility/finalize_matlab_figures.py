"""新算MATLAB图的确定性封装，不读取旧图来替换数值内容。"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

import pymupdf

from bootstrap import dump


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _content_bounds(page) -> pymupdf.Rect:
    """只排除整张白色背景；数据路径、标题、公式和所有注释均参与裁边。"""
    bounds = pymupdf.Rect()
    for drawing in page.get_drawings():
        background = (drawing.get('color') is None and drawing.get('fill') == (1., 1., 1.)
                      and drawing['rect'].get_area() > .9 * page.rect.get_area())
        if not background:
            bounds.include_rect(drawing['rect'])
    for block in page.get_text('dict')['blocks']:
        if block['type'] == 0:
            for line in block['lines']:
                for span in line['spans']:
                    bounds.include_rect(span['bbox'])
    if bounds.is_empty or bounds.is_infinite:
        raise RuntimeError('Cannot determine fresh six-panel content bounds')
    return bounds


def crop_six_panel(native_pdf: Path, final_pdf: Path) -> dict:
    with pymupdf.open(native_pdf) as native:
        page=native[0]
        bounds=_content_bounds(page)
        margin=1.5
        crop=pymupdf.Rect(bounds.x0-margin,bounds.y0-margin,bounds.x1+margin,bounds.y1+margin) & page.rect
        with pymupdf.open() as document:
            target=document.new_page(width=crop.width,height=crop.height)
            target.show_pdf_page(target.rect,native,0,clip=crop,keep_proportion=True)
            document.save(final_pdf,deflate=True)
    return {'native_pdf':str(native_pdf),'native_sha256':_sha(native_pdf),
            'final_sha256':_sha(final_pdf),'fresh_content_bbox_pt':list(bounds),
            'crop_bbox_pt':list(crop),'margin_pt':margin,
            'crop_translation_only':True,'scientific_paths_scaled':False,
            'historical_pdf_used':False}


def image_heatmap(native_pdf: Path, final_pdf: Path, native_patched_pdf: Path,
                  *, dash_measurement: Path) -> dict:
    """保持原image形式，fresh native vector字体/路径经600dpi AA0无缝渲染。

    仅恢复已测原Renderer红虚线的物理节奏；不改变contour坐标、色值或线宽。
    """
    evidence=json.loads(dash_measurement.read_text(encoding='utf-8'))
    if not evidence.get('passed') or evidence.get('resolved_dash_pt')!=[3.6,3.6]:
        raise RuntimeError('Original-renderer dash calibration has not actually passed')
    aa_before=pymupdf.TOOLS.show_aa_level()
    changed_operators=0
    with pymupdf.open(native_pdf) as native:
        before=native[0].get_drawings()
        red=[item for item in before if item.get('color') is not None
             and item['color'][0]>.6 and item['color'][1]<.2 and item['color'][2]<.2]
        if not red or any(abs(item['width']-.9)>1e-6 or item['dashes']!='[ 7.5 4.5 ] 0' for item in red):
            raise RuntimeError('Native heatmap red contour style changed; explicit calibration required')
        # 已实测原Renderer约3.6/3.6pt；当前R2025b CTM×0.75，4.8/4.8→3.6/3.6pt。
        for xref in native[0].get_contents():
            stream=native.xref_stream(xref)
            changed,count=re.subn(rb'\[10 6 \]0  d',b'[4.8 4.8 ]0  d',stream)
            if count:
                native.update_stream(xref,changed)
                changed_operators+=count
        if changed_operators!=4:
            raise RuntimeError(f'Expected exactly four red dash operators; found {changed_operators}')
        after=native[0].get_drawings()
        if len(before)!=len(after):
            raise RuntimeError('Rendering-layer restoration changed drawing count')
        for first,second in zip(before,after):
            if {k:v for k,v in first.items() if k not in {'dashes','seqno'}}!={k:v for k,v in second.items() if k not in {'dashes','seqno'}}:
                raise RuntimeError('Rendering-layer restoration changed scientific path, color or width')
            if first['dashes']!=second['dashes']:
                dash_values=[float(value) for value in re.findall(r'[0-9.]+',second['dashes'])]
                restored=(len(dash_values)==3 and abs(dash_values[0]-3.6)<1e-6
                          and abs(dash_values[1]-3.6)<1e-6 and dash_values[2]==0)
                if not(first.get('color') in [r['color'] for r in red]
                       and first['dashes']=='[ 7.5 4.5 ] 0' and restored):
                    raise RuntimeError('Rendering-layer restoration changed a non-red contour style')
        native.save(native_patched_pdf,deflate=True)
        try:
            pymupdf.TOOLS.set_aa_level(0)
            pix=native[0].get_pixmap(dpi=600,alpha=False)
            png=pix.tobytes('png')
        finally:
            # 独立恢复graphics/text两项，不假设调用方原设置相同。
            pymupdf.mupdf.fz_set_graphics_aa_level(aa_before['graphics'])
            pymupdf.mupdf.fz_set_text_aa_level(aa_before['text'])
        if pymupdf.TOOLS.show_aa_level()!=aa_before:
            raise RuntimeError('Rasterization failed to restore caller anti-aliasing settings')
    with pymupdf.open() as document:
        page=document.new_page(width=455,height=355)
        page.insert_image(pymupdf.Rect(1.5,1.5,453.5,353.5),stream=png,keep_proportion=True)
        document.save(final_pdf,deflate=True)
    return {'native_pdf':str(native_pdf),'native_sha256':_sha(native_pdf),
            'native_patched_pdf':str(native_patched_pdf),'native_patched_sha256':_sha(native_patched_pdf),
            'final_sha256':_sha(final_pdf),'dash_measurement':str(dash_measurement),
            'dash_measurement_sha256':_sha(dash_measurement),'red_dash_pt_before':[7.5,4.5],
            'red_dash_pt_restored':[3.6,3.6],'red_contour_paths_preserved':len(red),
            'changed_dash_operators':changed_operators,'raster_dpi':600,'raster_aa_level':0,
            'caller_aa_restored':True,'lossless_image_encoding':True,'uniform_image_fit':True,
            'historical_pdf_used':False,'data_coordinates_fonts_colors_widths_preserved':True}


def finalize(output_dir: Path, root: Path) -> dict:
    output_dir,root=Path(output_dir).resolve(),Path(root).resolve()
    workspace=output_dir/'workspace'
    if not workspace.is_dir() or workspace==root or workspace==root/'latex':
        raise ValueError('Finalization requires the isolated reproduction workspace')
    directory=output_dir/'validation/native_matlab_graphics'
    directory.mkdir(parents=True,exist_ok=True)
    six=workspace/'figures/optimal_control_with_quarantine_panels.pdf'
    heat=workspace/'scenario1_threshold_landscape/current_run/figures/scenario1_heatmaps_c0_eta.pdf'
    records={}
    for name,path in [('six_panel',six),('heatmap',heat)]:
        report=path.with_suffix('.geometry.json')
        if not report.is_file() or not json.loads(report.read_text(encoding='utf-8')).get('all_exports_succeeded'):
            raise RuntimeError(f'Missing verified native MATLAB HG export report: {report}')
        saved=directory/(path.stem+'.native_vector.pdf')
        if saved.exists():
            raise FileExistsError(saved)
        shutil.copy2(path,saved)
        # 先成功生成另一新文件，再替换刚生成的运行区图，错误时保留fresh native。
        packaged=path.with_suffix('.packaged.pdf')
        if packaged.exists():
            raise FileExistsError(packaged)
        if name=='six_panel':
            records[name]=crop_six_panel(saved,packaged)
        else:
            records[name]=image_heatmap(saved,packaged,directory/(path.stem+'.native_vector_shortdash.pdf'),
                dash_measurement=root/'reproducibility/assets/native_heatmap_dash_measurement.json')
        packaged.replace(path)
    result={'status':'generated','purpose':'deterministic packaging of freshly recomputed MATLAB figures',
            'historical_results_used':False,'records':records}
    dump(output_dir/'validation/matlab_graphics_finalization.json',result)
    return result
