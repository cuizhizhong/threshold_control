"""NEW-4w W4：西安设计阈值 η = 0.001N 下的图 8、图 9 与补充图 S8（N33）。

- 图 8（fig:xian:joint）：能力可行区域与成本权重相图。数据取自 results/new4w/ 下 W3 的输出
  （xian_capacity.npz、xian_phase.npz、xian_theta001.json）；画法与 NEW-4t 接收版相同：
  plot_new4p_figures.xian_joint 的版面，加 preview_supplement_style 的 parula 色带、红色点划等高线与色柱整理。
- 图 9（fig:xian:strategy-process）：四种策略的全过程。TDINN 与常规控制与 η 无关，取自冻结的
  reproducibility/results/20261003_release_final/xian/timeseries.csv；两种阈值控制取自 W3 的 xian_trajectories.csv。
  画法与 plot_new4p_figures.strategy_process 相同。
- 补充图 S8（fig:xian_heatmaps）：只把设计阈值参照线及其标注由 η = 26326（0.002N）移到 13163（0.001N），
  数据、色标、等高线与版式不变（复制 preview_style_heatmaps.preview_s8 的画法，参照值改为参数）。
输入在使用前登记 SHA-256；不求解模型。

运行（仓库根目录，先运行 new4w_xian_threshold.py）：python -X utf8 nr_audit/plot_new4w_figures.py
输出：paper/figures/new4w/{Main8,xian_strategy_process,S8}.pdf，PNG 预览写 paper/tmp/new4w/，收据写 results/new4w/figures.json。
"""
import hashlib
import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.collections import QuadMesh
from matplotlib.colors import LogNorm, Normalize
from matplotlib.lines import Line2D

import plot_new4p_figures as P
import plot_xian_fig2_style as F2
import preview_style_common as PC
import preview_style_heatmaps as H
from audit_common import ROOT, RESULTS, git_head

W3 = RESULTS / 'new4w'
FIG = ROOT / 'paper/figures/new4w'
PREVIEW = ROOT / 'paper/tmp/new4w'
XI = ROOT / 'reproducibility/results/20261003_release_final/xian'
INPUTS = [W3 / 'xian_theta001.json', W3 / 'xian_capacity.npz', W3 / 'xian_phase.npz', W3 / 'xian_trajectories.csv',
          XI / 'timeseries.csv', XI / 'observed.csv', XI / 'heatmap.csv', XI / 'reference.json']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    pdf = FIG / f'{name}.pdf'
    fig.savefig(pdf, dpi=600, metadata={'CreationDate': None, 'ModDate': None})
    fig.savefig(PREVIEW / f'{name}.png', dpi=200)
    plt.close(fig)
    return sha(pdf)


# ---------------------------------------------------------------- 图 8
def region_panel(ax, w3, title):
    with np.load(W3 / 'xian_capacity.npz') as d:
        u, q, region = d['u'], d['q'], d['region']
        bu, bq = d['boundary_u'], d['boundary_q']
        q_line, c_line = float(d['quarantine_line']), float(d['contact_line'])
    q0 = 0.323
    ax.pcolormesh(u, q, region, cmap=P.REGION_CMAP, vmin=-0.5, vmax=2.5, shading='auto', rasterized=True)
    for xs, ys in ((bu, bq), ([0, c_line], [q_line, q_line]), ([c_line, c_line], [q0, q_line])):
        ax.plot(xs, ys, color=P.BLACK, lw=P.STYLE['lw_vline'])
    cap = w3['capacity']
    ax.plot(cap['u_max'], cap['q_cap'], 'o', ms=3.6, color=P.RED, mec='white', mew=0.5, zorder=5)
    ax.set(xlim=(0, 1), ylim=(q0, 1))
    ax.set_xlabel(r'$1-c_{\min}/c_0$')
    ax.set_ylabel(r'$q_{\rm cap}$')
    ax.set_title(title)
    return dict(q_line=q_line, c_line=c_line, point=[cap['u_max'], cap['q_cap']])


