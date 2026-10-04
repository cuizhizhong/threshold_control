"""联合阈值控制补充数值（第 6.4 节新增图表的数据来源）。

用法（项目根目录）：
    python -B reproducibility/joint_extra/run.py [--out reproducibility/results/joint_extra_v1]
                                                 [--xian-reference <reference.json>]

输出均为未取整结果；图件由 figures.py 只从这些文件读取。
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core as JN  # noqa: E402

NS, NX = 8001, 4001                      # 状态网格、分配网格
STRATEGIES = ["contact_only", "alpha_0.5", "quarantine_only", "minimum_cost"]
KAPPA = np.unique(np.concatenate([-np.logspace(2, -4, 70), [0.0], np.logspace(-4, 2, 70),
                                  np.linspace(-1.5, 0.2, 171)]))
ALPHAS = np.linspace(0.0, 1.0, 41)
R_GRID = np.logspace(-1, np.log10(20.0), 161)
CAPACITY_POINTS = {"baseline": dict(u_max=0.5, q_cap=0.6), "xian": dict(u_max=0.5, q_cap=0.75)}


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (format(v, ".17g") if isinstance(v, float) else v) for k, v in r.items()})


def write_json(path: Path, obj) -> None:
    def conv(o):
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=conv, allow_nan=True) + "\n",
                    encoding="utf-8")


def allocations(p, s):
    return {"contact_only": JN.x_policy("contact_only", s),
            "alpha_0.5": JN.x_policy("alpha", s, 0.5),
            "quarantine_only": JN.x_policy("quarantine_only", s),
            "minimum_cost": JN.allocate(p, s, 1.0, 2.0, nx=NX)[0]}


def compare(case, p, ref, out):
    s = JN.s_grid(p, NS)
    rows, traj = [], []
    for k, x in allocations(p, s).items():
        r = JN.full_run(p, s, x)
        q = JN.plateau_quantities(p, s, x)
        rows.append(dict(case=case, strategy=k, t1=r["t1"], t2=r["t2"], duration=r["dT"],
                         t_end=r["t_end"], total_infections=r["total_infections"],
                         plateau_infections=r["plateau_infections"],
                         plateau_new_Sq=r["plateau_Sq"], plateau_new_Iq=r["plateau_Iq_new"],
                         peak_I_plus_Iq=r["peak_I_plus_Iq"],
                         peak_I_plus_Iq_over_eta=r["peak_I_plus_Iq"] / p["eta"],
                         t_peak_I_plus_Iq=r["t_peak_I_plus_Iq"], J=r["J"], J_c=r["Jc"], J_q=r["Jq"],
                         J_quadrature=q["J"], duration_quadrature=q["dT"],
                         conservation_infections=q["inf_plateau"], conservation_Sq=q["Sq_plateau"],
                         q_max=q["q_max"], c_min=q["c_min"], max_rel_drift=r["max_rel_drift"]))
        if case == "baseline":
            tr = r["traj"]
            for i in range(len(tr["t"])):
                traj.append(dict(strategy=k, t=float(tr["t"][i]), S=float(tr["S"][i]),
                                 I=float(tr["I"][i]), Sq=float(tr["Sq"][i]), Iq=float(tr["Iq"][i]),
                                 c=float(tr["c"][i]), q=float(tr["q"][i])))
    if case == "xian":
        T = JN.tdinn_run(p)
        st = ref["strategies"][0]
        rows.append(dict(case=case, strategy="TDINN_reference", t1=float("nan"), t2=float("nan"),
                         duration=float("nan"), t_end=ref["t_end_T"],
                         total_infections=ref["Itcum_T"], plateau_infections=float("nan"),
                         plateau_new_Sq=float("nan"), plateau_new_Iq=float("nan"),
                         peak_I_plus_Iq=T["peak_I_plus_Iq"],
                         peak_I_plus_Iq_over_eta=T["peak_I_plus_Iq"] / p["eta"],
                         t_peak_I_plus_Iq=float("nan"), J=ref["J_T"], J_c=st["J_c"], J_q=st["J_q"],
                         J_quadrature=float("nan"), duration_quadrature=float("nan"),
                         conservation_infections=float("nan"), conservation_Sq=float("nan"),
                         q_max=0.9844, c_min=3.4625, max_rel_drift=float("nan")))
    write_csv(out / f"compare_{case}.csv", rows)
    if traj:
        write_csv(out / f"trajectories_{case}.csv", traj)
    return rows


def frontier(case, p, out):
    s = JN.s_grid(p, 4001)
    rows = []
    for k in KAPPA:
        x, _ = JN.allocate(p, s, 1.0, 2.0, kappa=k, nx=2001)
        q = JN.plateau_quantities(p, s, x)
        rows.append(dict(kappa=float(k), duration=q["dT"], J=q["J"],
                         plateau_infections=q["inf_plateau"], plateau_new_Sq=q["Sq_plateau"]))
    write_csv(out / f"frontier_{case}.csv", rows)
    arows = []
    for a in ALPHAS:
        q = JN.plateau_quantities(p, s, JN.x_policy("alpha", s, a))
        arows.append(dict(alpha=float(a), duration=q["dT"], J=q["J"]))
    write_csv(out / f"alpha_family_{case}.csv", arows)


def capacity(cases, out):
    res = {}
    for case, p in cases.items():
        Sc, Sbar, Sstar = JN.basics(p)
        sst = Sstar / Sc
        pt = CAPACITY_POINTS[case]
        s = JN.s_grid(p, NS)
        x, _ = JN.allocate(p, s, 1.0, 2.0, cmin=(1 - pt["u_max"]) * p["c0"], qcap=pt["q_cap"], nx=NX)
        r = JN.full_run(p, s, x)
        q = JN.plateau_quantities(p, s, x)
        res[case] = dict(q0=p["q0"], s_star=sst,
                         q_required_quarantine_only=1 - (1 - p["q0"]) / sst,
                         u_required_contact_only=1 - 1 / sst,
                         joint_feasibility_bound=(1 - p["q0"]) / sst, point=pt,
                         duration=r["dT"], t1=r["t1"], t2=r["t2"], J=r["J"], t_end=r["t_end"],
                         total_infections=r["total_infections"], plateau_new_Sq=r["plateau_Sq"],
                         peak_I_plus_Iq_over_eta=r["peak_I_plus_Iq"] / p["eta"],
                         q_max=q["q_max"], c_min=q["c_min"], max_rel_drift=r["max_rel_drift"])
        tr = r["traj"]
        m = (tr["t"] >= r["t1"] - 0.5) & (tr["t"] <= r["t2"] + 0.5)
        write_csv(out / f"capacity_traj_{case}.csv",
                  [dict(t=float(t), c=float(c), q=float(qq)) for t, c, qq in
                   zip(tr["t"][m], tr["c"][m], tr["q"][m])])
    write_json(out / "capacity.json", res)
    return res


def phase(cases, out):
    summ = {}
    for case, p in cases.items():
        Sc, Sbar, Sstar = JN.basics(p)
        sbar, sst = Sbar / Sc, Sstar / Sc
        ssw = (3 + np.sqrt(9 - 8 * sbar)) / 2
        s = np.linspace(1.0, sst, 1201)
        Y = np.empty((len(R_GRID), len(s)))
        switch, two_lo, two_hi = [], [], []
        for i, r in enumerate(R_GRID):
            x, nl = JN.allocate(p, s, 1.0, r, nx=3001)
            y = np.where(s > 1 + 1e-12, (1 - x) / np.maximum(1 - 1 / s, 1e-300), r / (1 + r))
            Y[i] = np.clip(y, 0, 1)
            qo = (Y[i] < 1e-6) & (s > 1.0005)
            switch.append(float(s[np.argmax(qo)]) if qo.any() else np.nan)
            m = (nl > 1) & (s > 1.0005)
            two_lo.append(float(s[m].min()) if m.any() else np.nan)
            two_hi.append(float(s[m].max()) if m.any() else np.nan)
        switch = np.array(switch)
        dep = switch > ssw + 2 * (s[1] - s[0])
        np.savez(out / f"phase_{case}.npz", s=s, r=R_GRID, y=Y, switch=switch,
                 two_minima_lo=np.array(two_lo), two_minima_hi=np.array(two_hi))
        summ[case] = dict(s_sw=ssw, s_star=sst, sbar=sbar,
                          r_switch_departs_from_ssw=float(R_GRID[np.argmax(dep)]) if dep.any() else None,
                          r_quarantine_only_never_global=float(R_GRID[np.argmax(np.isnan(switch))])
                          if np.isnan(switch).any() else None,
                          max_terminal_share_error=float(np.max(np.abs(Y[:, 1] - R_GRID / (1 + R_GRID)))))
    write_json(out / "phase.json", summ)
    return summ


def structure_checks(cases, out):
    chk = {}
    for case, p in cases.items():
        Sc, Sbar, Sstar = JN.basics(p)
        sbar = Sbar / Sc
        ssw = (3 + np.sqrt(9 - 8 * sbar)) / 2
        s = np.linspace(1.001, Sstar / Sc, 3000)
        res = {}
        for r in (0.1, 0.5, 1.0, 2.0, 5.0, 20.0):
            h = 1e-7
            f = lambda x: JN.f_int(x, s, sbar, 1.0, r, 0.0)
            d_lo = (f(1 / s + h) - f(1 / s)) / h
            d_hi = (f(np.ones_like(s)) - f(1 - h)) / h
            mism = int(np.sum((d_hi <= 0) != (s >= ssw)))
            res[str(r)] = dict(contact_only_right_derivative_negative=bool(np.all(d_lo < 0)),
                               quarantine_only_local_iff_s_ge_ssw_mismatches=mism)
        chk[case] = dict(s_sw=ssw, checks=res)
    write_json(out / "structure_checks.json", chk)
    return chk


def convergence(cases, out):
    res = {}
    for case, p in cases.items():
        lv = []
        for ns, nx in ((4001, 2001), (8001, 4001), (16001, 8001)):
            s = JN.s_grid(p, ns)
            x, _ = JN.allocate(p, s, 1.0, 2.0, nx=nx)
            q = JN.plateau_quantities(p, s, x)
            lv.append(dict(ns=ns, nx=nx, J_min=q["J"], duration=q["dT"]))
        res[case] = dict(levels=lv,
                         rel_change_J=abs(lv[-1]["J_min"] - lv[-2]["J_min"]) / lv[-1]["J_min"],
                         rel_change_duration=abs(lv[-1]["duration"] - lv[-2]["duration"]) / lv[-1]["duration"])
    write_json(out / "convergence.json", res)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(JN.ROOT / "reproducibility/results/joint_extra_v1"))
    ap.add_argument("--baseline", default=str(JN.ROOT / JN.BASELINE_JSON))
    ap.add_argument("--xian-reference", default=str(JN.ROOT / JN.XIAN_REFERENCE))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pb = JN.baseline_params(a.baseline)
    px, ref = JN.xian_params(a.xian_reference)
    cases = {"baseline": pb, "xian": px}
    for case, p in cases.items():
        compare(case, p, ref, out)
    frontier("baseline", pb, out)
    capacity(cases, out)
    phase(cases, out)
    structure_checks(cases, out)
    conv = convergence(cases, out)
    write_json(out / "manifest.json", dict(
        created=_dt.datetime.now().isoformat(timespec="seconds"),
        inputs={a.baseline: sha(a.baseline), a.xian_reference: sha(a.xian_reference)},
        sources={f.name: sha(f) for f in (HERE / "core.py", HERE / "run.py", HERE / "figures.py")
                 if f.exists()},
        software=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        settings=dict(NS=NS, NX=NX, n_kappa=len(KAPPA), n_alpha=len(ALPHAS), n_r=len(R_GRID),
                      r_range=[float(R_GRID[0]), float(R_GRID[-1])], weights=[1.0, 2.0],
                      capacity_points=CAPACITY_POINTS, ode="DOP853 rtol=1e-11 atol=1e-13 N",
                      plateau="三阶段时间开环，名义 S(t) 预先构造 c(t), q(t)"),
        convergence=conv))
    print("written to", out)


if __name__ == "__main__":
    main()
