"""NEW-4p：数值部分重排所需的图件，按正文图 2 的风格绘制（样式与 NEW-4o 的 plot_xian_fig2_style.py 相同）。

- 图 5（fig:joint:capacity）：基准参数的能力可行区域与代表点上能力约束下的成本最优控制（原图 (a)(c)）；
- 图 6（fig:joint:phase）：基准参数的权重相图与几个权重的控制（原图 (a)(c)(d)）；
- 西安控制组合图（fig:xian:joint）：西安参数的能力可行区域与权重相图（原图 5(b)、6(b)）；
- 策略过程图（fig:xian:strategy-process）：在 NEW-4o 版上加入成本最优控制；
- 图 7（fig:xian:observed-fit）：西安拟合图改为同一风格（P4），数据与原图相同。

只读既有数据，使用前记录原字节 SHA-256，不求解模型、不重算相图背景：
- 能力约束与西安各控制的轨迹取自 reproducibility/results/20261005_sec7_v2_refinement/joint_extra/；
- 三种策略与观测取自 reproducibility/results/20261003_release_final/xian/；
- 相图背景、跳变曲线与剖面取自 NEW-4d 的缓存 results/new4d_figure7.{json,npz}，
  剖面上的跳变位置取自其绘图收据 results/new4d_figure7_render.json。
成本最优控制的 R_e 按正文第 2.2 节的定义 beta c (1-q) S / (gamma N) 由轨迹列计算，并用三种策略的已存 R_e 核对该式。

运行：python nr_audit/plot_new4p_figures.py。输出 paper/figures/new4p/*.pdf、paper/tmp/new4p/*.png（预览，不入库）
与 results/new4p_figures.json。
"""
import hashlib
import json
import re

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.lines import Line2D

import plot_xian_fig2_style as F2
from audit_common import ROOT, RESULTS, dump

JX = ROOT / 'reproducibility' / 'results' / '20261005_sec7_v2_refinement' / 'joint_extra'
XI = F2.SRC
INPUTS = [JX / n for n in ('capacity.json', 'capacity_baseline.npz', 'capacity_xian.npz',
                           'capacity_traj_baseline.csv', 'input_manifest.json', 'trajectories_xian.csv')]