def main8(w3):
    case = w3['phase']['case']
    with np.load(W3 / 'xian_phase.npz') as d:
        arrays = {k: d[k] for k in d.files}
    data = dict(cases=dict(xian=case))
    with plt.rc_context(PC.RC):
        fig = plt.figure(figsize=(P.TEXT_WIDTH_IN, 68 * P.MM))
        outer = fig.add_gridspec(1, 2, width_ratios=[1, 1.06], left=.075, right=.955, bottom=.15, top=.92, wspace=.24)
        right = outer[1].subgridspec(1, 2, width_ratios=[1, .045], wspace=.06)
        ax_r, ax_p, cax = fig.add_subplot(outer[0]), fig.add_subplot(right[0]), fig.add_subplot(right[1])
        chk = dict(capacity=region_panel(ax_r, w3, '(a) Feasible region'))
        pc, chk['phase'] = P.phase_panel(ax_p, data, arrays, 'xian', [(2.0, P.GRAY, ':')])
        ax_p.text(case['z_star'] - .1, 2.0 * 1.04, r'$r=2$', fontsize=P.STYLE['note'], color=(.3, .3, .3),
                  ha='left', va='bottom')
        ax_p.set_title('(b) Cost-optimal combination')
        P.colorbar(fig, pc, cax)
        # NEW-4t 接收版的样式：parula 色带，红色点划等高线、黑色数字，色柱只保留色带与刻度
        mesh = next(c for c in ax_p.collections if isinstance(c, QuadMesh))
        mesh.set_cmap(PC.palette())
        for c in ax_p.collections:
            if c is not mesh and hasattr(c, 'levels'):
                c.set_edgecolor(P.RED)
                c.set_linestyle('-.')
                c.set_linewidth(.6)
        for t in ax_p.texts:
            if t.get_text() in {f'0.{k}' for k in range(1, 10)}:
                t.set_color(P.BLACK)
                t.set_path_effects([])
            elif t.get_text() == r'$r=2$':
                t.set_color('white')
                t.set_path_effects([pe.withStroke(linewidth=.6, foreground='#222222', alpha=.7)])
        for line in list(cax.lines):
            line.remove()
        chk['pdf_sha256'] = save(fig, 'Main8')
    return chk


