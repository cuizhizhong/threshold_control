"""NEW-4s：正文图 4（fig:joint:compare）按正文图 2 的风格重绘（样式取自 plot_xian_fig2_style.py）。

基准参数下不考虑能力约束时四种控制的时间轨迹：(a) 接触率，(b) 隔离比例，(c) (I+I_q)/eta，(d) S/N。
数据与原图（reproducibility/joint_extra/figures.py:fig_compare）相同，只读
reproducibility/results/20261005_sec7_v2_refinement/joint_extra/ 的既有轨迹（使用前记录原字节 SHA-256），不求解模型。
只改字体、配色、线型与图例位置：三种控制用实线（仅减少接触绿色、仅隔离控制蓝色、成本最优控制紫色，与图 9 的颜色一致），
只有显式族 alpha = 0.5 用品红虚线；参照线 q0、1、S_c/N 为红色虚线；图例放在 (b) 右上角的空白处。
控制按计算段分段画，段间共同端点处补竖线，不跨跳变插值（同原图）。

运行：python nr_audit/plot_new4s_figures.py。输出 paper/figures/new4s/joint_compare_baseline.pdf、
paper/tmp/new4s/*.png（预览，不入库）与 results/new4s_figures.json。
"""
import hashlib
import json
import re

import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import plot_xian_fig2_style as F2
from audit_common import ROOT, dump

JX = ROOT / 'reproducibility' / 'results' / '20261005_sec7_v2_refinement' / 'joint_extra'
INPUTS = ['trajectories_baseline.csv', 'compare_baseline.csv', 'input_manifest.json']
OUT = ROOT / 'paper' / 'figures' / 'new4s'
PREVIEW = ROOT / 'paper' / 'tmp' / 'new4s'
MM, STYLE = F2.MM, F2.STYLE
PURPLE = (0.494, 0.184, 0.556)                       # 与图 9 中成本最优控制相同
LAWS = {   # 三种控制用实线，只有显式族用虚线；仅隔离与成本最优控制在前段重合，上层的紫线较细，蓝线仍可见
    'contact_only': dict(label='Contact reduction only', color=F2.GREEN, ls='-', lw=STYLE['lw_main']),
    'alpha_0.5': dict(label=r'Explicit family, $\alpha=0.5$', color=F2.MAGENTA, ls='--', lw=STYLE['lw_ref'] + .2),
    'quarantine_only': dict(label='Quarantine-only control', color=F2.BLUE, ls='-', lw=STYLE['lw_main'] + .3),
    'minimum_cost': dict(label='Cost-optimal control', color=PURPLE, ls='-', lw=STYLE['lw_ref']),
}
WIDTH_FRAC = 0.85


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def piecewise(ax, g, y, **kw):
    """按计算段画；段间共同端点处补竖线，不跨跳变插值。"""
    seg = (g.segment != g.segment.shift()).cumsum()
    parts = [p for _, p in g.assign(_y=y).groupby(seg, sort=False)]
    for p in parts:
        ax.plot(p.t, p._y, **kw)
    for a, b in zip(parts, parts[1:]):
        if abs(a.t.iloc[-1] - b.t.iloc[0]) <= 1e-10 * max(1, abs(b.t.iloc[0])):
            ax.plot([b.t.iloc[0]] * 2, [a._y.iloc[-1], b._y.iloc[0]], **kw)