INPUTS += [XI / n for n in ('timeseries.csv', 'observed.csv', 'summary.csv')]
INPUTS += [RESULTS / n for n in ('new4d_figure7.json', 'new4d_figure7.npz', 'new4d_figure7_render.json')]
OUT = ROOT / 'paper' / 'figures' / 'new4p'
PREVIEW = ROOT / 'paper' / 'tmp' / 'new4p'
MM, STYLE = F2.MM, F2.STYLE
TEXT_WIDTH_IN = F2.TEXT_WIDTH_PT / 72.0
BLUE, BLACK, RED, GREEN, GRAY = F2.BLUE, F2.BLACK, F2.RED, F2.GREEN, F2.GRAY
PURPLE = (0.494, 0.184, 0.556)                       # 图 2 配色中的紫色
REGION_CMAP = ListedColormap(['#efefef', '#f4cfc8', '#d3e4f3'])   # 不可行、只有联合控制可行、至少一种单控制可行
PHASE_CMAP = LinearSegmentedColormap.from_list('contact_share', ['#f5f9fd', '#a6cbe6', '#206fb6', '#062e5c'])
LEVELS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
REP = (1.0, 2.0, 3.17, 5.0, 15.0)                    # 与 NEW-4d 剖面相同的代表权重与颜色
REP_COLORS = ('#E69F00', '#009E73', '#CC79A7', '#0072B2', '#D55E00')
JUMP = dict(continuous=BLACK, endpoint=RED, internal=PURPLE)
TEXT_SUFFIXES = {'.csv', '.json'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def load_phase():
    """NEW-4d 相图缓存；先确认缓存与其绘图收据一致，再复用。"""
    data = json.loads((RESULTS / 'new4d_figure7.json').read_text(encoding='utf-8'))
    render = json.loads((RESULTS / 'new4d_figure7_render.json').read_text(encoding='utf-8'))
    npz = RESULTS / 'new4d_figure7.npz'
    if sha(npz) != data['npz_sha256'] or render['npz_sha256'] != data['npz_sha256'] \
            or render['data_sha256'] != text_sha(RESULTS / 'new4d_figure7.json'):
        raise ValueError('图 6 的相图缓存与绘图收据不一致，不能复用')
    return data, dict(np.load(npz)), render


def region_panel(ax, cap, case, title):
    item = cap[case]
    with np.load(JX / f'capacity_{case}.npz', allow_pickle=False) as d:
        u, q, region = d['u'], d['q'], d['region']
        bu, bq = d['boundary_u'], d['boundary_q']
        q_line, c_line = d['quarantine_line'].item(), d['contact_line'].item()
    ax.pcolormesh(u, q, region, cmap=REGION_CMAP, vmin=-0.5, vmax=2.5, shading='auto', rasterized=True)
    for xs, ys in ((bu, bq), ([0, c_line], [q_line, q_line]), ([c_line, c_line], [item['q0'], q_line])):
        ax.plot(xs, ys, color=BLACK, lw=STYLE['lw_vline'])
    pt = item['point']
    ax.plot(pt['u_max'], pt['q_cap'], 'o', ms=3.6, color=RED, mec='white', mew=0.5, zorder=5)
    ax.set(xlim=(0, 1), ylim=(item['q0'], 1))
    ax.set_xlabel(r'$1-c_{\min}/c_0$')
    ax.set_ylabel(r'$q_{\rm cap}$')
    ax.set_title(title)
    return dict(point=pt, q_required_quarantine_only=item['q_required_quarantine_only'],
                u_required_contact_only=item['u_required_contact_only'],
                J=item['metrics']['J'], duration=item['metrics']['duration'])


def phase_panel(ax, data, arrays, case, rep_lines):
    c = data['cases'][case]
    z, r, Y = (arrays[f'{case}_{v}'] for v in ('z', 'r', 'y'))
    pc = ax.pcolormesh(z, r, Y, cmap=PHASE_CMAP, vmin=0, vmax=1, shading='auto', rasterized=True)
    Ym = np.where(Y > 0, Y, np.nan)
    for levs, col in (([v for v in LEVELS if v <= .5], '#3d3d3a'), ([v for v in LEVELS if v > .5], 'white')):
        cs = ax.contour(z, r, Ym, levels=levs, colors=col, linewidths=.45)
        pos = []                     # 每条等高线取 S/S_c 最接近 1.75 的点标注，避开底边（r<1.15）与各权重参照线
        rep_r = np.array([rv for rv, _, _ in rep_lines])
        for segs in cs.allsegs:
            pts = np.concatenate([s for s in segs if len(s)])
            far = np.all(np.abs(np.log(pts[:, 1])[:, None] - np.log(rep_r)[None, :]) > .07, axis=1)
            ok = pts[(pts[:, 1] >= 1.15) & far]
            pts = ok if len(ok) else pts
            pos.append(tuple(pts[np.argmin(np.abs(pts[:, 0] - 1.75))]))
        ax.clabel(cs, fmt=lambda v: f'{v:g}', fontsize=STYLE['legend'], inline=True, inline_spacing=1, manual=pos)
    for kind in ('internal', 'endpoint'):
        pts = [(p['z'], p['r']) for p in c['gamma'] if p['kind'] == kind]
        if pts:
            ax.plot(*zip(*pts), color=JUMP[kind], lw=STYLE['lw_ref'])
    ax.plot([c['z_sw'], c['z_sw']], [0.9, c['r_hat']], color=JUMP['continuous'], lw=STYLE['lw_ref'])
    ax.plot(c['z_sw'], c['r_hat'], 'D', ms=2.6, mfc='white', mec=BLACK, mew=.5, zorder=6)
    ax.plot(c['z_star'], c['r_C'], 'v', ms=3.0, color=BLACK, zorder=6, clip_on=False)
    halo = [pe.Stroke(linewidth=1.5, foreground='white', alpha=.7), pe.Normal()]   # 细白边，只为在深色背景上可辨
    for rv, col, ls in rep_lines:
        ax.axhline(rv, color=col, lw=.9, ls=ls, path_effects=halo)
    ax.set(xlim=(c['z_star'], 1), ylim=(.92, 20), yscale='log')
    ax.set_yticks([1, 2, 3, 5, 10, 20])
    ax.set_yticklabels(['1', '2', '3', '5', '10', '20'])
    ax.minorticks_off()
    ax.set_xlabel(r'$S/S_c$ (time $\rightarrow$)')
    ax.set_ylabel(r'$r=w_q/w_c$')
    return pc, dict(r_cont=c['r_cont'], r_hat=c['r_hat'], r_C=c['r_C'], z_sw=c['z_sw'], z_star=c['z_star'],
                    gamma_points=len(c['gamma']))


def colorbar(fig, pc, cax):
    cb = fig.colorbar(pc, cax=cax)
    cb.set_label(r'$y$', rotation=0, labelpad=4)
    cb.outline.set_linewidth(STYLE['lw_axes'])
    for v in LEVELS:
        cb.ax.axhline(v, color='#3d3d3a' if v <= .5 else 'white', lw=.45)


def jump_handles(extra=()):
    hs = [Line2D([], [], color=JUMP['continuous'], lw=STYLE['lw_ref'], label=r'Continuous switch at $S_{\rm sw}$'),
          Line2D([], [], color=JUMP['endpoint'], lw=STYLE['lw_ref'], label='Jump from quarantine-only'),
          Line2D([], [], color=JUMP['internal'], lw=STYLE['lw_ref'], label='Interior-to-interior jump')]
    return hs + list(extra)


def capacity_baseline():
    cap = json.loads((JX / 'capacity.json').read_text(encoding='utf-8'))
    man = json.loads((JX / 'input_manifest.json').read_text(encoding='utf-8'))
    c0 = man['cases']['baseline']['parameters']['c0']
    tr = pd.read_csv(JX / 'capacity_traj_baseline.csv').sort_values('t', kind='stable')
    fig, (ax_r, ax_t) = plt.subplots(1, 2, figsize=(0.8 * TEXT_WIDTH_IN, 50 * MM))
    fig.subplots_adjust(left=.085, right=.985, bottom=.17, top=.9, wspace=.3)
    chk = region_panel(ax_r, cap, 'baseline', '(a) Feasible region')
    item = cap['baseline']
    pt, m = item['point'], item['metrics']
    stop = m['t2'] + item['plot_viewport']['post_exit_days']
    tr = tr[tr.t <= stop + 1e-9]
    u = 1 - tr.c / c0
    seg = (tr.segment != tr.segment.shift()).cumsum()     # 按计算段画，段间共同端点处补竖线，不跨跳变插值
    for y, col in ((u, GREEN), (tr.q, BLUE)):
        groups = [g for _, g in tr.assign(y=y).groupby(seg, sort=False)]
        for g in groups:
            ax_t.plot(g.t, g.y, color=col, lw=STYLE['lw_main'])
        for a, b in zip(groups, groups[1:]):
            if abs(a.t.iloc[-1] - b.t.iloc[0]) <= 1e-10 * max(1, abs(b.t.iloc[0])):
                ax_t.plot([b.t.iloc[0]] * 2, [a.y.iloc[-1], b.y.iloc[0]], color=col, lw=STYLE['lw_main'])
    for v, col in ((pt['q_cap'], BLUE), (pt['u_max'], GREEN)):
        ax_t.axhline(v, color=col, lw=STYLE['lw_ref'], ls='--', alpha=STYLE['ref_alpha'])
    ax_t.set(xlim=(0, stop), ylim=(0, max(pt['q_cap'], pt['u_max']) + 0.12))
    ax_t.set_xlabel(r'$t$')
    ax_t.set_ylabel(r'$q,\ 1-c/c_0$')
    ax_t.set_title('(b) Constrained cost-optimal control')
    F2.frame_legend(ax_t.legend(handles=[Line2D([], [], color=BLUE, lw=STYLE['lw_main'], label=r'$q$'),
                                         Line2D([], [], color=GREEN, lw=STYLE['lw_main'], label=r'$1-c/c_0$')],
                                loc='center right'))
    chk.update(t1=m['t1'], t2=m['t2'], post_exit_days=item['plot_viewport']['post_exit_days'],
               q_max_on_path=float(tr.q.max()), u_max_on_path=float(u.max()))
    return fig, chk


def phase_baseline():
    data, arrays, render = load_phase()
    q0 = json.loads((JX / 'input_manifest.json').read_text(encoding='utf-8'))['cases']['baseline']['parameters']['q0']
    # 版面：左侧相图近似正方形，色标紧贴其右；右侧上下两幅剖面共用横轴，与相图同高
    fig = plt.figure(figsize=(TEXT_WIDTH_IN, 96 * MM))
    outer = fig.add_gridspec(1, 2, width_ratios=[1.12, 1], left=.065, right=.985, bottom=.15, top=.945, wspace=.2)
    left = outer[0].subgridspec(1, 2, width_ratios=[1, .045], wspace=.06)
    right = outer[1].subgridspec(2, 1, hspace=.32)
    ax_a, cax = fig.add_subplot(left[0]), fig.add_subplot(left[1])
    ax_b = fig.add_subplot(right[0])
    ax_c = fig.add_subplot(right[1], sharex=ax_b)
    pc, chk = phase_panel(ax_a, data, arrays, 'base', [(rv, col, (0, (3, 1.6))) for rv, col in zip(REP, REP_COLORS)])
    ax_a.set_title('(a) Cost-optimal combination')
    colorbar(fig, pc, cax)
    c = data['cases']['base']
    zp = arrays['profile_z']
    q = lambda x, z: 1 - (1 - q0) / (x * z)
    used = []
    for k, (rv, col) in enumerate(zip(REP, REP_COLORS)):
        x = arrays[f'profile_{k}_x']
        jumps = next(p['jumps'] for p in render['profile_jumps'] if p['r'] == rv)
        cuts = [int(np.searchsorted(zp, j['z'])) for j in jumps]     # 跳变在 zp[cut-1] 与 zp[cut] 之间
        for ax, yv in ((ax_b, x), (ax_c, q(x, zp))):
            for m, (a, e) in enumerate(zip([0] + cuts, cuts + [zp.size])):
                ax.plot(zp[a:e], yv[a:e], color=col, lw=1.2, label=f'$r={rv:g}$' if m == 0 else None)
        for j in jumps:
            ax_b.plot([j['z']] * 2, [j['x_left'], j['x_right']], color=col, lw=STYLE['lw_vline'], ls=':')
            ax_c.plot([j['z']] * 2, [q(j['x_left'], j['z']), q(j['x_right'], j['z'])], color=col,
                      lw=STYLE['lw_vline'], ls=':')
        used.append(dict(r=rv, jumps=jumps))
    for ax, title, ylabel in ((ax_b, '(b) Contact rate', r'$c_c^*/c_0$'), (ax_c, '(c) Quarantine fraction', r'$q_c^*$')):
        ax.set_xlim(c['z_star'], 1)
        ax.axvline(c['z_sw'], color=GRAY, ls='--', lw=STYLE['lw_vline'])
        ax.set_ylabel(ylabel)
        ax.set_title(title)
    ax_b.tick_params(labelbottom=False)
    ax_c.set_xlabel(r'$S/S_c$ (time $\rightarrow$)')
    ax_b.set_ylim(.25, 1.04)
    ax_c.set_ylim(-.02, .8)
    ax_c.axhline(q0, color=BLACK, lw=STYLE['lw_vline'], ls='-.', alpha=STYLE['ref_alpha'])
    ax_c.text(c['z_star'] - .05, q0 + .02, r'$q_0$', fontsize=STYLE['note'], va='bottom')
    F2.frame_legend(ax_c.legend(loc='upper right', ncol=2, columnspacing=1.0, handlelength=1.8))
    sw = Line2D([], [], color=GRAY, ls='--', lw=STYLE['lw_vline'], label=r'$S_{\rm sw}/S_c$')
    F2.frame_legend(fig.legend(handles=jump_handles([sw]), loc='lower center', bbox_to_anchor=(.5, .008), ncol=4,
                               columnspacing=1.6))
    chk.update(profile_jumps=used)
    return fig, chk


def xian_joint():
    cap = json.loads((JX / 'capacity.json').read_text(encoding='utf-8'))
    data, arrays, _ = load_phase()
    # 版面与图 6 一致：两幅近似正方形的面板，色标紧贴相图右侧
    fig = plt.figure(figsize=(TEXT_WIDTH_IN, 74 * MM))
    outer = fig.add_gridspec(1, 2, width_ratios=[1, 1.06], left=.075, right=.955, bottom=.2, top=.925, wspace=.24)
    right = outer[1].subgridspec(1, 2, width_ratios=[1, .045], wspace=.06)
    ax_r, ax_p, cax = fig.add_subplot(outer[0]), fig.add_subplot(right[0]), fig.add_subplot(right[1])
    chk = dict(capacity=region_panel(ax_r, cap, 'xian', '(a) Feasible region'))
    pc, chk['phase'] = phase_panel(ax_p, data, arrays, 'xian', [(2.0, GRAY, ':')])
    ax_p.set_title('(b) Cost-optimal combination')
    colorbar(fig, pc, cax)
    r2 = Line2D([], [], color=GRAY, ls=':', lw=STYLE['lw_ref'], label=r'Default weight $r=2$')
    F2.frame_legend(fig.legend(handles=jump_handles([r2]), loc='lower center', bbox_to_anchor=(.5, .005), ncol=4,
                               columnspacing=1.4))
    return fig, chk


def strategy_process():
    """NEW-4o 的策略过程图加入成本最优控制；其余画法与 NEW-4o 相同。"""
    ts = pd.read_csv(XI / 'timeseries.csv')
    obs = pd.read_csv(XI / 'observed.csv')
    sm = pd.read_csv(XI / 'summary.csv').set_index('strategy')
    par = json.loads((JX / 'input_manifest.json').read_text(encoding='utf-8'))['cases']['xian']['parameters']
    jt = pd.read_csv(JX / 'trajectories_xian.csv')
    re_of = lambda d: par['beta'] * d.c * (1 - d.q) * d.S / (par['gamma'] * par['N'])
    curves = {}
    for name, st in F2.STRATEGIES.items():
        sub = ts[ts.strategy == name]
        curves[name] = (dict(st), sub.t, [sub.I, sub.c, sub.q, sub.Cc + sub.Cq, sub.Rt])
    curves['情景一阈值控制'][0]['label'] = 'Quarantine-only control'      # 两种阈值控制并列，图例写明控制
    mc = jt[jt.strategy == 'minimum_cost'].sort_values('t', kind='stable')
    qo = jt[jt.strategy == 'quarantine_only'].sort_values('t', kind='stable')
    opt = dict(label='Cost-optimal control', color=PURPLE, ls='--', lw=STYLE['lw_main'], zorder=5)
    curves['成本最优控制'] = (opt, mc.t, [mc.I, mc.c, mc.q, mc.Ctotal, re_of(mc)])
    thr = sm.loc['情景一阈值控制']
    t1, t2, eta = float(thr['t1']), float(thr['t2']), float(thr['eta'])
    mc_ctrl = mc[mc.phase == 'control']
    t2_opt = float(mc_ctrl.t.iloc[-1])
    t_obs_end = float(obs.t.iloc[-1])
    xend = max(float(ts.t.max()), float(mc.t.max()))

    fig = plt.figure(figsize=(135 * MM, 125 * MM))
    gs = fig.add_gridspec(3, 2, left=.105, right=.985, bottom=.075, top=.955, wspace=.30, hspace=.52)
    axes = [fig.add_subplot(gs[0, :]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1]),
            fig.add_subplot(gs[2, 0]), fig.add_subplot(gs[2, 1])]
    for st, t, ys in curves.values():
        for ax, y in zip(axes, ys):
            ax.plot(t, y, color=st['color'], ls=st['ls'], lw=st['lw'], zorder=st['zorder'])
    for ax in axes:
        F2.vline(ax, t_obs_end, GRAY)
        ax.axvline(t2_opt, color=PURPLE, lw=STYLE['lw_vline'], ls=':', alpha=STYLE['ref_alpha'], zorder=1)
    for i, y1, side1, y2 in ((0, .05, 'right', .05), (1, .05, 'right', .05), (2, .12, 'right', .12),
                             (4, .05, 'left', .05)):
        F2.vline(axes[i], t1, BLACK, r'$t_1$', y=y1, side=side1)
        F2.vline(axes[i], t2, BLACK, r'$t_2$', y=y2)
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
               for st, _, _ in curves.values()]
    handles += [Line2D([], [], ls='none', marker='o', ms=2.4, mfc='none', mec=BLACK, mew=0.4, label='Observed data'),
                Line2D([], [], color=RED, ls='--', lw=STYLE['lw_ref'], alpha=STYLE['ref_alpha'], label=r'$\eta$')]
    F2.frame_legend(axes[0].legend(handles=handles, loc='upper right', ncol=3, columnspacing=1.0))
    F2.frame_legend(axes[4].legend(handles=[Line2D([], [], color=RED, ls='--', lw=STYLE['lw_ref'],
                                                   alpha=STYLE['ref_alpha'], label=r'$R_e=1$')], loc='upper right'))
    # 核对：R_e 公式与三种策略的已存值一致；两份数据中的仅隔离控制相同；成本最优控制与表 2 一致
    re_err = {n: float(np.max(np.abs(re_of(ts[ts.strategy == n]) / ts[ts.strategy == n].Rt - 1)))
              for n in F2.STRATEGIES}
    qo_ctrl = qo[qo.phase == 'control']
    checks = dict(
        t1=t1, t2=t2, eta=eta, t_obs_end=t_obs_end,
        Re_formula_max_rel_err=re_err,
        quarantine_only_cross_check=dict(
            t1_diff=float(qo_ctrl.t.iloc[0]) - t1, t2_diff=float(qo_ctrl.t.iloc[-1]) - t2,
            Itcum_end_rel_diff=float(qo.Ctotal.iloc[-1] / thr['cum_total_infections'] - 1)),
        cost_optimal=dict(t1=float(mc_ctrl.t.iloc[0]), t2=t2_opt, duration=t2_opt - float(mc_ctrl.t.iloc[0]),
                          t_end=float(mc.t.iloc[-1]), Itcum_end=float(mc.Ctotal.iloc[-1]), I_max=float(mc.I.max()),
                          c_min=float(mc.c.min()), I_end=float(mc.I.iloc[-1])))
    return fig, checks


