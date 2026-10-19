"""NEW-4d 补充图：图7转折区的局部加密（原 NEW-2 图7 的 (c)(d) 面板），叠加闭式点。

只读复用 NEW-2 的缓存 new_figure7.json/.npz（经 plot_figure7.validate_cached_inputs 校验），不重新分类、
不重算背景；闭式尖点 (cusp_state, r_cont) 与 (z_sw, r̂) 取自 new4d_cost_structure.json。
横轴按时间方向（S 自左向右减小），与正文图7一致。

运行：python nr_audit/plot_figure7_detail.py
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

import plot_figure7 as F7
from audit_common import ROOT, RESULTS

OUT = ROOT / 'paper/figures/joint_v2/joint_phase_detail'
CS = RESULTS / 'new4d_cost_structure.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    d = json.loads(F7.DATA.read_text(encoding='utf-8'))
    F7.validate_cached_inputs(d)
    arrays = dict(np.load(F7.NPZ))
    cs = json.loads(CS.read_text(encoding='utf-8'))
    plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman', 'STIXGeneral', 'DejaVu Serif'],
                         'mathtext.fontset': 'stix', 'font.size': 8, 'axes.titlesize': 8, 'axes.labelsize': 9,
                         'xtick.labelsize': 8, 'ytick.labelsize': 8, 'pdf.fonttype': 42, 'axes.linewidth': .65,
                         'axes.spines.top': False, 'axes.spines.right': False, 'legend.frameon': False})
    cmap = LinearSegmentedColormap.from_list('contact_share', ['#f5f9fd', '#a6cbe6', '#206fb6', '#062e5c'])
    colors = {'continuous': '#161616', 'endpoint': '#c23b22', 'internal': '#9b3a97'}
    fig = plt.figure(figsize=(174 / 25.4, 78 / 25.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, .04], left=.085, right=.93, bottom=.27, top=.9, wspace=.3)
    axs = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    cax = fig.add_subplot(gs[0, 2])
    receipt = {}
    for k, (case, name) in enumerate((('base', 'Baseline'), ('xian', "Xi'an"))):
        ax = axs[k]
        z, r = arrays[case + '_z'], arrays[case + '_r']
        pc = ax.pcolormesh(z, arrays[case + '_background_r'], arrays[case + '_background_y'],
                           cmap=cmap, vmin=0, vmax=1, shading='auto', rasterized=True)
        for kind in colors:
            xs = []
            for row in d['cases'][case]['samples']:
                vals = [b['z'] for b in row['breakpoints'] if F7.edge_kind(b) == kind]
                xs.append(vals[0] if vals else np.nan)
            ax.plot(xs, r, color=colors[kind], lw=1.1)
            ax.scatter(xs, r, color=colors[kind], s=4, zorder=4, linewidths=0)
        o = cs['cases'][case]
        ax.axvline(o['z_sw'], color='#555555', ls='--', lw=.7)
        ax.plot(o['cusp_state'], o['r_cont'], 'o', ms=5, mfc='none', mec='#161616', mew=.9, zorder=6)
        ax.plot(o['z_sw'], o['r_hat'], 'D', ms=4.5, mfc='none', mec='#161616', mew=.9, zorder=6)
        ax.set(xlim=(z[-1], z[0]), ylim=(r[0], r[-1]), xlabel=r'$S/S_c$  (time $\rightarrow$)')
        if k == 0:
            ax.set_ylabel(r'$r=w_q/w_c$')
        ax.set_title(f'({chr(97 + k)}) {name}: transition detail', loc='left')
        receipt[case] = dict(cusp=[o['cusp_state'], o['r_cont']], switch=[o['z_sw'], o['r_hat']])
    cb = fig.colorbar(pc, cax=cax)
    cb.set_label(r'$y$', rotation=0, labelpad=5)
    handles = [Line2D([], [], c=colors['continuous'], lw=1.1, label='Continuous entry'),
               Line2D([], [], c=colors['endpoint'], lw=1.1, label='Endpoint-to-interior jump'),
               Line2D([], [], c=colors['internal'], lw=1.1, label='Interior-to-interior jump'),
               Line2D([], [], ls='none', marker='o', mfc='none', mec='#161616', label=r'Closed form $r_{\rm cont}$'),
               Line2D([], [], ls='none', marker='D', mfc='none', mec='#161616', label=r'Closed form $\hat r$ at $S_{\rm sw}$')]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .0), ncol=5, fontsize=7.5,
               columnspacing=1.3, handlelength=2.2)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT.with_suffix('.pdf'), dpi=400)
    fig.savefig(ROOT / 'tmp/new4d_figure7_detail_preview.png', dpi=200) if (ROOT / 'tmp').exists() else None
    plt.close(fig)
    (RESULTS / 'new4d_figure7_detail_render.json').write_text(json.dumps(dict(
        source_cache=dict(json=F7.DATA.relative_to(ROOT).as_posix(), npz_sha256=sha(F7.NPZ)),
        closed_form_markers=receipt, pdf_sha256=sha(OUT.with_suffix('.pdf'))), indent=2),
        encoding='utf-8', newline='\n')
    print('written', OUT.with_suffix('.pdf').relative_to(ROOT))


if __name__ == '__main__':
    main()
