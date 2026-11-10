"""NEW-4aj：正文图 1（fig:model_schematic）改为两幅——(a) 现有仓室示意图，(b) 阈值策略在 (S,I) 平面上的示意。

(a) 原样引用 paper/figures/Fig1.pdf（作者 PowerPoint 导出，不改文件），只在引用时裁去四周空白。
(b) 按正文图 2 的风格（plot_xian_fig2_style：Computer Modern、蓝色实线为阈值策略、黑色点划线为常规控制、
红色虚线为阈值、黑色点线标记 t1/t2）在印刷尺寸下直接绘制；刻度都是带下标的符号，字号比图 2 各大约 1 pt。
曲线形状取自常规轨迹的首次积分 I(S)=C+(beta2/beta1)(S_ref-S)+rho1*ln(S/S_ref)，取示意常数 rho1=1、S_c=1，
不对应任一参数组；不解 ODE、不优化、不读取任何数值结果。横轴 S 自左向右增大（与 Miclo 等的相图一致），
时间沿轨迹从右向左推进。两幅由 pdflatex 拼成一个 PDF，(a)(b) 标签用 Computer Modern。

运行（仓库根目录）：python nr_audit/plot_fig1_combined.py
输出 paper/figures/new4aj/Fig1_combined.pdf 与 nr_audit/results/new4aj_fig1.json；中间文件在 paper/tmp/new4aj/（不入库）。
"""
import hashlib
import json
import re
import shutil
import subprocess

import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.transforms import blended_transform_factory

import plot_xian_fig2_style as F2   # 只取样式常数
from audit_common import ROOT

STYLE, RC = F2.STYLE, F2.RC
FIG1 = ROOT / 'paper' / 'figures' / 'Fig1.pdf'
BUILD = ROOT / 'paper' / 'tmp' / 'new4aj'
OUT = ROOT / 'paper' / 'figures' / 'new4aj'
RECEIPT = ROOT / 'nr_audit' / 'results' / 'new4aj_fig1.json'
TW = F2.TEXT_WIDTH_PT

# Fig1.pdf 页面 850.56×576 bp；按 300 dpi 渲染量得的空白边（左 33.6、下 32.9、右 3.8、上 18.7 bp）
# 各留约 1 bp 后裁去，只改引用时的显示范围，不改 Fig1.pdf 本身。
FIG1_PAGE = (850.56, 576.0)
FIG1_TRIM = (32.5, 32.0, 2.5, 17.5)     # 左、下、右、上（bp）
FIG1_ASPECT = ((FIG1_PAGE[0] - FIG1_TRIM[0] - FIG1_TRIM[2])
               / (FIG1_PAGE[1] - FIG1_TRIM[1] - FIG1_TRIM[3]))
W_LEFT, W_RIGHT = 0.50 * TW, 0.48 * TW  # 两幅在版心中的宽度（pt）
HEIGHT = W_LEFT / FIG1_ASPECT           # 左图高度，也是右图坐标框的高度
PAD_B, PAD_T = 19.0, 2.0                # 右图坐标框下方（刻度与轴标签）与上方的留白（pt）
H_RIGHT = HEIGHT + PAD_B + PAD_T        # 左图与右图坐标框上下对齐，刻度标签伸到左图下方

# 示意常数：S_c=1，rho1=1（于是 beta2/beta1=1）；beta2/beta1 只缩放纵轴，不改形状。
# S0、S* 与 eta 的取法使三个阶段在横轴上的宽度相近，起点 I0≈0.03。
SC, S_STAR, S0, ETA = 1.0, 2.2, 2.69, 0.316


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def orbit(s, s_ref, i_ref):
    """常规控制下过 (s_ref, i_ref) 的轨道。"""
    return i_ref + (s_ref - s) / SC + np.log(s / s_ref)


def arrow(ax, s_from, s_to, f, color):
    ax.add_patch(FancyArrowPatch((s_from, f(s_from)), (s_to, f(s_to)),
                                 arrowstyle='-|>,head_length=0.7,head_width=0.35',
                                 mutation_scale=6.5, color=color, lw=0.5, zorder=6))


