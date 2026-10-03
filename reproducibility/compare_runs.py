"""比较两个独立运行的数值输出及图形渲染，不比较 PDF 时间戳。"""
from __future__ import annotations
import json
import re
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pymupdf
from bootstrap import dump


def _font_streams(doc, page):
    return sorted((font[1:6], hashlib.sha256(doc.extract_font(font[0])[3]).hexdigest())
                  for font in page.get_fonts())


def _panel_bracket_geometry(first_page, second_page) -> dict:
    """只允许 MATLAB 非数学面板编号末尾右括号的水平字距量化。

    不允许编号字母、数字刻度、数学字符、颜色、字体或科学路径变化。
    """
    first_raw, second_raw = first_page.get_text('rawdict'), second_page.get_text('rawdict')
    if first_raw.keys() != second_raw.keys() or first_raw['width'] != second_raw['width'] or first_raw['height'] != second_raw['height']:
        return {'passed': False, 'reason': 'page text structure changed'}
    first_blocks, second_blocks = first_raw['blocks'], second_raw['blocks']
    if len(first_blocks) != len(second_blocks):
        return {'passed': False, 'reason': 'text blocks changed'}
    changes, chars_checked = [], 0
    for ba, bb in zip(first_blocks, second_blocks):
        if ba.get('type') != 0 or bb.get('type') != 0:
            if ba != bb:
                return {'passed': False, 'reason': 'non-text block changed'}
            continue
        if {k:v for k,v in ba.items() if k not in {'bbox','lines'}} != {k:v for k,v in bb.items() if k not in {'bbox','lines'}} or len(ba['lines']) != len(bb['lines']):
            return {'passed': False, 'reason': 'text block properties changed'}
        for la, lb in zip(ba['lines'], bb['lines']):
            if {k:v for k,v in la.items() if k not in {'bbox','spans'}} != {k:v for k,v in lb.items() if k not in {'bbox','spans'}} or len(la['spans']) != len(lb['spans']):
                return {'passed': False, 'reason': 'text line properties changed'}
            for sa, sb in zip(la['spans'], lb['spans']):
                if {k:v for k,v in sa.items() if k not in {'bbox','chars'}} != {k:v for k,v in sb.items() if k not in {'bbox','chars'}}:
                    return {'passed': False, 'reason': 'font, size, color, or other span property changed'}
                if len(sa['chars']) != len(sb['chars']):
                    return {'passed': False, 'reason': 'character count changed'}
                text = ''.join(c['c'] for c in sa['chars'])
                changed = False
                for i, (ca, cb) in enumerate(zip(sa['chars'], sb['chars'])):
                    chars_checked += 1
                    if ca == cb:
                        continue
                    dx = cb['origin'][0] - ca['origin'][0]
                    allowed = (re.fullmatch(r'\([a-f]\)', text) is not None
                               and sa['font'] == 'TimesNewRomanPS-BoldMT'
                               and i == len(sa['chars'])-1 and ca['c'] == cb['c'] == ')'
                               and 0 < abs(dx) <= .8
                               and ca['origin'][1] == cb['origin'][1]
                               and {k:v for k,v in ca.items() if k not in {'origin','bbox'}} == {k:v for k,v in cb.items() if k not in {'origin','bbox'}}
                               and ca['bbox'][1] == cb['bbox'][1] and ca['bbox'][3] == cb['bbox'][3]
                               and abs(cb['bbox'][0]-ca['bbox'][0]-dx) < 1e-6
                               and abs(cb['bbox'][2]-ca['bbox'][2]-dx) < 1e-6)
                    if not allowed:
                        return {'passed': False, 'reason': 'non-exempt character position changed', 'text': text}
                    changed = True
                    changes.append({'span': text, 'character': ')', 'delta_x_pt': dx,
                                    'first_origin': ca['origin'], 'second_origin': cb['origin'],
                                    'first_bbox': ca['bbox'], 'second_bbox': cb['bbox']})
                if not changed and sa['bbox'] != sb['bbox']:
                    return {'passed': False, 'reason': 'non-exempt span bounding box changed'}
    return {'passed': bool(changes), 'changes': changes, 'characters_checked': chars_checked,
            'all_other_characters_exact': True}


