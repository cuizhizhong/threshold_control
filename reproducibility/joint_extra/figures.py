"""联合控制新增图的只读绘图层；样式沿用候选图，不求解科学模型。"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.font_manager import FontProperties, findfont
import numpy as np

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "STIXGeneral", "STIX", "DejaVu Serif"],
    "mathtext.fontset": "stix", "axes.unicode_minus": False,
    "font.size": 9.0, "axes.labelsize": 10.0, "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5, "legend.fontsize": 7.8, "axes.linewidth": 0.9,
    "axes.edgecolor": "#000000", "xtick.color": "#000000", "ytick.color": "#000000",
    "axes.spines.top": False, "axes.spines.right": False,
    "lines.solid_capstyle": "round", "lines.dash_capstyle": "round",
    "legend.frameon": False, "legend.handlelength": 2.1, "legend.labelspacing": 0.3,
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "svg.hashsalt": "threshold-control-joint-v2",
})
COL = {"quarantine_only": "#084a91", "minimum_cost": "#b2182b",
       "contact_only": "#1b9e77", "alpha_0.5": "#6BADD7"}
LS = {key: "-" for key in COL}
LS["alpha_0.5"] = (0, (4.5, 2.0))
LAB = {"contact_only": "Contact reduction only",
       "alpha_0.5": r"Explicit allocation ($\alpha=0.5$)",
       "quarantine_only": "Quarantine only", "minimum_cost": "Minimum-cost allocation"}
ORDER = ["contact_only", "alpha_0.5", "quarantine_only", "minimum_cost"]
REF = "#7a7a7a"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for key, value in row.items():
            if value is None or value == "":
                row[key] = None
                continue
            try:
                row[key] = float(value)
            except ValueError:
                pass
    return rows


def is_passed(value):
    return value is True or value == 1 or str(value).lower() in {"true", "1", "passed"}


def require_accepted(res):
    validation = read_json(res / "validation.json")
    tasks = validation.get("tasks", {})
    if not all(is_passed(tasks.get(key, {}).get("passed")) for key in ("A", "B", "C")):
        raise RuntimeError("任务 A–C 尚未全部通过数值验收，不能生成其投稿图件。")
    return validation


def case_parts(manifest, case):
    item = manifest["cases"][case]
    return item.get("params", item.get("parameters", item)), item["derived"]


def panel_label(ax, label, x=-0.13, y=1.06):
    ax.text(x, y, label, transform=ax.transAxes, fontsize=11,
            fontweight="bold", va="bottom", ha="left")


def save(fig, out, name):
    paths = []
    for ext in ("pdf", "svg", "png"):
        path = out / f"{name}.{ext}"
        metadata = {"CreationDate": None, "ModDate": None} if ext == "pdf" else (
            {"Date": None} if ext == "svg" else None)
        fig.savefig(path, dpi=300 if ext == "png" else None, metadata=metadata)
        paths.append(path)
    plt.close(fig)
    return paths


def piecewise_control(ax, rows, field, **kwargs):
    """按计算段绘控制；共同端点处画竖线，不跨跳变做平滑插值。"""
    groups = []
    for row in sorted(rows, key=lambda item: item["t"]):
        segment = row.get("segment", row.get("phase", "all"))
        if not groups or groups[-1][0] != segment:
            groups.append((segment, []))
        groups[-1][1].append(row)
    for _, group in groups:
        ax.plot([row["t"] for row in group], [row[field] for row in group], **kwargs)
    for (_, left), (_, right) in zip(groups, groups[1:]):
        t_left, t_right = left[-1]["t"], right[0]["t"]
        if abs(t_left - t_right) <= 1e-10 * max(1, abs(t_right)):
            ax.plot([t_right, t_right], [left[-1][field], right[0][field]], **kwargs)


def fig_compare(res, out, manifest, width):
    rows = read_csv(res / "trajectories_baseline.csv")
    comp = {row["strategy"]: row for row in read_csv(res / "compare_baseline.csv")}
    params, derived = case_parts(manifest, "baseline")
    eta, population, q0 = params["eta"], params["N"], params["q0"]
    fig, axs = plt.subplots(2, 2, figsize=(width, 4.55), constrained_layout=True)
    tmax = max(comp[key]["t_end"] for key in ORDER)
    for key in ORDER:
        group = sorted([row for row in rows if row["strategy"] == key], key=lambda row: row["t"])
        kw = dict(color=COL[key], ls=LS[key], lw=1.6 if key == "alpha_0.5" else 1.7)
        piecewise_control(axs[0, 0], group, "c", **kw)
        piecewise_control(axs[0, 1], group, "q", **kw)
        t = [row["t"] for row in group]
        axs[1, 0].plot(t, [(row["I"] + row["Iq"]) / eta for row in group], **kw)
        axs[1, 1].plot(t, [row["S"] / population for row in group], **kw)
    for ax, value, label, offset in (
        (axs[0, 1], q0, r"$q_0$", 0.015),
        (axs[1, 0], 1, "1", 0.03),
        (axs[1, 1], derived["Sc"] / population, r"$S_c/N$", 0.02),
    ):
        ax.axhline(value, color=REF, lw=0.9, ls=(0, (3, 2)))
        ax.text(tmax, value + offset, label, ha="right", va="bottom", color=REF, fontsize=8.5)
    for ax, letter, ylabel in zip(axs.flat, "abcd",
                                  [r"$c(t)$", r"$q(t)$", r"$(I+I_q)/\eta$", r"$S/N$"]):
        ax.set_xlim(0, tmax)
        ax.set_xlabel(r"$t$")
        ax.set_ylabel(ylabel)
        panel_label(ax, f"({letter})")
    axs[0, 1].set_ylim(0, None)
    axs[1, 0].set_ylim(0, None)
    handles = [Line2D([], [], color=COL[key], ls=LS[key], lw=1.7, label=LAB[key]) for key in ORDER]
    fig.legend(handles=handles, loc="outside lower center", ncol=2, columnspacing=1.6)
    return save(fig, out, "joint_compare_baseline")


def fig_capacity(res, out, manifest, width):
    capacity = read_json(res / "capacity.json")
    trajectory = read_csv(res / "capacity_traj_baseline.csv")
    fig, axs = plt.subplots(1, 3, figsize=(width, 2.45), constrained_layout=True,
                            gridspec_kw=dict(width_ratios=[1, 1, 1.15]))
    cmap = ListedColormap(["#efefef", "#f4cfc8", "#d3e4f3"])
    for ax, case, label in ((axs[0], "baseline", "(a)"), (axs[1], "xian", "(b)")):
        item = capacity[case]
        with np.load(res / f"capacity_{case}.npz", allow_pickle=False) as data:
            u, q, region = data["u"], data["q"], data["region"]
            boundary_u, boundary_q = data["boundary_u"], data["boundary_q"]
            quarantine_line, contact_line = data["quarantine_line"].item(), data["contact_line"].item()
        ax.pcolormesh(u, q, region, cmap=cmap, vmin=-0.5, vmax=2.5,
                      shading="auto", rasterized=True)
        ax.plot(boundary_u, boundary_q, color="#555555", lw=0.8)
        ax.plot([0, contact_line], [quarantine_line, quarantine_line], color="#555555", lw=0.8)
        ax.plot([contact_line, contact_line], [item["q0"], quarantine_line], color="#555555", lw=0.8)
        point = item["point"]
        ax.plot(point["u_max"], point["q_cap"], "o", ms=5.5,
                color=COL["minimum_cost"], mec="white", mew=1)
        ax.set_xlabel(r"$1-c_{\min}/c_0$")
        ax.set_ylabel(r"$q_{\mathrm{cap}}$")
        ax.set_xlim(0, 1)
        ax.set_ylim(item["q0"], 1)
        panel_label(ax, label, x=-0.2)
        ax.text(0.97, 0.97, "at least one\nsingle control feasible", transform=ax.transAxes,
                ha="right", va="top", fontsize=7.4, linespacing=1)
        ax.text(0.04, 0.05, "infeasible if\nstarted at $I=\\eta$", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=7.4, linespacing=1)
        note_x, note_y = {"baseline": (0.46, 0.716), "xian": (0.47, 0.812)}[case]
        # 标签取已计算红区内的邻近位置，避免历史标签坐标落入另一分类。
        joint_rows, joint_cols = np.where(region == 1)
        if not len(joint_rows):
            raise ValueError(f"{case} 的能力图没有已计算的联合必要区域。")
        closest = np.argmin((u[joint_cols] - note_x)**2 + (q[joint_rows] - note_y)**2)
        note_x, note_y = u[joint_cols[closest]], q[joint_rows[closest]]
        ax.text(note_x, note_y, "joint needed", fontsize=7, ha="center", va="center")
    ax = axs[2]
    params, _ = case_parts(manifest, "baseline")
    point = capacity["baseline"]["point"]
    metric = capacity["baseline"].get("metrics", capacity["baseline"])
    viewport = capacity["baseline"]["plot_viewport"]["post_exit_days"]
    stop_time = metric["t2"] + viewport
    # 用坐标视窗裁切完整真实轨迹；不复制末值，也不丢掉跨视窗终点的线段。
    rows = sorted(trajectory, key=lambda row: row["t"])
    contact_rows = [{**row, "u": 1 - row["c"] / params["c0"]} for row in rows]
    piecewise_control(ax, contact_rows, "u", color=COL["contact_only"], lw=1.7)
    piecewise_control(ax, rows, "q", color=COL["quarantine_only"], lw=1.7)
    for value, color, text in ((point["q_cap"], COL["quarantine_only"], r"$q_{\mathrm{cap}}$"),
                                (point["u_max"], COL["contact_only"], r"$1-c_{\min}/c_0$")):
        ax.axhline(value, color=color, lw=0.8, ls=(0, (3, 2)))
        ax.text(stop_time, value + 0.012, text, ha="right", va="bottom", fontsize=8.5)
    ax.set_ylim(0, max(point["q_cap"], point["u_max"]) + 0.22)
    ax.set_xlim(0, stop_time)
    ax.set_xlabel(r"$t$")
    ax.legend(handles=[Line2D([], [], color=COL["contact_only"], lw=1.7, label=r"$1-c/c_0$"),
                       Line2D([], [], color=COL["quarantine_only"], lw=1.7, label=r"$q$")],
              loc="upper right")
    panel_label(ax, "(c)")
    return save(fig, out, "joint_capacity")


def fig_phase(res, out, width):
    summary = read_json(res / "phase.json")
    cmap = LinearSegmentedColormap.from_list(
        "blues", ["#f5f9fd", "#d3e4f3", "#a6cbe6", "#6BADD7", "#3a8cc4", "#206FB6", "#084a91", "#062e5c"])
    fig, axs = plt.subplots(1, 2, figsize=(width, 2.75), constrained_layout=True)
    for ax, case, label in ((axs[0], "baseline", "(a)"), (axs[1], "xian", "(b)")):
        with np.load(res / f"phase_{case}.npz", allow_pickle=False) as data:
            s, ratio, y, switch = data["s"], data["r"], data["y"], data["switch"]
            classification = data["classification"]
        sw, start = summary[case]["s_sw"], summary[case]["s_star"]
        y = np.ma.masked_where(classification == 3, y)
        pc = ax.pcolormesh(s, ratio, y, cmap=cmap, vmin=0, vmax=1, shading="auto", rasterized=True)
        if np.any(classification == 1) and np.any(classification != 1):
            ax.contour(s, ratio, (classification == 1).astype(float), levels=[0.5],
                       colors="#000000", linewidths=0.9)
        valid = np.isfinite(switch)
        # 与局部竖线重合时由黑色区域边界表示，红线沿用候选图的分离显示。
        separated = valid & (switch > sw + 2 * (s[1] - s[0]))
        ax.plot(switch[separated], ratio[separated], color=COL["minimum_cost"], lw=1.4)
        ax.axvline(sw, color="#000000", lw=0.8, ls=(0, (3, 2)))
        ax.text(sw + 0.04, 0.115, r"$S_{\rm sw}/S_c$", fontsize=8.5, va="bottom")
        ax.axhline(2, color="#000000", lw=0.7, ls=":")
        ax.text(start - 0.04, 2.1, r"$r=2$", ha="right", va="bottom", fontsize=8.5)
        ax.text(1 + 0.42 * (sw - 1), 0.45, "mixed", ha="center", fontsize=8)
        quarantine_x = 0.5 * (sw + start)
        i_state = int(np.argmin(np.abs(s - quarantine_x)))
        i_ratio = int(np.argmin(np.abs(ratio - 0.45)))
        if classification[i_ratio, i_state] == 1:
            ax.text(quarantine_x, 0.45, "quarantine only", ha="center", fontsize=8)
        ax.text(1 + 0.5 * (sw - 1), 9, "mainly contact\nreduction", ha="center", va="center",
                fontsize=8, color="#ffffff", linespacing=1)
        ax.set_yscale("log")
        ax.set_xlim(1, start)
        ax.set_ylim(ratio[0], ratio[-1])
        ax.set_xlabel(r"$S/S_c$")
        ax.set_ylabel(r"$r=w_q/w_c$")
        panel_label(ax, label, x=-0.16)
    cb = fig.colorbar(pc, ax=axs, shrink=0.92, pad=0.015, aspect=22)
    cb.set_label(r"Normalized contact reduction $y$", fontsize=9)
    cb.ax.tick_params(labelsize=8)
    return save(fig, out, "joint_phase_weights")


def fig_duration(res, out, width):
    frontier = [row for row in read_csv(res / "frontier_baseline.csv") if is_passed(row["passed"])]
    alpha = read_csv(res / "alpha_family_baseline.csv")
    comp = {row["strategy"]: row for row in read_csv(res / "compare_baseline.csv")}
    fig, ax = plt.subplots(figsize=(0.6 * width, 2.75), constrained_layout=True)
    for positive, linestyle, label in (
        (True, "-", r"Computed solutions ($\kappa\geq0$)"),
        (False, (0, (2, 1.5)), r"Computed solutions ($\kappa<0$)"),
    ):
        selected = sorted([row for row in frontier if (row["kappa"] >= 0) == positive],
                          key=lambda row: row["duration"])
        groups = {}
        for row in selected:
            # connection_group 来自计算层，避免将按κ顺序标记的缺口反向错接。
            groups.setdefault(row.get("connection_group", "observed"), []).append(row)
        for idx, group in enumerate(groups.values()):
            if group:
                ax.plot([row["duration"] for row in group], [row["J"] for row in group],
                        color=COL["minimum_cost"], lw=1.7, ls=linestyle, marker=".", ms=1.6,
                        label=label if idx == 0 else None)
    alpha.sort(key=lambda row: row["duration"])
    ax.plot([row["duration"] for row in alpha], [row["J"] for row in alpha],
            color=COL["alpha_0.5"], lw=1.5, ls=(0, (4.5, 2)),
            label=r"Explicit family, $\alpha\in[0,1]$")
    for key in ("quarantine_only", "minimum_cost", "contact_only"):
        ax.plot(comp[key]["duration_state"], comp[key]["J_state"], "o", ms=6.5,
                color=COL[key], mec="white", mew=1.2, zorder=5, ls="none", label=LAB[key])
    ax.set_xscale("log")
    ax.set_xticks([6, 8, 10, 15, 20, 30])
    ax.set_xticklabels(["6", "8", "10", "15", "20", "30"])
    ax.minorticks_off()
    ax.set_xlabel(r"Control duration $\Delta t$")
    ax.set_ylabel(r"Quadratic cost $J$")
    ax.legend(loc="upper left", fontsize=7.4)
    return save(fig, out, "joint_frontier_baseline")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--res", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--textwidth-bp", type=float, required=True,
                        help="当前模板实际正文宽度（bp）；从编译或模板测得，不沿用旧固定数值。")
    args = parser.parse_args()
    if args.textwidth_bp <= 0 or args.textwidth_bp > 1000:
        raise ValueError("正文宽度无效。")
    validation = require_accepted(args.res)
    if args.out.exists() and any(args.out.iterdir()):
        raise FileExistsError("图件输出目录必须为空，不能覆盖历史或正式图件。")
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = read_json(args.res / "input_manifest.json")
    width = args.textwidth_bp / 72
    made = fig_compare(args.res, args.out, manifest, width)
    made += fig_capacity(args.res, args.out, manifest, width)
    made += fig_phase(args.res, args.out, width)
    if is_passed(validation.get("tasks", {}).get("D", {}).get("passed")):
        made += fig_duration(args.res, args.out, width)
    sources = [path for path in args.res.iterdir() if path.suffix in {".json", ".csv", ".npz"}]
    labels = {"joint_compare_baseline": "fig:joint:compare", "joint_capacity": "fig:joint:capacity",
              "joint_phase_weights": "fig:joint:phase", "joint_frontier_baseline": "fig:joint:frontier"}
    record = {"results_directory": str(args.res.resolve()), "textwidth_bp": args.textwidth_bp,
              "figures": [{"label": labels[path.stem], "file": str(path),
                           "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                          for path in made if path.suffix == ".pdf"],
              "exports": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in made},
              "inputs": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sources},
              "plotting_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "font_candidates": plt.rcParams["font.serif"],
              "resolved_serif_font": Path(findfont(FontProperties(family="serif"))).name,
              "matplotlib_version": matplotlib.__version__, "numpy_version": np.__version__,
              "note": "绘图仅读取本轮验收输出；连线不表示未计算的时长也已认证。"}
    (args.out / "figure_manifest.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                                                  encoding="utf-8")
    print(f"图件输出：{args.out}")


if __name__ == "__main__":
    main()
