"""NEW-4ap（N44）：删去能力约束后，正文图 8（fig:xian:joint）改为与图 6 相同的版面。

- (a) 西安参数的权重相图：复用 results/new4w/xian_phase.npz 与 xian_theta001.json 的 phase.case
  （使用前按 results/new4al_notation.json 登记的 SHA-256 校验），画法同 NEW-4t 接收版的图 6、图 8：
  plot_new4p_figures.phase_panel 加 parula 色带、红色点划等高线、黑色等值数字，色柱只留色带与刻度。
- (b)(c) 五个代表权重 r = 1, 2, 2.63, 4, 10 的接触率与隔离比例剖面：用图 6 剖面的同一逐状态求解器
  （plot_figure7_contour.x_and_label，即 allocation.argmin_state，定理 5.1 的有限比较）在 S/S_c ∈ [1, S*/S_c]
  的 2001 个等距点上求解，跳变位置用同一模块的 profile_jumps 二分定位。这是本轮新增的计算（N44 授权）；
  不解 ODE、不重算相图背景，西安参数、初值与既有结果文件不变。

另写出第 7.2 节引用的剖面读数（results/new4ap_fig8.json），由 make_numbers.new4ap_readings() 生成宏。

运行（仓库根目录）：E:/anaconda/envs/thesis/python.exe -X utf8 nr_audit/plot_new4ap_fig8.py
输出：paper/figures/new4ap/Main8.pdf，PNG 预览 paper/tmp/new4ap/Main8.png，
      收据 nr_audit/results/new4ap_fig8.json，剖面数组 nr_audit/results/new4ap_fig8_profiles.npz。
"""
import hashlib
import json

import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import QuadMesh

import params as PR
import plot_figure7_contour as F7
import plot_new4p_figures as P
import plot_xian_fig2_style as F2
import preview_style_common as PC
from audit_common import ROOT, RESULTS, dump

W3 = RESULTS / 'new4w'
FIG = ROOT / 'paper/figures/new4ap'
PREVIEW = ROOT / 'paper/tmp/new4ap'
NPZ_OUT = RESULTS / 'new4ap_fig8_profiles.npz'
REP = (1.0, 2.0, 2.63, 4.0, 10.0)          # 连续两档、r_cont 与 r̂ 之间、由仅隔离段跳入、没有仅隔离段
N_PROFILE = 2001
INPUTS = [W3 / 'xian_theta001.json', W3 / 'xian_phase.npz']
CODE = [ROOT / 'nr_audit' / n for n in ('allocation.py', 'plot_figure7_contour.py', 'plot_new4p_figures.py',
                                         'preview_style_common.py', 'plot_xian_fig2_style.py', 'params.py')]
AUTH = 'AGENTS.md N44（NEW-4ap）：作者 2026-11-15 决定删去能力约束，图 8 改为权重相图加两幅剖面'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def check_inputs():
    """输入在使用前按最近一次登记（NEW-4al 收据，图 8 的上一版即由它生成）的身份校验。"""
    reg = json.loads((RESULTS / 'new4al_notation.json').read_text(encoding='utf-8'))['inputs']
    out = {}
    for p in INPUTS:
        key = p.relative_to(ROOT).as_posix()
        got = dict(sha256=sha(p), content_sha256=text_sha(p) if p.suffix == '.json' else sha(p))
        exp = reg[key]
        assert got['sha256'] == exp['sha256'] or got['content_sha256'] == exp['content_sha256'], f'输入身份不符：{key}'
        out[key] = got
    return out


def profiles(case, q0):
    b, zstar = case['b'], case['z_star']
    zp = np.linspace(1.0, zstar, N_PROFILE)
    xs, jumps = [], []
    for rv in REP:
        x = np.array([1.0] + [F7.x_and_label(zv, b, rv)[0] for zv in zp[1:]])
        js = [dict(z=float(j[1]), x_left=float(j[2]), x_right=float(j[3]), kind=j[4]) for j in F7.profile_jumps(b, rv, zp, x)]
        xs.append(x)
        jumps.append(js)
    return zp, xs, jumps


