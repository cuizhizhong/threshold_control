"""NEW-4ap（N44）：删去能力约束的收据。只登记身份，不做计算。

记录经作者授权从稿件中删去的陈述、标签与图，被取代图件的 SHA-256，图 8 的新旧文件，以及本轮新增与改值的数字宏。
图件文件、计算代码与历史收据都原样保留；本脚本只读取它们的字节。图 8 剖面的新增计算在 plot_new4ap_fig8.py。

运行（先运行 plot_new4ap_fig8.py 与 make_numbers.py）：python nr_audit/new4ap_scope_receipt.py
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'nr_audit/results/new4ap_scope.json'
MAIN = 'paper/flatten_curve_analysis_cn.tex'
SUPP = 'paper/flatten_curve_supplement_cn.tex'

REMOVED_FIGURES = {
    'joint_capacity_baseline': dict(label='fig:joint:capacity', pdf='paper/figures/new4al/joint_capacity_baseline.pdf',
                                    former_tex='paper/sections/06_numerics.tex'),
}
REPLACED_FIGURES = {
    'Main8': dict(label='fig:xian:joint', old_pdf='paper/figures/new4al/Main8.pdf', new_pdf='paper/figures/new4ap/Main8.pdf',
                  tex='paper/sections/07_xian.tex', receipt='nr_audit/results/new4ap_fig8.json'),
}
REMOVED_STATEMENTS = ['cor:joint:feasibility', 'cor:joint:capped-comparison', 'cor:joint:single-endpoints',
                      'cor:joint:capacity-clip', 'cor:joint:allocation-range']
REMOVED_ITEMS = ['prop:joint:global-structure(iv)', 'prop:joint:terminal-allocation(iii)', 'prop:joint:minimum-threshold(ii)']
REMOVED_LABELS = sorted(REMOVED_STATEMENTS + [
    'eq:joint:allocation-range', 'eq:joint:bounds', 'eq:joint:capacity-clip', 'eq:joint:capped-duration',
    'eq:joint:feasibility', 'fig:joint:capacity', 'sec:joint:capacity-numerics'])
# 引言第 4 段描述 Avram 等工作的“受干预能力限制”保留；S_c^{+} 是极限记号，故只查 c^{+}(S)、c^{-}(S)
REMOVED_TERMS = ['能力约束', '不限制干预能力', '干预能力有限', '能力代表点', r'\mathcal A(\eta;', 'c^{+}(S)', 'c^{-}(S)',
                 r'c_{\min}', r'q_{\max}', r'\jointcapacitypostexitdays']
NEW_MACROS = ['\\nrXianWtFourSwitch', '\\nrXianWtFourCutPct', '\\nrXianWtTenCutPct', '\\nrXianWtTenStartQ']
CHANGED_MACROS = {'\\nrConvPlateauMax': ['4.6\\times10^{-9}', '1.3\\times10^{-9}'],
                  '\\nrConvExitMax': ['1.8\\times10^{-7}', '3.8\\times10^{-8}']}


def sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def input_files(main):
    text = (ROOT / main).read_text(encoding='utf-8')
    names = re.findall(r'^\\input\{((?:sections|appendices|supplement_sections)/[^}]+)\}', text, flags=re.M)
    return [main] + [f'paper/{n}.tex' for n in names]


def main():
    files = {m: input_files(m) for m in (MAIN, SUPP)}
    current = ''.join((ROOT / f).read_text(encoding='utf-8') for fs in files.values() for f in fs)
    assert not [lab for lab in REMOVED_LABELS if f'\\label{{{lab}}}' in current or f'{{{lab}}}' in current]
    assert not [t for t in REMOVED_TERMS if t in current], [t for t in REMOVED_TERMS if t in current]
    macros = {m['macro']: m['display'] for m in
              json.loads((ROOT / 'nr_audit/results/nr_numbers_map.json').read_text(encoding='utf-8'))['macros']}
    assert all(m in macros for m in NEW_MACROS)
    assert all(macros[m] == v[1] for m, v in CHANGED_MACROS.items())
    receipt = dict(
        authorization='AGENTS.md N44（NEW-4ap）', pre_cut_tag='pre-capacity-cut-20261115', base_commit='b1522b5',
        scientific_activity=dict(ode_solves=0, fits=0, phase_background_recomputed=False,
                                 new_computation='图 8(b)(c) 五个权重的逐状态剖面，见 nr_audit/results/new4ap_fig8.json'),
        current_inputs=files,
        removed_figures={k: dict(v, pdf_sha256=sha(v['pdf'])) for k, v in REMOVED_FIGURES.items()},
        replaced_figures={k: dict(v, old_pdf_sha256=sha(v['old_pdf']), new_pdf_sha256=sha(v['new_pdf']))
                          for k, v in REPLACED_FIGURES.items()},
        removed_statements=REMOVED_STATEMENTS, removed_items=REMOVED_ITEMS, removed_labels=REMOVED_LABELS,
        removed_terms=REMOVED_TERMS, new_macros=NEW_MACROS, changed_macros=CHANGED_MACROS,
        convergence_note='收敛宏不再计入 new4w/convergence.json 中 kind=cap、capacity=true 的两组能力代表点，结果文件不改')
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(f'写出 {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
