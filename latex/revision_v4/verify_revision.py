"""生成图表改排的可复核记录、页图及新旧编号映射。"""
from pathlib import Path
import re, json, hashlib, subprocess, sys, shutil
from collections import Counter
import fitz
from PIL import Image, ImageDraw
from decimal import Decimal
HERE=Path(__file__).resolve().parent
LATEX=HERE.parent
ROOT=LATEX.parent
QA=HERE/"qa"
def read(p): return p.read_text(encoding="utf-8-sig")
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
old=read(HERE/"before/flatten_curve_analysis_cn.tex")
new=read(LATEX/"flatten_curve_analysis_cn.tex")
sup=read(LATEX/"flatten_curve_supplement_cn.tex")
def blocks(s,env): return re.findall(r"\\begin\{"+env+r"\}.*?\\end\{"+env+r"\}",s,re.S)
checks={}
for env in ["theorem","lemma","proposition","corollaryn","remarkn","proof","equation","align"]:
    a,b=Counter(blocks(old,env)),Counter(blocks(new,env))
    checks[env]={"before":sum(a.values()),"after":sum(b.values()),"unchanged":a==b}
def citations(s): return sorted(set(k.strip() for x in re.findall(r"\\(?:cite|parencite|textcite)\{([^}]+)\}",s) for k in x.split(",")))
checks["citations"]={"before":citations(old),"after":citations(new),"unchanged":citations(old)==citations(new)}
checks["references_bib_unchanged"]=digest(HERE/"before/references.bib")==digest(LATEX/"references.bib")
checks["counts"]={"main_figures":len(blocks(new.split(r"\appendix")[0],"figure")),"appendix_figures":len(blocks(new.split(r"\appendix")[1],"figure")),"main_tables":len(blocks(new,"table")),"supplement_tables":len(blocks(sup,"table"))}
assert list(checks["counts"].values())==[16,4,4,3]
def labels(s): return re.findall(r"\\label\{([^}]+)\}",s)
declared=set(labels(new)+labels(sup))
refs=set(re.findall(r"\\(?:ref|eqref)\{([^}]+)\}",new+sup))
checks["undefined_source_refs"]=sorted(refs-declared)
checks["duplicate_labels"]=[k for k,v in Counter(labels(new)).items() if v>1]
def numeric_rows(table):
    rows=[]
    for line in table.splitlines():
        cells=line.split("&")
        if len(cells)<2: continue
        nums=[]
        for cell in cells[1:]:
            cell=cell.strip().rstrip("\\").strip().strip("{}")
            if re.fullmatch(r"-?\d+(?:\.\d+)?",cell): nums.append(Decimal(cell))
        if nums: rows.append((cells[0].strip(),nums))
    return rows
ot=blocks(old,"table");st=blocks(sup,"table")
expected=[]
for index in [3,4]:
    rows=dict(numeric_rows(ot[index]))
    selected=[rows[k] for k in [r"$t_1$",r"$\Delta t$",r"$t_{\rm end}$",r"$q_{\max}$",r"$J$",r"$I_{t_{\rm cum}}$"]]
    expected += [list(x) for x in zip(*selected)]
actual=[values for label,values in numeric_rows(st[0]) if label.startswith("$")]
checks["S1_transpose_values"]={"numeric_cells":sum(map(len,actual)),"unchanged":actual==expected}
checks["S2_initial_values"]={"unchanged":[v for _,v in numeric_rows(st[1])]==[v for _,v in numeric_rows(ot[6])]}
original_eta=[line for line in ot[8].splitlines() if re.match(r"\s+\d+\s*&",line)]
expected=[[Decimal(line.split("&")[j].strip().rstrip("\\").strip()) for j in [1,6,4,5,7,8]] for line in original_eta]
actual=[]
for line in st[2].splitlines():
    if re.match(r"0\.\d+\s*&",line):
        actual.append([Decimal(cell.strip().rstrip("\\").strip()) for cell in line.split("&")])
checks["S3_selected_columns"]={"numeric_cells":sum(map(len,actual)),"unchanged":actual==expected}
QA.mkdir(exist_ok=True)
(QA/"source_integrity.json").write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding="utf-8")
for src,name in [
(ROOT/"archive_unused/generated_snapshots/scenario1_threshold_landscape_current_run/output_csv/main_c0_summary.csv","baseline_c0_full.csv"),
(ROOT/"archive_unused/generated_snapshots/scenario1_threshold_landscape_current_run/output_csv/main_eta_summary.csv","baseline_eta_full.csv"),
(ROOT/"archive_unused/generated_snapshots/xian_control_comparison_main/xian_eta_sensitivity.csv","xian_eta_full.csv"),
(ROOT/"archive_unused/generated_snapshots/xian_control_comparison_main/xian_control_comparison_summary.csv","strategy_summary_full.csv"),
(ROOT/"archive_unused/fit_method_comparison/fit_method_summary.csv","initial_fit_full.csv")]:
    shutil.copy2(src,HERE/"data"/name)
