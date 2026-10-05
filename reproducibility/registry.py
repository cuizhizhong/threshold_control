"""全文图表、理论与数字的来源清单。

清单把供应方记录、静态定位、本机计算和图件再生成分别记录。
含数字的陈述被定位不等于逐项对账；没有独立对账记录的数字保持待核对。
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


PACKAGE="joint_control/threshold_control_reproducible_release_20261002"
BASELINE={"N":763,"S0":762,"I0":1,"beta":.155,"gamma":.3504,
          "delta_q":.3504,"c0":10,"q0":.01526}

# 这里只声明本项目新入口可运行；历史文件列为科学来源，不作隐式运行入口。
RUNTIME=["reproducibility/run_all.py","reproducibility/run_all.ps1",
         "reproducibility/joint.py","reproducibility/xian.py",
         "reproducibility/population.py","reproducibility/c0.py",
         "reproducibility/figures.py","reproducibility/matlab_stage.m",
         "reproducibility/joint_extra/run.py","reproducibility/joint_extra/core.py",
         "reproducibility/joint_extra/figures.py","reproducibility/joint_extra/manuscript.py",
         "reproducibility/manuscript_version.py","reproducibility/postprocess_joint_extra.py",
         "reproducibility/run_selection.py"]
FIGURE_SOURCES={
 "fig:model_schematic":("schematic",["reproducibility/assets/SIQR模型示意图_复现修正版.pptx",
     "reproducibility/assets/model_s_to_sq.svg","reproducibility/assets/model_gamma.svg",
     "reproducibility/assets/model_delta_q.svg","reproducibility/assets/model_repair_source.json",
     "refs/SIQR模型示意图_Nature配色_可编辑.pptx"],{"role":"静态模型图及三处公式标签修复，不是数值结果输入"}),
 "fig:scenario1:single-sim":("baseline",["code/scenario1_q_control_with_quarantine_panels.m"],{"eta_fraction":.05}),
 "fig:baseline:q-joint":("baseline",["scenario1_threshold_landscape/common/q_control_tau.m","latex/revision_layout_v5/layout_matlab.m"],{"c0_values":[4,5,8,10,12],"eta_fractions":[.002,.006,.01,.02]}),
 "fig:scenario1_heatmaps_c0_eta":("baseline",["scenario1_threshold_landscape/scripts/generate_landscape_data.m","scenario1_threshold_landscape/scripts/plot_heatmaps.m"],{"grid_rows":28438}),
 "fig:s1:lambda-sensitivity":("inflection",["scenario1_inflection/fig_lambda_sensitivity.py","scenario1_inflection/inflection_analysis.py"],{"beta_q0_panel":[.10,.12,.155]}),
 "fig:s1:inflection-scan":("inflection",["scenario1_inflection/fig_scan_t.py","scenario1_inflection/inflection_analysis.py"],{"varied":["q0","beta","c0","eta_fraction"]}),
 "fig:scenario1_summary_c0":("baseline",["scenario1_threshold_landscape/common/compute_metrics.m","latex/revision_layout_v5/layout_matlab.m"],{"eta_fractions":[.002,.006,.01,.02]}),
 "fig:scenario1_summary_eta":("baseline",["scenario1_threshold_landscape/common/compute_metrics.m","latex/revision_layout_v5/layout_matlab.m"],{"c0_values":[5,8,10,12]}),
 "fig:xian:observed-fit":("xian",["真实数据/Xianguankong.xlsx","xian_control_comparison/xian_control_comparison.py"],{"window_days":40,"observation":"整数日累计增量"}),
 "fig:xian:strategy-process":("xian",["xian_control_comparison/xian_control_comparison.py"],{"eta_fraction":.002,"end":"各策略下降 I=1"}),
 "fig:xian_eta_sens":("xian",["xian_control_comparison/xian_control_comparison.py"],{"eta_fractions":[.0001,.0002,.0005,.001,.0015,.002,.003,.004,.005,.0075,.01]}),
 "fig:xian_heatmaps":("xian",["xian_control_comparison/threshold_landscape_analysis/threshold_landscape_analysis.py"],{"varied":["eta","c0"]}),
 "fig:dom":("population",["xian_dom/caliber.py","xian_dom/compute_B.py","xian_dom/dom_pretty.py"],{"varied":["N_eff","eta"]}),
 "fig:dom:levers":("population",["xian_dom/panels.py","latex/revision_style_restore/restore_figures.py"],{"left_N_eff":20000,"right_eta":100}),
 "fig:c0-panel":("c0",["c0_sensitivity/run_c0_sensitivity.py","latex/revision_style_restore/restore_figures.py"],{"N_eff":20000,"theta":.002}),
 "fig:c0-phase":("c0",["c0_sensitivity/run_c0_sensitivity.py","latex/revision_style_restore/restore_figures.py"],{"varied":["theta","c0"]}),
 "fig:panel_N_decomp":("population",["xian_dom/plot_B_decomp.py","xian_dom/caliber.py"],{"eta":100}),
 "fig:dom:critical-cases":("population",["xian_dom/panels.py","latex/revision_style_restore/restore_figures.py"],{"cases":"由新参照求三类临界有效人口"}),
 "fig:c0-scan":("c0",["c0_sensitivity/run_c0_sensitivity.py"],{"N_eff":20000,"theta":.002}),
 "fig:c0-beta-existence":("c0",["c0_sensitivity/run_c0_sensitivity.py"],{"theta":.002,"q0":.323,"varied":["c0","beta"]}),
 "fig:joint:compare":("joint_extra",["reproducibility/joint_extra/core.py","reproducibility/joint_extra/run.py","reproducibility/joint_extra/figures.py"],{"task":"A"}),
 "fig:joint:capacity":("joint_extra",["reproducibility/joint_extra/core.py","reproducibility/joint_extra/run.py","reproducibility/joint_extra/figures.py"],{"task":"B"}),
 "fig:joint:phase":("joint_extra",["reproducibility/joint_extra/core.py","reproducibility/joint_extra/run.py","reproducibility/joint_extra/figures.py"],{"task":"C"}),
 "fig:joint:frontier":("joint_extra",["reproducibility/joint_extra/core.py","reproducibility/joint_extra/run.py","reproducibility/joint_extra/figures.py"],{"task":"D"}),
}
TABLE_SOURCES={
 "tab:sensitivity":("theory",["scenario1_inflection/inflection_analysis.py","scenario1_inflection/verify_anchors.py"],["命题公式推导符号","数值偏导仅作交叉核对"]),
 "tab:xian_initial_fit":("xian",["真实数据/Xianguankong.xlsx","reproducibility/xian.py"],["xian/fit.json","xian/reference.json"]),
 "tab:xian_summary":("xian",["reproducibility/xian.py"],["xian/summary.csv","xian/diagnostics.json"]),
 "tab:dom:thresholds":("population",["reproducibility/population.py","xian_dom/caliber.py"],["population/critical.json","population/arcs.csv"]),
 "tab:sup:baseline":("baseline",["scenario1_threshold_landscape/common/compute_metrics.m"],["workspace/scenario1_threshold_landscape/current_run/output_csv/landscape_summary.csv"]),
 "tab:sup:initial":("xian",["真实数据/Xianguankong.xlsx","reproducibility/xian.py"],["xian/S2_difference.json","xian/fit.json","固定 I0=1 的40天窗口结果需另外逐项核对"]),
 "tab:sup:eta":("xian",["reproducibility/xian.py"],["xian/eta_scan.csv"]),
 "tab:joint:compare":("joint_extra",["reproducibility/joint_extra/core.py","reproducibility/joint_extra/run.py","reproducibility/joint_extra/manuscript.py"],["joint_extra/compare_baseline.csv","joint_extra/compare_xian.csv","joint_extra/validation.json"]),
}
NUMBER=re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def _load(path: Path):
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return None


def _sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def _relative(path: Path, root: Path):
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _braced(text: str, begin: int) -> tuple[str,int]:
    while begin<len(text) and text[begin]!="{":
        begin+=1
    if begin==len(text):
        return "",begin
    depth=1;position=begin+1
    while position<len(text) and depth:
        if text[position]=="{" and text[position-1]!="\\": depth+=1
        elif text[position]=="}" and text[position-1]!="\\": depth-=1
        position+=1
    return text[begin+1:position-1],position


def _contexts(text: str):
    events=[];section="";subsection=""
    for match in re.finditer(r"\\(section|subsection)\*?\{",text):
        title,_=_braced(text,match.end()-1)
        if match[1]=="section": section=title;subsection=""
        else: subsection=title
        events.append((match.start(),section,subsection))
    return events


def _context(events,offset):
    candidates=[x for x in events if x[0]<=offset]
    return {"section":candidates[-1][1],"subsection":candidates[-1][2]} if candidates else {"section":"","subsection":""}


def _blocks(text: str, kinds: str):
    pattern=re.compile(r"\\begin\{("+kinds+r")\}(.*?)\\end\{\1\}",re.S)
    return list(pattern.finditer(text))


def _source_record(root: Path,source: str):
    path=root/source
    return {"path":source,"exists":path.is_file(),"sha256":_sha(path)}


def _diagnostic(output: Path,family: str,approved_tasks=None):
    if family in ["baseline","inflection"]:
        data=_load(output/"validation/baseline_science.json")
        return bool(data and data.get("status")=="pass"),"validation/baseline_science.json"
    if family in ["xian","population","c0"]:
        data=_load(output/family/"diagnostics.json")
        return bool(data and data.get("passed")),family+"/diagnostics.json"
    if family=="joint_extra":
        data=_load(output/"joint_extra/validation.json")
        tasks=approved_tasks or ['A','B','C','D']
        return bool(data and all(data.get('tasks',{}).get(task,{}).get('passed') is True for task in tasks)),"joint_extra/validation.json"
    return False,None


def _status(local: bool,supplier: bool=True):
    return "reproduced" if local else "supplier" if supplier else "static"


def _numeric_inventory(text: str,doc: str):
    events=_contexts(text);rows=[];offset=0
    for line_number,line in enumerate(text.splitlines(keepends=True),1):
        clean=line.split("%",1)[0].strip()
        if clean and NUMBER.search(clean) and not clean.startswith(("\\includegraphics","\\setlength","\\documentclass","%!")):
            rows.append({"source":doc,"line":line_number,**_context(events,offset),
                "text":line.strip(),"numeric_tokens":NUMBER.findall(clean),
                "status":"located_pending_scalar_check","evidence":"仅定位，不等于实算或逐项对账。","passed":None})
        offset+=len(line)
    return rows


def build_registry(root: Path,output_dir: Path) -> dict:
    root,output=Path(root).resolve(),Path(output_dir).resolve()
    from manuscript_version import load_version
    version=load_version(root)
    diagnostic_for=lambda family:_diagnostic(output,family,version['approved_tasks'] if version else None)
    output.mkdir(parents=True,exist_ok=True)
    # 核查真正构建的输入；仅在没有本轮稿件时回退到正式稿或冻结稿。
    built=output/"document/latex/flatten_curve_analysis_cn.tex"
    staged=output/"manuscript/staged.tex"
    if built.is_file():
        main=built
        supplement=built.with_name("flatten_curve_supplement_cn.tex")
    elif staged.is_file():
        main=staged
        supplement=output/"manuscript/staged_supplement.tex"
    else:
        main=root/"latex/flatten_curve_analysis_cn.tex"
        if not main.is_file() or "thm:joint:cost-minimum" not in main.read_text(encoding="utf-8-sig"):
            main=root/PACKAGE/"latex/flatten_curve_analysis_cn.tex"
        supplement=main.with_name("flatten_curve_supplement_cn.tex")
    documents=[("main",main),("supplement",supplement)]
    sync=_load(output/"manuscript_changes.json") or {}
    cell_checks=sync.get("numerical_cells",[])
    figure_report=_load(output/"validation/figure_generation.json") or {}
    # 编号会随插图顺移，证据只按标签/相对资产路径绑定。
    generated={}
    for item in figure_report.get("figures",[]):
        if item.get('label'):
            generated[item['label']]=item
        file=item.get('file') or item.get('path')
        if file:
            path=Path(file)
            try:
                relative=path.resolve().relative_to((output/'figures').resolve()).as_posix()
            except ValueError:
                relative=path.as_posix().removeprefix('figures/')
            generated[relative]=item
    new_figures=_load(output/'joint_extra/figure_manifest.json') or {}
    for item in new_figures.get('figures',[]):
        if item.get('label'):
            generated[item['label']]=item
    figures=[];tables=[];equations=[];theory=[];numeric=[];sections=[]
    for role,path in documents:
        text=path.read_text(encoding="utf-8-sig")
        doc=_relative(path,root);events=_contexts(text)
        for offset,title,subtitle in events:
            sections.append({"source":doc,"line":text.count("\n",0,offset)+1,
                             "section":title,"subsection":subtitle,"status":"static"})
        for kind,target in [("figure",figures),("table",tables)]:
            for block in _blocks(text,kind):
                labels=re.findall(r"\\label\{([^}]+)\}",block[2])
                caption_match=re.search(r"\\caption\{",block[2])
                caption,_=_braced(block[2],caption_match.end()-1) if caption_match else ("",0)
                primary=labels[0] if labels else "missing_label"
                number=len(target)+1 if kind=="figure" else sum(x["document_role"]==role for x in target)+1
                context=_context(events,block.start())
                if kind=="figure":
                    family,sources,params=FIGURE_SOURCES.get(primary,("unmapped",[],{}))
                    image=re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}",block[2])
                    asset=generated.get(primary) or (generated.get(image[0].removeprefix('figures/')) if image else None)
                    inherited=bool(asset and (asset.get('inherited') or asset.get('status')=='inherited'))
                    has_asset=bool(asset and (family=='joint_extra' or inherited or not figure_report.get("historical_pickle_replay_used",True)))
                    science_pass,diagnostic=diagnostic_for(family)
                    if family=="schematic": science_pass=has_asset
                    local=has_asset and science_pass and not inherited
                    params={**BASELINE,**params} if family in ["baseline","inflection"] else params
                    extra={"image":image,"numeric_source_diagnostic":diagnostic,
                           "local_asset_regenerated":has_asset and not inherited,
                           "inherited_asset":inherited,
                           "scalar_anchors_status":"需与 numeric_statements/专门对账逐项对应",
                           "final_page_visual_review":"不由图件生成自动认证"}
                    artifacts=["figures/"+image[0].removeprefix("figures/")] if image else []
                else:
                    family,sources,artifacts=TABLE_SOURCES.get(primary,("unmapped",[],[]))
                    inherited=bool(sync.get('inherited_science',{}).get('used') and family not in {'joint_extra','theory','unmapped'})
                    # 有模块通过不意味着表中每个单元已与新值对账。
                    local=False;params={"caption":caption}
                    extra={"numeric_cells":[{"row":row.strip(),"tokens":NUMBER.findall(row)}
                        for row in block[2].splitlines() if "&" in row and NUMBER.search(row)],
                        "cell_reconciliation_status":"pending_individual_checks"}
                    if inherited:
                        extra.update(inherited_asset=True,cell_reconciliation_status='inherited_approved_table',
                                     reconciliation_scope='表体继承批准稿源；本轮不新计算旧表或宣称新增逐项收敛。')
                    diagnostic_pass,diagnostic=diagnostic_for(family)
                    extra.update({"local_numeric_source_available":diagnostic_pass,
                                  "numeric_source_diagnostic":diagnostic})
                    matched=[c for c in cell_checks if c.get("label")==primary and
                             c.get("document")==("main" if role=="main" else "supplement")]
                    if matched:
                        checked=all(c.get("passed") is True and c.get("new") in block[2] for c in matched)
                        local=checked
                        extra.update({"individual_cell_checks":matched,
                                      "cell_reconciliation_status":"fresh_cells_checked" if checked else "cell_check_failed",
                                      "reconciliation_scope":"列示来源绑定的数值单元；表头、定义及理论依据单独静态保留。"})
                        artifacts.append("manuscript_changes.json")
                    if primary=='tab:joint:compare':
                        fragments=[change for change in sync.get('changes',[]) if change.get('anchor')=='comparison']
                        exact=bool(len(fragments)==1 and block.group(0) in fragments[0]['new'])
                        local=diagnostic_pass and exact
                        extra.update(publication_fragment_exact=exact,
                                     cell_reconciliation_status='generated_from_current_csv' if local else 'pending',
                                     reconciliation_scope='新表由同轮两组四策略CSV的纯文案函数生成；验证记录与最终表体匹配。')
                        artifacts.append('manuscript_changes.json')
                    artifacts=[x for x in artifacts if not x.startswith(("命题","数值","固定"))]
                target.append({"id":("fig" if kind=="figure" else "table")+str(number),
                    "number":number,"document_role":role,"label":primary,"aliases":labels,
                    "caption":caption,"source_document":doc,"line":text.count("\n",0,block.start())+1,
                    **context,"family":family,"source":[_source_record(root,x) for x in sources],
                    "params":params,"command":{"entry":"reproducibility/run_all.ps1",
                        "template":"powershell -ExecutionPolicy Bypass -File reproducibility/run_all.ps1 -OutputDirectory <NEW_EMPTY_OUTPUT> -Matlab <MATLAB_FROM_PATH> -Repeats 2",
                        "python_template":"reproducibility/.venv/Scripts/python.exe -B reproducibility/run_all.py --output <NEW_EMPTY_OUTPUT> --matlab <MATLAB_FROM_PATH> --repeats 2",
                        "actual_output":str(output),"stage":family,
                        "precondition":"NEW_EMPTY_OUTPUT 必须尚不存在；运行时读取 PATH 中 MATLAB 的完整路径。"},
                    "artifacts":artifacts,"status":"static" if family=="theory" else 'inherited' if inherited else _status(local),
                    "evidence":{"static_located":True,"supplier_asset_present":True,
                        "local_module_executed":bool(diagnostic_for(family)[0]),
                        "local_asset_and_numeric_source_reproduced":local},
                    "passed":True if local else None,**extra})
        for block in _blocks(text,r"equation\*?|align\*?|gather\*?|multline\*?"):
            labels=re.findall(r"\\label\{([^}]+)\}",block[2])
            if labels:
                equations.append({"source":doc,"line":text.count("\n",0,block.start())+1,
                    "environment":block[1],"labels":labels,**_context(events,block.start()),
                    "status":"static","passed":None,"evidence":"公式位置及标签；数值测试不能替代证明。"})
        statements=_blocks(text,r"theorem|lemma|proposition|corollaryn|remarkn")
        proofs=_blocks(text,"proof")
        for index,block in enumerate(statements):
            next_position=statements[index+1].start() if index+1<len(statements) else len(text)
            proof=next((x for x in proofs if block.end()<=x.start()<next_position),None)
            theory.append({"source":doc,"line":text.count("\n",0,block.start())+1,
                "environment":block[1],"labels":re.findall(r"\\label\{([^}]+)\}",block[2]),
                **_context(events,block.start()),"proof_line":text.count("\n",0,proof.start())+1 if proof else None,
                "proof_end_line":text.count("\n",0,proof.end())+1 if proof else None,
                "status":"static","passed":None,"evidence":"定位已有论证；未认证完整数学证明。"})
        numeric.extend(_numeric_inventory(text,doc))
    joint=_load(output/"joint/results.json")
    anchor_checks=[]
    if joint:
        for strategy,field,expected in [("minimum_cost","cost","2.1183"),
            ("minimum_cost","duration","7.7536"),("quarantine_only","cost","2.2236"),
            ("contact_only","cost","11.9390"),("quarantine_only","duration","5.9026")]:
            row=next(x for x in joint["rows"] if x["strategy"]==strategy)
            anchor_checks.append({"id":"joint_"+strategy+"_"+field,
                "source":["reproducibility/joint.py",PACKAGE+"/numerics/joint_comparison.py"],
                "params":joint["parameters"],"command":{"entry":"reproducibility/joint.py","args":["--output-dir",str(output)]},
                "artifacts":["joint/results.json","joint/openloop_check.json"],
                "evidence":"本机实际完整类候选积分及预先时间开环，论文四位小数比较。",
                "expected_rounded":expected,"computed":row[field],"status":"reproduced",
                "passed":bool(joint.get("passed") and f'{row[field]:.4f}'==expected)})
    # 只收录在同步稿中找到新显示值的明确来源绑定，不以模块通过替代逐项对账。
    for change in sync.get("changes",[]):
        if change.get("unrounded_value") is None:
            continue
        role="main" if change.get("document")=="main" else "supplement"
        doc_path=dict(documents)[role]
        present=change["new"] in doc_path.read_text(encoding="utf-8-sig")
        anchor_checks.append({"id":"paper:"+change["anchor"],"source":[change["source"]],
            "params":{"document_role":role},"command":{"entry":"reproducibility/paper_sync.py","api":"prepare_manuscript"},
            "artifacts":["manuscript_changes.json"],"evidence":"来源绑定的替换记录和实际构建输入中的显示值。",
            "expected_rounded":change["new"],"computed":change["unrounded_value"],
            "status":"reproduced" if present else "local","passed":present,
            "scope":"仅本记录显示值；不自动覆盖该段其余数字。"})
    coverage={"figures":len(figures),"main_tables":sum(x["document_role"]=="main" for x in tables),
              "supplement_tables":sum(x["document_role"]=="supplement" for x in tables),
              "equation_groups":len(equations),"theorem_statements":len(theory),
              "numeric_statements_located":len(numeric)}
    if version:
        expected_figures=version['inventory']['main']['figures']
        structure_passed=([{'label':x['label'],'aliases':x['aliases'],'image':x['image'][0].removeprefix('figures/')} for x in figures]==expected_figures
                          and [x['label'] for x in tables if x['document_role']=='main']==[x['label'] for x in version['inventory']['main']['tables']]
                          and [x['label'] for x in tables if x['document_role']=='supplement']==[x['label'] for x in version['inventory']['supplement']['tables']])
    else:
        structure_passed=(coverage["figures"]==20 and coverage["main_tables"]==4 and coverage["supplement_tables"]==3)
    structure_passed=structure_passed and all(x['family']!='unmapped' for x in figures+tables)
    registry={"documents":[{"role":r,"source":_relative(p,root),"sha256":_sha(p),
                            "formal_target":"latex/"+("flatten_curve_analysis_cn.tex" if r=="main" else "flatten_curve_supplement_cn.tex")} for r,p in documents],
        "coverage":coverage,"structure_passed":structure_passed,"manuscript_version":version['version'] if version else 'frozen_20261002',
        "runtime_dependencies":RUNTIME,"sections":sections,"figures":figures,"tables":tables,
        "equations":equations,"theory_and_proof":theory,"key_numerical_checks":anchor_checks,
        "numeric_statements":numeric,
        "status_definition":{"static":"本轮定位/代码审阅","supplier":"供应方提供工程或记录，未当成本机实测",
            "inherited":"继承明确既有验收资产及哈希；本轮没有重算该旧图",
            "local":"本机已执行但尚未完成本项对账","reproduced":"本项已有明确本机复现证据"},
        "passed":structure_passed,
        "passed_scope":"仅结构覆盖完整；并不表示所有数值锚点、图表单元或数学证明通过。"}
    (output/"registry.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# 全文来源与复现清单","",f"覆盖：{coverage['figures']} 幅图、{coverage['main_tables']} 张正文表、{coverage['supplement_tables']} 张补充表。",
        f"另定位 {coverage['equation_groups']} 组编号公式、{coverage['theorem_statements']} 个理论陈述、{coverage['numeric_statements_located']} 行含数字陈述。",
        "","结构清单通过不代表所有数字对账完成。静态/供应方/本机执行/本机复现分开记录；未实算锚点保持待核对。","",
        "| 项目 | 标签 | 部分 | 状态 | 本机数值/图件证据 |","|---|---|---|---|---|"]
    for entry in figures+tables:
        caption=entry["caption"].replace("|","/").replace("\n"," ")[:65]
        prefix="图" if entry in figures else "表S" if entry["document_role"]=="supplement" else "表"
        lines.append(f"| {prefix}{entry['number']} {caption} | `{entry['label']}` | {entry['family']} | {entry['status']} | {', '.join(entry['artifacts'])} |")
    lines.extend(["","## 已明确核对的联合数值","","| 数字 | 本机结果 | 论文取整 | 状态 |","|---|---:|---:|---|"])
    for entry in anchor_checks:
        if entry['id'].startswith('joint_'):
            lines.append(f"| {entry['id']} | {entry['computed']:.14g} | {entry['expected_rounded']} | {'通过' if entry['passed'] else '未通过'} |")
    lines.extend(["","## 仍需逐项核对","","每个图注、表格数值单元及含数字正文行都保留位置和来源；详细项目见 JSON。",
                  "供应方历史锚点不是本机证据；理论/证明不因数值一致性而标通过。",
                  "SI S2 固定 I0=1 的40天窗口只依据其对应配置的单元核对记录，不能被拟合基准结果替代。"])
    (output/"registry.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return {"passed":structure_passed,"coverage":coverage,
            "artifacts":["registry.json","registry.md"],
            "unreconciled_numeric_statements":len(numeric),
            "note":"结构完整；未据此宣称全部数字通过。"}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    result=build_registry(args.root,args.output_dir)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result["passed"] else 1)