def observed_fit():
    """图 7（fig:xian:observed-fit）：观测窗口内的日新增病例与 TDINN 重构。
    模型日新增与原图（restore_figures.xian）相同：累计流量在整数日上插值后取相邻日之差；只改字体、配色与线型。"""
    ts = pd.read_csv(XI / 'timeseries.csv')
    obs = pd.read_csv(XI / 'observed.csv')
    td = ts[ts.strategy == 'TDINN控制']
    fig, axes = plt.subplots(1, 2, figsize=(TEXT_WIDTH_IN, 58 * MM))
    fig.subplots_adjust(left=.07, right=.985, bottom=.19, top=.89, wspace=.22)
    days = np.arange(len(obs) + 1)
    model = {}
    for ax, col, obs_col, title in zip(axes, ('Cc', 'Cq'), ('community_new', 'quarantine_new'),
                                       ('(a) Community-detected cases', '(b) Quarantine-detected cases')):
        y = np.diff(np.interp(days, td.t, td[col]))
        model[col] = y
        ax.plot(obs.t, y, color=GREEN, lw=STYLE['lw_main'], zorder=3)
        ax.scatter(obs.t, obs[obs_col], s=6, facecolors='none', edgecolors=BLACK, linewidths=0.5, zorder=4)
        ax.set(xlim=(-.5, len(obs) - .5), ylim=(0, None))
        ax.set_xticks([0, 12, 24, 39], ['Dec 09', 'Dec 21', 'Jan 02', 'Jan 17'])
        ax.set_xlabel('Date')
        ax.set_ylabel('Daily new cases')
        ax.set_title(title)
    F2.frame_legend(axes[1].legend(handles=[
        Line2D([], [], ls='none', marker='o', ms=2.4, mfc='none', mec=BLACK, mew=0.5, label='Observed data'),
        Line2D([], [], color=GREEN, lw=STYLE['lw_main'], label='Model (fitted $I_0$, TDINN control)')],
        loc='upper right'))
    checks = dict(observed_days=int(len(obs)), observed_total=int(obs.total_new.sum()),
                  observed_community=int(obs.community_new.sum()), observed_quarantine=int(obs.quarantine_new.sum()),
                  model_total_40d=float(model['Cc'].sum() + model['Cq'].sum()),
                  model_peak_community=float(model['Cc'].max()), model_peak_quarantine=float(model['Cq'].max()))
    return fig, checks