aux=read(LATEX/"flatten_curve_analysis_cn.aux")
positions={k:(n,p) for k,n,p in re.findall(r"\\newlabel\{([^}]+)\}\{\{([^}]+)\}\{([^}]+)\}",aux)}
fmap=[
(1,"fig:model_schematic","保留"),(2,"fig:scenario1:single-sim","保留图文件及显示尺寸"),
(3,"fig:s1:lambda-sensitivity","移到拐点分析"),(4,None,"删除正文浮动体；原图与源数据保留"),
(5,"fig:s1:inflection-scan","移到拐点分析"),("6、7","fig:baseline:q-joint","合并为 1×2，移入敏感性分析"),
(8,"fig:scenario1_summary_c0","保留图文件、显示尺寸及作者图注"),(9,"fig:scenario1_summary_eta","保留图文件、显示尺寸及作者图注"),
(10,"fig:scenario1_heatmaps_c0_eta","保留图文件和显示尺寸，移入敏感性分析"),
("11、12 的日新增面板","fig:xian:observed-fit","观测—重构 1×2"),
("12 的其余面板、13、14","fig:xian:strategy-process","全过程 5 面板"),
(15,"fig:xian_eta_sens","保留；明确时间参照的含义"),(16,"fig:xian_heatmaps","保留"),
("17、18",None,"移除重复图，保留数值与初值条件区分"),
(19,"fig:dom","保留，检查人口下界与区域遮罩"),
("20、21","fig:dom:levers","合并 2×2，全部五个人口规模保留"),
(22,"fig:panel_N_decomp","移入附录 A"),(23,"fig:c0-panel","保留并修正图注交叉指代"),
(24,"fig:c0-phase","Stationary curve；重排等值线标签"),
("25、26、27","fig:dom:critical-cases","合并为附录 3×2"),
(28,"fig:c0-scan","保留附录"),(29,"fig:c0-beta-existence","保留附录")]
lines=["# 图号对应（以实际 aux 编号为准）","","| 原图 | 新图 / 页 | 操作 |","|---|---|---|"]
for oldn,key,action in fmap:
    dest=(f"{positions[key][0]} / p{positions[key][1]}" if key else "—")
    lines.append(f"| {oldn} | {dest} | {action} |")
(HERE/"old_to_new_figures.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
lines=["# 表号对应","","| 原表 | 去向 | 内容 |","|---|---|---|",
"| 1、2 | 主表 1 | 四类控制量的导数符号及依据；原完整表保存在 before |",
"| 3 | 第 6 节正文 | 基准参数、状态、时间、控制强度、峰值和数值误差；完整表保存在 before |",
"| 4、5 | 补充表 S1 | 两组参数实验；完整输出含 S*、Sc 见 data/baseline_*_full.csv |",
"| 6 | 主表 2 | 十项参数及初值，并保留文献来源 |",
"| 7 | 补充表 S2 | 保留原显示值，交代初值拟合与事件积分的数值差异 |",
"| 8、10 | 主表 3 | 三策略的四项比较量，TDINN 精细参照放表注；完整成本分项保存于 data/strategy_summary_full.csv |",
"| 9 | 补充表 S3 | 六列阈值敏感性；完整九列及原输出见 data/xian_eta_full.csv 和 before |",
"| 11 | 主表 4 | 五项人口界值；原中间阈值与上下界保存在 before 中的完整表 |"]
(HERE/"old_to_new_tables.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
# 对全部页面生成渲染图；接触表只用于定位，细节仍检查单页。
for base in ["flatten_curve_analysis_cn","flatten_curve_supplement_cn"]:
    doc=fitz.open(LATEX/(base+".pdf"))
    folder=QA/"final_render"/base
    folder.mkdir(exist_ok=True,parents=True)
    pages=[]
    for i,page in enumerate(doc):
        pix=page.get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False)
        path=folder/f"page_{i+1:02}.png";pix.save(path)
        pages.append(path)
    for i in range(0,len(pages),4):
        imgs=[]
        for p in pages[i:i+4]:
            img=Image.open(p).convert("RGB");img.thumbnail((720,1019));imgs.append(img)
        canvas=Image.new("RGB",(1440,2090),"#ddd");draw=ImageDraw.Draw(canvas)
        for j,img in enumerate(imgs):
            x=(j%2)*720;y=(j//2)*1045
            draw.text((x+10,y+2),f"{base} p{i+j+1}",fill="black")
            canvas.paste(img,(x,y+22))
        canvas.save(folder/f"sheet_{i//4+1:02}.png")
    print(base,len(doc),"pages")
print(json.dumps(checks,ensure_ascii=False,indent=2))
# 审计必须对应最终图文件，不能复用重排前的结果。
skill=Path.home()/".codex/skills/nature-figure/scripts"
result=subprocess.run([sys.executable,str(skill/"validate_figure.py"),str(HERE/"plot_revisions.py"),"--json"],capture_output=True,text=True,encoding="utf-8")
(QA/"plot_source_audit.json").write_text(result.stdout,encoding="utf-8")
for pdf in sorted((LATEX/"figures/revision_v4").glob("*.pdf")):
    result=subprocess.run([sys.executable,str(skill/"audit_pdf_text.py"),str(pdf),"--min-pt","5","--json"],capture_output=True,text=True,encoding="utf-8")
    (QA/(pdf.stem+".text.json")).write_text(result.stdout,encoding="utf-8")
    assert result.returncode==0,result.stdout
    result=subprocess.run([sys.executable,str(skill/"audit_figure_collisions.py"),str(pdf),"--json-out",str(QA/(pdf.stem+".collisions.json"))],capture_output=True,text=True,encoding="utf-8")
    print(pdf.name,result.stdout.split("summary:")[-1].strip())
    assert result.returncode==0,result.stdout
    (QA/(pdf.stem+".sha256")).write_text(digest(pdf)+"\n",encoding="ascii")

