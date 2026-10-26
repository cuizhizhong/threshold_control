"""NEW-4o：按正文图 2（fig:scenario1:single-sim，MATLAB 导出）的风格重绘正文图 8 与补充图 S11。

图 8（fig:xian:strategy-process）为西安参数下三种策略的全过程，图 S11（fig:xian_eta_sens）为仅隔离控制随 eta/N 的扫描。
只读 reproducibility/results/20261003_release_final/xian/ 的既有数据（使用前记录原字节 SHA-256），不重算、不改数据；
面板布局、坐标尺度与范围沿用原图（restore_figures.xian 与 xian_control_comparison.plot_eta_sensitivity），只改字体、字号、配色与线型。

图 2 的样式取自 code/scenario1_q_control_with_quarantine_panels.m：
- LaTeX 字体（Computer Modern），面板上方居中标题，图例带黑框，坐标框四边封闭、刻度朝内；
- 蓝色实线为仅隔离阈值控制，黑色点划线为常规控制，红色虚线为阈值参照，黑色点线标记 t1、t2（参照线透明度 0.7）；
- 图 2 导出后在正文中缩至 0.7 倍版心宽，MATLAB 字号与线宽折算到印刷尺寸约为原值的 0.50 倍。这里按印刷尺寸直接设定：
  刻度 5.5 pt、轴标签 6.5 pt、标题 7 pt、图例 5 pt、t1/t2 标注 5.5 pt；主曲线 1.5 pt、对照线 1.0 pt、竖线 0.6 pt。
图 8 中 TDINN 控制取图 2 配色中的绿色，观测数据为黑色空心圆；图 S11 中 TDINN 参照线用同一绿色虚线，t_end 取图 2 的品红。

运行：python nr_audit/plot_xian_fig2_style.py。输出 paper/figures/new4o/*.pdf、paper/tmp/new4o/*.png（预览，不入库）
与 results/new4o_xian_figures.json。
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
from matplotlib.transforms import blended_transform_factory

from audit_common import ROOT, dump

SRC = ROOT / 'reproducibility' / 'results' / '20261003_release_final' / 'xian'
INPUTS = ['timeseries.csv', 'observed.csv', 'summary.csv', 'eta_scan.csv', 'reference.json']
OUT = ROOT / 'paper' / 'figures' / 'new4o'
PREVIEW = ROOT / 'paper' / 'tmp' / 'new4o'
MM = 1 / 25.4
TEXT_WIDTH_PT = 452.9679          # 主稿与补充材料的版心宽（elegantpaper，A4 左右各 1 in）

STYLE = dict(tick=5.5, label=6.5, title=7.0, legend=5.0, note=5.5,
             lw_main=1.5, lw_ref=1.0, lw_vline=0.6, lw_axes=0.4, ref_alpha=0.7)
BLUE, BLACK, RED = (0.0, 0.0, 1.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)
GREEN, MAGENTA, GRAY = (0.0, 0.55, 0.08), (1.0, 0.0, 1.0), (0.55, 0.55, 0.55)

RC = {
    'font.family': 'serif', 'font.serif': ['cmr10'], 'mathtext.fontset': 'cm',
    'axes.unicode_minus': False, 'axes.formatter.use_mathtext': True, 'pdf.fonttype': 42,
    'font.size': STYLE['tick'], 'axes.labelsize': STYLE['label'], 'axes.titlesize': STYLE['title'],
    'xtick.labelsize': STYLE['tick'], 'ytick.labelsize': STYLE['tick'], 'legend.fontsize': STYLE['legend'],
    'axes.linewidth': STYLE['lw_axes'], 'axes.titlepad': 3.0, 'axes.labelpad': 2.0,
    'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'xtick.major.size': 2.5, 'ytick.major.size': 2.5, 'xtick.minor.size': 1.4, 'ytick.minor.size': 1.4,
    'xtick.major.width': STYLE['lw_axes'], 'ytick.major.width': STYLE['lw_axes'],
    'xtick.minor.width': 0.3, 'ytick.minor.width': 0.3, 'xtick.major.pad': 2.0, 'ytick.major.pad': 2.0,
    'legend.frameon': True, 'legend.fancybox': False, 'legend.edgecolor': 'k', 'legend.framealpha': 1.0,
    'legend.borderpad': 0.35, 'legend.handlelength': 2.2, 'legend.labelspacing': 0.25,
    'legend.handletextpad': 0.5, 'legend.borderaxespad': 0.6,
}

STRATEGIES = {   # 原数据中的策略名 → 图 8 的图例与画法
    '情景一阈值控制': dict(label='Threshold control', color=BLUE, ls='-', lw=STYLE['lw_main'], zorder=3),
    '常规控制': dict(label='Routine control', color=BLACK, ls='-.', lw=STYLE['lw_ref'], zorder=4),
    'TDINN控制': dict(label='TDINN control', color=GREEN, ls='-', lw=STYLE['lw_main'], zorder=3),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frame_legend(leg):
    leg.get_frame().set_linewidth(STYLE['lw_axes'])
    return leg


def vline(ax, t, color, label=None, y=0.05, side='right'):
    """竖点线；label 按图 2 标在线旁（side 为文字相对竖线的一侧，y 为轴坐标高度），避开曲线。"""
    ax.axvline(t, color=color, lw=STYLE['lw_vline'], ls=':', alpha=STYLE['ref_alpha'], zorder=1)
    if label:
        tr = blended_transform_factory(ax.transData, ax.transAxes)
        dx, ha = (2.5, 'left') if side == 'right' else (-2.5, 'right')
        ax.text(t + dx, y, label, transform=tr, fontsize=STYLE['note'], ha=ha, va='bottom')


def strategy_process():
    ts = pd.read_csv(SRC / 'timeseries.csv')
    obs = pd.read_csv(SRC / 'observed.csv')
    sm = pd.read_csv(SRC / 'summary.csv').set_index('strategy')
    assert set(ts.strategy.unique()) == set(STRATEGIES), ts.strategy.unique()
    thr = sm.loc['情景一阈值控制']
    t1, t2, eta = float(thr['t1']), float(thr['t2']), float(thr['eta'])
    t_obs_end = float(obs.t.iloc[-1])
    xend = float(ts.t.max())

    fig = plt.figure(figsize=(135 * MM, 125 * MM))
    gs = fig.add_gridspec(3, 2, left=.105, right=.985, bottom=.075, top=.955, wspace=.30, hspace=.52)
    axes = [fig.add_subplot(gs[0, :]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1]),
            fig.add_subplot(gs[2, 0]), fig.add_subplot(gs[2, 1])]
    record = {}
    for name, st in STRATEGIES.items():
        sub = ts[ts.strategy == name]
        ys = [sub.I, sub.c, sub.q, sub.Cc + sub.Cq, sub.Rt]
        for ax, y in zip(axes, ys):
            ax.plot(sub.t, y, color=st['color'], ls=st['ls'], lw=st['lw'], zorder=st['zorder'])
        record[st['label']] = dict(points=int(len(sub)), t_last=float(sub.t.iloc[-1]),
                                   I_max=float(sub.I.max()), Itcum_last=float((sub.Cc + sub.Cq).iloc[-1]))
    for ax in axes:
        vline(ax, t_obs_end, GRAY)
    # 标注位置：(c) 上移以避开 q0 处的水平线；(e) 的 t1 标在竖线左侧，避开 t1 之后下降的两条曲线
    for i, y1, side1, y2 in ((0, .05, 'right', .05), (1, .05, 'right', .05), (2, .12, 'right', .12),
                             (4, .05, 'left', .05)):
        vline(axes[i], t1, BLACK, r'$t_1$', y=y1, side=side1)
        vline(axes[i], t2, BLACK, r'$t_2$', y=y2)
    titles = [r'(a) $I$', r'(b) $c(t)$', r'(c) $q(t)$', r'(d) $I_{t_{\rm cum}}$', r'(e) $R_e$']
    ylabels = [r'$I(t)$', r'$c(t)$', r'$q(t)$', r'$I_{t_{\rm cum}}(t)$', r'$R_e(t)$']
    for ax, title, ylabel in zip(axes, titles, ylabels):
        ax.set_xlim(0, xend)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
    for ax in axes[3:]:
        ax.set_xlabel(r'$t$')
    axes[0].set_yscale('log')
    axes[0].set_ylim(1, 1.08 * ts.I.max())
    axes[0].axhline(eta, color=RED, lw=STYLE['lw_ref'], ls='--', alpha=STYLE['ref_alpha'], zorder=2)
    axes[3].set_yscale('symlog', linthresh=100)
    axes[3].set_ylim(0, 1.15 * (ts.Cc + ts.Cq).max())
    axes[3].scatter(obs.t, obs.total_cum, s=4, facecolors='none', edgecolors=BLACK, linewidths=0.4, zorder=6)
    axes[4].set_ylim(0, max(1.2, 1.08 * ts.Rt.max()))
    axes[4].axhline(1, color=RED, lw=STYLE['lw_ref'], ls='--', alpha=STYLE['ref_alpha'], zorder=2)
    handles = [Line2D([], [], color=st['color'], ls=st['ls'], lw=st['lw'], label=st['label'])
               for st in STRATEGIES.values()]
    handles += [Line2D([], [], ls='none', marker='o', ms=2.4, mfc='none', mec=BLACK, mew=0.4, label='Observed data'),
                Line2D([], [], color=RED, ls='--', lw=STYLE['lw_ref'], alpha=STYLE['ref_alpha'], label=r'$\eta$')]
    # 三列图例放在 eta 线上方的空白处，不遮挡参照线
    frame_legend(axes[0].legend(handles=handles, loc='upper right', ncol=3, columnspacing=1.0))
    frame_legend(axes[4].legend(handles=[Line2D([], [], color=RED, ls='--', lw=STYLE['lw_ref'],
                                                alpha=STYLE['ref_alpha'], label=r'$R_e=1$')], loc='upper right'))
    checks = dict(t1=t1, t2=t2, eta=eta, t_obs_end=t_obs_end, observed_points=int(len(obs)), strategies=record,
                  # 时间序列是离散采样，其最大值与汇总表峰值只差采样误差
                  peak_rel_diff_vs_summary={STRATEGIES[n]['label']: float(ts[ts.strategy == n].I.max()
                                                                          / sm.loc[n, 'peak_I'] - 1)
                                            for n in STRATEGIES})
    checks['peak_matches_summary'] = {k: abs(v) < 1e-4 for k, v in checks['peak_rel_diff_vs_summary'].items()}
    return fig, checks


def eta_sensitivity():
    sc = pd.read_csv(SRC / 'eta_scan.csv')
    ref = json.loads((SRC / 'reference.json').read_text(encoding='utf-8'))
    td = next(r for r in ref['strategies'] if r['strategy'] == 'TDINN控制')
    x = 100.0 * sc.eta_fraction.to_numpy()
    width_in = 0.7 * TEXT_WIDTH_PT / 72.0
    fig, axes = plt.subplots(2, 2, figsize=(width_in, 84 * MM))
    fig.subplots_adjust(left=.125, right=.985, bottom=.115, top=.94, wspace=.36, hspace=.42)
    ax_q, ax_j, ax_cum, ax_time = axes.ravel()
    line = dict(color=BLUE, lw=STYLE['lw_main'], marker='o', ms=2.6, mew=0)
    ref_line = dict(color=GREEN, lw=STYLE['lw_ref'], ls='--', alpha=STYLE['ref_alpha'], label='TDINN')
    ax_q.plot(x, sc.q_start, label=r'$q_c(t_1)$', **line)
    ax_j.plot(x, sc.J, label=r'$J$', **line)
    ax_j.axhline(float(td['J']), **ref_line)
    ax_cum.plot(x, sc.cum_total_infections, label=r'$I_{t_{\rm cum}}$', **line)
    ax_cum.axhline(float(td['cum_total_infections']), **ref_line)
    ax_time.plot(x, sc.control_duration, label=r'$\Delta t$', **line)
    ax_time.plot(x, sc.clear_time, color=MAGENTA, lw=STYLE['lw_main'], marker='s', ms=2.4, mew=0,
                 label=r'$t_{\rm end}$')
    ax_time.axhline(float(td['clear_time']), **ref_line)
    for ax in (ax_j, ax_cum, ax_time):
        ax.set_yscale('log')
    titles = [r'(a) $q_c(t_1)$', r'(b) $J$', r'(c) $I_{t_{\rm cum}}$', r'(d) $\Delta t$, $t_{\rm end}$']
    ylabels = [r'$q_c(t_1)$', r'$J$', r'$I_{t_{\rm cum}}$', 'time (days)']
    locs = ['upper right', 'upper right', 'center right', 'upper right']
    for ax, title, ylabel, loc in zip(axes.ravel(), titles, ylabels, locs):
        ax.set_xscale('log')
        ax.set_xlim(float(x.min() * 0.84), float(x.max() * 1.18))
        ax.set_xticks([0.01, 0.1, 1.0])
        ax.set_xticklabels(['0.01', '0.1', '1'])
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        frame_legend(ax.legend(loc=loc))
    for ax in (ax_cum, ax_time):
        ax.set_xlabel(r'$\eta/N$ (%)')
    checks = dict(scan_points=int(len(sc)), eta_percent=[float(v) for v in x],
                  tdinn=dict(J=float(td['J']), cum_total_infections=float(td['cum_total_infections']),
                             clear_time=float(td['clear_time'])))
    return fig, checks


def embedded_fonts(path):
    return sorted(set(re.findall(rb'/BaseFont\s*/([A-Za-z0-9+\-]+)', path.read_bytes())))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    inputs = {f'{SRC.relative_to(ROOT).as_posix()}/{n}': sha256(SRC / n) for n in INPUTS}
    outputs, checks = {}, {}
    with plt.rc_context(RC):
        for name, fn in (('xian_strategy_process', strategy_process), ('xian_eta_sensitivity', eta_sensitivity)):
            fig, chk = fn()
            pdf = OUT / f'{name}.pdf'
            fig.savefig(pdf, metadata={'CreationDate': None, 'ModDate': None})
            fig.savefig(PREVIEW / f'{name}.png', dpi=300)
            plt.close(fig)
            outputs[pdf.relative_to(ROOT).as_posix()] = dict(
                sha256=sha256(pdf), size_mm=[round(float(v) / MM, 2) for v in fig.get_size_inches()],
                fonts=[f.decode() for f in embedded_fonts(pdf)])
            checks[name] = chk
    assert all(re.search(r'cm(r|mi|sy|ex)10', f, re.I) for o in outputs.values() for f in o['fonts']), outputs
    dump('new4o_xian_figures.json', dict(script='nr_audit/plot_xian_fig2_style.py', style_reference='code/scenario1_q_control_with_quarantine_panels.m',
                                         style=STYLE, inputs_sha256=inputs, outputs=outputs, checks=checks))
    print(json.dumps(dict(outputs=outputs), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
