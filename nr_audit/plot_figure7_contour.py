"""NEW-4d 图7：成本最优控制的等高线相图（基准、西安）与基准参数下代表权重的控制剖面。

图件问题：在 (S/S_c, r) 平面上，成本最优控制怎样组合两种措施，何时连续、何时跳变？
证据：逐状态有限比较（allocation.argmin_state，定理 5.1）在规则网格上精确求解；跳变曲线由同一求解器
在 S 上扫描并二分定位；闭式点 r_cont（定理 5.5）与 r̂（补充命题）取自 new4d_cost_structure.json。
类型：quantitative grid；Python；174 mm 宽；四个面板横轴按时间方向（S 自左向右减小），r ∈ [1, 20]。
不重算 ODE；旧 phase/NPZ 与 new_figure7.* 只读保留（补充材料局部面板仍由它们生成）。

运行：python nr_audit/plot_figure7_contour.py [--reuse-data]
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

import allocation as AL
import params as PR
import state_integrals as SI
from audit_common import ROOT, RESULTS

OUT = ROOT / 'paper/figures/joint_v2/joint_phase_contour'
DATA = RESULTS / 'new4d_figure7.json'
NPZ = RESULTS / 'new4d_figure7.npz'
CS = RESULTS / 'new4d_cost_structure.json'
R_MIN, R_MAX = 1.0, 20.0
REP = (1.0, 2.0, 3.17, 5.0, 15.0)                 # 基准剖面的代表权重
REP_COLORS = ('#E69F00', '#009E73', '#CC79A7', '#0072B2', '#D55E00')
LEVELS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_sha(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def inputs():
    files = [ROOT / 'nr_audit/allocation.py', ROOT / 'nr_audit/params.py', ROOT / 'nr_audit/state_integrals.py', CS]
    return {p.relative_to(ROOT).as_posix(): text_sha(p) for p in files}


def x_and_label(z, b, r):
    x, _, info = AL.argmin_state(float(z), b, 1.0, float(r))
    return x, info['label']


def bisect_jump(b, r, zl, zr, xl, ll, xr, lr):
    """在 [zl, zr] 上二分；两侧仍分离才是跳变（陡峭的连续段会收拢）。返回 (z_J, 左侧 x, 右侧 x, 类型) 或 None。"""
    for _ in range(60):
        zm = 0.5 * (zl + zr)
        xm, lm = x_and_label(zm, b, r)
        if abs(xm * zm - xl * zl) < abs(xm * zm - xr * zr):
            zl, xl, ll = zm, xm, lm
        else:
            zr, xr, lr = zm, xm, lm
    if abs(xr * zr - xl * zl) > 1e-6:
        kind = 'endpoint' if 'hi' in (ll, lr) else 'internal'
        return 0.5 * (zl + zr), xl, xr, kind
    return None


def jump_in(b, r, z_lo, z_hi, n=3000):
    """在 [z_lo, z_hi] 上找成本最优控制的第一个跳变：返回 (z_J, 左侧 x, 右侧 x, 类型) 或 None。"""
    zs = np.linspace(z_lo, z_hi, n)
    xs, labs = zip(*(x_and_label(z, b, r) for z in zs))
    u = np.array(xs) * zs
    du = np.abs(np.diff(u))
    k = np.flatnonzero(du > max(20 * np.median(du), 1e-4))
    for j in k:
        jmp = bisect_jump(b, r, zs[j], zs[j + 1], xs[j], labs[j], xs[j + 1], labs[j + 1])
        if jmp is not None:
            return jmp
    return None


def profile_jumps(b, r, zp, x):
    """剖面网格上的跳变：候选区间与 jump_in 同一判据，逐个二分确认；返回 [(区间下标 j, z_J, 左侧 x, 右侧 x, 类型)]。"""
    u = x * zp
    du = np.abs(np.diff(u))
    out = []
    for j in np.flatnonzero(du > max(20 * np.median(du), 1e-4)):
        zl, zr = zp[j], zp[j + 1]
        xl, ll = x_and_label(zl, b, r) if zl > 1 else (1.0, 'deg')
        xr, lr = x_and_label(zr, b, r)
        jmp = bisect_jump(b, r, zl, zr, xl, ll, xr, lr)
        if jmp is not None:
            out.append((int(j),) + tuple(jmp))
    return out


def compute():
    cs = json.loads(CS.read_text(encoding='utf-8'))
    d = dict(script='nr_audit/plot_figure7_contour.py', source_hashes=inputs(), r_range=[R_MIN, R_MAX],
             rep_weights=list(REP), levels=list(LEVELS), cases={})
    arrays = {}
    for case, P in PR.CASES.items():
        o = cs['cases'][case]
        b, zsw, zstar = P.z_bar, o['z_sw'], SI.start_state(P)['z_star']
        z = np.linspace(1.002, zstar, 300)
        r = np.geomspace(0.9, R_MAX, 300)
        Y = np.zeros((r.size, z.size))
        for i, rv in enumerate(r):
            for j, zv in enumerate(z):
                x, lab = x_and_label(zv, b, rv)
                Y[i, j] = 0.0 if lab == 'hi' else (1 - x) / (1 - 1 / zv)
        # 跳变曲线：r ∈ (r_cont, R_MAX]，在 [尖点状态 - 0.05, z*] 上扫描
        gamma = []
        for rv in np.concatenate([np.linspace(o['r_cont'] * (1 + 1e-3), o['r_hat'], 25), np.geomspace(o['r_hat'], R_MAX, 60)[1:]]):
            jmp = jump_in(b, rv, o['cusp_state'] - 0.05, zstar)
            if jmp is None:
                continue
            gamma.append(dict(r=float(rv), z=float(jmp[0]), x_left=float(jmp[1]), x_right=float(jmp[2]), kind=jmp[3]))
        # r_C：仅隔离段在 z* 处消失的权重（二分；只用于图中标记）
        lo, hi = o['r_hat'], 60.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if x_and_label(zstar * (1 - 1e-12), b, mid)[1] == 'hi':
                lo = mid
            else:
                hi = mid
        d['cases'][case] = dict(b=b, z_sw=zsw, z_star=zstar, r_cont=o['r_cont'], r_hat=o['r_hat'],
                                cusp_state=o['cusp_state'], r_C=0.5 * (lo + hi), gamma=gamma)
        arrays[case + '_z'], arrays[case + '_r'], arrays[case + '_y'] = z, r, Y
        print(case, 'grid done; gamma points', len(gamma), 'r_C', round(0.5 * (lo + hi), 4), flush=True)
    # 基准剖面
    P = PR.CASES['base']
    b, zstar = P.z_bar, d['cases']['base']['z_star']
    zp = np.linspace(1.0, zstar, 4001)
    for k, rv in enumerate(REP):
        arrays[f'profile_{k}_x'] = np.array([1.0] + [x_and_label(zv, b, rv)[0] for zv in zp[1:]])
    arrays['profile_z'] = zp
    np.savez_compressed(NPZ, **arrays)
    d['npz_sha256'] = sha(NPZ)
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8', newline='\n')
    return d, arrays


def render(d, arrays):
    plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman', 'STIXGeneral', 'DejaVu Serif'],
                         'mathtext.fontset': 'stix', 'font.size': 8, 'axes.titlesize': 8, 'axes.labelsize': 9,
                         'xtick.labelsize': 8, 'ytick.labelsize': 8, 'pdf.fonttype': 42, 'svg.fonttype': 'none',
                         'axes.linewidth': .65, 'axes.spines.top': False, 'axes.spines.right': False,
                         'legend.frameon': False})
    cmap = LinearSegmentedColormap.from_list('contact_share', ['#f5f9fd', '#a6cbe6', '#206fb6', '#062e5c'])
    colors = {'continuous': '#161616', 'endpoint': '#c23b22', 'internal': '#9b3a97'}
    halo = [pe.Stroke(linewidth=2.4, foreground='white'), pe.Normal()]
    fig = plt.figure(figsize=(174 / 25.4, 150 / 25.4))
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, .045], left=.085, right=.93, bottom=.16, top=.95,
                          hspace=.45, wspace=.18)
    axA, axB, cax = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 2])
    axC, axD = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
    for k, (ax, case, name) in enumerate(((axA, 'base', 'Baseline'), (axB, 'xian', "Xi'an"))):
        c = d['cases'][case]
        z, r, Y = (arrays[case + '_' + v] for v in ('z', 'r', 'y'))
        pc = ax.pcolormesh(z, r, Y, cmap=cmap, vmin=0, vmax=1, shading='auto', rasterized=True)
        Ym = np.where(Y > 0, Y, np.nan)
        for levs, col in (([v for v in LEVELS if v <= .5], '#3d3d3a'), ([v for v in LEVELS if v > .5], 'white')):
            cs_ = ax.contour(z, r, Ym, levels=levs, colors=col, linewidths=.55)
            pos = []
            for v in levs:
                for zc in (1.75, 1.45, 1.2, 2.08, 2.18):
                    j = int(np.argmin(np.abs(z - zc)))
                    hit = np.flatnonzero((Y[:-1, j] - v) * (Y[1:, j] - v) < 0)
                    if hit.size:
                        pos.append((z[j], r[hit[0]]))
                        break
            ax.clabel(cs_, fmt=lambda v: f'{v:g}', fontsize=6.5, inline=True, inline_spacing=1, manual=pos)
        g = c['gamma']
        for kind in ('internal', 'endpoint'):
            pts = [(p['z'], p['r']) for p in g if p['kind'] == kind]
            if pts:
                ax.plot(*zip(*pts), color=colors[kind], lw=1.2)
        ax.plot([c['z_sw'], c['z_sw']], [0.9, c['r_hat']], color=colors['continuous'], lw=1.0)
        ax.plot(c['z_sw'], c['r_hat'], 'D', ms=3.6, mfc='white', mec='#161616', mew=.8, zorder=6)
        ax.plot(c['z_star'], c['r_C'], 'v', ms=4, color='#161616', zorder=6, clip_on=False)
        if case == 'base':
            for rv, col in zip(REP, REP_COLORS):
                ax.axhline(rv, color=col, lw=1.0, ls=(0, (4, 2)), path_effects=halo)
        else:
            ax.axhline(2, color='#666666', lw=.7, ls=':')
        ax.set(xlim=(c['z_star'], 1), ylim=(.92, R_MAX), yscale='log')
        ax.set_yticks([1, 2, 3, 5, 10, 20]); ax.set_yticklabels(['1', '2', '3', '5', '10', '20']); ax.minorticks_off()
        ax.set_xlabel(r'$S/S_c$  (time $\rightarrow$)')
        if k == 0:
            ax.set_ylabel(r'$r=w_q/w_c$')
        else:
            ax.tick_params(labelleft=False)
        ax.set_title(f'({chr(97 + k)}) {name}: cost-optimal combination', loc='left')
    cb = fig.colorbar(pc, cax=cax)
    cb.set_label(r'$y$', rotation=0, labelpad=5)
    for v in LEVELS:
        cb.ax.axhline(v, color='#3d3d3a' if v <= .5 else 'white', lw=.55)
    P = PR.CASES['base']
    c = d['cases']['base']
    zp = arrays['profile_z']
    profile_receipt = []
    for kk, (rv, col) in enumerate(zip(REP, REP_COLORS)):
        x = arrays[f'profile_{kk}_x']
        jumps = profile_jumps(P.z_bar, rv, zp, x)
        profile_receipt.append(dict(r=rv, jumps=[dict(z=float(zj), x_left=float(xl), x_right=float(xr), kind=kd)
                                                 for _, zj, xl, xr, kd in jumps]))
        cuts = [j + 1 for j, *_ in jumps]                 # 只在确认的跳变处断开曲线
        q = lambda xv, zv: 1 - (1 - P.q0) / (xv * zv)
        for ax, yv in ((axC, x), (axD, q(x, zp))):
            for m, (a, e) in enumerate(zip([0] + cuts, cuts + [zp.size])):
                ax.plot(zp[a:e], yv[a:e], color=col, lw=1.3, label=f'$r={rv:g}$' if m == 0 else None)
        for _, zj, xl, xr, _ in jumps:                    # 跳变处画竖直点线，连接两侧的最优取值
            axC.plot([zj, zj], [xl, xr], color=col, lw=.7, ls=(0, (2, 1.5)))
            axD.plot([zj, zj], [q(xl, zj), q(xr, zj)], color=col, lw=.7, ls=(0, (2, 1.5)))
    for ax, lab, yl in ((axC, '(c) Baseline: contact rate', r'$c^*/c_0$'),
                        (axD, '(d) Baseline: quarantine fraction', r'$q^*$')):
        ax.set_xlim(c['z_star'], 1)
        ax.axvline(c['z_sw'], color='#555555', ls='--', lw=.7)
        ax.set_xlabel(r'$S/S_c$  (time $\rightarrow$)')
        ax.set_ylabel(yl)
        ax.set_title(lab, loc='left')
    axD.axhline(P.q0, color='#888888', lw=.6)
    axD.text(c['z_star'] - .05, P.q0 + .012, r'$q_0$', fontsize=7.5, color='#666666', va='bottom')
    axD.legend(fontsize=7.5, loc='upper right', handlelength=2.2)
    handles = [Line2D([], [], c=colors['continuous'], lw=1.0, label=r'Continuous switch at $S_{\rm sw}$'),
               Line2D([], [], c=colors['endpoint'], lw=1.2, label='Jump from quarantine-only'),
               Line2D([], [], c=colors['internal'], lw=1.2, label='Interior-to-interior jump'),
               Line2D([], [], c='#555555', ls='--', lw=.7, label=r'$S_{\rm sw}/S_c$')]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .005), ncol=4, fontsize=7.5,
               columnspacing=1.6, handlelength=2.4)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT.with_suffix('.pdf'), dpi=400)
    fig.savefig(OUT.with_suffix('.svg'), dpi=400)
    svg = OUT.with_suffix('.svg')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines()) + '\n',
                   encoding='utf-8', newline='\n')
    fig.savefig(ROOT / 'paper/revision_notes/NEW_4e_figure7_after.png', dpi=200)
    plt.close(fig)
    (RESULTS / 'new4d_figure7_render.json').write_text(json.dumps(dict(
        render_script_sha256=text_sha(__file__), data_sha256=text_sha(DATA), npz_sha256=sha(NPZ),
        pdf_sha256=sha(OUT.with_suffix('.pdf')), width_mm=174, height_mm=150, profile_jumps=profile_receipt,
        source_hashes_unchanged=inputs() == d['source_hashes']), indent=2), encoding='utf-8', newline='\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reuse-data', action='store_true')
    args = ap.parse_args()
    if args.reuse_data:
        d = json.loads(DATA.read_text(encoding='utf-8'))
        if inputs() != d['source_hashes'] or sha(NPZ) != d['npz_sha256']:
            raise ValueError('图7输入或缓存已变，不能复用')
        arrays = dict(np.load(NPZ))
    else:
        d, arrays = compute()
    render(d, arrays)


if __name__ == '__main__':
    main()