def embedded_fonts(path):
    return sorted(set(re.findall(rb'/BaseFont\s*/([A-Za-z0-9+\-]+)', path.read_bytes())))


FIGURES = (('joint_capacity_baseline', capacity_baseline), ('joint_phase_baseline', phase_baseline),
           ('xian_joint', xian_joint), ('xian_strategy_process', strategy_process),
           ('xian_observed_fit', observed_fit))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    inputs = {}
    for p in INPUTS:
        rec = dict(sha256=sha(p))
        if p.suffix in TEXT_SUFFIXES:
            rec['content_sha256'] = text_sha(p)
        inputs[p.relative_to(ROOT).as_posix()] = rec
    outputs, checks = {}, {}
    with plt.rc_context(F2.RC):
        for name, fn in FIGURES:
            fig, chk = fn()
            pdf = OUT / f'{name}.pdf'
            fig.savefig(pdf, dpi=400, metadata={'CreationDate': None, 'ModDate': None})
            fig.savefig(PREVIEW / f'{name}.png', dpi=300)
            outputs[pdf.relative_to(ROOT).as_posix()] = dict(
                sha256=sha(pdf), size_mm=[round(float(v) / MM, 2) for v in fig.get_size_inches()],
                fonts=[f.decode() for f in embedded_fonts(pdf)])
            plt.close(fig)
            checks[name] = chk
    assert all(re.search(r'cm(r|mi|sy|ex)10', f, re.I) for o in outputs.values() for f in o['fonts']), outputs
    dump('new4p_figures.json', dict(script='nr_audit/plot_new4p_figures.py', style_module='nr_audit/plot_xian_fig2_style.py',
                                    style=STYLE, inputs=inputs, outputs=outputs, checks=checks))
    print(json.dumps(dict(outputs=outputs), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
