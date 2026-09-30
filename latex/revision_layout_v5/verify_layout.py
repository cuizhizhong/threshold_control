"""核查改动范围、缓存数值、最终字号与 PDF 页面；保存原始检查报告。"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import re
import subprocess
import sys
import numpy as np
import pandas as pd
import pymupdf as fitz
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
LATEX=HERE.parent
ROOT=LATEX.parent
QA=HERE/'qa'
OUT=LATEX/'figures'/'layout_v5'
SKILL=Path.home()/'.codex'/'skills'/'nature-figure'/'scripts'
sys.path.insert(0,str(SKILL))
import audit_panel_alignment as alignment
import audit_figure_collisions as collisions


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def source_scope():
    before=(HERE/'before'/'flatten_curve_analysis_cn.tex').read_text(encoding='utf-8-sig')
    after=(LATEX/'flatten_curve_analysis_cn.tex').read_text(encoding='utf-8-sig')
    allowed={2,4,5,6,7,8,9,10,14,15,16,17,18}
    labels=[]
    def normalize(text):
        blocks=list(re.finditer(r'\\begin\{figure\}.*?\\end\{figure\}',text,re.S))
        for i,m in reversed(list(enumerate(blocks,1))):
            if i in allowed:
                label=re.search(r'\\label\{([^}]+)\}',m[0])[1]
                text=text[:m.start()]+'FIGURE:'+label+text[m.end():]
        return text
    assert normalize(before)==normalize(after),'批准图块以外发生变化'
    for pattern in [r'\\label\{[^}]+\}',r'\\cite\{[^}]+\}']:
        assert re.findall(pattern,before)==re.findall(pattern,after)
    for name in ['references.bib','flatten_curve_supplement_cn.tex']:
        assert digest(LATEX/name)==digest(HERE/'before'/name),name
    for p in (HERE/'before'/'figures').rglob('*'):
        if p.is_file(): assert digest(p)==digest(LATEX/'figures'/p.relative_to(HERE/'before'/'figures')),p
    return {'approved_figure_blocks_only':True,'labels_citations_bib_supplement_unchanged':True,
            'all_previous_figure_assets_unchanged':True}


def native_checks():
    table=pd.read_csv(ROOT/'archive_unused/generated_snapshots/scenario1_threshold_landscape_current_run/output_csv/landscape_summary.csv')
    results={}
    for name in ['baseline_q_joint','c0_sensitivity_selected_eta','eta_sensitivity_selected_c0']:
        d=json.loads((QA/(name+'.matlab_geometry.json')).read_text(encoding='utf-8'))
        ordered=sorted(zip(d['positions'],d['series']),key=lambda v:(-v[0][1],v[0][0]))
        columns=2 if name=='baseline_q_joint' else 3
        panels=[]
        for k,(pos,_) in enumerate(ordered):
            x,y,w,h=pos
            panels.append({'id':chr(97+k),'bbox_pt':[x,y,x+w,y+h],
                           'grid_id':'native','row_start':k//columns,'row_stop':k//columns+1,
                           'col_start':k%columns,'col_stop':k%columns+1,
                           'panel_label_anchor_pt':[x-.02*w,y+1.015*h]})
        manifest={'schema_version':1,'backend':'matlab','figure':dict(zip(['width_pt','height_pt'],d['size_bp'])),'panels':panels}
        mpath=QA/(name+'.alignment-layout.json'); mpath.write_text(json.dumps(manifest),encoding='utf-8')
        result=subprocess.run([sys.executable,str(SKILL/'audit_panel_alignment.py'),str(mpath),
                               '--json-out',str(QA/(name+'.alignment.json')),'--strict'],capture_output=True,text=True)
        assert result.returncode==0,result.stdout+result.stderr
        matched=0; points=0
        for k,(_,series) in enumerate(ordered):
            curves=[s for s in series if len(np.atleast_1d(s['x']))>10]
            if name=='baseline_q_joint':
                vals=[4,5,8,10,12] if k==0 else [.002,.006,.010,.020]
                expected=[]
                for v in vals:
                    row=table[np.isclose(table.c0,v if k==0 else 10)&np.isclose(table.eta_frac,.05 if k==0 else v)].iloc[0]
                    tau=np.linspace(0,row.Delta_t,max(350,int(np.ceil(12*row.Delta_t))))
                    ss=row.S_bar+(row.S_star-row.S_bar)*np.exp(-row.c0*row.eta*tau/row.N)
                    expected.append((row.t1+tau,1-row.gamma*row.N/(row.beta*row.c0*ss)))
            else:
                field=['t1','Delta_t','t_end','q_max','J','I_t_cum'][k]
                is_c0=name=='c0_sensitivity_selected_eta'
                vals=[.002,.006,.010,.020] if is_c0 else [5,8,10,12]
                expected=[]
                for v in vals:
                    sub=table[np.isclose(table.eta_frac if is_c0 else table.c0,v)]
                    sub=sub[sub.valid.astype(bool)&np.isfinite(sub[field])]
                    if not is_c0: sub=sub.sort_values('eta_percent')
                    expected.append(((sub.c0 if is_c0 else sub.eta_percent).to_numpy(),sub[field].to_numpy()))
            assert len(curves)==len(expected),(name,k,len(curves),len(expected))
            for x,y in expected:
                found=[s for s in curves if len(s['x'])==len(x) and np.allclose(s['x'],x,rtol=1e-12,atol=1e-10)
                       and np.allclose(s['y'],y,rtol=1e-12,atol=1e-10)]
                assert len(found)==1,(name,k)
                matched+=1; points+=len(x)
        results[name]={'alignment':'PASS','curves_equal_original_formulas_or_csv':matched,'points_checked':points}
    return results


def figure_audit(pdf):
    font=subprocess.run([sys.executable,str(SKILL/'audit_pdf_text.py'),str(pdf),'--min-pt','5','--json'],capture_output=True,text=True,encoding='utf-8')
    (QA/(pdf.stem+'.font.json')).write_text(font.stdout,encoding='utf-8')
    assert font.returncode==0,pdf.stem+' 字号'
    result=collisions.audit_pdf(pdf)
    (QA/(pdf.stem+'.collision.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (QA/(pdf.stem+'.collision.txt')).write_text(collisions.render_text(result),encoding='utf-8')
    return {'figure':pdf.stem,'font':json.loads(font.stdout),'raw_collision_verdict':result['verdict'],
            'raw_collision_summary':result['summary'],'sha256':digest(pdf)}


def review_geometry():
    reviews=[]; unresolved=[]
    for rp in QA.glob('*.collision.json'):
        report=json.loads(rp.read_text(encoding='utf-8'))
        page=fitz.open(report['pdf'])[0]; drawings=page.get_drawings(); clips={}; active={}
        for item in page.get_drawings(extended=True):
            level=item['level'];active={k:v for k,v in active.items() if k<level}
            if item['type']=='clip':active[level]=fitz.Rect(item['scissor'])
            elif 'seqno' in item:
                clip=fitz.Rect(page.rect)
                for r in active.values():clip &= r
                clips[item['seqno']]=clip
        chars=[(chr(c[0]),fitz.Rect(c[3])) for t in page.get_texttrace() for c in t['chars'] if chr(c[0]).strip()]
        for f in report['findings']:
            row={'figure':rp.stem,'finding':f}
            target=fitz.Rect(f['text_bbox'])
            if f['severity']=='FAIL' and f['kind']=='text-stroke':
                relevant=[(c,r) for c,r in chars if target.contains(r)]
                hits=[]
                for index in f['object_indexes']:
                    item=drawings[index];clip=clips.get(item['seqno'],page.rect)
                    segments=collisions._segments_from_items(item['items'])
                    for c,r in relevant:
                        visible=fitz.Rect(collisions.rect_expand(collisions.rect_inset(tuple(r),.6),item['width']/2)) & clip
                        if not visible.is_empty and any(collisions.segment_intersects_rect(s,tuple(visible)) for s in segments):
                            hits.append({'char':c,'bbox':list(r),'path':index})
                row['glyph_path_hits']=hits
                if relevant and not hits:
                    row['resolution']='false_positive_verified_clipping_or_merged_text_boxes'
                else:row['resolution']='requires_visual_review';unresolved.append(row)
            elif f['severity']=='FAIL' and f['kind']=='text-text' and f['text']=='IT' and f.get('other_text')=='peak':
                row['resolution']='requires_math_glyph_visual_review'
            elif f['severity']=='WARN':row['resolution']='requires_visual_review_of_inset_background_or_bar_edge'
            else: row['resolution']='unresolved';unresolved.append(row)
            region=target
            if f.get('other_text'):region |= fitz.Rect(f['other_bbox'])
            if f['severity']=='FAIL' and row['resolution']!='false_positive_verified_clipping_or_merged_text_boxes':
                crop=QA/f'review_{len(reviews):03}.png'
                page.get_pixmap(clip=region+(-4,-4,4,4),dpi=600).save(crop)
                row['crop']=str(crop)
            reviews.append(row)
    (QA/'collision_geometry_review.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding='utf-8')
    return [{'figure':r['figure'],'text':r['finding']['text'],'hits':r.get('glyph_path_hits')} for r in unresolved]


def pages():
    aux=(LATEX/'flatten_curve_analysis_cn.aux').read_text(encoding='utf-8')
    mapping={}
    for m in re.finditer(r'\\newlabel\{(fig:[^}]+)\}\{\{(\d+)\}\{(\d+)\}',aux):
        if int(m[2]) in {2,4,5,6,7,8,9,10,14,15,16,17,18}:mapping[int(m[2])]=int(m[3])
    doc=fitz.open(LATEX/'flatten_curve_analysis_cn.pdf')
    refs=[i+1 for i,p in enumerate(doc) if '参考文献' in p.get_text()]
    chosen={p+d for p in mapping.values() for d in [-1,0,1]}|set(refs)
    files=[]
    for p in sorted(chosen):
        if 1<=p<=len(doc):
            path=QA/f'page_{p:02}.png';doc[p-1].get_pixmap(dpi=130).save(path);files.append(path)
    cells=[]
    for path in files:
        im=Image.open(path).convert('RGB');im.thumbnail((290,425))
        cell=Image.new('RGB',(310,450),'white');cell.paste(im,((310-im.width)//2,20))
        ImageDraw.Draw(cell).text((5,3),path.stem,fill='black');cells.append(cell)
    sheet=Image.new('RGB',(310*4,450*((len(cells)+3)//4)),'#cccccc')
    for i,im in enumerate(cells):sheet.paste(im,((i%4)*310,(i//4)*450))
    sheet.save(QA/'pages_contact.png')
    bibliography=doc[refs[-1]-1].get_text() if refs else ''
    assert all(f'[{i}]' in bibliography for i in range(1,6)),bibliography
    return {'figure_pages':mapping,'page_count':len(doc),'bibliography_pages':refs,'five_references_visible':True}


def main():
    report=source_scope()
    report['matlab_data_checks']=native_checks()
    report['figures']=list(ThreadPoolExecutor(max_workers=4).map(figure_audit,sorted(OUT.glob('*.pdf'))))
    report['geometry_requires_visual_review']=review_geometry()
    report.update(pages())
    log=(LATEX/'flatten_curve_analysis_cn.log').read_text(encoding='utf-8',errors='replace')
    report['layout_or_reference_warnings']=re.findall(r'^.*(?:Overfull|Underfull|Float too large|Reference .*undefined|Citation .*undefined).*$',log,re.M)
    assert not report['layout_or_reference_warnings']
    preflight=subprocess.run([sys.executable,str(SKILL/'validate_figure.py'),str(HERE/'layout_python.py')],capture_output=True,text=True,encoding='utf-8')
    (QA/'source_preflight.txt').write_text(preflight.stdout,encoding='utf-8')
    report['source_preflight_exit_code']=preflight.returncode
    (QA/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='figures'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