# ---------------------------------------------------------------- 图 9
def strategy_process(w3):
    ts = pd.read_csv(XI / 'timeseries.csv')
    obs = pd.read_csv(XI / 'observed.csv')
    nt = pd.read_csv(W3 / 'xian_trajectories.csv')
    curves = {}
    for name in ('常规控制', 'TDINN控制'):
        sub = ts[ts.strategy == name]
        curves[name] = (dict(F2.STRATEGIES[name]), sub.t, [sub.I, sub.c, sub.q, sub.Cc + sub.Cq, sub.Rt])
    qo = nt[nt.strategy == 'quarantine_only'].sort_values('t', kind='stable')
    mc = nt[nt.strategy == 'minimum_cost'].sort_values('t', kind='stable')
    st_q = dict(F2.STRATEGIES['情景一阈值控制'])
    st_q['label'] = 'Quarantine-only control'
    curves['仅隔离控制'] = (st_q, qo.t, [qo.I, qo.c, qo.q, qo.Ctotal, qo.Rt])
    opt = dict(label='Cost-optimal control', color=P.PURPLE, ls='--', lw=P.STYLE['lw_main'], zorder=5)
    curves['成本最优控制'] = (opt, mc.t, [mc.I, mc.c, mc.q, mc.Ctotal, mc.Rt])
    order = ['仅隔离控制', '常规控制', 'TDINN控制', '成本最优控制']        # 与 NEW-4p 图例顺序相同
    curves = {k: curves[k] for k in order}
    law = w3['laws']
    t1, t2, eta = law['q_only']['t1'], law['q_only']['t2'], w3['settings']['eta']
    t2_opt = law['opt']['t2']
    t_obs_end = float(obs.t.iloc[-1])
    xend = max(float(ts.t.max()), float(qo.t.max()), float(mc.t.max()))
    Imax = max(float(ts.I.max()), float(qo.I.max()), float(mc.I.max()))
    Cmax = max(float((ts.Cc + ts.Cq).max()), float(qo.Ctotal.max()), float(mc.Ctotal.max()))
    Rmax = max(float(ts.Rt.max()), float(qo.Rt.max()), float(mc.Rt.max()))
    with plt.rc_context(PC.RC):
        fig = plt.figure(figsize=(135 * P.MM, 125 * P.MM))
        gs = fig.add_gridspec(3, 2, left=.105, right=.985, bottom=.075, top=.955, wspace=.30, hspace=.52)
        axes = [fig.add_subplot(gs[0, :]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1]),
                fig.add_subplot(gs[2, 0]), fig.add_subplot(gs[2, 1])]
        for st, t, ys in curves.values():
            for ax, y in zip(axes, ys):
                ax.plot(t, y, color=st['color'], ls=st['ls'], lw=st['lw'], zorder=st['zorder'])
        for ax in axes:
            F2.vline(ax, t_obs_end, P.GRAY)
            ax.axvline(t2_opt, color=P.PURPLE, lw=P.STYLE['lw_vline'], ls=':', alpha=P.STYLE['ref_alpha'], zorder=1)
        for i, y1, side1, y2 in ((0, .05, 'right', .05), (1, .05, 'right', .05), (2, .12, 'right', .12),
                                 (4, .05, 'left', .05)):
            F2.vline(axes[i], t1, P.BLACK, r'$t_1$', y=y1, side=side1)
            F2.vline(axes[i], t2, P.BLACK, r'$t_2$', y=y2)
        titles = [r'(a) $I$', r'(b) $c(t)$', r'(c) $q(t)$', r'(d) $I_{t_{\rm cum}}$', r'(e) $R_e$']
        ylabels = [r'$I(t)$', r'$c(t)$', r'$q(t)$', r'$I_{t_{\rm cum}}(t)$', r'$R_e(t)$']
        for ax, title, ylabel in zip(axes, titles, ylabels):
            ax.set_xlim(0, xend)
            ax.set_title(title)
            ax.set_ylabel(ylabel)
        for ax in axes[3:]:
            ax.set_xlabel(r'$t$')
        axes[0].set_yscale('log')
        axes[0].set_ylim(1, 1.08 * Imax)
        axes[0].axhline(eta, color=P.RED, lw=P.STYLE['lw_ref'], ls='--', alpha=P.STYLE['ref_alpha'], zorder=2)
        axes[3].set_yscale('symlog', linthresh=100)
        axes[3].set_ylim(0, 1.15 * Cmax)
        axes[3].scatter(obs.t, obs.total_cum, s=4, facecolors='none', edgecolors=P.BLACK, linewidths=0.4, zorder=6)
        axes[4].set_ylim(0, max(1.2, 1.08 * Rmax))
        axes[4].axhline(1, color=P.RED, lw=P.STYLE['lw_ref'], ls='--', alpha=P.STYLE['ref_alpha'], zorder=2)
        handles = [Line2D([], [], color=st['color'], ls=st['ls'], lw=st['lw'], label=st['label'])
                   for st, _, _ in curves.values()]
        handles += [Line2D([], [], ls='none', marker='o', ms=2.4, mfc='none', mec=P.BLACK, mew=0.4, label='Observed data'),
                    Line2D([], [], color=P.RED, ls='--', lw=P.STYLE['lw_ref'], alpha=P.STYLE['ref_alpha'], label=r'$\eta$')]
        F2.frame_legend(axes[0].legend(handles=handles, loc='upper right', ncol=3, columnspacing=1.0))
        F2.frame_legend(axes[4].legend(handles=[Line2D([], [], color=P.RED, ls='--', lw=P.STYLE['lw_ref'],
                                                       alpha=P.STYLE['ref_alpha'], label=r'$R_e=1$')], loc='upper right'))
        qc, mcc = qo[qo.phase == 'control'], mc[mc.phase == 'control']
        checks = dict(t1=t1, t2=t2, t2_opt=t2_opt, eta=eta, t_obs_end=t_obs_end, xend=xend,
                      q_only=dict(t1_traj=float(qc.t.iloc[0]), t2_traj=float(qc.t.iloc[-1]),
                                  I_dev_max=float((qc.I / eta - 1).abs().max()),
                                  Itcum_end=float(qo.Ctotal.iloc[-1]), t_end=float(qo.t.iloc[-1])),
                      cost_optimal=dict(t1_traj=float(mcc.t.iloc[0]), t2_traj=float(mcc.t.iloc[-1]),
                                        I_dev_max=float((mcc.I / eta - 1).abs().max()),
                                        Itcum_end=float(mc.Ctotal.iloc[-1]), t_end=float(mc.t.iloc[-1]),
                                        c_min=float(mc.c.min())))
        checks['pdf_sha256'] = save(fig, 'xian_strategy_process')
    return checks


