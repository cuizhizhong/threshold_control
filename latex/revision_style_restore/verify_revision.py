"""本轮源文件边界、引用、PDF 字号/碰撞及页面渲染检查。"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import fitz
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
LATEX=HERE.parent
QA=HERE/"qa"
SKILL=Path.home()/".codex"/"skills"/"nature-figure"/"scripts"
LABELS=["fig:xian:observed-fit","fig:xian:strategy-process","fig:dom:levers",
        "fig:c0-phase","fig:dom:critical-cases"]
NAMES=["xian_observed_fit","xian_strategy_process","population_threshold_levers",
       "c0_phase_stationary","critical_population_cases"]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def normalized(text):
    # 本轮仅允许五个 figure 块和表 2 的含义单位发生变化。
    def replace(m):
        match=re.search(r"\\label\{([^}]+)\}",m[0])
        return "FIGURE:"+match[1] if match and match[1] in LABELS else m[0]
    text=re.sub(r"\\begin\{figure\}.*?\\end\{figure\}",replace,text,flags=re.S)
    m=re.search(r"\\begin\{table\}.*?\\label\{tab:xian_initial_fit\}.*?\\end\{table\}",text,re.S)
    # 定位该表，避免允许其他表的改动。
    start=text.rfind(r"\begin{table}",0,text.index(r"\label{tab:xian_initial_fit}"))
    end=text.index(r"\end{table}",start)+len(r"\end{table}")
    block=text[start:end].replace("（人）","").replace(r"（$\mathrm d^{-1}$）","")
    return text[:start]+block+text[end:]

def contact(files,path,cols=3,width=320):
    imgs=[]
    for f in files:
        im=Image.open(f).convert("RGB")
        im.thumbnail((width,460))
        cell=Image.new("RGB",(width+16,490),"white")
        cell.paste(im,((width+16-im.width)//2,24))
        ImageDraw.Draw(cell).text((8,5),f.stem,fill="black")
        imgs.append(cell)
    out=Image.new("RGB",((width+16)*cols,490*((len(imgs)+cols-1)//cols)),"#dddddd")
    for i,im in enumerate(imgs): out.paste(im,((i%cols)*(width+16),(i//cols)*490))
    out.save(path)

def main():
    before=(HERE/"before"/"flatten_curve_analysis_cn.tex").read_text(encoding="utf-8-sig")
    after=(LATEX/"flatten_curve_analysis_cn.tex").read_text(encoding="utf-8-sig")
    assert normalized(before)==normalized(after), "非批准区域发生变化"
    assert re.findall(r"\\label\{[^}]+\}",before)==re.findall(r"\\label\{[^}]+\}",after)
    assert re.findall(r"\\cite\{[^}]+\}",before)==re.findall(r"\\cite\{[^}]+\}",after)
    assert digest(LATEX/"references.bib")==digest(HERE/"before"/"references.bib")
    assert digest(LATEX/"flatten_curve_supplement_cn.tex")==digest(HERE/"before"/"flatten_curve_supplement_cn.tex")
    assert all(digest(p)==digest(LATEX/"figures"/"revision_v4"/p.name)
               for p in (HERE/"before"/"figures").glob("*.*"))
    audit={"scope_checks":"PASS", "labels_unchanged":True,"citations_unchanged":True,
           "bibliography_unchanged":True,"supplement_source_unchanged":True,"previous_figures_unchanged":True}
    for name in NAMES:
        pdf=LATEX/"figures"/"style_restored"/(name+".pdf")
        out=subprocess.run([sys.executable,str(SKILL/"audit_pdf_text.py"),str(pdf),"--min-pt","5","--json"],capture_output=True,text=True)
        (QA/(name+".font.json")).write_text(out.stdout,encoding="utf-8")
        assert out.returncode==0, name+" glyph floor"
        result=subprocess.run([sys.executable,str(SKILL/"audit_figure_collisions.py"),str(pdf),"--json-out",str(QA/(name+".collision.json"))],capture_output=True,text=True)
        (QA/(name+".collision.txt")).write_text(result.stdout,encoding="utf-8")
        audit[name]={"font":json.loads(out.stdout),"collision_exit_code":result.returncode,"sha256":digest(pdf)}
    result=subprocess.run([sys.executable,str(SKILL/"validate_figure.py"),str(HERE/"restore_figures.py")],capture_output=True,text=True)
    (QA/"source_preflight.txt").write_text(result.stdout,encoding="utf-8")
    originals=["fig_panel_A","fig_panel_B","fig_panel_A_Ncumstar","fig_panel_A_Nstar45","fig_panel_A_Nstarinf","c0_sensitivity_phase"]
    for name in originals:
        doc=fitz.open(LATEX/"figures"/(name+".pdf"))
        doc[0].get_pixmap(dpi=180).save(QA/("original_"+name+".png"))
    metadata=json.loads((LATEX/"revision_v4"/"data"/"dominance_metadata.json").read_text(encoding="utf-8"))
    numbers=[]
    for oldname,records,newname in [
        ("fig_panel_A",metadata["cases"][0],"population_threshold_levers"),
        ("fig_panel_B",metadata["fixed_eta"],"population_threshold_levers"),
        ("fig_panel_A_Ncumstar",metadata["cases"][1],"critical_population_cases"),
        ("fig_panel_A_Nstar45",metadata["cases"][2],"critical_population_cases"),
        ("fig_panel_A_Nstarinf",metadata["cases"][3],"critical_population_cases")]:
        oldtext=fitz.open(LATEX/"figures"/(oldname+".pdf"))[0].get_text()
        newtext=fitz.open(LATEX/"figures"/"style_restored"/(newname+".pdf"))[0].get_text()
        values=[f"{r['Itcum']:,.0f}" for r in records]
        assert all(v in oldtext and v in newtext for v in values),(oldname,values)
        numbers.append({"original":oldname,"combined":newname,"bar_labels":values,"match":True})
    audit["original_pdf_bar_labels"]=numbers
    aux=(LATEX/"flatten_curve_analysis_cn.aux").read_text(encoding="utf-8")
    pages={label:int(re.search(r"\\newlabel\{"+re.escape(label)+r"\}\{\{[^}]+\}\{(\d+)\}",aux)[1]) for label in LABELS+["tab:xian_initial_fit"]}
    doc=fitz.open(LATEX/"flatten_curve_analysis_cn.pdf")
    selected=set()
    for page in pages.values(): selected.update([page-1,page,page+1])
    refpages=[i+1 for i,p in enumerate(doc) if "参考文献" in p.get_text()]
    selected.update(refpages)
    files=[]
    for p in sorted(selected):
        if not 1<=p<=len(doc):continue
        path=QA/f"final_page_{p:02}.png"
        doc[p-1].get_pixmap(dpi=150).save(path); files.append(path)
    contact(files,QA/"final_pages_contact.png")
    # 修改前页面的渲染供版面比较。
    old=fitz.open(HERE/"before"/"flatten_curve_analysis_cn.pdf")
    for p in sorted(selected):
        if 1<=p<=len(old): old[p-1].get_pixmap(dpi=90).save(QA/f"before_page_{p:02}.png")
    audit.update(pages=pages,page_count=len(doc),bibliography_pages=refpages)
    (QA/"verification.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in audit.items() if k not in NAMES},ensure_ascii=False,indent=2))

if __name__=="__main__":main()
