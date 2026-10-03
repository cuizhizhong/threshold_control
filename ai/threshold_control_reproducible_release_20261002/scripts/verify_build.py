#!/usr/bin/env python3
"""在临时目录中从零编译，不覆盖交付PDF；逐页比较重编PDF和锁定PDF。

需要XeLaTeX、Biber、PyMuPDF。使用120 dpi RGB逐像素比较并比较提取文本。
TeX或字体版本不同可能改变排版；此时应查看报告，不能当作内容一致。
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
try:
    import fitz
except ImportError:
    raise SystemExit('Install PyMuPDF with requirements-audit.txt first.')
ROOT=Path(__file__).resolve().parents[1]

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir',type=Path,default=ROOT/'validation/build_recheck')
    args=ap.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    for executable in ('xelatex','biber'):
        if shutil.which(executable) is None:ap.exit(1,'Missing executable: '+executable+'\n')
    report={'dpi':120,'renderer':fitz.VersionBind,'documents':{}}
    try:
        with tempfile.TemporaryDirectory(prefix='threshold-build-') as tmp:
            latex=Path(tmp)/'latex';shutil.copytree(ROOT/'latex',latex)
            # Remove all generated data, including the delivered convenience bbl.
            for p in latex.iterdir():
                if p.suffix in {'.pdf','.aux','.bbl','.bcf','.blg','.log','.out','.toc','.xml'} or p.name.endswith('.run.xml'):
                    p.unlink()
            texopts=['-interaction=nonstopmode','-halt-on-error']
            jobs=[['xelatex',*texopts,'flatten_curve_supplement_cn.tex']]*2
            jobs += [['xelatex',*texopts,'flatten_curve_analysis_cn.tex'],
                     ['biber','flatten_curve_analysis_cn'],
                     ['xelatex',*texopts,'flatten_curve_analysis_cn.tex'],
                     ['xelatex',*texopts,'flatten_curve_analysis_cn.tex']]
            with (out/'stdout.log').open('w',encoding='utf-8') as log:
                for cmd in jobs:
                    subprocess.run(cmd,cwd=latex,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
            for stem in ('flatten_curve_analysis_cn','flatten_curve_supplement_cn'):
                ref=ROOT/'latex'/(stem+'.pdf');new=latex/(stem+'.pdf')
                da=fitz.open(ref);db=fitz.open(new);rows=[]
                for i in range(max(len(da),len(db))):
                    if i>=min(len(da),len(db)):
                        rows.append({'page':i+1,'pixel_equal':False,'text_equal':False});continue
                    a=da[i].get_pixmap(dpi=120,alpha=False);b=db[i].get_pixmap(dpi=120,alpha=False)
                    eq=(a.width,a.height)==(b.width,b.height) and a.samples==b.samples
                    rows.append({'page':i+1,'pixel_equal':eq,'text_equal':da[i].get_text()==db[i].get_text(),
                      'reference_pixel_sha256':hashlib.sha256(a.samples).hexdigest(),
                      'rebuilt_pixel_sha256':hashlib.sha256(b.samples).hexdigest()})
                report['documents'][stem]={'reference_pages':len(da),'rebuilt_pages':len(db),
                    'reference_sha256':sha(ref),'rebuilt_sha256':sha(new),
                    'all_pages_pixel_equal':all(x['pixel_equal'] for x in rows),
                    'all_pages_text_equal':all(x['text_equal'] for x in rows),'pages':rows}
                shutil.copy2(new,out/(stem+'.pdf'))
                shutil.copy2(latex/(stem+'.log'),out/(stem+'.log'))
            shutil.copy2(latex/'flatten_curve_analysis_cn.blg',out/'flatten_curve_analysis_cn.blg')
        (out/'comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        ok=all(x['all_pages_pixel_equal'] and x['all_pages_text_equal'] for x in report['documents'].values())
        print(json.dumps({'passed':ok,'report':str(out/'comparison.json'),'archived_pdf_modified':False},ensure_ascii=False,indent=2))
        if not ok:ap.exit(1,'Compilation succeeded but rendering differs; inspect comparison.json.\n')
    except (subprocess.SubprocessError,OSError,RuntimeError) as exc:ap.exit(1,str(exc)+'\n')

if __name__=='__main__':main()