def joint_compare():
    tr = pd.read_csv(JX / 'trajectories_baseline.csv')
    comp = pd.read_csv(JX / 'compare_baseline.csv').set_index('strategy')
    man = json.loads((JX / 'input_manifest.json').read_text(encoding='utf-8'))['cases']['baseline']
    par, der = man.get('params', man.get('parameters')), man['derived']
    eta, N, q0, Sc = par['eta'], par['N'], par['q0'], der['Sc']
    tmax = float(max(comp.loc[k, 't_end'] for k in LAWS))
    fig, axes = plt.subplots(2, 2, figsize=(WIDTH_FRAC * F2.TEXT_WIDTH_PT / 72, 100 * MM))
    fig.subplots_adjust(left=.085, right=.985, bottom=.085, top=.95, wspace=.26, hspace=.42)
    ax_c, ax_q, ax_i, ax_s = axes.ravel()
    record = {}
    for key, st in LAWS.items():
        g = tr[tr.strategy == key].sort_values('t', kind='stable')
        kw = dict(color=st['color'], ls=st['ls'], lw=st['lw'])
        piecewise(ax_c, g, g.c, **kw)
        piecewise(ax_q, g, g.q, **kw)
        ax_i.plot(g.t, (g.I + g.Iq) / eta, **kw)
        ax_s.plot(g.t, g.S / N, **kw)
        record[key] = dict(points=int(len(g)), t_last=float(g.t.iloc[-1]), t_end=float(comp.loc[key, 't_end']),
                           peak_ratio=float(((g.I + g.Iq) / eta).max()),
                           peak_ratio_table=float(comp.loc[key, 'peak_I_plus_Iq_over_eta']))
    ref = dict(color=F2.RED, lw=STYLE['lw_ref'], ls='--', alpha=STYLE['ref_alpha'], zorder=1)
    for ax, value, text in ((ax_q, q0, r'$q_0$'), (ax_i, 1.0, r'$1$'), (ax_s, Sc / N, r'$S_c/N$')):
        ax.axhline(value, **ref)
        ax.text(tmax * .985, value, text, ha='right', va='bottom', fontsize=STYLE['note'], color=F2.RED)
    for ax, title, ylabel in zip(axes.ravel(), ('(a)', '(b)', '(c)', '(d)'),
                                 (r'$c(t)$', r'$q(t)$', r'$(I+I_q)/\eta$', r'$S/N$')):
        ax.set_xlim(0, tmax)
        ax.set_xlabel(r'$t$')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
    ax_q.set_ylim(0, None)
    ax_i.set_ylim(0, None)
    handles = [Line2D([], [], color=st['color'], ls=st['ls'], lw=st['lw'], label=st['label']) for st in LAWS.values()]
    F2.frame_legend(ax_q.legend(handles=handles, loc='upper right'))
    checks = dict(eta=eta, N=N, q0=q0, Sc_over_N=Sc / N, tmax=tmax, laws=record,
                  peak_matches_table={k: abs(v['peak_ratio'] / v['peak_ratio_table'] - 1) < 1e-3 for k, v in record.items()},
                  ends_at_clearance={k: abs(v['t_last'] - v['t_end']) < 1e-6 for k, v in record.items()})
    return fig, checks


def embedded_fonts(path):
    return sorted(set(re.findall(rb'/BaseFont\s*/([A-Za-z0-9+\-]+)', path.read_bytes())))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    inputs = {f'{JX.relative_to(ROOT).as_posix()}/{n}': sha(JX / n) for n in INPUTS}
    with plt.rc_context(F2.RC):
        fig, checks = joint_compare()
        pdf = OUT / 'joint_compare_baseline.pdf'
        fig.savefig(pdf, metadata={'CreationDate': None, 'ModDate': None})
        fig.savefig(PREVIEW / 'joint_compare_baseline.png', dpi=300)
        size = [round(float(v) / MM, 2) for v in fig.get_size_inches()]
        plt.close(fig)
    out = {pdf.relative_to(ROOT).as_posix(): dict(sha256=sha(pdf), size_mm=size,
                                                  fonts=[f.decode() for f in embedded_fonts(pdf)])}
    assert all(re.search(r'cm(r|mi|sy|ex)10', f, re.I) for o in out.values() for f in o['fonts']), out
    dump('new4s_figures.json', dict(script='nr_audit/plot_new4s_figures.py', style_module='nr_audit/plot_xian_fig2_style.py',
                                    style=STYLE, inputs_sha256=inputs, outputs=out, checks=checks))
    print(json.dumps(dict(outputs=out, checks=checks), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
