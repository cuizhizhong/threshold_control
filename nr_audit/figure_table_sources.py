"""按正式tex环境建立图表映射；历史报告、标量核验与本轮重绘分开登记。"""
import csv
import hashlib
import json
import re
import subprocess
from audit_common import ROOT, RESULTS

D='reproducibility/results/20261003_release_final'
E='reproducibility/results/20261005_sec7_v2_refinement/joint_extra'
A='nr_audit/results'
L='git:pipeline-final-20261006:latex/revision_layout_v5'
H='pipeline-final-20261006:reproducibility/release_reports/20261005_sec7_v2_refinement/collection/run_1/validation/figure_generation.json'

# 输入数据有独立CSV/NPZ时列实际数据；公式驱动轨迹列源入口及参数，不把PDF当作输入证据。
FIG={
'fig:model_schematic':('reproducibility/assets/SIQR模型示意图_复现修正版.pptx','reproducibility/figures.py:_export_model'),
'fig:scenario1:single-sim':('code/scenario1_q_control_with_quarantine_panels.m:参数与轨迹方程','code/scenario1_q_control_with_quarantine_panels.m'),
'fig:scenario1_summary_eta':(f'{D}/baseline/landscape_summary.csv;{D}/baseline/eta_sensitivity_c0_10.csv','nr_audit/plot_new4r_tradeoff.py'),
'fig:sup:eta-summary':(f'{D}/baseline/eta_sensitivity_c0_10.csv;{D}/baseline/main_eta_summary.csv',f'{L}/layout_matlab.m'),
'fig:scenario1_summary_c0':(f'{D}/baseline/c0_sensitivity_selected_eta.csv;{D}/baseline/main_c0_summary.csv',f'{L}/layout_matlab.m'),
'fig:joint:compare':(f'{E}/trajectories_baseline.csv;{E}/compare_baseline.csv;{E}/input_manifest.json','nr_audit/plot_new4s_figures.py:joint_compare'),
'fig:joint:capacity':(f'{E}/capacity_baseline.npz;{E}/capacity.json;{E}/capacity_traj_baseline.csv;{E}/input_manifest.json','nr_audit/plot_new4p_figures.py:capacity_baseline'),
'fig:joint:phase':(f'{A}/new4d_cost_structure.json;nr_audit/allocation.py;nr_audit/params.py','nr_audit/plot_figure7_contour.py；NEW-4p版面：nr_audit/plot_new4p_figures.py:phase_baseline'),
'fig:xian:joint':(f'{E}/capacity_xian.npz;{E}/capacity.json;{A}/new4d_figure7.json;{A}/new4d_figure7.npz','nr_audit/plot_new4p_figures.py:xian_joint'),
'fig:sup:phase-detail':(f'{E}/phase_baseline.npz;{E}/phase_xian.npz;{E}/phase.json;{A}/weight_brackets.json;{A}/new_figure7.json;{A}/new_figure7.npz;{A}/new4d_cost_structure.json','nr_audit/plot_figure7_detail.py'),
'fig:joint:frontier':(f'{E}/frontier_baseline.csv;{E}/alpha_family_baseline.csv','reproducibility/joint_extra/figures.py:fig_duration'),
'fig:xian:observed-fit':(f'{D}/xian/observed.csv;{D}/xian/timeseries.csv;{D}/xian/fit.json;真实数据/Xianguankong.xlsx','nr_audit/plot_new4p_figures.py:observed_fit'),
'fig:xian:strategy-process':(f'{D}/xian/timeseries.csv;{D}/xian/observed.csv;{D}/xian/summary.csv;{E}/trajectories_xian.csv;{E}/input_manifest.json','nr_audit/plot_new4p_figures.py:strategy_process'),
'fig:baseline:q-joint':(f'{D}/baseline/main_c0_summary.csv;{D}/baseline/main_eta_summary.csv;scenario1_threshold_landscape/common/compute_trajectory.m',f'{L}/layout_matlab.m'),
'fig:scenario1_heatmaps_c0_eta':(f'{D}/baseline/landscape_summary.csv','scenario1_threshold_landscape/scripts/plot_heatmaps.m'),
'fig:s1:lambda-sensitivity':('scenario1_inflection/inflection_analysis.py:解析式;scenario1_inflection/fig_lambda_sensitivity.py:BASE与specs','scenario1_inflection/fig_lambda_sensitivity.py'),
'fig:s1:inflection-scan':('scenario1_inflection/inflection_analysis.py:解析式;scenario1_inflection/fig_scan_t.py:base与sweeps','scenario1_inflection/fig_scan_t.py'),
'fig:xian_eta_sens':(f'{D}/xian/eta_scan.csv;{D}/xian/reference.json',f'{L}/layout_python.py'),
'fig:xian_heatmaps':(f'{D}/xian/heatmap.csv;{D}/xian/reference.json',f'{L}/layout_python.py'),
'fig:c0-panel':(f'{D}/c0/timeseries.csv;{D}/c0/representative_summary.csv;{D}/c0/parameters.json',f'{L}/layout_python.py'),
'fig:c0-scan':(f'{D}/c0/scan.csv;{D}/c0/extended_scan.csv;{D}/c0/cumulative_curve.csv;{D}/c0/extrema.json','reproducibility/c0.py:run_c0'),
'fig:c0-phase':(f'{D}/c0/phase.npz;{D}/c0/parameters.json',f'{L}/layout_python.py'),
'fig:c0-beta-existence':(f'{D}/c0/beta_existence.npz;{D}/c0/parameters.json','reproducibility/c0.py:run_c0'),
}
TAB={
'tab:xian_initial_fit':('joint_control/threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json;'+f'{D}/xian/reference.json;{D}/xian/fit.json','nr_audit/sources.py'),
'tab:joint:compare':(f'{E}/compare_baseline.csv;{A}/regression.json','nr_audit/audit_baseline.py'),
'tab:xian:joint-compare':(f'{E}/compare_xian.csv;{A}/regression.json','nr_audit/audit_baseline.py'),
'tab:xian_summary':(f'{D}/xian/summary.csv;{D}/xian/reference.json;{A}/regression.json','nr_audit/audit_baseline.py'),
'tab:sensitivity':('paper/appendices/A_proofs_sensitivity.tex:解析导数与证明;paper/supplement_sections/S2_single_control.tex:prop:contact-effects;paper/supplement_sections/S3_inflection.tex:prop:s1:lambda-sensitivity','nr_audit/theory_checks.py'),
'tab:sup:baseline':(f'{D}/baseline/main_c0_summary.csv;{D}/baseline/main_eta_summary.csv;{D}/baseline/representative_cases.csv','nr_audit/audit_baseline.py'),
'tab:sup:fit':(f'{A}/fit_reconstruction.json;真实数据/Xianguankong.xlsx','nr_audit/audit_fit.py'),
'tab:sup:initial':(f'{D}/xian/S2_window.csv;{D}/xian/S2_difference.json;{A}/fit_reconstruction.json','nr_audit/audit_fit.py'),
'tab:sup:ic':(f'{A}/initial_condition.json','nr_audit/audit_initial_condition.py'),
'tab:sup:eta':(f'{D}/xian/eta_scan.csv;{A}/regression.json','nr_audit/audit_baseline.py'),
'tab:sup:convergence':(f'{A}/convergence.json','nr_audit/audit_convergence.py'),
'tab:joint:weight-transitions':(f'{A}/weight_brackets.json','nr_audit/audit_weights.py'),
'tab:sup:return:cinf':(f'{A}/noreturn_inf_crosscheck.json','nr_audit/audit_noreturn_inf.py'),
'tab:sup:return:term':(f'{A}/return_import.json;r7_return/results/r7_3_exponential_return.json','nr_audit/import_return_numbers.py'),
}