def compare_figure(first_pdf: Path, second_pdf: Path, relative_name: str,
                   *, baseline_data_equal: bool = False, dpi: int = 120) -> dict:
    """通常逐像素检查；三幅指定 MATLAB 图采用证据约束的窄例外。"""
    with pymupdf.open(first_pdf) as da, pymupdf.open(second_pdf) as db:
        if len(da) != 1 or len(db) != 1:
            return {'file': relative_name, 'passed': False, 'reason': 'figure page count'}
        a, b = da[0], db[0]
        pa, pb = a.get_pixmap(dpi=dpi, alpha=False), b.get_pixmap(dpi=dpi, alpha=False)
        same_size = (pa.width, pa.height) == (pb.width, pb.height) and a.rect == b.rect
        if not same_size:
            return {'file': relative_name, 'passed': False, 'reason': 'figure dimensions changed'}
        diff = np.abs(np.frombuffer(pa.samples, dtype=np.uint8).astype(int)
                      - np.frombuffer(pb.samples, dtype=np.uint8).astype(int))
        changed_fraction = np.count_nonzero(diff) / diff.size
        default_okay = not np.any(diff) or (diff.max() <= 1 and changed_fraction < 1e-4)
        report = {'file': relative_name, 'passed': bool(default_okay),
                  'pixel_equal': bool(not np.any(diff)), 'render_dpi': dpi,
                  'maximum_channel_difference': int(diff.max()),
                  'changed_channel_count': int(np.count_nonzero(diff)),
                  'changed_channel_fraction': changed_fraction}
        if default_okay:
            return report
        name = relative_name.replace('\\', '/')
        if name not in {'layout_v5/baseline_q_joint.pdf', 'layout_v5/eta_sensitivity_selected_c0.pdf',
                        'scenario1_heatmaps_c0_eta.pdf'}:
            return report
        vectors_equal = a.get_drawings() == b.get_drawings()
        fonts_equal = _font_streams(da, a) == _font_streams(db, b)
        report.update(scientific_vectors_exact=vectors_equal, embedded_font_streams_exact=fonts_equal)
        if not vectors_equal or not fonts_equal:
            return report
        if name.startswith('layout_v5/'):
            if a.get_images() or b.get_images():
                return report
            text_check = _panel_bracket_geometry(a, b)
            report['panel_bracket_check'] = text_check
            if not text_check['passed']:
                return report
            # 像素差必须局限于获准右括号的字形框，不允许其他区域的差异。
            mask = np.zeros((pa.height, pa.width), dtype=bool)
            for change in text_check['changes']:
                box = pymupdf.Rect(change['first_bbox']) | pymupdf.Rect(change['second_bbox'])
                x0, y0 = np.floor(np.array([box.x0, box.y0]) * dpi/72).astype(int) - 2
                x1, y1 = np.ceil(np.array([box.x1, box.y1]) * dpi/72).astype(int) + 2
                mask[max(0,y0):min(pa.height,y1), max(0,x0):min(pa.width,x1)] = True
            pixels_changed = np.any(diff.reshape(pa.height, pa.width, 3) != 0, axis=2)
            outside = int(np.count_nonzero(pixels_changed & ~mask))
            report['changed_pixels_outside_brackets'] = outside
            report['passed'] = outside == 0 and changed_fraction <= 5e-4
            report['exception'] = 'MATLAB panel closing-parenthesis horizontal spacing only, <=0.8pt'
        else:
            # 原生高分辨率 JPEG heatmap 的极少色值量化差；向量/字形/数值输入须精确同。
            ia, ib = a.get_images(), b.get_images()
            metadata_a = [v[1:7] for v in ia]
            metadata_b = [v[1:7] for v in ib]
            text_flags = pymupdf.TEXTFLAGS_RAWDICT & ~pymupdf.TEXT_PRESERVE_IMAGES
            raw_text_equal = a.get_text('rawdict', flags=text_flags) == b.get_text('rawdict', flags=text_flags)
            info_a = [{k:v for k,v in item.items() if k != 'size'} for item in a.get_image_info()]
            info_b = [{k:v for k,v in item.items() if k != 'size'} for item in b.get_image_info()]
            same_image_geometry = (len(ia) == len(ib) == 1 and metadata_a == metadata_b
                                   and info_a == info_b)
            report.update(raw_text_geometry_exact=raw_text_equal,
                          image_geometry_exact=same_image_geometry,
                          baseline_grid_bytes_exact=baseline_data_equal)
            if same_image_geometry:
                im_a, im_b = pymupdf.Pixmap(da, ia[0][0]), pymupdf.Pixmap(db, ib[0][0])
                image_diff = np.abs(np.frombuffer(im_a.samples, dtype=np.uint8).astype(int)
                                    - np.frombuffer(im_b.samples, dtype=np.uint8).astype(int))
                report['native_jpeg_decoded_maximum_channel_difference'] = int(image_diff.max())
                report['native_jpeg_decoded_changed_fraction'] = np.count_nonzero(image_diff)/image_diff.size
            report['passed'] = bool(raw_text_equal and same_image_geometry and baseline_data_equal
                                    and diff.max() <= 2 and changed_fraction <= 1e-4)
            report['exception'] = 'MATLAB native heatmap <=2 rendered channel levels in <=0.01% channels'
        return report

