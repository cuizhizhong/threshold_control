"""NEW-4al（AGENTS.md N40）：隔离比例两个记号调换后，重绘图内含这两个记号的四幅图。

记号调换：能力上限 q_cap → q_max；仅隔离控制在 t1 跳升到的隔离比例 q_max → q_1。
图内只改坐标轴文字，其余画法、数据与版式不变：
- 正文图 5（fig:joint:capacity）：plot_new4p_figures.capacity_baseline，纵轴 $q_{\\rm cap}$ → $q_{\\max}$；
- 正文图 8（fig:xian:joint）：plot_new4w_figures.main8，纵轴 $q_{\\rm cap}$ → $q_{\\max}$；
- 补充图 S1（fig:scenario1_summary_c0）、S2（fig:sup:eta-summary）：preview_style_curves.metric_summaries，
  面板 (d) 纵轴 $q_{\\max}$ → $q_1$。
做法：调用原绘图函数，在原 rc 设置下先按原参数保存未改字的图，核对与现入稿图件逐字节相同（证明本次重画与原图一致），
再只替换上述文字后另存到 paper/figures/new4al/。不求解模型、不重算任何数据；原图件与历史收据只读。

运行（仓库根目录；原图件由不同环境生成，须用对应环境复现）：
  E:/anaconda/envs/thesis/python.exe -X utf8 nr_audit/plot_new4al_notation.py fig:joint:capacity fig:xian:joint
  E:/anaconda/python.exe -X utf8 nr_audit/plot_new4al_notation.py fig:scenario1_summary_c0 fig:sup:eta-summary
输出：paper/figures/new4al/{joint_capacity_baseline,Main8,S1,S2}.pdf，收据 results/new4al_notation.json。
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.text import Text

import plot_new4p_figures as P4
import plot_new4w_figures as W
import plot_xian_fig2_style as F2
import preview_style_curves as SC
import preview_style_common as PC
from audit_common import ROOT, RESULTS, git_head

OUT = ROOT / 'paper/figures/new4al'
TMP = ROOT / 'paper/tmp/new4al'
RECEIPT = RESULTS / 'new4al_notation.json'
OLD_CAP, NEW_CAP = r'$q_{\rm cap}$', r'$q_{\max}$'
OLD_MAX, NEW_MAX = r'$q_{\max}$', r'$q_1$'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_sha(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def fonts(path):
    return sorted(set(f.decode() for f in re.findall(rb'/BaseFont\s*/([A-Za-z0-9+\-]+)', Path(path).read_bytes())))


def texts(fig):
    return [t.get_text() for t in fig.findobj(Text) if t.get_visible() and t.get_text()]


def relabel(fig, old, new):
    hits = [t for t in fig.findobj(Text) if t.get_text() == old]
    assert hits, f'图中没有 {old}'
    for t in hits:
        t.set_text(new)
    assert old not in texts(fig)
    return len(hits)


def finish(fig, name, current_rel, old, new, savefig_kw, draw_first=False):
    """在调用者的 rc 设置下：未改字的重画须与现入稿图件逐字节相同，再改字另存。"""
    TMP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    if draw_first:
        fig.canvas.draw()
    repro = TMP / f'{name}_reproduced.pdf'
    fig.savefig(repro, **savefig_kw)
    before = texts(fig)                      # 保存后刻度文字已生成
    current = ROOT / current_rel
    assert sha(repro) == sha(current), f'{name}：未改字的重画与现入稿图件不同，不能只改文字'
    n = relabel(fig, old, new)
    if draw_first:
        fig.canvas.draw()
    pdf = OUT / f'{name}.pdf'
    fig.savefig(pdf, **savefig_kw)
    fig.savefig(TMP / f'{name}.png', dpi=200)
    after = texts(fig)
    assert [t for t in before if t != old] == [t for t in after if t != new]
    rec = dict(current_pdf=current_rel, current_pdf_sha256=sha(current), reproduced_sha256=sha(repro),
               reproduced_identical=True, pdf=pdf.relative_to(ROOT).as_posix(), pdf_sha256=sha(pdf),
               text_change=dict(old=old, new=new, count=n), other_texts_unchanged=True,
               fonts=fonts(pdf), size_mm=[round(float(v) / F2.MM, 2) for v in fig.get_size_inches()],
               environment=dict(python=sys.version.split()[0], matplotlib=matplotlib.__version__))
    assert rec['fonts'] and all(re.search(r'cm(r|mi|sy|ex)10', f, re.I) for f in rec['fonts']), rec['fonts']
    plt.close(fig)
    return rec


def capacity_baseline():
    with plt.rc_context(F2.RC):
        fig, _ = P4.capacity_baseline()
        return finish(fig, 'joint_capacity_baseline', 'paper/figures/new4p/joint_capacity_baseline.pdf',
                      OLD_CAP, NEW_CAP, dict(dpi=400, metadata={'CreationDate': None, 'ModDate': None}))


def main8():
    w3 = json.loads((W.W3 / 'xian_theta001.json').read_text(encoding='utf-8'))
    assert w3['precheck']['ok']
    box = {}
    original_save = W.save

    def capture(fig, name):
        assert name == 'Main8'
        box['rec'] = finish(fig, 'Main8', 'paper/figures/new4w/Main8.pdf', OLD_CAP, NEW_CAP,
                            dict(dpi=600, metadata={'CreationDate': None, 'ModDate': None}))
        return box['rec']['pdf_sha256']

    W.save = capture
    try:
        W.main8(w3)
    finally:
        W.save = original_save
    return box['rec']


def metric_summary(name, number, by_eta):
    box = {}
    original_save = SC.save

    def capture(fig, fig_name, checks, inputs, old_pdf):
        assert fig_name == number
        box['inputs'] = inputs
        box['rec'] = finish(fig, number, f'paper/figures/new4t/{number}.pdf', OLD_MAX, NEW_MAX,
                            dict(dpi=600, metadata={'CreationDate': None, 'ModDate': None}), draw_first=True)
        return box['rec']

    SC.save = capture
    try:
        with plt.rc_context(PC.RC):
            SC.metric_summaries(name, number, by_eta)
    finally:
        SC.save = original_save
    box['rec']['source_inputs'] = box['inputs']
    return box['rec']


JOBS = {
    'fig:joint:capacity': capacity_baseline,
    'fig:xian:joint': main8,
    'fig:scenario1_summary_c0': lambda: metric_summary('c0_sensitivity_selected_eta', 'S1', False),
    'fig:sup:eta-summary': lambda: metric_summary('eta_sensitivity_selected_c0', 'S2', True),
}


def main(selected):
    """原图件由不同环境生成：图 5、图 8 用 thesis 环境（Python 3.10），S1、S2 用 base 环境（Python 3.12）。
    分两次运行、各选对应的图，收据按图合并；每幅图都须先通过逐字节复现检查。"""
    out = json.loads(RECEIPT.read_text(encoding='utf-8')) if RECEIPT.exists() else {}
    inputs = {}
    for p in [*P4.INPUTS[:5], *W.INPUTS[:3]]:
        inputs[p.relative_to(ROOT).as_posix()] = dict(sha256=sha(p), content_sha256=text_sha(p))
    figures = out.get('figures', {})
    for key in selected:
        figures[key] = JOBS[key]()
    out.update(script='nr_audit/plot_new4al_notation.py', git_head=git_head(), authorization='AGENTS.md N40（NEW-4al）',
               notation={'q_cap': 'q_max（能力上限）', 'q_max': 'q_1（仅隔离控制在 t1 跳升到的隔离比例）'},
               scientific_activity=dict(ode_solves=0, optimization_solves=0, fits=0, classification_solves=0),
               inputs=inputs, figures=dict(sorted(figures.items())))
    RECEIPT.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: dict(pdf=figures[k]['pdf'], change=figures[k]['text_change'], env=figures[k]['environment'])
                      for k in selected}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main(sys.argv[1:] or list(JOBS))
