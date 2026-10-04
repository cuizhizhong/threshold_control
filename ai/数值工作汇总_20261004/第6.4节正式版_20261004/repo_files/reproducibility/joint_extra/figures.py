"""第 6.4 节新增图件（英文图面）。只读取 run.py 的输出，不重新计算。

用法（项目根目录）：
    python -B reproducibility/joint_extra/figures.py [--res reproducibility/results/joint_extra_v1]
                                                     [--out latex/figures/joint_v1]
图宽按 \\textwidth = 451.28 bp（或其指定比例）精确设置，插图时缩放为 1.0；改 figsize 后用 pdfinfo 复量。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[2]
TEXTWIDTH_IN = 451.28 / 72.0

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "STIXGeneral", "STIX", "DejaVu Serif"],
    "mathtext.fontset": "stix", "axes.unicode_minus": False,
    "font.size": 9.0, "axes.labelsize": 10.0, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
    "legend.fontsize": 7.8, "axes.linewidth": 0.9, "axes.edgecolor": "#000000",
    "xtick.color": "#000000", "ytick.color": "#000000",
    "axes.spines.top": False, "axes.spines.right": False,
    "lines.solid_capstyle": "round", "lines.dash_capstyle": "round",
    "legend.frameon": False, "legend.handlelength": 2.1, "legend.labelspacing": 0.3,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})

# 策略颜色与线型（与稿件现有图件的蓝色系、红色强调、灰色参照线一致）
COL = {"quarantine_only": "#084a91", "minimum_cost": "#b2182b", "contact_only": "#1b9e77",
       "alpha_0.5": "#6BADD7"}
LS = {"quarantine_only": "-", "minimum_cost": "-", "contact_only": "-", "alpha_0.5": (0, (4.5, 2.0))}
LW = {"quarantine_only": 1.7, "minimum_cost": 1.7, "contact_only": 1.7, "alpha_0.5": 1.6}
LAB = {"contact_only": "Contact reduction only", "alpha_0.5": r"Explicit allocation ($\alpha=0.5$)",
       "quarantine_only": "Quarantine only", "minimum_cost": "Minimum-cost allocation"}
ORDER = ["contact_only", "alpha_0.5", "quarantine_only", "minimum_cost"]
REF = "#7a7a7a"


def read_csv(path):
    with open(path, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for k, v in r.items():
            try:
                r[k] = float(v)
            except ValueError:
                pass
    return rows


def panel_label(ax, txt, x=-0.13, y=1.06):
    ax.text(x, y, txt, transform=ax.transAxes, fontsize=11, fontweight="bold", va="bottom", ha="left")


def save(fig, out, name):
    paths = []
    for ext in ("pdf", "svg", "png"):
        p = out / f"{name}.{ext}"
        fig.savefig(p, dpi=300 if ext == "png" else None)
        paths.append(p)
    plt.close(fig)
    return paths


def fig_compare(res, out, params):
    rows = read_csv(res / "trajectories_baseline.csv")
    comp = {r["strategy"]: r for r in read_csv(res / "compare_baseline.csv")}
    eta, N, c0, q0 = params["eta"], params["N"], params["c0"], params["q0"]
    Sc = json.loads((res / "capacity.json").read_text(encoding="utf-8"))  # 仅用于读 s*，不改结果
    fig, axs = plt.subplots(2, 2, figsize=(TEXTWIDTH_IN, 4.55), constrained_layout=True)
    tmax = max(comp[k]["t_end"] for k in ORDER)
    for k in ORDER:
        t = np.array([r["t"] for r in rows if r["strategy"] == k])
        o = np.argsort(t)
        get = lambda f: np.array([r[f] for r in rows if r["strategy"] == k])[o]
        t = t[o]
        kw = dict(color=COL[k], ls=LS[k], lw=LW[k])
        axs[0, 0].plot(t, get("c"), **kw)
        axs[0, 1].plot(t, get("q"), **kw)
        axs[1, 0].plot(t, (get("I") + get("Iq")) / eta, **kw)
        axs[1, 1].plot(t, get("S") / N, **kw)
    axs[0, 1].axhline(q0, color=REF, lw=0.9, ls=(0, (3, 2)))
    axs[0, 1].text(tmax, q0 + 0.015, r"$q_0$", ha="right", va="bottom", color=REF, fontsize=8.5)
    axs[1, 0].axhline(1.0, color=REF, lw=0.9, ls=(0, (3, 2)))
    axs[1, 0].text(tmax, 1.03, r"$\eta$", ha="right", va="bottom", color=REF, fontsize=8.5)
    sc_over_n = comp["quarantine_only"]["conservation_infections"]  # 占位，下面用参数计算 Sc
    Sc_val = params["gamma"] * N / (params["beta"] * c0 * (1 - q0))
    axs[1, 1].axhline(Sc_val / N, color=REF, lw=0.9, ls=(0, (3, 2)))
    axs[1, 1].text(tmax, Sc_val / N + 0.02, r"$S_c/N$", ha="right", va="bottom", color=REF, fontsize=8.5)
    ylabels = [r"$c(t)$", r"$q(t)$", r"$(I+I_q)/\eta$", r"$S/N$"]
    for a, lab, yl in zip(axs.flat, "abcd", ylabels):
        a.set_xlim(0, tmax)
        a.set_xlabel(r"$t$")
        a.set_ylabel(yl)
        panel_label(a, f"({lab})")
    axs[0, 1].set_ylim(0, None)
    axs[1, 0].set_ylim(0, None)
    h = [Line2D([], [], color=COL[k], ls=LS[k], lw=LW[k], label=LAB[k]) for k in ORDER]
    fig.legend(handles=h, loc="outside lower center", ncol=4, columnspacing=1.4)
    return save(fig, out, "joint_compare_baseline")


def fig_frontier(res, out):
    F = read_csv(res / "frontier_baseline.csv")
    A = read_csv(res / "alpha_family_baseline.csv")
    comp = {r["strategy"]: r for r in read_csv(res / "compare_baseline.csv")}
    fig, ax = plt.subplots(figsize=(0.6 * TEXTWIDTH_IN, 2.75), constrained_layout=True)
    f = np.array([[r["duration"], r["J"]] for r in F])
    f = f[np.argsort(f[:, 0])]
    a = np.array([[r["duration"], r["J"]] for r in A])
    ax.plot(f[:, 0], f[:, 1], color=COL["minimum_cost"], lw=1.7,
            label=r"Minimum cost for given $\Delta t$")
    ax.plot(a[:, 0], a[:, 1], color=COL["alpha_0.5"], lw=1.5, ls=(0, (4.5, 2.0)),
            label=r"Explicit family, $\alpha\in[0,1]$")
    for k, mk in (("quarantine_only", "o"), ("minimum_cost", "o"), ("contact_only", "o")):
        ax.plot(comp[k]["duration_quadrature"], comp[k]["J_quadrature"], mk, ms=6.5, color=COL[k],
                mec="white", mew=1.2, zorder=5, ls="none", label=LAB[k])
    ax.set_xscale("log")
    ax.set_xticks([6, 8, 10, 15, 20, 30])
    ax.set_xticklabels(["6", "8", "10", "15", "20", "30"])
    ax.minorticks_off()
    ax.set_xlabel(r"Control duration $\Delta t$")
    ax.set_ylabel(r"Quadratic cost $J$")
    ax.legend(loc="upper left", fontsize=7.4)
    return save(fig, out, "joint_frontier_baseline")


def fig_capacity(res, out, params_by_case):
    cap = json.loads((res / "capacity.json").read_text(encoding="utf-8"))
    tr = read_csv(res / "capacity_traj_baseline.csv")
    fig, axs = plt.subplots(1, 3, figsize=(TEXTWIDTH_IN, 2.45), constrained_layout=True,
                            gridspec_kw=dict(width_ratios=[1, 1, 1.15]))
    cmap = ListedColormap(["#efefef", "#f4cfc8", "#d3e4f3"])
    for ax, case, lab in ((axs[0], "baseline", "(a)"), (axs[1], "xian", "(b)")):
        c = cap[case]
        q0 = c["q0"]
        U, Q = np.meshgrid(np.linspace(0, 0.999, 600), np.linspace(q0, 0.999, 600))
        single = (Q >= c["q_required_quarantine_only"]) | (U >= c["u_required_contact_only"])
        joint = (1 - U) * (1 - Q) <= c["joint_feasibility_bound"]
        reg = np.where(single, 2, np.where(joint, 1, 0))
        ax.pcolormesh(U, Q, reg, cmap=cmap, vmin=-0.5, vmax=2.5, shading="auto", rasterized=True)
        ax.contour(U, Q, reg, levels=[0.5, 1.5], colors=["#555555"], linewidths=0.8)
        pt = c["point"]
        ax.plot(pt["u_max"], pt["q_cap"], "o", ms=5.5, color=COL["minimum_cost"], mec="white", mew=1.0)
        ax.set_xlabel(r"$1-c_{\min}/c_0$")
        ax.set_ylabel(r"$q_{\mathrm{cap}}$")
        ax.set_xlim(0, 1)
        ax.set_ylim(q0, 1)
        panel_label(ax, lab, x=-0.2)
        # 区域标注
        ax.text(0.97, 0.97, "single control\nfeasible", transform=ax.transAxes, ha="right", va="top",
                fontsize=7.4, linespacing=1.0)
        ax.text(0.04, 0.05, "infeasible if\nstarted at $I=\\eta$", transform=ax.transAxes, ha="left",
                va="bottom", fontsize=7.4, linespacing=1.0)
        uj, qj = {"baseline": (0.46, 0.716), "xian": (0.47, 0.812)}[case]   # 标注位置（数据坐标）
        ax.text(uj, qj, "joint needed", fontsize=7.0, ha="center", va="center")
    ax = axs[2]
    t = np.array([r["t"] for r in tr])
    o = np.argsort(t)
    t = t[o]
    c = np.array([r["c"] for r in tr])[o]
    q = np.array([r["q"] for r in tr])[o]
    c0 = params_by_case["baseline"]["c0"]
    pt = cap["baseline"]["point"]
    ax.plot(t, 1 - c / c0, color=COL["contact_only"], lw=1.7, label=r"$1-c/c_0$")
    ax.plot(t, q, color=COL["quarantine_only"], lw=1.7, label=r"$q$")
    ax.axhline(pt["q_cap"], color=COL["quarantine_only"], lw=0.8, ls=(0, (3, 2)))
    ax.axhline(pt["u_max"], color=COL["contact_only"], lw=0.8, ls=(0, (3, 2)))
    ax.text(t[-1], pt["q_cap"] + 0.012, r"$q_{\mathrm{cap}}$", ha="right", va="bottom", fontsize=8.5)
    ax.text(t[-1], pt["u_max"] + 0.012, r"$1-c_{\min}/c_0$", ha="right", va="bottom", fontsize=8.5)
    ax.set_ylim(0, 0.68)
    ax.set_xlabel(r"$t$")
    ax.legend(loc="center right")
    panel_label(ax, "(c)", x=-0.13)
    return save(fig, out, "joint_capacity")


def fig_phase(res, out):
    summ = json.loads((res / "phase.json").read_text(encoding="utf-8"))
    cmap = LinearSegmentedColormap.from_list(
        "blues", ["#f5f9fd", "#d3e4f3", "#a6cbe6", "#6BADD7", "#3a8cc4", "#206FB6", "#084a91", "#062e5c"])
    fig, axs = plt.subplots(1, 2, figsize=(TEXTWIDTH_IN, 2.75), constrained_layout=True)
    for ax, case, lab in ((axs[0], "baseline", "(a)"), (axs[1], "xian", "(b)")):
        d = np.load(res / f"phase_{case}.npz")
        s, r, Y, sw = d["s"], d["r"], d["y"], d["switch"]
        ssw, sst = summ[case]["s_sw"], summ[case]["s_star"]
        pc = ax.pcolormesh(s, r, Y, cmap=cmap, vmin=0, vmax=1, shading="auto", rasterized=True)
        ax.contour(s, r, (Y < 1e-6).astype(float), levels=[0.5], colors="#000000", linewidths=0.9)
        dep = sw > ssw + 2 * (s[1] - s[0])
        ok = ~np.isnan(sw) & dep
        ax.plot(sw[ok], r[ok], color=COL["minimum_cost"], lw=1.6)
        ax.axvline(ssw, color="#000000", lw=0.8, ls=(0, (3, 2)))
        ax.text(ssw + 0.04, 0.115, r"$s_{sw}$", fontsize=8.5, va="bottom")
        ax.axhline(2.0, color="#000000", lw=0.7, ls=":")
        ax.text(sst - 0.04, 2.1, r"$r=2$", ha="right", va="bottom", fontsize=8.5)
        ax.text(0.5 * (ssw + sst), 0.45, "quarantine only", ha="center", fontsize=8)
        ax.text(1 + 0.42 * (ssw - 1), 0.45, "mixed", ha="center", fontsize=8)
        ax.text(1 + 0.5 * (ssw - 1), 9.0, "mainly contact\nreduction", ha="center", va="center",
                fontsize=8, color="#ffffff", linespacing=1.0)
        ax.set_yscale("log")
        ax.set_xlim(1, sst)
        ax.set_ylim(r[0], r[-1])
        ax.set_xlabel(r"$s=S/S_c$")
        ax.set_ylabel(r"$r=w_q/w_c$")
        panel_label(ax, lab, x=-0.16)
    cb = fig.colorbar(pc, ax=axs, shrink=0.92, pad=0.015, aspect=22)
    cb.set_label(r"Contact share $y$", fontsize=9)
    cb.ax.tick_params(labelsize=8)
    return save(fig, out, "joint_phase_weights")


def main():
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import core as JN
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default=str(ROOT / "reproducibility/results/joint_extra_v1"))
    ap.add_argument("--out", default=str(ROOT / "latex/figures/joint_v1"))
    a = ap.parse_args()
    res, out = Path(a.res), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pb = JN.baseline_params()
    px, _ = JN.xian_params()
    made = []
    made += fig_compare(res, out, pb)
    made += fig_frontier(res, out)
    made += fig_capacity(res, out, {"baseline": pb, "xian": px})
    made += fig_phase(res, out)
    man = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in made if p.suffix == ".pdf"}
    man["figures.py"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    man["results_manifest"] = hashlib.sha256((res / "manifest.json").read_bytes()).hexdigest()
    (out / "figure_manifest.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
    print("figures written to", out)


if __name__ == "__main__":
    main()
