"""NEW-4r：正文图 3（fig:scenario1_summary_eta）改为阈值取舍图，按正文图 2 的风格绘制（样式取自 plot_xian_fig2_style.py）。

基准参数下的仅隔离控制：横轴为总累计新增感染，(a) 纵轴为控制时长，(b) 纵轴为成本 J，纵轴均为线性刻度；
c0 = 5, 8, 10, 12 各一条曲线（颜色区分），沿 eta/N ∈ [0.2%, 5%] 变化；eta/N = 0.2%, 0.5%, 1%, 2%, 5% 处的点
用标记形状区分（c0 = 5 的曲线与其他曲线交错，以形状而非连线标识同一阈值）。
只读 reproducibility/results/20261003_release_final/baseline/ 的既有扫描（使用前记录原字节 SHA-256），不求解模型。
c0 = 10 的曲线另与同目录 eta_sensitivity_c0_10.csv 逐点核对；收据记录正文 3.4 节所用数字与各 c0 曲线间的相对差。

运行：python nr_audit/plot_new4r_tradeoff.py。输出 paper/figures/new4r/threshold_tradeoff.pdf、
paper/tmp/new4r/threshold_tradeoff.png（预览，不入库）与 results/new4r_tradeoff.json。
"""
import hashlib
import json
import re

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import plot_xian_fig2_style as F2
from audit_common import ROOT, dump

SRC = ROOT / 'reproducibility' / 'results' / '20261003_release_final' / 'baseline'
INPUTS = ['landscape_summary.csv', 'eta_sensitivity_c0_10.csv']
OUT = ROOT / 'paper' / 'figures' / 'new4r'
PREVIEW = ROOT / 'paper' / 'tmp' / 'new4r'
MM, STYLE = F2.MM, F2.STYLE
C0 = (5, 8, 10, 12)
COLORS = (F2.GREEN, F2.MAGENTA, F2.BLUE, F2.BLACK)                # 图 2 的配色；基准 c0 = 10 用图 2 主曲线的蓝色
MARKS = (0.2, 0.5, 1.0, 2.0, 5.0)                                 # 标点的 eta/N（%）
SHAPES = ('o', 's', '^', 'D', 'v')                                # 依次对应 MARKS
ETA_RANGE = (0.2, 5.0)
WIDTH_FRAC = 0.9


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def curves():
    d = pd.read_csv(SRC / 'landscape_summary.csv')
    d = d[d.valid == 1]
    out = {}
    for c0 in C0:
        s = d[np.isclose(d.c0, c0)].sort_values('eta_percent')
        s = s[(s.eta_percent >= ETA_RANGE[0] - 1e-9) & (s.eta_percent <= ETA_RANGE[1] + 1e-9)]
        out[c0] = s.reset_index(drop=True)
    return out


def spread(cs, col):
    """各 c0 曲线在共同的累计感染区间上，col 的最大相对差（对数插值）。"""
    lo = max(s.I_t_cum.min() for s in cs.values())
    hi = min(s.I_t_cum.max() for s in cs.values())
    x = np.linspace(lo, hi, 200)
    v = np.array([np.exp(np.interp(x, s.I_t_cum, np.log(s[col]))) for s in cs.values()])
    return dict(itcum_range=[float(lo), float(hi)], max_rel_spread=float(np.max(v.max(0) / v.min(0) - 1)))


def threshold_tradeoff():
    cs = curves()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_FRAC * F2.TEXT_WIDTH_PT / 72, 58 * MM))
    fig.subplots_adjust(left=.085, right=.985, bottom=.17, top=.9, wspace=.28)
    for ax, col, ylabel, title in ((axes[0], 'Delta_t', r'$\Delta t$', '(a) Control duration'),
                                   (axes[1], 'J', r'$J$', '(b) Intervention cost')):
        for (c0, s), color in zip(cs.items(), COLORS):
            ax.plot(s.I_t_cum, s[col], color=color, lw=STYLE['lw_ref'] + .2, zorder=3, label=f'$c_0={c0}$')
            for m, shape in zip(MARKS, SHAPES):
                r = s[np.isclose(s.eta_percent, m)].iloc[0]
                ax.plot(r.I_t_cum, r[col], shape, ms=3.2, mfc=color, mec='k', mew=.4, zorder=4)
        ax.set_ylim(bottom=0)
        ax.set_xlim(160, 355)
        ax.set_xlabel(r'Total cumulative new infections $I_{t_{\rm cum}}$')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
    F2.frame_legend(axes[0].legend(loc='upper right'))
    marks = [Line2D([], [], ls='none', marker=shape, ms=3.2, mfc=(.8, .8, .8), mec='k', mew=.4, label=f'{m:g}%')
             for m, shape in zip(MARKS, SHAPES)]
    F2.frame_legend(axes[1].legend(handles=marks, loc='upper right', title=r'$\eta/N$', title_fontsize=STYLE['legend']))
    ref = pd.read_csv(SRC / 'eta_sensitivity_c0_10.csv').sort_values('eta_percent')
    s10 = cs[10]
    m10 = s10.merge(ref, on='eta_percent', suffixes=('', '_ref'))
    pick = lambda m, c: float(s10.loc[np.isclose(s10.eta_percent, m), c].iloc[0])
    checks = dict(
        points_per_c0={c0: int(len(s)) for c0, s in cs.items()},
        c0_10_vs_eta_scan=dict(matched=int(len(m10)),
                               max_rel_diff={c: float(np.max(np.abs(m10[c] / m10[c + '_ref'] - 1)))
                                             for c in ('Delta_t', 'J', 'I_t_cum')}),
        text_numbers=dict(dt_02=pick(.2, 'Delta_t'), dt_2=pick(2, 'Delta_t'), itcum_02=pick(.2, 'I_t_cum'),
                          itcum_2=pick(2, 'I_t_cum'), J_02=pick(.2, 'J'), J_2=pick(2, 'J'),
                          tend_02=pick(.2, 't_end'), tend_2=pick(2, 't_end')),
        spread_across_c0=dict(J=spread(cs, 'J'), Delta_t=spread(cs, 'Delta_t')))
    return fig, checks


def embedded_fonts(path):
    return sorted(set(re.findall(rb'/BaseFont\s*/([A-Za-z0-9+\-]+)', path.read_bytes())))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    inputs = {f'{SRC.relative_to(ROOT).as_posix()}/{n}': sha(SRC / n) for n in INPUTS}
    with plt.rc_context(F2.RC):
        fig, checks = threshold_tradeoff()
        pdf = OUT / 'threshold_tradeoff.pdf'
        fig.savefig(pdf, metadata={'CreationDate': None, 'ModDate': None})
        fig.savefig(PREVIEW / 'threshold_tradeoff.png', dpi=300)
        size = [round(float(v) / MM, 2) for v in fig.get_size_inches()]
        plt.close(fig)
    out = {pdf.relative_to(ROOT).as_posix(): dict(sha256=sha(pdf), size_mm=size,
                                                  fonts=[f.decode() for f in embedded_fonts(pdf)])}
    assert all(re.search(r'cm(r|mi|sy|ex)10', f, re.I) for o in out.values() for f in o['fonts']), out
    dump('new4r_tradeoff.json', dict(script='nr_audit/plot_new4r_tradeoff.py', style_module='nr_audit/plot_xian_fig2_style.py',
                                     style=STYLE, inputs_sha256=inputs, outputs=out, checks=checks))
    print(json.dumps(dict(outputs=out, checks=checks), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