# ---------------------------------------------------------------- 补充图 S8
def heatmaps(design_eta, design_label):
    """preview_style_heatmaps.preview_s8 的画法，设计阈值参照线的位置与标注改为参数。"""
    source, reference = XI / 'heatmap.csv', XI / 'reference.json'
    peak = float(json.loads(reference.read_text(encoding='utf-8'))['I_peak_T'])
    reference_positions = [peak, design_eta]
    frame = pd.read_csv(source, float_precision='round_trip')
    x, y = np.sort(frame.eta.unique()), np.sort(frame.c0.unique())
    fields = [('control_duration', r'$\Delta t$'), ('clear_time', r'$t_{\rm end}$'),
              ('cum_total_infections', r'$I_{t_{\rm cum}}$'), ('J', r'$J$')]
    checks = dict(reference_positions=reference_positions, design_label=design_label, metrics={})
    with plt.rc_context(PC.RC):
        fig, axes, cbaxes = H.four_panel_grid(104)
        for k, (ax, cax, (metric, symbol)) in enumerate(zip(axes, cbaxes, fields)):
            z = frame.pivot(index='c0', columns='eta', values=metric).reindex(index=y, columns=x).to_numpy()
            finite = z[np.isfinite(z)]
            lo, hi = float(finite.min()), float(finite.max())
            norm = Normalize(lo, hi) if metric == 'cum_total_infections' else LogNorm(lo, hi)
            ax.set_xscale('log')
            mesh = ax.pcolormesh(x, y, np.ma.masked_invalid(z), shading='auto', cmap=PC.palette(),
                                 norm=norm, edgecolors='face', linewidth=.2,
                                 antialiased=False, snap=True, rasterized=True)
            ax.set_xlim(ax.get_xlim())
            ax.set_ylim(ax.get_ylim())
            ax.set_xticks([100, 1000, 10000, 30000], ['100', '1000', '10000', '30000'])
            ax.set_yticks([6, 8, 10, 12, 13])
            fig.canvas.draw()
            levels = H.xian_contour_levels(z, metric)
            contours = ax.contour(x, y, z, levels=levels, colors=[P.RED], linestyles='-.',
                                  linewidths=P.STYLE['lw_vline'])
            H.label_xian_contours(ax, contours, x, y, '%.3g' if metric == 'cum_total_infections' else '%.0f',
                                  reference_positions)
            for eta, dash in ((peak, (0, (4, 2))), (design_eta, (0, (1.2, 2.)))):
                ax.axvline(eta, color=P.BLACK, lw=P.STYLE['lw_vline'], ls=dash, alpha=.82, zorder=5)
            if metric == 'control_duration':
                for eta, label in ((peak, r'$I_{\rm peak}^{\rm T}$'), (design_eta, design_label)):
                    ax.text(eta, float(y.max()) * .985, label, rotation=90, ha='right', va='top',
                            fontsize=P.STYLE['note'], color=P.BLACK, clip_on=False)
            if k >= 2:
                ax.set_xlabel(r'$\eta$')
            else:
                ax.tick_params(labelbottom=False)
            if k % 2 == 0:
                ax.set_ylabel(r'$c_0$')
            else:
                ax.tick_params(labelleft=False)
            ax.set_title(f'({chr(97 + k)})')
            cb = H.math_colorbar(fig, mesh, cax, symbol)
            if metric == 'cum_total_infections':
                cb.formatter.set_powerlimits((0, 0))
                cb.update_ticks()
            checks['metrics'][metric] = dict(color_limits=[lo, hi], contour_levels=levels.tolist())
        H.tighten_colorbars(fig, zip(axes, cbaxes))
        checks['pdf_sha256'] = save(fig, 'S8')
    return checks


def main():
    inputs = {p.relative_to(ROOT).as_posix(): dict(sha256=sha(p), content_sha256=text_sha(p)) for p in INPUTS}
    w3 = json.loads((W3 / 'xian_theta001.json').read_text(encoding='utf-8'))
    assert w3['precheck']['ok']
    out = dict(script='nr_audit/plot_new4w_figures.py', git_head=git_head(), authorization='AGENTS.md N33（NEW-4w）',
               inputs=inputs, Main8=main8(w3), strategy_process=strategy_process(w3),
               S8=heatmaps(w3['settings']['eta'], r'$\eta=0.001N$'))
    (W3 / 'figures.json').write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float),
                                     encoding='utf-8', newline='\n')
    print(json.dumps({k: out[k] for k in ('Main8', 'strategy_process')}, ensure_ascii=False, indent=1, default=float)[:3000])


if __name__ == '__main__':
    main()
