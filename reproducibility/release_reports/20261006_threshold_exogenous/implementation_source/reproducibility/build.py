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

def _active_tex(text: str) -> str:
    """引用和出版指令只检查未注释的源码。"""
    return re.sub(r'(?m)(?<!\\)%.*$', '', text)


def _citation_keys(text: str) -> set[str]:
    return {key.strip() for group in re.findall(
        r'\\(?:cite|parencite|textcite)\*?(?:\[[^\]]*\])*\{([^}]+)\}',
        _active_tex(text)) for key in group.split(',') if key.strip()}


def _needs_bibliography(text: str) -> bool:
    return bool(_citation_keys(text) or '\\printbibliography' in _active_tex(text))


def _document_jobs(texts: dict[str, str]) -> list[list[str]]:
    """旧补充稿两遍 XeLaTeX；含独立文献的补充稿与正文均执行完整链。"""
    options=['-interaction=nonstopmode','-halt-on-error']
    jobs=[]
    for stem in STEMS:
        xe=['xelatex',*options,stem+'.tex']
        if stem == STEMS[1] or _needs_bibliography(texts[stem]):
            jobs.extend([xe,['biber',stem],xe.copy(),xe.copy()])
        else:
            jobs.extend([xe,xe.copy()])
    return jobs


def _bibliography_report(latex: Path, stem: str, text: str, bibkeys: set[str],
                         heading_pages: list[int]) -> tuple[dict, list[str]]:
    """两份文档分别核对引用；正文历史平铺报告字段由调用方继续提供。"""
    keys=_citation_keys(text)
    print_count=_active_tex(text).count('\\printbibliography')
    enabled=stem == STEMS[1] or _needs_bibliography(text)
    warnings=[]; printed=set(); failures=[]
    missing=sorted(keys-bibkeys)
    failures.extend(stem+': missing bibliography entry '+key for key in missing)
    if enabled:
        blg=latex/(stem+'.blg')
        if not blg.is_file():
            failures.append(stem+': Biber log missing')
        else:
            warnings=[line for line in blg.read_text(encoding='utf-8',errors='replace').splitlines()
                      if re.search(r'WARN|ERROR',line)]
            failures.extend(stem+': '+line for line in warnings)
        bbl=latex/(stem+'.bbl')
        if not bbl.is_file():
            failures.append(stem+': Biber output missing')
        else:
            printed=set(re.findall(r'\\entry\{([^}]+)\}',bbl.read_text(encoding='utf-8',errors='replace')))
        if print_count != 1:
            failures.append(stem+': manuscript must have exactly one bibliography')
        if not heading_pages:
            failures.append(stem+': bibliography heading not rendered in PDF')
    missing_printed=sorted(keys-printed)
    failures.extend(stem+': bibliography did not emit '+key for key in missing_printed)
    return {'enabled':enabled,'citation_keys':sorted(keys),'missing_citations':missing,
            'printed_bibliography_keys':sorted(printed),'missing_printed_references':missing_printed,
            'biber_warnings':warnings,'bibliography_heading_pages':heading_pages,
            'bibliography_print_count':print_count},failures


