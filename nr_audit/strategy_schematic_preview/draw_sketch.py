"""绘制独立的阈值策略概念草图，不读写论文源文件或历史数值结果。

左图使用首次积分的示意坐标；右图画一个允许控制的三阶段时间示意。
坐标不对应论文中的任一参数组，也不求解 ODE、优化或参数扫描。
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np


OUT = Path(__file__).resolve().parent
BLUE = "#1756a9"
RED = "#c53737"
GRAY = "#8b9198"
INK = "#20262c"

plt.rcParams.update({
    "font.family": "Times New Roman",
    "mathtext.fontset": "stix",
    "font.size": 12,
    "axes.labelsize": 13,
    "axes.titlesize": 14,
    "axes.linewidth": 0.9,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "svg.fonttype": "none",
    "savefig.facecolor": "white",
})


def arrow(ax, start, end, color=BLUE, lw=1.7, size=13, **kwargs):
    patch = FancyArrowPatch(start, end, arrowstyle="-|>",
                            mutation_scale=size, color=color,
                            linewidth=lw, zorder=6, **kwargs)
    ax.add_patch(patch)


fig = plt.figure(figsize=(13.4, 6.1))
ax = fig.add_axes([0.065, 0.30, 0.405, 0.56])
bx = fig.add_axes([0.58, 0.30, 0.365, 0.56])
for axis in (ax, bx):
    axis.spines[["top", "right"]].set_visible(False)
    axis.tick_params(direction="out", length=4)

# 左图：用解析首次积分画形状，不给出实际人数或时间读数。
sc, s_star, s0, eta = 1.0, 3.0, 4.0, 0.8
shared_ylim = (0, 1.98)
routine = lambda s: eta + s_star - s + np.log(s / s_star)
after = lambda s: eta + sc - s + np.log(s / sc)
s_routine = np.linspace(s0, 0.03, 900)
i_routine = routine(s_routine)
mask = i_routine >= 0
ax.plot(s_routine[mask], i_routine[mask], color=GRAY, lw=1.8,
        ls=(0, (3.5, 2.8)), zorder=1)
ax.axhline(eta, color=RED, lw=1.1, ls=(0, (5, 3)), zorder=0)
ax.axvline(sc, color="#bfc5cb", lw=1, ls=(0, (2, 3)), zorder=0)
s_pre = np.linspace(s0, s_star, 220)
s_post = np.linspace(sc, 0.03, 500)
i_post = after(s_post)
keep = i_post >= 0
ax.plot(s_pre, routine(s_pre), color=BLUE, lw=2.8)
ax.plot([s_star, sc], [eta, eta], color=BLUE, lw=3.2)
ax.plot(s_post[keep], i_post[keep], color=BLUE, lw=2.8)
ax.scatter([s_star, sc], [eta, eta], s=48, color=BLUE,
           edgecolors="white", linewidths=1, zorder=7)
ax.scatter([s0], [routine(s0)], s=24, color=BLUE, zorder=7)
arrow(ax, (3.78, routine(3.78)), (3.48, routine(3.48)))
arrow(ax, (2.3, eta), (1.78, eta), lw=2.2, size=15)
arrow(ax, (0.68, after(0.68)), (0.47, after(0.47)))

ax.annotate(r"Start at $t_1$" + "\n" + r"$(S^*,\eta)$", xy=(s_star, eta),
            xytext=(3.48, 1.11), ha="center", va="center",
            arrowprops={"arrowstyle": "-", "color": "#56616a", "lw": 0.8},
            fontsize=12)
ax.annotate(r"Exit at $t_2$" + "\n" + r"$(S_c,\eta)$", xy=(sc, eta),
            xytext=(0.64, 1.09), ha="center", va="center",
            arrowprops={"arrowstyle": "-", "color": "#56616a", "lw": 0.8},
            fontsize=12)
ax.text(2.04, 0.96, r"$I=\eta,\quad R_e=1$", ha="center",
        color=BLUE, fontsize=13)
ax.text(1.72, 1.72, "Routine control throughout", color="#747b83",
        ha="center", fontsize=11)
ax.text(3.75, 0.63, "Routine", ha="center", fontsize=11)
ax.text(0.75, 0.24, "Routine", ha="center", fontsize=11)
ax.text(2.05, 0.57, "Threshold control", ha="center", color=BLUE, fontsize=12)
ax.set(xlim=(0, 4.22), ylim=shared_ylim,
       xticks=[sc, s_star, s0], xticklabels=[r"$S_c$", r"$S^*$", r"$S_0$"],
       yticks=[eta], yticklabels=[r"$\eta$"],
       xlabel=r"Community susceptible individuals, $S$",
       ylabel=r"Non-isolated infected individuals, $I$")
ax.set_title("(a) Threshold strategy in state space", loc="left", pad=17)
ax.annotate("", xy=(0.15, -0.235), xytext=(0.87, -0.235),
            xycoords="axes fraction", annotation_clip=False,
            arrowprops={"arrowstyle": "-|>", "color": INK, "lw": 1})
ax.text(0.51, -0.31, "Time advances as S decreases", transform=ax.transAxes,
        ha="center", va="center", fontsize=11)

# 右图：只画代表性时间曲线。启动处连续但可有折角，退出处水平相切。
# 下式仅指定草图的形状，不对应某一参数组的 ODE 解。
t1, t2, t_max = 2.4, 6.1, 11.0
t_pre = np.linspace(0, t1, 200)
t_post = np.linspace(t2, t_max, 350)
i0_sketch = routine(s0)
growth = np.log(eta / i0_sketch) / t1
i_pre = i0_sketch * np.exp(growth * t_pre)
i_post_time = eta * np.exp(-0.22 * (t_post - t2)**2)
# 常规对照在启动前与蓝线相同，随后保持正斜率，并与左图匹配峰高。
# 该解析形状只用于示意，不是新的 ODE 仿真结果。
t_routine_after = np.linspace(t1, t_max, 500)
peak_log_ratio = np.log(routine(sc) / eta)
curvature = growth**2 / (4 * peak_log_ratio)
elapsed = t_routine_after - t1
i_routine_time = eta * np.exp(growth * elapsed - curvature * elapsed**2)
bx.axvspan(t1, t2, color="#eaf2fc", zorder=0)
bx.axhline(eta, color=RED, lw=1.1, ls=(0, (5, 3)), zorder=1)
for time in (t1, t2):
    bx.axvline(time, color="#a7afb7", lw=1, ls=(0, (3, 3)), zorder=1)
bx.plot(np.concatenate([t_pre, t_routine_after[1:]]),
        np.concatenate([i_pre, i_routine_time[1:]]),
        color=GRAY, lw=1.8, ls=(0, (3.5, 2.8)), zorder=1)
bx.plot(t_pre, i_pre, color=BLUE, lw=2.8)
bx.plot([t1, t2], [eta, eta], color=BLUE, lw=3.2)
bx.plot(t_post, i_post_time, color=BLUE, lw=2.8)
bx.scatter([t1, t2], [eta, eta], s=48, color=BLUE,
           edgecolors="white", linewidths=1, zorder=7)
bx.text(t1 / 2, 1.83, "Routine\ncontrol", ha="center", va="center", fontsize=12)
bx.text((t1 + t2) / 2, 1.83, "Threshold\ncontrol", ha="center", va="center",
        color=BLUE, fontsize=12)
bx.text((t2 + t_max) / 2, 1.83, "Return to\nroutine control", ha="center",
        va="center", fontsize=12)
routine_peak_time = t1 + growth / (2 * curvature)
bx.annotate("Routine control\nthroughout", xy=(routine_peak_time + 0.25, routine(sc) - 0.03),
            xytext=(7.4, 1.49), ha="center", va="center", color="#747b83",
            fontsize=11,
            arrowprops={"arrowstyle": "-", "color": GRAY, "lw": 0.8})
bx.text((t1 + t2) / 2, 0.58, r"$I=\eta,\quad R_e=1$", color=BLUE,
        ha="center", fontsize=13)
bx.set(xlim=(0, t_max), ylim=shared_ylim,
       xticks=[0, t1, t2], xticklabels=["0", r"$t_1$", r"$t_2$"],
       yticks=[eta], yticklabels=[r"$\eta$"],
       xlabel=r"Time, $t$",
       ylabel=r"Non-isolated infected individuals, $I(t)$")
bx.set_title("(b) Three stages in time", loc="left", pad=17)
bx.annotate("", xy=(t1 / t_max, -0.235), xytext=(t2 / t_max, -0.235),
            xycoords="axes fraction", annotation_clip=False,
            arrowprops={"arrowstyle": "|-|", "color": BLUE, "lw": 1.2})
bx.text((t1 + t2) / (2 * t_max), -0.31, r"$\Delta t=t_2-t_1$",
        transform=bx.transAxes, ha="center", va="center", color=BLUE, fontsize=12)

fig.text(0.5, 0.045,
         "Conceptual sketch of a threshold strategy; axes are schematic.",
         ha="center", va="center", fontsize=11, color="#606a74")
# 验证两图的阈值位置在最终画布中完全对齐。
fig.canvas.draw()
assert ax.get_ylim() == bx.get_ylim()
assert abs(ax.transData.transform((0, eta))[1]
           - bx.transData.transform((0, eta))[1]) < 1e-8
fig.savefig(OUT / "threshold_strategy_time_sketch.png", dpi=200)
fig.savefig(OUT / "threshold_strategy_time_sketch.svg")
plt.close(fig)
print(OUT / "threshold_strategy_time_sketch.png")
print(OUT / "threshold_strategy_time_sketch.svg")