def main():
    history=json.loads(subprocess.check_output(['git','show',H],cwd=ROOT))
    bylabel={r['label']:r for r in history['figures']}
    rows=[]
    for folder in ('sections','appendices','supplement_sections'):
        for file in sorted((ROOT/'paper'/folder).glob('*.tex')):
            text=file.read_text(encoding='utf-8')
            for match in re.finditer(r'\\begin\{(figure|table)\*?\}([\s\S]*?)\\end\{\1\*?\}',text):
                kind,body=match.group(1),match.group(2)
                labels=re.findall(r'\\label\{([^}]+)\}',body)
                if not labels:
                    raise ValueError(f'图表缺标签: {file}')
                label=labels[0]
                inputs,entry=(FIG if kind=='figure' else TAB)[label]
                artifact=''
                same=None
                status='历史/NR标量依据已定位；本轮未全量重算'
                if kind=='figure':
                    inc=re.search(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',body).group(1)
                    candidate=ROOT/'paper'/inc
                    if not candidate.exists(): candidate=ROOT/'paper/figures'/inc
                    if not candidate.exists(): raise FileNotFoundError(candidate)
                    artifact=candidate.relative_to(ROOT).as_posix()
                    old=bylabel.get(label)
                    same=bool(old and hashlib.sha256(candidate.read_bytes()).hexdigest()==old['file_sha256'])
                    status='历史生成报告PDF字节匹配；本轮未重绘' if same else 'R7-a改图；入口已定位，不能沿用旧PDF身份'
                    if label=='fig:joint:phase' and (RESULTS/'new4d_figure7.json').exists():
                        inputs+=';nr_audit/results/new4d_figure7.json;nr_audit/results/new4d_figure7.npz'
                        status='NEW-4d逐状态精确求解与重绘（等高线相图与基准剖面）；见new4d_figure7.json'
                    if label=='fig:sup:phase-detail':
                        status='NEW-4d由NEW-2已验证缓存重绘局部加密面板并叠加闭式点；见new4d_figure7_detail_render.json'
                    if artifact.startswith('paper/figures/new4p/'):
                        status='NEW-4p只读既有数据按图2风格重绘（相图复用NEW-4d缓存）；见new4p_figures.json'
                    if artifact.startswith('paper/figures/new4r/'):
                        status='NEW-4r只读既有基准扫描按图2风格绘制阈值取舍图；见new4r_tradeoff.json'
                    if artifact.startswith('paper/figures/new4s/'):
                        status='NEW-4s只读既有轨迹按图2风格重绘；见new4s_figures.json'
                rows.append(dict(labels='|'.join(labels),kind=kind,tex=file.relative_to(ROOT).as_posix(),
                    artifact=artifact,inputs=inputs,generation_or_audit_entry=entry,
                    historical_report=H if kind=='figure' else 'nr_audit/results/regression.json或所列理论/专项结果',
                    old_pdf_hash_matches=same,status=status))
    assert len(rows)==27,(len(rows),rows)      # NEW-4r：正文 9 图 5 表，补充 8 图 5 表
    with open(RESULTS/'figure_table_sources.csv','w',encoding='utf-8-sig',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    receipt=dict(formal_figures=sum(r['kind']=='figure' for r in rows),
        formal_tables=sum(r['kind']=='table' for r in rows),
        historical_pdf_matches=sum(r['old_pdf_hash_matches'] is True for r in rows),
        historical_source=H,historical_visual_review_not_claimed=True)
    (RESULTS/'new_figure_table_mapping_summary.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(receipt)


if __name__=='__main__':
    main()