def draw_panel():
    plt.rcParams.update(RC)
    plt.rcParams.update({'xtick.top': False, 'ytick.right': False, 'xtick.labelsize': 6.5,
                         'ytick.labelsize': 6.5, 'axes.labelsize': 7.0})
    fig = plt.figure(figsize=(W_RIGHT / 72, H_RIGHT / 72))
    left, right = 17 / W_RIGHT, 1 - 3 / W_RIGHT
    bottom, top = PAD_B / H_RIGHT, 1 - PAD_T / H_RIGHT
    ax = fig.add_axes([left, bottom, right - left, top - bottom])
    blue, black, red = F2.BLUE, F2.BLACK, F2.RED

    pre = lambda s: orbit(s, S_STAR, ETA)   # 启动前与“始终常规控制”同一条轨道
    post = lambda s: orbit(s, SC, ETA)      # 退出后的常规轨道
    s_dash = np.linspace(S_STAR, 0.02, 800)
    i_dash = pre(s_dash)
    ax.plot(s_dash[i_dash >= 0], i_dash[i_dash >= 0], color=black, ls='-.',
            lw=STYLE['lw_ref'], zorder=2)
    ax.axhline(ETA, color=red, ls='--', lw=STYLE['lw_ref'], alpha=STYLE['ref_alpha'], zorder=1)
    for s in (S_STAR, SC):
        ax.axvline(s, color=black, ls=':', lw=STYLE['lw_vline'], alpha=STYLE['ref_alpha'], zorder=1)

    s_pre = np.linspace(S0, S_STAR, 200)
    s_post = np.linspace(SC, 0.02, 600)
    i_post = post(s_post)
    kw = dict(color=blue, lw=STYLE['lw_main'], solid_capstyle='round', zorder=4)
    ax.plot(s_pre, pre(s_pre), **kw)
    ax.plot([S_STAR, SC], [ETA, ETA], **kw)
    ax.plot(s_post[i_post >= 0], i_post[i_post >= 0], **kw)
    ax.plot([S0, S_STAR, SC], [pre(S0), ETA, ETA], 'o', ms=2.6, color=blue, mec='white',
            mew=0.4, zorder=7)
    arrow(ax, 2.56, 2.40, pre, blue)
    arrow(ax, 1.68, 1.52, lambda s: ETA + 0 * s, blue)
    arrow(ax, 0.76, 0.66, post, blue)

    x_right, ytop = S0 + 0.16, 1.0
    note = STYLE['note'] + 0.5
    ax.text((x_right + S_STAR) / 2, ytop - 0.035, 'Baseline\ncontrol', ha='center', va='top',
            fontsize=note, linespacing=1.1)
    ax.text((S_STAR + SC) / 2, ytop - 0.035, 'Threshold-control phase', ha='center', va='top',
            fontsize=note)
    ax.text(SC / 2, ytop - 0.035, 'Baseline\ncontrol', ha='center', va='top', fontsize=note,
            linespacing=1.1)
    ax.text((S_STAR + SC) / 2, ETA - 0.04, r'$R_e=1$', ha='center', va='top', fontsize=note,
            color=blue)
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for s, lab in ((S_STAR, r'$t_1$'), (SC, r'$t_2$')):
        ax.text(s + 0.03, 0.04, lab, transform=tr, ha='left', va='bottom', fontsize=note)

    ax.set_xlim(0, x_right)
    ax.set_ylim(0, ytop)
    ax.set_xticks([S0, S_STAR, SC], [r'$S_0$', r'$S^*$', r'$S_c$'])
    ax.set_yticks([ETA], [r'$\eta$'])
    ax.set_xlabel(r'$S$')
    ax.set_ylabel(r'$I$', rotation=0, labelpad=2, va='center')
    pdf = BUILD / 'fig1b_panel.pdf'
    fig.savefig(pdf, metadata={'CreationDate': None, 'ModDate': None})
    axes_center = (left + right) / 2      # (b) 标签对准坐标框中心
    plt.close(fig)
    return pdf, axes_center


