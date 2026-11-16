"""NEW-4at（N48）：删去显式控制族的收据。只登记身份，不做任何计算。

记录经作者授权从稿件中删去的陈述、条目与标签，存档源文件 S4_explicit_control.tex 的内容哈希，表 1、表 3 删去的
alpha = 0.5 一行及其去向，以及图 4 的新旧图件（新图见 results/new4at_fig4.json）。源文件、旧图与历史收据原样保留。

运行：python nr_audit/new4at_scope_receipt.py（先运行 plot_new4at_fig4.py）
"""
import hashlib
import json
import re
from pathlib import Path

from text_identity import content_sha256

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'nr_audit/results/new4at_scope.json'
MAIN = 'paper/flatten_curve_analysis_cn.tex'
SUPP = 'paper/flatten_curve_supplement_cn.tex'
ARCHIVED = 'paper/supplement_sections/S4_explicit_control.tex'

REMOVED_STATEMENTS = ['thm:joint:explicit', 'thm:joint:comparison(ii)：显式族的控制时长随 alpha 严格递减']
REMOVED_LABELS = sorted(['sec:sup:explicit', 'thm:joint:explicit', 'eq:joint:explicit-S', 'eq:joint:explicit-duration',
                         'eq:joint:explicit-zero', 'eq:joint:explicit-c', 'eq:joint:explicit-q'])
REMOVED_ROWS = {
    'tab:joint:compare': dict(row='显式族 $\\alpha=0.5$ & 9.24 & 37.11 & 323.4 & 346.2 & 2.55 & 1.64',
                              source='reproducibility/results/20261005_sec7_v2_refinement/joint_extra/compare_baseline.csv（strategy=alpha_0.5）'),
    'tab:xian:joint-compare': dict(row='显式族 $\\alpha=0.5$ & 250.01 & 468.70 & 2.556 & 7.776 & 89.88 & 3.32',
                                   source='nr_audit/results/new4w/xian_theta001.json（laws.alpha）'),
}


def sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def input_files(main):
    text = (ROOT / main).read_text(encoding='utf-8')
    names = re.findall(r'^\\input\{((?:sections|appendices|supplement_sections)/[^}]+)\}', text, flags=re.M)
    return [main] + [f'paper/{n}.tex' for n in names]


def main():
    files = {m: input_files(m) for m in (MAIN, SUPP)}
    assert ARCHIVED not in files[SUPP]
    current = ''.join((ROOT / f).read_text(encoding='utf-8') for fs in files.values() for f in fs)
    assert not [lab for lab in REMOVED_LABELS if lab in current]
    assert '\\alpha=0.5' not in current and '显式族' not in current and '显式控制族' not in current
    fig4 = json.loads((ROOT / 'nr_audit/results/new4at_fig4.json').read_text(encoding='utf-8'))
    receipt = dict(
        authorization='AGENTS.md N48（NEW-4at）', pre_cut_tag='pre-explicit-cut-20261116', base_commit='fa7787a',
        scientific_activity=dict(ode_solves=0, optimization_solves=0, fits=0, redraws=1),
        current_inputs=files,
        archived_source=dict(path=ARCHIVED, content_sha256=content_sha256((ROOT / ARCHIVED).read_bytes()),
                             note='原样保留，不再由补充主文件 \\input；恢复时加回该行、导言中的指引句与第 4.2 节'),
        removed_statements=REMOVED_STATEMENTS, removed_labels=REMOVED_LABELS, removed_table_rows=REMOVED_ROWS,
        figure4=dict(superseded=fig4['superseded'], current=list(fig4['outputs'])[0],
                     current_sha256=next(iter(fig4['outputs'].values()))['sha256']),
        macro_changes={'\\nrConvTolMaxRel': dict(old='3\\times10^{-12}', new='2\\times10^{-12}',
                                                 reason='收敛宏不再计入两组参数的 alpha = 0.5')})
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(f'写出 {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
