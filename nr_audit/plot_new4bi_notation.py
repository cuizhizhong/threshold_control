"""NEW-4bi（AGENTS.md N63）：权重界限 r_cont 改记 r_* 后，重绘图内含该记号的补充图 S5（fig:sup:phase-detail）。

图内只改图例中的一条文字 $r_{\\rm cont}$ → $r_*$，其余画法、数据与版式不变。
做法同 NEW-4al（plot_new4al_notation.py）：调用原绘图函数 preview_style_heatmaps.preview_s6，在原 rc 设置下
先按原参数保存未改字的图，核对与现入稿图件 paper/figures/new4t/S6.pdf 逐字节相同，再只替换该文字后另存到
paper/figures/new4bi/S6.pdf。preview_s6 只读已登记的缓存（plot_figure7 的 DATA、NPZ 与 new4d_cost_structure.json，
使用前校验），不分类、不求解；原图件与历史收据只读。

运行（仓库根目录）：
  E:/anaconda/python.exe -X utf8 nr_audit/plot_new4bi_notation.py
输出：paper/figures/new4bi/S6.pdf，收据 results/new4bi_notation.json。
"""
import json
import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

import preview_style_heatmaps as H
import plot_new4al_notation as AL
from audit_common import ROOT, RESULTS, git_head

AL.OUT = ROOT / 'paper/figures/new4bi'
AL.TMP = ROOT / 'paper/tmp/new4bi'
RECEIPT = RESULTS / 'new4bi_notation.json'
OLD, NEW = r'$r_{\rm cont}$', r'$r_*$'
CURRENT = 'paper/figures/new4t/S6.pdf'


def s6():
    box = {}
    original_save = H.save

    def capture(fig, name, checks, inputs, old_pdf):
        assert name == 'S6'
        box['inputs'] = inputs
        box['checks'] = dict(new_classifications=checks['new_classifications'],
                             new_background_solves=checks['new_background_solves'],
                             new_ode_solves=checks['new_ode_solves'],
                             cache_validation_passed=checks['cache_validation_passed'])
        box['rec'] = AL.finish(fig, 'S6', CURRENT, OLD, NEW,
                               dict(dpi=600, metadata={'CreationDate': None, 'ModDate': None}), draw_first=True)
        return box['rec']

    H.save = capture
    try:
        H.preview_s6()
    finally:
        H.save = original_save
    rec = box['rec']
    rec['source_inputs'] = box['inputs']
    rec['source_checks'] = box['checks']
    return rec


def main():
    rec = s6()
    out = dict(script='nr_audit/plot_new4bi_notation.py', git_head=git_head(), authorization='AGENTS.md N63（NEW-4bi）',
               notation={'r_cont': 'r_*（连续结构的权重界限）', 'c_TDINN, q_TDINN': 'c_D, q_D（只在正文式 7.1，不涉及图件）'},
               scientific_activity=dict(ode_solves=0, optimization_solves=0, fits=0, classification_solves=0),
               figures={'fig:sup:phase-detail': rec})
    RECEIPT.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(pdf=rec['pdf'], change=rec['text_change'], env=rec['environment']), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
