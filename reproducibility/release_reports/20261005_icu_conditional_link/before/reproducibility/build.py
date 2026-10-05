"""完整工程独立编译与 PDF 检查；显式关闭句柄以兼容 Windows。"""
from __future__ import annotations
import hashlib
import json
import re
import shutil
import subprocess
import traceback
from pathlib import Path
import pymupdf
from PIL import Image, ImageDraw
from bootstrap import dump, sha

STEMS=('flatten_curve_supplement_cn','flatten_curve_analysis_cn')

def _run(output_dir: Path, root: Path, *, figure_dir: Path | None=None,
        main_text: str | None=None, supplement_text: str | None=None) -> dict:
    out=output_dir/'document'; latex=out/'latex'
    latex.mkdir(parents=True,exist_ok=True)
    for name in ('flatten_curve_analysis_cn.tex','flatten_curve_supplement_cn.tex','references.bib','elegantpaper.cls'):
        shutil.copy2(root/'latex'/name,latex/name)
    if main_text is not None:
        (latex/'flatten_curve_analysis_cn.tex').write_text(main_text,encoding='utf-8')
    if supplement_text is not None:
        (latex/'flatten_curve_supplement_cn.tex').write_text(supplement_text,encoding='utf-8')
    assets=figure_dir or root/'latex/figures'
    shutil.copytree(assets,latex/'figures',dirs_exist_ok=True)
    for exe in ('xelatex','biber'):
        if not shutil.which(exe):
            raise FileNotFoundError(f'未找到 {exe}')
    options=['-interaction=nonstopmode','-halt-on-error']
    jobs=[['xelatex',*options,STEMS[0]+'.tex']]*2
    jobs += [['xelatex',*options,STEMS[1]+'.tex'],['biber',STEMS[1]],
             ['xelatex',*options,STEMS[1]+'.tex'],['xelatex',*options,STEMS[1]+'.tex']]
    with (out/'stdout.log').open('w',encoding='utf-8') as log:
        for job in jobs:
            subprocess.run(job,cwd=latex,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=360)
    failures=[]; log_report={}; documents={}
    fatal=r'undefined|Missing character|Overfull|Float too large|multiply defined|^!|(?:LaTeX|Package \S+) Error:'
    for stem in STEMS:
        txt=(latex/(stem+'.log')).read_text(encoding='utf-8',errors='replace')
        hits=[l for l in txt.splitlines() if re.search(fatal,l,re.I)]
        warnings=[l for l in txt.splitlines() if 'Warning' in l or 'Underfull' in l]
        log_report[stem]={'fatal':hits,'warnings':warnings}
        failures.extend(hits)
        pdf=latex/(stem+'.pdf'); render=out/'render'/stem; render.mkdir(parents=True,exist_ok=True)
        pages=[]; outside=[]; fonts=set()
        with pymupdf.open(pdf) as doc:
            for i,page in enumerate(doc):
                page.get_pixmap(dpi=120,alpha=False).save(render/f'{i+1:03}.png')
                for block in page.get_text('dict')['blocks']:
                    for line in block.get('lines',[]):
                        for span in line.get('spans',[]):
                            fonts.add(span['font'])
                            # 排版几何预检仅检测超出纸张，不能代替视觉审查。
                            if span['text'].strip() and not (page.rect+(-1,-1,1,1)).contains(pymupdf.Rect(span['bbox'])):
                                outside.append({'page':i+1,'text':span['text'],'bbox':span['bbox']})
                pages.append({'page':i+1,'text_sha256':hashlib.sha256(page.get_text().encode()).hexdigest(),
                              'image_count':len(page.get_images()),'render':str((render/f'{i+1:03}.png').relative_to(output_dir))})
        documents[stem]={'page_count':len(pages),'pdf_sha256':sha(pdf),'fonts':sorted(fonts),
                         'outside_page_text':outside,'pages':pages}
        failures.extend([str(x) for x in outside])
        # 4页一组，供整篇版面审阅；重点页另看单页120dpi图。
        for start in range(0,len(pages),4):
            sheet=Image.new('RGB',(1240,1800),'#dedede'); draw=ImageDraw.Draw(sheet)
            for j in range(4):
                if start+j>=len(pages):break
                with Image.open(render/f'{start+j+1:03}.png') as img:
                    img.thumbnail((610,850))
                    x=(j%2)*620+5; y=(j//2)*900+25
                    sheet.paste(img,(x,y)); draw.text((x,y-20),f'{stem}: page {start+j+1}',fill='black')
            sheet.save(render/f'contact_{start+1:03}.png')
    blg=(latex/(STEMS[1]+'.blg')).read_text(encoding='utf-8',errors='replace')
    bibhits=[l for l in blg.splitlines() if re.search(r'WARN|ERROR',l)]
    failures.extend(bibhits)
    text=(latex/(STEMS[1]+'.tex')).read_text(encoding='utf-8')
    citation_keys=set(k.strip() for group in re.findall(r'\\(?:cite|parencite|textcite)\*?(?:\[[^\]]*\])*\{([^}]+)\}',text) for k in group.split(','))
    bibkeys=re.findall(r'@\w+\s*\{\s*([^,]+),',(latex/'references.bib').read_text(encoding='utf-8'))
    missing=sorted(citation_keys-set(bibkeys)); failures.extend(missing)
    bbl=(latex/(STEMS[1]+'.bbl')).read_text(encoding='utf-8',errors='replace')
    printed_keys=set(re.findall(r'\\entry\{([^}]+)\}',bbl))
    missing_printed=sorted(citation_keys-printed_keys)
    failures.extend('bibliography did not emit '+k for k in missing_printed)
    if text.count('\\printbibliography')!=1:
        failures.append('Main manuscript must have exactly one bibliography')
    with pymupdf.open(latex/(STEMS[1]+'.pdf')) as doc:
        bibliography_pages=[i+1 for i,page in enumerate(doc) if '参考文献' in page.get_text()]
    if not bibliography_pages:failures.append('Bibliography heading not rendered in main PDF')
    report={'passed':not failures,'documents':documents,'logs':log_report,'biber_warnings':bibhits,
            'citation_keys':sorted(citation_keys),'bibliography_entries':len(bibkeys),'missing_citations':missing,
            'printed_bibliography_keys':sorted(printed_keys),'missing_printed_references':missing_printed,
            'bibliography_heading_pages':bibliography_pages,
            'main_bibliography_print_count':text.count('\\printbibliography'),
            'visual_review':'pending_manual_review','failures':failures,
            'scope':'实际完整编译与纸张边界预检，不是逐页视觉认证。'}
    dump(out/'build_report.json',report)
    if failures:
        raise RuntimeError('编译/引用/纸张边界核查失败：'+str(failures[:5]))
    return report


def run(output_dir: Path, root: Path, *, figure_dir: Path | None=None,
        main_text: str | None=None, supplement_text: str | None=None) -> dict:
    try:
        return _run(output_dir,root,figure_dir=figure_dir,main_text=main_text,supplement_text=supplement_text)
    except Exception as exc:
        path=output_dir/'document/build_report.json'
        prior=json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}
        dump(path,{**prior,'passed':False,'error':str(exc),'traceback':traceback.format_exc(),
                   'log':'document/stdout.log','visual_review':'not_passed'})
        raise