def _json_errors(a,b,first,second,prefix=''):
    if isinstance(a,dict) and isinstance(b,dict):
        ignore={'elapsed_seconds','runtime','provenance'}
        ak=set(a)-ignore;bk=set(b)-ignore
        if ak!=bk:return [prefix+' keys']
        return [error for key in sorted(ak) for error in _json_errors(a[key],b[key],first,second,prefix+'/'+key)]
    if isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b):return [prefix+' length']
        return [error for i,(x,y) in enumerate(zip(a,b)) for error in _json_errors(x,y,first,second,prefix+'/'+str(i))]
    if isinstance(a,bool) or isinstance(b,bool):return [] if type(a)==type(b) and a==b else [prefix]
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return [] if np.isclose(a,b,rtol=1e-10,atol=1e-9,equal_nan=True) else [prefix]
    if isinstance(a,str) and isinstance(b,str):
        normalize=lambda s,root:s.replace(str(root),'<OUTPUT>').replace(root.as_posix(),'<OUTPUT>')
        return [] if normalize(a,first)==normalize(b,second) else [prefix]
    return [] if a==b else [prefix]

def _numbers(obj, prefix=''):
    if isinstance(obj,dict):
        for key,value in obj.items():
            if key not in {'elapsed_seconds','runtime','software','provenance'}:
                yield from _numbers(value,prefix+'/'+key)
    elif isinstance(obj,list):
        for i,value in enumerate(obj):yield from _numbers(value,prefix+'/'+str(i))
    elif isinstance(obj,(int,float)) and not isinstance(obj,bool):
        yield prefix,float(obj)

