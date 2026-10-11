"""(s, r) 平面上的最优分配相图：r = w_q/w_c，颜色为接触承担份额 y = (1-c/c0)/(1-Sc/S)。"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

import joint_numerics as JN
if not (JN.ROOT / "ai/threshold_control_reproducible_release_20261002").exists():
    JN.ROOT = Path("/home/claude/cuizhizhong/threshold_control")  # 本会话的仓库副本位置
OUT = Path(__file__).resolve().parent

plt.rcParams.update({"font.family": ["Noto Sans CJK SC", "DejaVu Sans"], "axes.unicode_minus": False,
                     "font.size": 9, "axes.titlesize": 10, "axes.titlelocation": "left",
                     "axes.edgecolor": "#8a8a85", "xtick.color": "#5c5c58", "ytick.color": "#5c5c58",
                     "axes.labelcolor": "#3b3b38"})
CMAP = LinearSegmentedColormap.from_list(
    "blue_seq", ["#f4f8fd", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"])

R = np.logspace(-1, np.log10(20), 161)
cases = {"baseline": JN.baseline_params()}
cases["xian"], _ = JN.xian_params()
res = {}
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), constrained_layout=True)
for ax, (case, p) in zip(axes, cases.items()):
    Sc, Sbar, Sstar = JN.basics(p)
    sbar, sst = Sbar / Sc, Sstar / Sc
    ssw = (3 + np.sqrt(9 - 8 * sbar)) / 2
    s = np.linspace(1.0, sst, 1201)
    Y = np.empty((len(R), len(s)))
    switch, two_lo, two_hi = [], [], []
    for i, r in enumerate(R):
        x, nl = JN.allocate(p, s, 1.0, r, nx=3001)
        y = np.where(s > 1 + 1e-12, (1 - x) / np.maximum(1 - 1 / s, 1e-300), r / (1 + r))
        y = np.clip(y, 0, 1)
        Y[i] = y
        q_only = (y < 1e-6) & (s > 1.0005)
        # 全局最优首次进入仅隔离的状态（若存在）
        switch.append(float(s[np.argmax(q_only)]) if q_only.any() else np.nan)
        m = (nl > 1) & (s > 1.0005)
        two_lo.append(float(s[m].min()) if m.any() else np.nan)
        two_hi.append(float(s[m].max()) if m.any() else np.nan)
    switch = np.array(switch)
    jumpy = switch > ssw + 2 * (s[1] - s[0])
    r_dep = float(R[np.argmax(jumpy)]) if jumpy.any() else None          # 切换点离开 s_sw 的最小 r
    r_none = float(R[np.argmax(np.isnan(switch))]) if np.isnan(switch).any() else None  # 仅隔离从不全局最优
    pc = ax.pcolormesh(s, R, Y, cmap=CMAP, vmin=0, vmax=1, shading="auto", rasterized=True)
    ax.contour(s, R, (Y < 1e-6).astype(float), levels=[0.5], colors="#3b3b38", linewidths=1.0)
    ok = ~np.isnan(switch) & jumpy
    ax.plot(switch[ok], R[ok], color="#eb6834", lw=2.0, label="全局最优在此跳到仅隔离")
    ax.axvline(ssw, color="#3b3b38", lw=0.9, ls=(0, (4, 2)))
    ax.text(ssw, 0.105, f"  $s_{{sw}}={ssw:.3f}$", color="#3b3b38", va="bottom")
    ax.axhline(2.0, color="#5c5c58", lw=0.8, ls=":")
    ax.text(sst, 2.0, "论文默认 $r=2$ ", ha="right", va="bottom", color="#3b3b38")
    xq = 0.5 * (ssw + sst)
    ax.text(xq, 0.55, "仅隔离", ha="center", color="#3b3b38", fontsize=10)
    ax.text(1.0 + 0.3 * (sst - 1), 13.0, "以减少接触为主", ha="center", color="#ffffff", fontsize=10)
    ax.text(1.0 + 0.35 * (ssw - 1), 0.5, "两种措施\n混合", ha="center", color="#ffffff"
            if False else "#1f1f1d", fontsize=10)
    ax.set_yscale("log")
    ax.set_ylim(R[0], R[-1])
    ax.set_xlim(1, sst)
    ax.set_xlabel(r"$s=S/S_c$（退出 $s=1$ $\leftarrow$　$\rightarrow$ 启动 $s=s^*$）")
    ax.set_ylabel(r"权重比 $r=w_q/w_c$（对数轴）")
    ax.set_title(("(a) 基准参数" if case == "baseline" else "(b) 西安参数")
                 + f"，$s^*={sst:.3f}$")
    ax.legend(frameon=False, loc="lower right", bbox_to_anchor=(1, 0.1), labelcolor="#1f1f1d")
    res[case] = dict(s_sw=ssw, s_star=sst, sbar=sbar, r_switch_departs_from_ssw=r_dep,
                     r_q_only_never_global=r_none,
                     switch_at=dict(zip([f"{r:.3g}" for r in R[::20]], switch[::20].tolist())),
                     terminal_share_check=float(np.max(np.abs(Y[:, 1] - R / (1 + R)))))
cb = fig.colorbar(pc, ax=axes, shrink=0.9, pad=0.01)
cb.set_label(r"接触承担份额 $y$（0 为仅隔离，1 为仅减少接触）")
fig.suptitle("任意权重下的类内最小成本分配（黑线围出仅隔离区；虚线 $s=s_{sw}$ 与权重无关）",
             x=0.01, ha="left", fontsize=11)
fig.savefig(OUT / "figures/fig_phase_weights.pdf")
fig.savefig(OUT / "figures/fig_phase_weights.png", dpi=170)
(OUT / "results/phase_weights.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                                encoding="utf-8")
print(json.dumps(res, ensure_ascii=False, indent=1))
