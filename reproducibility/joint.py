"""联合阈值基准的本地复现与预先时间开环核对。

冻结包只作只读来源。完整类候选比较沿用原核心；时间开环核对先生成
名义轨迹和控制表，再把固定的时间插值函数输入完整 SIQR 方程。
数值一致性支持论文四位小数，不构成严格根隔离或浮点尾数认证。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import warnings

import numpy as np
from numpy.polynomial import Polynomial
import scipy
from scipy.integrate import quad, solve_ivp
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq


PACKAGE = "ai/threshold_control_reproducible_release_20261002"
Y = Polynomial([0.0, 1.0])


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2,
                               allow_nan=False) + "\n", encoding="utf-8")


def _csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: format(v, ".17g") if isinstance(v, float) else v
                             for k, v in row.items()})


def _load_core(root: Path):
    path = root / PACKAGE / "numerics/joint_comparison.py"
    name = "_joint_frozen_" + _sha(path)[:12]
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        # 直接执行读入的源码，避免普通 import 在冻结包写入 __pycache__。
        exec(compile(path.read_bytes(),str(path),"exec"),module.__dict__)
    return sys.modules[name]


def _scaled_candidates(S: float, p) -> tuple[float, list[dict]]:
    """退化区间在 y=(1-c/c0)/(1-Sc/S) 中比较全部候选。

    直接使用代数等价的 h'(y) 多项式，避免先展开原五次式再平移造成
    消减。z=0 的端点单独处理；不预设唯一、凸或单峰。
    """
    z = 1.0 - p.Sc / S
    if z <= 0:
        return 1.0, [{"contact_fraction": p.wq / (p.wc+p.wq),
                      "value": 0.0, "root_residual": 0.0}]
    b = p.barS / S
    u = Polynomial([1.0, -z])
    poly = (p.wc * (2*Y*u**3*(u-b) + z*Y**2*u**3)
            + p.wq * (-2*(1-z)*(1-Y)*(u-b) + z*(1-Y)**2*u))
    candidates = [(0.0, 0.0), (1.0, 0.0)]
    for root in poly.roots():
        if abs(root.imag) <= 1e-9*(1+abs(root.real)) and -1e-10 <= root.real <= 1+1e-10:
            y = float(np.clip(root.real, 0, 1))
            scale = max(1.0, float(np.sum(np.abs(poly.coef))))
            candidates.append((y, float(abs(poly(y))/scale)))
    records = []
    for y, residual in candidates:
        uval = 1-z*y
        value = (p.wc*y*y + p.wq*(1-y)**2/uval**2)/(uval-b)
        records.append({"contact_fraction": y, "value": float(value),
                        "root_residual": residual})
    selected = min(records, key=lambda r: (r["value"], -r["contact_fraction"]))
    return float(1-z*selected["contact_fraction"]), records


def _profile(name: str, S: float, p, core) -> float:
    s = max(float(S), p.Sc)
    if name == "contact_only":
        return p.Sc/s
    if name == "alpha_0.5":
        return .5+.5*p.Sc/s
    if name == "quarantine_only":
        return 1.0
    if 1-p.Sc/s < 1e-4:
        return _scaled_candidates(s, p)[0]
    return core.optimal_x(s, p)


def _root_diagnostics(p, scalar: dict, core) -> dict:
    states = np.unique(np.r_[np.linspace(p.Sc, scalar["Sstar"], 257)[1:],
                            p.Sc/(1-np.asarray([1e-3, 1e-5, 1e-7, 1e-9, 1e-11, 1e-13]))])
    rows = []
    for S in states:
        r, b = p.Sc/S, p.barS/S
        poly = (p.wc*core.X**3*(core.X-1)*(core.X+1-2*b)
                + p.wq*(core.X-r)*(-core.X**2+3*r*core.X-2*b*r))
        candidates = core.stationary_candidates(r, b, p.wc, p.wq)
        selected = core.optimal_x(float(S), p)
        stable, stable_candidates = _scaled_candidates(float(S), p)
        records = []
        for x in candidates:
            endpoint = abs(x-r) < 1e-10 or abs(x-1) < 1e-10
            denominator = sum(abs(float(a))*abs(x)**k for k, a in enumerate(poly.coef))
            residual = float(abs(poly(x))/max(denominator, 1e-300))
            records.append({"x": x, "value": float(core.dimensionless_cost(x,r,b,p.wc,p.wq)),
                            "endpoint": bool(endpoint), "normalized_polynomial_residual": residual})
        branch = "lower" if abs(selected-r)<1e-10 else "upper" if abs(selected-1)<1e-10 else "interior"
        rows.append({"S": float(S), "z": float(1-r), "selected_x": float(selected),
                     "scaled_selected_x": stable, "absolute_selection_difference": abs(selected-stable),
                     "selected_branch": branch, "candidates": records,
                     "scaled_candidates": stable_candidates})
    regular = [r for r in rows if r["z"] >= 1e-4]
    root_errors = [x["normalized_polynomial_residual"] for row in rows
                   for x in row["candidates"] if not x["endpoint"]]
    max_gap = max(r["absolute_selection_difference"] for r in regular)
    max_root_residual = max(root_errors, default=0.0)
    transitions = []
    ordered = sorted(regular, key=lambda r: r["S"])
    for first, second in zip(ordered, ordered[1:]):
        if first["selected_branch"] != second["selected_branch"]:
            transitions.append({"S_interval": [first["S"],second["S"]],
                                "branches": [first["selected_branch"],second["selected_branch"]]})
    return {"state_count": len(rows), "rows": rows,
            "maximum_nonendpoint_normalized_root_residual": max_root_residual,
            "maximum_selection_difference_nonshrinking_interval": max_gap,
            "sampled_branch_transitions": transitions,
            "coordinate_cross_check_passed": max_gap < 1e-7 and max_root_residual < 1e-8,
            "notes": ["原坐标与缩放坐标分别计算全部有限候选，核对选中值与分支。",
                      "退出区间缩小时采用缩放候选避免消减；保留原核心输出。",
                      "数值实根筛选不是严格区间根隔离，采样分支稳定不认证区间外。"]}


def _quadrature(p, scalar: dict, core, eps: float) -> dict:
    rows = []
    for baseline in scalar["rows"]:
        name = baseline["strategy"]
        def duration_integrand(S):
            x = _profile(name, S, p, core)
            return p.N/(p.eta*p.c0*(x*S-p.barS))
        def cost_integrand(S):
            x = _profile(name, S, p, core)
            return duration_integrand(S)*(p.wc*(1-x)**2+p.wq*(1-p.Sc/(x*S))**2)
        duration, duration_estimate = quad(duration_integrand,p.Sc,scalar["Sstar"],
                                          epsabs=eps,epsrel=eps*.1,limit=500)
        cost, cost_estimate = quad(cost_integrand,p.Sc,scalar["Sstar"],
                                  epsabs=eps,epsrel=eps*.1,limit=500)
        rows.append({"strategy": name, "duration": duration, "cost": cost,
                     "quad_duration_error_estimate": duration_estimate,
                     "quad_cost_error_estimate": cost_estimate,
                     "difference_from_frozen_core_duration": abs(duration-baseline["duration"]),
                     "difference_from_frozen_core_cost": abs(cost-baseline["cost"])})
    return {"epsabs": eps, "epsrel": eps*.1, "rows": rows,
            "error_estimate_is_rigorous_bound": False}


def _openloop(p, scalar: dict, core, level: str) -> tuple[dict, list[dict]]:
    fine = level == "fine"
    rtol, atol, control_samples = (2e-11,2e-12,4097) if fine else (2e-9,2e-10,1025)
    def rhs(y, c, q, active):
        S,I,Sq,Iq,R,C,J = y
        inf = p.beta*c*S*I/p.N
        to_sq = (1-p.beta)*c*q*S*I/p.N
        cost = p.wc*(1-c/p.c0)**2+p.wq*((q-p.q0)/(1-p.q0))**2 if active else 0.0
        return [-inf-to_sq,inf*(1-q)-p.gamma*I,to_sq,
                inf*q-p.delta_q*Iq,p.gamma*I+p.delta_q*Iq,inf,cost]
    def regular(t,y):
        return rhs(y,p.c0,p.q0,False)
    def trigger(t,y):
        return y[1]-p.eta
    trigger.terminal=True
    trigger.direction=1
    pre = solve_ivp(regular,(0,2*scalar["t1"]+1),[p.S0,p.I0,0,0,0,0,0],
                    events=trigger,dense_output=True,method="DOP853",rtol=rtol,atol=atol,
                    max_step=scalar["t1"]/100)
    if not pre.success or not len(pre.t_events[0]):
        raise RuntimeError("未到达共同的上升阈值事件。")
    t1 = float(pre.t_events[0][0])
    entry = pre.y_events[0][0]
    reports, traces = [], []
    for baseline in scalar["rows"]:
        name = baseline["strategy"]
        # 此处只解一维名义轨迹；之后完整方程中的控制不访问其实际状态。
        def nominal_rhs(t,y):
            S=max(float(y[0]),p.Sc)
            return [-p.eta*p.c0*(_profile(name,S,p,core)*S-p.barS)/p.N]
        def nominal_exit(t,y):
            return y[0]-p.Sc
        nominal_exit.terminal=True
        nominal_exit.direction=-1
        nominal = solve_ivp(nominal_rhs,(0,baseline["duration"]*1.3),[scalar["Sstar"]],
                            events=nominal_exit,dense_output=True,method="DOP853",
                            rtol=rtol*.1,atol=atol*.1,max_step=baseline["duration"]/150)
        if not nominal.success or not len(nominal.t_events[0]):
            raise RuntimeError(name+": 名义 S(t) 未到达退出状态。")
        duration=float(nominal.t_events[0][0])
        time_grid=np.linspace(0,duration,control_samples)
        breaks=[]
        if name=="minimum_cost":
            # 上端点转入内部驻点时，控制连续但其导数可以改变。分别插值
            # 两侧，避免 PCHIP 跨这一已知分支边界平滑而改变开环控制。
            d=p.barS/p.Sc
            r_boundary=2/(3+np.sqrt(9-8*d))
            S_boundary=p.Sc/r_boundary
            if p.Sc<S_boundary<scalar["Sstar"]:
                breaks.append(float(brentq(lambda t: nominal.sol(t)[0]-S_boundary,0,duration)))
        time_grid=np.unique(np.r_[time_grid,breaks])
        nominal_S=np.maximum(nominal.sol(time_grid)[0],p.Sc)
        xx=np.asarray([_profile(name,S,p,core) for S in nominal_S])
        cc=p.c0*xx
        qq=1-(1-p.q0)*p.Sc/(xx*nominal_S)
        cc[-1],qq[-1]=p.c0,p.q0
        boundaries=[0.0]+breaks+[duration]
        interpolation=[]
        for left,right in zip(boundaries,boundaries[1:]):
            mask=(time_grid>=left)&(time_grid<=right)
            interpolation.append((right,PchipInterpolator(time_grid[mask],cc[mask]),
                                   PchipInterpolator(time_grid[mask],qq[mask])))
        def controls(t):
            relative=float(np.clip(t-t1,0,duration))
            for right,c_time,q_time in interpolation:
                if relative<=right:
                    return float(c_time(relative)),float(q_time(relative))
            raise RuntimeError("开环时间表超出已定义区间。")
        # 由预先的名义时钟退出，记录实际 S、I 的偏差而不把它们强制修正。
        def controlled(t,y):
            c,q=controls(t)
            return rhs(y,c,q,True)
        t2=t1+duration
        mid=solve_ivp(controlled,(t1,t2),entry,dense_output=True,method="DOP853",
                      rtol=rtol,atol=atol,max_step=duration/150)
        if not mid.success:
            raise RuntimeError(name+": 开环完整方程积分失败。")
        exit_state=mid.y[:,-1]
        def clearance(t,y):
            return y[1]-1
        clearance.terminal=True
        clearance.direction=-1
        post=solve_ivp(regular,(t2,t2+2*scalar["post_control_duration"]+1),exit_state,
                       events=clearance,dense_output=True,method="DOP853",
                       rtol=rtol,atol=atol,max_step=scalar["post_control_duration"]/150)
        if not post.success or not len(post.t_events[0]):
            raise RuntimeError(name+": 开环恢复后未达到下降清零事件。")
        tend=float(post.t_events[0][0])
        final=post.y_events[0][0]
        check_times=np.linspace(t1,t2,1201)
        controlled_states=mid.sol(check_times)
        maximum_mass=0.0
        minimum_compartment=float("inf")
        for sol,start,stop in [(pre,0,t1),(mid,t1,t2),(post,t2,tend)]:
            sample=sol.sol(np.linspace(start,stop,1201))
            maximum_mass=max(maximum_mass,float(np.max(abs(np.sum(sample[:5],axis=0)-p.N))))
            minimum_compartment=min(minimum_compartment,float(np.min(sample[:5])))
        errors={"duration_days": abs(duration-baseline["duration"]),
                "cost_days": abs(float(final[6])-baseline["cost"]),
                "clearance_time_days":abs(tend-baseline["t_end"]),
                "total_new_infections_persons":abs(float(final[5])-baseline["total_infections"]),
                "control_new_infections_persons":abs(float(exit_state[5]-entry[5])-baseline["new_infections_control"]),
                "control_new_Sq_persons":abs(float(exit_state[2]-entry[2])-baseline["new_Sq_control"]),
                "exit_S_persons":abs(float(exit_state[0])-p.Sc),
                "exit_I_persons":abs(float(exit_state[1])-p.eta),
                "plateau_I_max_abs_error_persons":float(np.max(abs(controlled_states[1]-p.eta))),
                "population_max_abs_error_persons":maximum_mass}
        report={"strategy":name,"t1":t1,"t2":t2,"t_end":tend,
                "duration":duration,"cost":float(final[6]),
                "total_new_infections":float(final[5]),"absolute_errors":errors,
                "minimum_sampled_compartment":minimum_compartment,
                "control_samples":control_samples,
                "nominal_branch_break_times":breaks,
                "nominal_time_table":{"relative_time_days":time_grid.tolist(),
                    "S":nominal_S.tolist(),"c":cc.tolist(),"q":qq.tolist(),
                    "interpolation":"各分支区间分别使用 PCHIP，切换点保留左右邻域。"},
                "controls_within_basic_bounds":bool(min(cc)>0 and max(cc)<=p.c0+1e-10
                    and min(qq)>=p.q0-1e-10 and max(qq)<1),
                "passed":max(errors.values())<5e-5 and minimum_compartment>=-1e-8}
        report["passed"]=bool(report["passed"] and report["controls_within_basic_bounds"])
        reports.append(report)
        for phase,sol,start,stop in [("before",pre,0,t1),("control",mid,t1,t2),("after",post,t2,tend)]:
            times=np.linspace(start,stop,301)
            actual=sol.sol(times).T
            for t,y in zip(times,actual):
                c,q=controls(t) if phase=="control" else (p.c0,p.q0)
                traces.append({"strategy":name,"phase":phase,"time_days":float(t),
                    "S":float(y[0]),"I":float(y[1]),"Sq":float(y[2]),"Iq":float(y[3]),
                    "R":float(y[4]),"total_new_infections":float(y[5]),"J":float(y[6]),
                    "c":float(c),"q":float(q),
                    "S_nominal":float(nominal.sol(np.clip(t-t1,0,duration))[0]) if phase=="control" else ""})
    return {"level":level,"rtol":rtol,"atol":atol,"rows":reports,
            "control_implementation":"先解独立名义 S(t)，固定 PCHIP 时间表；实际 ODE 不访问实时 S 求控制。",
            "entry_time_error":abs(t1-scalar["t1"]),
            "passed":all(r["passed"] for r in reports)},traces


def run(output_dir: Path, root: Path) -> dict:
    """输出本地证据；不改冻结包、旧结果、论文及图件。"""
    root,output_dir=Path(root).resolve(),Path(output_dir).resolve()
    out=output_dir/"joint"
    out.mkdir(parents=True,exist_ok=True)
    core=_load_core(root)
    config_path=root/PACKAGE/"numerics/inputs/baseline_parameters.json"
    config=json.loads(config_path.read_text(encoding="utf-8"))
    p=core.Parameters(**config["parameters"])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fine=core.compute(p,eps=1e-9,ode_check=False)
        coarse=core.compute(p,eps=1e-7,ode_check=False)
        roots=_root_diagnostics(p,fine,core)
        quadrature_fine=_quadrature(p,fine,core,1e-9)
        quadrature_coarse=_quadrature(p,fine,core,1e-7)
        open_coarse,_=_openloop(p,fine,core,"coarse")
        open_fine,traces=_openloop(p,fine,core,"fine")
    convergence=[]
    for f,c,of,oc in zip(fine["rows"],coarse["rows"],open_fine["rows"],open_coarse["rows"]):
        convergence.append({"strategy":f["strategy"],
            "core_integral_absolute_change":{k:abs(f[k]-c[k]) for k in ["duration","cost","total_infections","t_end","new_Sq_control"]},
            "openloop_absolute_change":{k:abs(of[k]-oc[k]) for k in ["duration","cost","total_new_infections","t_end"]}})
    selected=next(r for r in fine["rows"] if r["strategy"]=="minimum_cost")
    rounded=(f'{selected["cost"]:.4f}'=="2.1183" and f'{selected["duration"]:.4f}'=="7.7536")
    convergence_ok=all(max(r["core_integral_absolute_change"].values())<5e-5
                       and max(r["openloop_absolute_change"].values())<5e-5 for r in convergence)
    quadrature_ok=all(r["difference_from_frozen_core_duration"]<5e-5
                      and r["difference_from_frozen_core_cost"]<5e-5 for r in quadrature_fine["rows"])
    passed=bool(rounded and convergence_ok and quadrature_ok and open_fine["passed"]
                and open_coarse["passed"] and roots["coordinate_cross_check_passed"])
    fine.update({"coarse_result":coarse,"convergence":convergence,
        "stable_quadrature":{"fine":quadrature_fine,"coarse":quadrature_coarse},
        "four_decimal_manuscript_match":rounded,"passed":passed,
        "software":{"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__},
        "source_hashes":{"core":_sha(root/PACKAGE/"numerics/joint_comparison.py"),
                         "input":_sha(config_path),"local_runner":_sha(Path(__file__))},
        "warnings":[str(w.message) for w in caught],
        "precision_boundary":"binary64 数值及两档收敛/时间开环交叉核对支持论文四位小数；不认证全部尾数、根完整性或一般全局最优。",
        "capacity_scope":"本次仍是无额外能力约束基准；未执行受限能力或临床医疗占用扩展。"})
    _json(out/"results.json",fine)
    _csv(out/"results.csv",fine["rows"])
    _json(out/"root_diagnostics.json",roots)
    _json(out/"openloop_check.json",{"fine":open_fine,"coarse":open_coarse,
                                     "convergence":convergence,"passed":passed})
    _csv(out/"trajectories.csv",traces)
    artifacts=[str((out/name).relative_to(output_dir)).replace("\\","/") for name in
               ["results.json","results.csv","openloop_check.json","trajectories.csv","root_diagnostics.json"]]
    return {"passed":passed,"artifacts":artifacts,"J_min":selected["cost"],
            "duration_days":selected["duration"],"four_decimal_match":rounded,
            "openloop_passed":open_fine["passed"],
            "maximum_openloop_absolute_error":max(max(r["absolute_errors"].values()) for r in open_fine["rows"]),
            "numerical_global_optimality_certified":False}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir",type=Path,required=True)
    arguments=parser.parse_args()
    result=run(arguments.output_dir,arguments.root)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result["passed"] else 1)