def compare(first: Path, second: Path, report_path: Path) -> dict:
    cases=[]; failures=[]
    for folder in (first,second):
        path=folder/'run_report.json'
        if not path.is_file() or not json.loads(path.read_text(encoding='utf-8')).get('passed'):
            failures.append('incomplete run '+str(folder))
    for stage in ('xian','population','c0','joint',
                  'workspace/scenario1_threshold_landscape/current_run/output_csv'):
        if not (first/stage).is_dir() or not (second/stage).is_dir():
            failures.append('missing stage '+stage);continue
        aset={a.relative_to(first) for a in (first/stage).rglob('*') if a.is_file() and a.suffix in {'.csv','.json','.npz'}}
        bset={b.relative_to(second) for b in (second/stage).rglob('*') if b.is_file() and b.suffix in {'.csv','.json','.npz'}}
        if aset!=bset:failures.append('different artifact set '+stage)
        if not aset:failures.append('empty stage '+stage)
        for a in sorted((first/stage).rglob('*')):
            if not a.is_file() or a.suffix not in {'.csv','.json','.npz'}:continue
            rel=a.relative_to(first); b=second/rel
            if not b.exists():failures.append('missing '+str(rel));continue
            errors=[]; fields=0
            if a.suffix=='.csv':
                aa=pd.read_csv(a); bb=pd.read_csv(b)
                if list(aa.columns)!=list(bb.columns) or len(aa)!=len(bb):
                    failures.append('shape '+str(rel));continue
                for key in aa.columns:
                    if pd.api.types.is_numeric_dtype(aa[key]):
                        x=aa[key].to_numpy(float); y=bb[key].to_numpy(float); fields+=len(x)
                        if not np.allclose(x,y,rtol=1e-10,atol=1e-9,equal_nan=True):errors.append(key)
                    elif aa[key].fillna('').tolist()!=bb[key].fillna('').tolist():errors.append(key)
            elif a.suffix=='.json':
                aa=json.loads(a.read_text(encoding='utf-8'));bb=json.loads(b.read_text(encoding='utf-8'))
                fields=len(dict(_numbers(aa)))
                errors=_json_errors(aa,bb,first,second)
            else:
                with np.load(a) as aa,np.load(b) as bb:
                    if set(aa.files)!=set(bb.files):errors.append('array keys')
                    else:
                        for key in aa.files:
                            fields+=aa[key].size
                            if aa[key].shape!=bb[key].shape or aa[key].dtype!=bb[key].dtype:
                                errors.append(key+' shape/dtype')
                            elif not np.allclose(aa[key],bb[key],rtol=1e-10,atol=1e-9,equal_nan=True):errors.append(key)
            cases.append({'file':str(rel).replace('\\','/'),'numeric_fields':fields,'passed':not errors,'different_fields':errors[:10]})
            if errors:failures.append(str(rel))
    plots=[]
    baseline_grid=Path('workspace/scenario1_threshold_landscape/current_run/output_csv/landscape_summary.csv')
    baseline_data_equal=((first/baseline_grid).is_file() and (second/baseline_grid).is_file()
                         and (first/baseline_grid).read_bytes()==(second/baseline_grid).read_bytes())
    aset={p.relative_to(first/'figures') for p in (first/'figures').rglob('*.pdf')}
    bset={p.relative_to(second/'figures') for p in (second/'figures').rglob('*.pdf')}
    if aset!=bset:failures.append('different figure artifact set')
    for a in sorted((first/'figures').rglob('*.pdf')):
        b=second/'figures'/a.relative_to(first/'figures')
        if not b.exists():failures.append('missing plot '+a.name);continue
        check=compare_figure(a,b,a.relative_to(first/'figures').as_posix(),baseline_data_equal=baseline_data_equal)
        plots.append(check)
        if not check['passed']:failures.append('render '+a.name)
    if len(plots)!=20:failures.append(f'figure count {len(plots)} != 20')
    for name in ('manuscript_changes.json','validation/independent_checks.json',
                 'validation/baseline_science.json'):
        a=first/name;b=second/name
        if not a.is_file() or not b.is_file():
            failures.append('missing validation '+name);continue
        aa=json.loads(a.read_text(encoding='utf-8'));bb=json.loads(b.read_text(encoding='utf-8'))
        errors=_json_errors(aa,bb,first,second)
        cases.append({'file':name,'numeric_fields':len(dict(_numbers(aa))),'passed':not errors,'different_fields':errors[:10]})
        if errors:failures.append(name)
    report={'passed':not failures,'numeric_files':cases,'figure_render_checks':plots,
            'numerical_tolerance':{'relative':1e-10,'absolute':1e-9},'failures':failures,
            'pdf_metadata_ignored':True,'visual_review_required':True}
    dump(report_path,report);return report