def _run(output_dir: Path, root: Path, *, figure_dir: Path | None=None,
        main_text: str | None=None, supplement_text: str | None=None,
        bibliography_path: Path | None=None, build_script_path: Path | None=None) -> dict:
    root=Path(root).resolve()
    bibliography = Path(bibliography_path) if bibliography_path is not None else root/'latex/references.bib'
    bibliography = (root/bibliography).resolve() if not bibliography.is_absolute() else bibliography.resolve()
    if not bibliography.is_file():
        raise FileNotFoundError('编译文献库缺失：'+str(bibliography))
    bibliography_sha256 = sha(bibliography)
    build_script = Path(build_script_path) if build_script_path is not None else root/'latex/build_paper.ps1'
    build_script = (root/build_script).resolve() if not build_script.is_absolute() else build_script.resolve()
    if not build_script.is_file():
        if build_script_path is not None:
            raise FileNotFoundError('受控编译脚本缺失：'+str(build_script))
        build_script = None
    build_script_input = ({'source':str(build_script),'sha256':sha(build_script)}
                          if build_script is not None else None)
    out=output_dir/'document'; latex=out/'latex'
    latex.mkdir(parents=True,exist_ok=True)
    for name in ('flatten_curve_analysis_cn.tex','flatten_curve_supplement_cn.tex','elegantpaper.cls'):
        shutil.copy2(root/'latex'/name,latex/name)
    shutil.copy2(bibliography,latex/'references.bib')
    if sha(latex/'references.bib') != bibliography_sha256:
        raise RuntimeError('隔离编译文献库复制后哈希不一致')
    if build_script is not None:
        shutil.copy2(build_script,latex/'build_paper.ps1')
        if sha(latex/'build_paper.ps1') != build_script_input['sha256']:
            raise RuntimeError('隔离编译脚本复制后哈希不一致')
    if main_text is not None:
        (latex/'flatten_curve_analysis_cn.tex').write_text(main_text,encoding='utf-8')
    if supplement_text is not None:
        (latex/'flatten_curve_supplement_cn.tex').write_text(supplement_text,encoding='utf-8')
    assets=figure_dir or root/'latex/figures'
    shutil.copytree(assets,latex/'figures',dirs_exist_ok=True)
    for exe in ('xelatex','biber'):
        if not shutil.which(exe):
            raise FileNotFoundError(f'未找到 {exe}')
    texts={stem:(latex/(stem+'.tex')).read_text(encoding='utf-8-sig') for stem in STEMS}
    jobs=_document_jobs(texts)
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
    bibkeys=re.findall(r'@\w+\s*\{\s*([^,]+),',(latex/'references.bib').read_text(encoding='utf-8'))
    bibliographies={}
    for stem in STEMS:
        with pymupdf.open(latex/(stem+'.pdf')) as doc:
            heading_pages=[i+1 for i,page in enumerate(doc) if '参考文献' in page.get_text()]
        bibliographies[stem],bibfailures=_bibliography_report(latex,stem,texts[stem],set(bibkeys),heading_pages)
        failures.extend(bibfailures)
    main_bibliography=bibliographies[STEMS[1]]
    report={'passed':not failures,'documents':documents,'logs':log_report,
            'biber_warnings':main_bibliography['biber_warnings'],
            'bibliography_input':{'source':str(bibliography),'sha256':bibliography_sha256},
            'build_script_input':build_script_input,'executed_jobs':jobs,'bibliographies':bibliographies,
            'citation_keys':main_bibliography['citation_keys'],'bibliography_entries':len(bibkeys),
            'missing_citations':main_bibliography['missing_citations'],
            'printed_bibliography_keys':main_bibliography['printed_bibliography_keys'],
            'missing_printed_references':main_bibliography['missing_printed_references'],
            'bibliography_heading_pages':main_bibliography['bibliography_heading_pages'],
            'main_bibliography_print_count':main_bibliography['bibliography_print_count'],
            'visual_review':'pending_manual_review','failures':failures,
            'scope':'实际完整编译与纸张边界预检，不是逐页视觉认证。'}
    dump(out/'build_report.json',report)
    if failures:
        raise RuntimeError('编译/引用/纸张边界核查失败：'+str(failures[:5]))
    return report


def run(output_dir: Path, root: Path, *, figure_dir: Path | None=None,
        main_text: str | None=None, supplement_text: str | None=None,
        bibliography_path: Path | None=None, build_script_path: Path | None=None) -> dict:
    try:
        return _run(output_dir,root,figure_dir=figure_dir,main_text=main_text,supplement_text=supplement_text,
                    bibliography_path=bibliography_path,build_script_path=build_script_path)
    except Exception as exc:
        path=output_dir/'document/build_report.json'
        prior=json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}
        dump(path,{**prior,'passed':False,'error':str(exc),'traceback':traceback.format_exc(),
                   'log':'document/stdout.log','visual_review':'not_passed'})
        raise