def readings(case, q0, zp, xs, jumps):
    """第 7.2 节引用的剖面读数：c/c0 = x，q = 1 - (1-q0)/(x z)。"""
    q = lambda x, z: 1 - (1 - q0) / (x * z)
    out = []
    for rv, x, js in zip(REP, xs, jumps):
        k_min = int(np.argmin(x))
        out.append(dict(r=rv, jumps=js, min_c_over_c0=float(x[k_min]), z_at_min=float(zp[k_min]),
                        start_c_over_c0=float(x[-1]), start_q=float(q(x[-1], zp[-1])),
                        quarantine_only_at_start=bool(abs(x[-1] - 1) < 1e-12)))
    by = {d['r']: d for d in out}
    # 读数与相图的结构判据一致：r_cont < 2.63 < r̂ < 4 < B→C < 10
    assert case['r_cont'] < 2.63 < case['r_hat'] < 4.0 < case['r_C'] < 10.0, case
    assert not by[1.0]['jumps'] and not by[2.0]['jumps'] and not by[10.0]['jumps']
    j263, j4 = by[2.63]['jumps'], by[4.0]['jumps']
    assert len(j263) == 1 and j263[0]['kind'] == 'internal' and j263[0]['z'] < case['z_sw']
    assert len(j4) == 1 and j4[0]['kind'] == 'endpoint' and j4[0]['z'] > case['z_sw'] and j4[0]['x_right'] == 1.0
    assert by[1.0]['quarantine_only_at_start'] and by[4.0]['quarantine_only_at_start'] and not by[10.0]['quarantine_only_at_start']
    # 闭式核对：r_cont < r < r̂ 时两个内部取值之间的跳变位于 ζ_j = 2[b + (1-b)√r]（补充命题 prop:sup:jump）
    zj = 2 * (case['b'] + (1 - case['b']) * np.sqrt(2.63))
    assert abs(j263[0]['z'] - zj) < 2 * (zp[1] - zp[0]), (j263[0]['z'], zj)
    # r = 2 的最大接触降幅与表 3 注下的读数（第 7.2 节 28.2%）一致
    assert f"{100 * (1 - by[2.0]['min_c_over_c0']):.1f}" == '28.2'
    return out, float(zj)