COMBINED = r"""\pdfinfoomitdate=1
\pdftrailerid{}
\pdfsuppressptexinfo=-1
\documentclass[border=0.5pt]{standalone}
\usepackage{graphicx,tikz}
\begin{document}
\fontsize{7}{8}\selectfont
\begin{tikzpicture}[inner sep=0pt]
\node[anchor=south west] (L) at (0,%(yl).3fpt) {\includegraphics[width=%(wl).3fpt,trim=%(trim)s,clip]{%(fig1)s}};
\node[anchor=south west] (R) at (%(xr).3fpt,0) {\includegraphics[width=%(wr).3fpt]{fig1b_panel.pdf}};
\node[anchor=base] at (%(xa).3fpt,%(yt).3fpt) {(a)};
\node[anchor=base] at (%(xb).3fpt,%(yt).3fpt) {(b)};
\end{tikzpicture}
\end{document}
"""


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    fig1_sha = sha256(FIG1)
    panel, axes_center = draw_panel()
    gap = TW - W_LEFT - W_RIGHT
    tex = COMBINED % dict(wl=W_LEFT, wr=W_RIGHT, xr=W_LEFT + gap, fig1=FIG1.as_posix(),
                          xa=W_LEFT / 2, xb=W_LEFT + gap + axes_center * W_RIGHT,
                          yl=PAD_B, yt=H_RIGHT + 2.0,
                          trim=' '.join(f'{v}bp' for v in FIG1_TRIM))
    (BUILD / 'fig1_combined.tex').write_text(tex, encoding='utf-8', newline='\n')
    subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'fig1_combined.tex'],
                   cwd=BUILD, check=True, stdout=subprocess.DEVNULL)
    out = OUT / 'Fig1_combined.pdf'
    shutil.copyfile(BUILD / 'fig1_combined.pdf', out)
    if sha256(FIG1) != fig1_sha:
        raise RuntimeError('Fig1.pdf 在绘图期间被改动')

    # pdflatex 压缩对象流，字体名不在原始字节中，改用 poppler 的 pdffonts 列出
    listing = subprocess.run(['pdffonts', str(out)], check=True, capture_output=True, text=True).stdout
    fonts = sorted({line.split()[0].split('+')[-1] for line in listing.splitlines()[2:] if line.strip()})
    assert fonts and all(re.search(r'cm(r|mi|sy|ex)\d+', f, re.I) for f in fonts), fonts
    receipt = dict(
        round='NEW-4aj', label='fig:model_schematic', script='nr_audit/plot_fig1_combined.py',
        inputs={'paper/figures/Fig1.pdf': dict(sha256=fig1_sha, use='panel (a), included unchanged',
                                               trim_bp_left_bottom_right_top=list(FIG1_TRIM))},
        outputs={'paper/figures/new4aj/Fig1_combined.pdf': dict(sha256=sha256(out), fonts=fonts)},
        layout=dict(text_width_pt=TW, width_fraction_a=0.50, width_fraction_b=0.48,
                    panel_a_height_pt=HEIGHT, panel_b_height_pt=H_RIGHT,
                    note='(b) 坐标框与 (a) 上下对齐'),
        schematic=dict(formula='I(S)=I_ref+(S_ref-S)/S_c+ln(S/S_ref) (rho1=1, S_c=1)',
                       S_c=SC, S_star=S_STAR, S0=S0, eta=ETA, I0=float(orbit(S0, S_STAR, ETA)),
                       s_axis='increasing left to right; time runs right to left'),
        scientific_activity=dict(ode_solves=0, optimization_solves=0, fits=0, data_files_read=0),
    )
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8',
                       newline='\n')
    print(out, receipt['outputs'][out.relative_to(ROOT).as_posix()]['sha256'])


if __name__ == '__main__':
    main()
