"""生成联合控制补充数值：四策略比较、成本—时长前沿、能力案例、权重敏感性、线性成本稳健性。"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import joint_numerics as JN

OUT = Path(__file__).resolve().parent
(OUT / "results").mkdir(exist_ok=True)
(OUT / "figures").mkdir(exist_ok=True)

plt.rcParams.update({"font.family": ["Noto Sans CJK SC", "DejaVu Sans"], "axes.unicode_minus": False,
                     "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#8a8a85", "axes.labelcolor": "#3b3b38",
                     "xtick.color": "#5c5c58", "ytick.color": "#5c5c58", "axes.titlesize": 10,
                     "axes.titlelocation": "left"})
GRID = dict(axis="y", color="#e4e4df", lw=0.6)
COL = {"quarantine_only": "#2a78d6", "minimum_cost": "#eb6834", "contact_only": "#1baf7a",
       "alpha_0.5": "#eda100"}
LAB = {"quarantine_only": "仅隔离", "minimum_cost": "类内最小成本分配", "contact_only": "仅减少接触",
       "alpha_0.5": r"显式策略 $\alpha=0.5$"}
LS = {"quarantine_only": "-", "minimum_cost": "-", "contact_only": "-", "alpha_0.5": (0, (4, 2))}
ORDER = ["contact_only", "alpha_0.5", "quarantine_only", "minimum_cost"]
NS, NX = 8001, 4001


def save(fig, name):
    fig.savefig(OUT / "figures" / f"{name}.pdf")
    fig.savefig(OUT / "figures" / f"{name}.png", dpi=170)
    plt.close(fig)


def jdump(obj, name):
    def conv(o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    (OUT / "results" / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=conv),
                                        encoding="utf-8")


def csvdump(rows, name):
    with open(OUT / "results" / name, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (format(v, ".10g") if isinstance(v, float) else v) for k, v in r.items()})


CASES = {"baseline": JN.baseline_params()}
XP, XREF = JN.xian_params()
CASES["xian"] = XP
summary = {}

# ============================================================ 1. 同条件四策略比较
runs = {}
for case, p in CASES.items():
    Sc, Sbar, Sstar = JN.basics(p)
    s = JN.s_grid(p, NS)
    xs = {"contact_only": JN.x_policy("contact_only", s),
          "alpha_0.5": JN.x_policy("alpha", s, 0.5),
          "quarantine_only": JN.x_policy("quarantine_only", s),
          "minimum_cost": JN.allocate(p, s, 1, 2, nx=NX)[0]}
    rows = []
    for k in ORDER:
        r = JN.full_run(p, s, xs[k])
        q = JN.plateau_quantities(p, s, xs[k])
        runs[(case, k)] = r
        rows.append(dict(case=case, strategy=k, t1=r["t1"], duration=r["dT"], t_end=r["t_end"],
                         total_infections=r["total_infections"],
                         plateau_infections=r["plateau_infections"],
                         plateau_new_Sq=r["plateau_Sq"], plateau_new_Iq=r["plateau_Iq_new"],
                         peak_I_plus_Iq=r["peak_I_plus_Iq"],
                         peak_I_plus_Iq_over_eta=r["peak_I_plus_Iq"] / p["eta"],
                         J=r["J"], J_c=r["Jc"], J_q=r["Jq"], J_lin_1_2=r["Jc"] + 2 * r["Jq"],
                         q_max=q["q_max"], c_min=q["c_min"], J_quadrature=q["J"],
                         conservation_infections=q["inf_plateau"], conservation_Sq=q["Sq_plateau"],
                         max_rel_drift=r["max_rel_drift"]))
    if case == "xian":
        T = JN.tdinn_run(p)
        runs[(case, "tdinn")] = T
        rows.append(dict(case=case, strategy="TDINN(reference.json)", t1=0.0,
                         duration=XREF["t_end_T"], t_end=XREF["t_end_T"],
                         total_infections=XREF["Itcum_T"], plateau_infections=float("nan"),
                         plateau_new_Sq=float("nan"), plateau_new_Iq=float("nan"),
                         peak_I_plus_Iq=T["peak_I_plus_Iq"],
                         peak_I_plus_Iq_over_eta=T["peak_I_plus_Iq"] / p["eta"],
                         J=XREF["J_T"], J_c=XREF["strategies"][0]["J_c"],
                         J_q=XREF["strategies"][0]["J_q"],
                         J_lin_1_2=XREF["strategies"][0]["J_c"] + 2 * XREF["strategies"][0]["J_q"],
                         q_max=0.9844, c_min=3.4625, J_quadrature=float("nan"),
                         conservation_infections=float("nan"), conservation_Sq=float("nan"),
                         max_rel_drift=float("nan")))
    csvdump(rows, f"compare_{case}.csv")
    summary[f"compare_{case}"] = rows
    summary[f"basics_{case}"] = dict(Sc=Sc, Sbar=Sbar, Sstar=Sstar, s_star=Sstar / Sc,
                                     sbar=Sbar / Sc, s_sw=(3 + np.sqrt(9 - 8 * Sbar / Sc)) / 2,
                                     eta=p["eta"], N=p["N"])

    # 图：控制与状态轨迹
    fig, ax = plt.subplots(2, 2, figsize=(10, 6.4), constrained_layout=True)
    for k in ORDER:
        r = runs[(case, k)]
        tr = r["traj"]
        kw = dict(color=COL[k], ls=LS[k], lw=1.8)
        ax[0, 0].plot(tr["t"], tr["c"], **kw)
        ax[0, 1].plot(tr["t"], tr["q"], **kw)
        ax[1, 0].plot(tr["t"], (tr["I"] + tr["Iq"]) / p["eta"], **kw)
        ax[1, 1].plot(tr["t"], tr["S"] / p["N"], **kw)
    if case == "xian":
        T = runs[(case, "tdinn")]["traj"]
        kw = dict(color="#5c5c58", ls=(0, (1, 1.5)), lw=1.4)
        ax[0, 0].plot(T["t"], T["c"], **kw)
        ax[0, 1].plot(T["t"], T["q"], **kw)
        ax[1, 0].plot(T["t"], (T["I"] + T["Iq"]) / p["eta"], **kw)
    tmax = max(runs[(case, k)]["t_end"] for k in ORDER)
    ax[0, 0].set_title("(a) 接触率 $c(t)$")
    ax[0, 1].set_title("(b) 隔离比例 $q(t)$")
    ax[1, 0].set_title(r"(c) 感染者总数 $(I+I_q)/\eta$（$I$ 本身在平台期恒为 $\eta$）")
    ax[1, 1].set_title("(d) 社区易感者 $S/N$")
    ax[1, 0].axhline(1, color="#8a8a85", lw=0.8, ls=":")
    ax[1, 1].axhline(Sc / p["N"], color="#8a8a85", lw=0.8, ls=":")
    ax[1, 1].text(tmax * 0.99, Sc / p["N"], "$S_c/N$", ha="right", va="bottom", color="#5c5c58")
    for a in ax.flat:
        a.set_xlim(0, tmax)
        a.set_xlabel("时间（天）")
        a.grid(**GRID)
    h = [Line2D([], [], color=COL[k], ls=LS[k], lw=1.8, label=LAB[k]) for k in ORDER]
    if case == "xian":
        h.append(Line2D([], [], color="#5c5c58", ls=(0, (1, 1.5)), lw=1.4, label="TDINN 参照"))
    fig.legend(handles=h, loc="outside lower center", ncol=len(h), frameon=False)
    ttl = {"baseline": "基准参数（N=763，η=0.05N，权重 1:2）：相同启动与退出状态下的四种分配",
           "xian": "西安参数（η=0.002N，权重 1:2）：相同启动与退出状态下的四种分配"}[case]
    fig.suptitle(ttl, x=0.01, ha="left", fontsize=11)
    save(fig, f"fig_compare_{case}")

# ============================================================ 2. 成本—时长前沿
for case, p in CASES.items():
    s = JN.s_grid(p, 4001)
    qq = JN.plateau_quantities(p, s, JN.x_policy("quarantine_only", s))
    cc = JN.plateau_quantities(p, s, JN.x_policy("contact_only", s))
    kap = np.unique(np.concatenate([-np.logspace(2, -4, 70), [0.0], np.logspace(-4, 2, 70),
                                np.linspace(-1.5, 0.2, 171)]))
    front = []
    for k in kap:
        x, _ = JN.allocate(p, s, 1, 2, kappa=k, nx=2001)
        q = JN.plateau_quantities(p, s, x)
        front.append(dict(kappa=k, dT=q["dT"], J=q["J"], inf=q["inf_plateau"], Sq=q["Sq_plateau"]))
    alph = []
    for a in np.linspace(0, 1, 41):
        q = JN.plateau_quantities(p, s, JN.x_policy("alpha", s, a))
        alph.append(dict(alpha=a, dT=q["dT"], J=q["J"]))
    summary[f"frontier_{case}"] = dict(front=front, alpha=alph, q_only=qq, c_only=cc)
    csvdump(front, f"frontier_{case}.csv")
    fig, ax = plt.subplots(figsize=(6.2, 4.2), constrained_layout=True)
    F = np.array([[r["dT"], r["J"]] for r in front])
    o = np.argsort(F[:, 0])
    ax.plot(F[o, 0], F[o, 1], color=COL["minimum_cost"], lw=2, label=r"给定时长下的类内最小成本（扫描 $\kappa$）")
    A = np.array([[r["dT"], r["J"]] for r in alph])
    ax.plot(A[:, 0], A[:, 1], color=COL["alpha_0.5"], lw=1.5, ls=(0, (4, 2)),
            label=r"显式族 $\alpha\in[0,1]$")
    m = [r for r in front if r["kappa"] == 0.0][0]
    for (xv, yv, k, txt) in [(qq["dT"], qq["J"], "quarantine_only", "仅隔离"),
                             (cc["dT"], cc["J"], "contact_only", "仅减少接触"),
                             (m["dT"], m["J"], "minimum_cost", r"最小成本（$\kappa=0$）")]:
        ax.plot(xv, yv, "o", ms=8, color=COL[k], mec="white", mew=1.5, zorder=5)
        ax.annotate(txt, (xv, yv), textcoords="offset points", xytext=(8, 6), color="#3b3b38")
    ax.set_xscale("log")
    ax.set_xlabel(r"平台期时长 $\Delta t$（天，对数轴）")
    ax.set_ylabel("二次成本 $J$")
    ax.grid(**GRID)
    ax.legend(frameon=False, loc="upper left")
    ttl = {"baseline": "基准参数", "xian": "西安参数"}[case]
    ax.set_title(f"成本—时长前沿（{ttl}）")
    save(fig, f"fig_frontier_{case}")

# ============================================================ 3. 能力案例
cap_cases = {"baseline": dict(umax=0.5, qcap=0.6), "xian": dict(umax=0.5, qcap=0.75)}
fig, ax = plt.subplots(1, 3, figsize=(12, 3.9), constrained_layout=True,
                       gridspec_kw=dict(width_ratios=[1, 1, 1.25]))
cap_res = {}
for j, (case, p) in enumerate(CASES.items()):
    Sc, Sbar, Sstar = JN.basics(p)
    sst = Sstar / Sc
    q0 = p["q0"]
    qmax_req = 1 - (1 - q0) / sst
    umin_req = 1 - 1 / sst
    K = (1 - q0) / sst
    U, Q = np.meshgrid(np.linspace(0, 0.999, 500), np.linspace(q0, 0.999, 500))
    single = (Q >= qmax_req) | (U >= umin_req)
    joint = (1 - U) * (1 - Q) <= K
    region = np.where(single, 2, np.where(joint, 1, 0))
    a = ax[j]
    a.contourf(U, Q, region, levels=[-0.5, 0.5, 1.5, 2.5],
               colors=["#f1f0ec", "#fbd9c9", "#cde2fb"])
    a.contour(U, Q, region, levels=[0.5, 1.5], colors=["#8a8a85"], linewidths=0.8)
    a.text(0.08, 0.06 + q0 * 0.3, "到阈值再启动\n已不可行", color="#3b3b38", transform=a.transAxes)
    a.text(0.27, 0.70, "需要联合分配", color="#3b3b38", transform=a.transAxes, va="center")
    a.text(0.6, 0.9, "单一控制可行", color="#3b3b38", transform=a.transAxes)
    cc_ = cap_cases[case]
    a.plot(cc_["umax"], cc_["qcap"], "o", ms=8, color=COL["minimum_cost"], mec="white", mew=1.5)
    a.set_xlabel(r"最大接触减少 $1-c_{\min}/c_0$")
    a.set_ylabel(r"隔离能力上限 $q_{\rm cap}$")
    a.set_title(("(a) 基准参数" if case == "baseline" else "(b) 西安参数")
                + f"：仅隔离需 $q\\geq{qmax_req:.3f}$")
    cap_res[case] = dict(q_required_quarantine_only=qmax_req, contact_reduction_required_contact_only=umin_req,
                         joint_feasibility_bound=K, point=cc_)
    # 代表轨迹
    s = JN.s_grid(p, NS)
    cmin = (1 - cc_["umax"]) * p["c0"]
    x, nl = JN.allocate(p, s, 1, 2, cmin=cmin, qcap=cc_["qcap"], nx=NX)
    r = JN.full_run(p, s, x)
    q = JN.plateau_quantities(p, s, x)
    cap_res[case].update(duration=r["dT"], J=r["J"], t_end=r["t_end"],
                         total_infections=r["total_infections"], plateau_new_Sq=r["plateau_Sq"],
                         peak_I_plus_Iq_over_eta=r["peak_I_plus_Iq"] / p["eta"],
                         max_rel_drift=r["max_rel_drift"], q_max=q["q_max"], c_min=q["c_min"])
    runs[(case, "capped")] = r
tr = runs[("baseline", "capped")]["traj"]
p = CASES["baseline"]
m = (tr["t"] >= runs[("baseline", "capped")]["t1"] - 0.5) & (tr["t"] <= runs[("baseline", "capped")]["t2"] + 0.5)
uc = 1 - tr["c"] / p["c0"]
uq = (tr["q"] - p["q0"]) / (1 - p["q0"])
a = ax[2]
a.plot(tr["t"][m], uc[m], color=COL["contact_only"], lw=2, label=r"接触减少 $1-c/c_0$")
a.plot(tr["t"][m], tr["q"][m], color=COL["quarantine_only"], lw=2, label=r"隔离比例 $q$")
a.axhline(cap_cases["baseline"]["qcap"], color=COL["quarantine_only"], lw=0.8, ls=":")
a.axhline(cap_cases["baseline"]["umax"], color=COL["contact_only"], lw=0.8, ls=":")
a.text(tr["t"][m][-1], cap_cases["baseline"]["qcap"] + 0.015, r"$q_{\rm cap}=0.6$", ha="right",
       color="#5c5c58")
a.text(tr["t"][m][-1], cap_cases["baseline"]["umax"] + 0.015, r"接触减少上限 0.5", ha="right",
       color="#5c5c58")
a.set_xlabel("时间（天）")
a.set_title(r"(c) 基准参数代表点（橙点）的类内最小成本分配")
a.grid(**GRID)
a.legend(frameon=False, loc="center right")
save(fig, "fig_capacity")
summary["capacity"] = cap_res
jdump(cap_res, "capacity.json")

# ============================================================ 4. 权重敏感性
RS = [0.5, 1.0, 2.0, 5.0]
RC = ["#86b6ef", "#5598e7", "#2a78d6", "#104281"]
fig, ax = plt.subplots(1, 2, figsize=(11, 4.0), constrained_layout=True)
wres = {}
for j, (case, p) in enumerate(CASES.items()):
    Sc, Sbar, Sstar = JN.basics(p)
    sbar = Sbar / Sc
    ssw = (3 + np.sqrt(9 - 8 * sbar)) / 2
    s = JN.s_grid(p, NS)
    a = ax[j]
    wres[case] = []
    for r_, col in zip(RS, RC):
        x, nl = JN.allocate(p, s, 1.0, r_, nx=NX)
        y = np.where(s > 1 + 1e-9, (1 - x) / np.maximum(1 - 1 / s, 1e-300), r_ / (1 + r_))
        q = JN.plateau_quantities(p, s, x, 1.0, r_)
        jumps = s[1:][np.abs(np.diff(y)) > 0.05]
        multi = s[(nl > 1) & (s > 1.001)]
        wres[case].append(dict(r=r_, J=q["J"], duration=q["dT"], plateau_infections=q["inf_plateau"],
                               plateau_new_Sq=q["Sq_plateau"], terminal_share_numeric=float(y[1]),
                               terminal_share_theory=r_ / (1 + r_),
                               quarantine_only_from_s=float(s[np.argmax((y < 1e-6) & (s > 1.01))])
                               if np.any((y < 1e-6) & (s > 1.01)) else None,
                               jump_at_s=jumps.tolist(),
                               two_local_minima_s_range=[float(multi.min()), float(multi.max())]
                               if len(multi) else None))
        a.plot(s, y, color=col, lw=1.8, label=f"$r=w_q/w_c={r_:g}$")
        a.plot(1, r_ / (1 + r_), "o", ms=5, color=col)
    a.axvline(ssw, color="#8a8a85", lw=0.8, ls=":")
    a.text(ssw, 0.97, f"  $s_{{sw}}={ssw:.3f}$", color="#5c5c58", va="top")
    a.set_xlabel(r"$s=S/S_c$（退出在 $s=1$，启动在 $s=s^*$）")
    a.set_ylabel(r"接触承担份额 $y=(1-c/c_0)/(1-S_c/S)$")
    a.set_ylim(-0.02, 1.0)
    a.set_title(("(a) 基准参数" if case == "baseline" else "(b) 西安参数")
                + r"：$y=0$ 为仅隔离，$y=1$ 为仅减少接触")
    a.grid(**GRID)
    a.legend(frameon=False, loc="upper right", bbox_to_anchor=(1, 0.88))
save(fig, "fig_weights")
summary["weights"] = wres
jdump(wres, "weights.json")

# ============================================================ 5. 线性成本稳健性（西安）
p = CASES["xian"]
Sc, Sbar, Sstar = JN.basics(p)
s = JN.s_grid(p, NS)
sbar = Sbar / Sc
r_ = 2.0
x_lin = np.where(s > sbar + r_ * (1 - sbar), 1.0, 1 / s)
lin = {}
for k, x in [("quarantine_only", JN.x_policy("quarantine_only", s)),
             ("minimum_cost_quadratic", JN.allocate(p, s, 1, 2, nx=NX)[0]),
             ("linear_optimal", x_lin), ("contact_only", JN.x_policy("contact_only", s))]:
    q = JN.plateau_quantities(p, s, x)
    lin[k] = dict(J_quadratic=q["J"], J_linear=q["J_lin"], duration=q["dT"])
lin["TDINN"] = dict(J_quadratic=XREF["J_T"],
                    J_linear=XREF["strategies"][0]["J_c"] + 2 * XREF["strategies"][0]["J_q"],
                    duration=XREF["t_end_T"])
lin["linear_switch_s"] = sbar + r_ * (1 - sbar)
summary["linear_xian"] = lin
jdump(lin, "linear_cost_xian.json")

# ============================================================ 6. 结构命题数值核对
chk = {}
for case, p in CASES.items():
    Sc, Sbar, Sstar = JN.basics(p)
    sbar = Sbar / Sc
    ssw = (3 + np.sqrt(9 - 8 * sbar)) / 2
    s = np.linspace(1.001, Sstar / Sc, 3000)
    out = {}
    for r_ in RS + [0.1, 20.0]:
        h = 1e-7
        f = lambda x: JN.f_int(x, s, sbar, 1.0, r_, 0.0)
        d_lo = (f(1 / s + h) - f(1 / s)) / h          # 仅接触端的右导数
        d_hi = (f(np.ones_like(s)) - f(1 - h)) / h     # 仅隔离端的左导数
        out[str(r_)] = dict(contact_only_never_local_min=bool(np.all(d_lo < 0)),
                            q_only_local_iff_s_ge_ssw=bool(np.all((d_hi <= 0) == (s >= ssw))
                                                           or np.sum((d_hi <= 0) != (s >= ssw)) <= 2))
    chk[case] = dict(s_sw=ssw, checks=out)
summary["structure_checks"] = chk
jdump(summary, "summary.json")
print(json.dumps(dict(cap=cap_res, weights=wres, linear=lin, checks=chk), ensure_ascii=False,
                 indent=1, default=float))