def render(case, arrays, zp, xs, jumps, q0):
    q = lambda x, z: 1 - (1 - q0) / (x * z)
    with plt.rc_context(PC.RC):
        fig = plt.figure(figsize=(P.TEXT_WIDTH_IN, 90 * P.MM))
        outer = fig.add_gridspec(1, 2, width_ratios=[1.12, 1], left=.065, right=.985, bottom=.11, top=.945, wspace=.2)
        left = outer[0].subgridspec(1, 2, width_ratios=[1, .045], wspace=.06)
        right = outer[1].subgridspec(2, 1, hspace=.32)
        ax_a, cax = fig.add_subplot(left[0]), fig.add_subplot(left[1])
        ax_b = fig.add_subplot(right[0])
        ax_c = fig.add_subplot(right[1], sharex=ax_b)
        pc, chk = P.phase_panel(ax_a, dict(cases=dict(xian=case)), arrays, 'xian',
                                [(rv, col, (0, (3, 1.6))) for rv, col in zip(REP, P.REP_COLORS)])
        ax_a.set_title('(a) Cost-optimal combination')
        P.colorbar(fig, pc, cax)
        # NEW-4t 接收版的样式：parula 色带，红色点划等高线、黑色数字，色柱只保留色带与刻度
        mesh = next(c for c in ax_a.collections if isinstance(c, QuadMesh))
        mesh.set_cmap(PC.palette())
        for c in ax_a.collections:
            if c is not mesh and hasattr(c, 'levels'):
                c.set_edgecolor(P.RED)
                c.set_linestyle('-.')
                c.set_linewidth(.6)
        for t in ax_a.texts:
            if t.get_text() in {f'0.{k}' for k in range(1, 10)}:
                t.set_color(P.BLACK)
                t.set_path_effects([])
        for line in list(cax.lines):
            line.remove()
        for rv, col, x, js in zip(REP, P.REP_COLORS, xs, jumps):
            cuts = [int(np.searchsorted(zp, j['z'])) for j in js]       # 跳变在 zp[cut-1] 与 zp[cut] 之间
            for ax, yv in ((ax_b, x), (ax_c, q(x, zp))):
                for m, (a, e) in enumerate(zip([0] + cuts, cuts + [zp.size])):
                    ax.plot(zp[a:e], yv[a:e], color=col, lw=1.2, label=f'$r={rv:g}$' if m == 0 else None)
            for j in js:
                ax_b.plot([j['z']] * 2, [j['x_left'], j['x_right']], color=col, lw=P.STYLE['lw_vline'], ls=':')
                ax_c.plot([j['z']] * 2, [q(j['x_left'], j['z']), q(j['x_right'], j['z'])], color=col,
                          lw=P.STYLE['lw_vline'], ls=':')
        for ax, title, ylabel in ((ax_b, r'(b) $c(t)$', r'$c_c^*/c_0$'), (ax_c, r'(c) $q(t)$', r'$q_c^*$')):
            ax.set_xlim(case['z_star'], 1)
            ax.axvline(case['z_sw'], color=P.GRAY, ls='--', lw=P.STYLE['lw_vline'])
            ax.set_ylabel(ylabel)
            ax.set_title(title)
        ax_b.tick_params(labelbottom=False)
        ax_c.set_xlabel(r'$S/S_c$ (time $\rightarrow$)')
        ax_b.set_ylim(.2, 1.04)
        ax_c.set_ylim(q0 - .04, .9)
        ax_c.axhline(q0, color=P.BLACK, lw=P.STYLE['lw_vline'], ls='-.', alpha=P.STYLE['ref_alpha'])
        ax_c.text(case['z_star'] - .05, q0 + .012, r'$q_0$', fontsize=P.STYLE['note'], va='bottom')
        F2.frame_legend(ax_c.legend(loc='upper right', ncol=2, columnspacing=1.0, handlelength=1.8))
        FIG.mkdir(parents=True, exist_ok=True)
        PREVIEW.mkdir(parents=True, exist_ok=True)
        pdf = FIG / 'Main8.pdf'
        fig.savefig(pdf, dpi=600, metadata={'CreationDate': None, 'ModDate': None})
        fig.savefig(PREVIEW / 'Main8.png', dpi=200)
        plt.close(fig)
    return chk, sha(pdf)


def main():
    inputs = check_inputs()
    w3 = json.loads((W3 / 'xian_theta001.json').read_text(encoding='utf-8'))
    case = w3['phase']['case']
    X = PR.CASES['xian']
    assert abs(case['b'] - X.z_bar) < 1e-12
    with np.load(W3 / 'xian_phase.npz') as d:
        arrays = {k: d[k] for k in d.files}
    zp, xs, jumps = profiles(case, X.q0)
    rd, zj = readings(case, X.q0, zp, xs, jumps)
    np.savez_compressed(NPZ_OUT, profile_z=zp, **{f'profile_{k}_x': x for k, x in enumerate(xs)})
    chk, pdf_sha = render(case, arrays, zp, xs, jumps, X.q0)
    dump('new4ap_fig8.json', dict(
        script='nr_audit/plot_new4ap_fig8.py', authorization=AUTH, label='fig:xian:joint',
        inputs=inputs, code={p.relative_to(ROOT).as_posix(): text_sha(p) for p in CODE},
        scientific_activity=dict(ode_solves=0, phase_background_recomputed=False, fits=0,
                                 per_state_minimizations=len(REP) * (N_PROFILE - 1),
                                 note='五个权重各 2000 个状态的逐状态有限比较（定理 5.1），另有 profile_jumps 的二分；不解 ODE'),
        rep_weights=list(REP), profile_points=N_PROFILE, case=dict(b=case['b'], z_sw=case['z_sw'], z_star=case['z_star'],
                                                                   r_cont=case['r_cont'], r_hat=case['r_hat'], r_C=case['r_C']),
        zeta_j_closed_form_r263=zj, readings=rd, phase_checks=chk,
        profiles_npz=dict(path=NPZ_OUT.relative_to(ROOT).as_posix(), sha256=sha(NPZ_OUT)),
        output=dict(pdf='paper/figures/new4ap/Main8.pdf', pdf_sha256=pdf_sha,
                    replaces='paper/figures/new4al/Main8.pdf（只读保留）')))
    print(json.dumps(rd, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
