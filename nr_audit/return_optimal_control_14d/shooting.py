"""14天正回流的独立分段常控制shooting求解器。

平台按矩阵指数精确传播；成本用Gauss求积。只在显式CLI调用或solve调用时优化。
本文件不修改冻结来源。数值结果不构成一般全局最优性证明。
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp
from scipy.linalg import expm, expm_frechet
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def parameters(case: str) -> dict:
    """从冻结参数源只读取值。"""
    source = ROOT / "r7_return" / "params.py"
    spec = importlib.util.spec_from_file_location("_return_shooting_params", source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previous_bytecode_setting = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous_bytecode_setting
    p = module.CASES[case]
    data = asdict(p)
    data.update(sc=p.S_c / p.N, theta=p.eta / p.N, omega=1.0 / 14.0)
    return data


def starting_state(case: str) -> dict:
    """独立计算同一含回流常规轨迹的启动状态；只积分三个闭合状态。"""
    p = parameters(case)
    n, beta, c0, q0 = p["N"], p["beta"], p["c0"], p["q0"]
    a = c0 * (beta + (1-beta)*q0)
    b = beta*c0*(1-q0)
    d = (1-beta)*c0*q0

    def rhs(t, y):
        s, logi, sq = y
        i = np.exp(logi)
        return [-a*s*i+p["omega"]*sq, b*s-p["gamma"], d*s*i-p["omega"]*sq]

    def trigger(t, y):
        return y[1] - np.log(p["theta"])

    trigger.terminal = True
    trigger.direction = 1
    result = solve_ivp(rhs, (0, 5000),
                       [p["S0"]/n, np.log(p["I0"]/n), p["Sq0"]/n],
                       events=trigger, method="DOP853", rtol=1e-12,
                       atol=[1e-14, 1e-12, 1e-16], max_step=0.5)
    if not result.success or not len(result.t_events[0]):
        raise RuntimeError(f"{case}: 未定位到触发状态: {result.message}")
    return dict(case=case, t1=float(result.t[-1]), s_N=float(result.y[0,-1]),
                sq_N=float(result.y[2,-1]), i_N=p["theta"], method="DOP853")


class TailMap:
    """退出后固定动力学的值及对退出Sq/N的敏感度，不截断于I=1。"""
    def __init__(self, p: dict, safety_only=False):
        self.p = p
        self.safety_only = safety_only
        self.cache = {}
        self.calls = 0

    def __call__(self, sq_exit: float) -> dict:
        key = float(sq_exit)
        if key in self.cache:
            return self.cache[key]
        p = self.p
        beta, c0, q0, omega = p["beta"], p["c0"], p["q0"], p["omega"]
        a = c0*(beta+(1-beta)*q0)
        b = beta*c0*(1-q0)
        d = (1-beta)*c0*q0
        # 优化内部采用比最终总感染预算更小的尾量；最终仍由独立评价器复核。
        eps_persons = 1e-8 if p["name"] == "base" else 1e-5
        eps_N = eps_persons/p["N"]

        def rhs(t, y):
            s, logi, sq = y[:3]
            i = np.exp(logi)
            jac = np.array([[-a*i, -a*s*i, omega],
                            [b, 0., 0.],
                            [d*i, d*s*i, -omega]])
            return np.r_[[-a*s*i+omega*sq, b*s-p["gamma"], d*s*i-omega*sq],
                         jac@y[3:]]

        def stop(t, y):
            u = y[0]+y[2]
            if self.safety_only:
                return p["sc"]*(1.-1e-9)-u
            return eps_N*p["gamma"]*(1-u/p["sc"]) - beta*c0*u*np.exp(y[1])

        stop.direction, stop.terminal = 1, True

        def peak(t, y):
            return y[0]-p["sc"]

        peak.direction, peak.terminal = -1, False
        y0 = [p["sc"], np.log(p["theta"]), key, 0., 0., 1.]
        out = solve_ivp(rhs, (0., 100000.), y0, method="DOP853", rtol=3e-11,
                        atol=[2e-14, 2e-12, 2e-14, 1e-11, 1e-10, 1e-11],
                        events=[stop, peak], max_step=2., dense_output=True)
        self.calls += 1
        if not out.success or not len(out.t_events[0]):
            raise RuntimeError(f"尾段不完整: {out.message}")
        y = out.y[:,-1]
        u = y[0]+y[2]
        bound_N = beta*c0*u*np.exp(y[1])/(p["gamma"]*(1-u/p["sc"]))
        # 含退出边界峰值。真内峰高于边界时用事件敏感度。
        max_ratio, peak_grad, peak_time = 1., 0., 0.
        for t, v in zip(out.t_events[1], out.y_events[1]):
            if t <= 1e-8:
                continue
            ratio = np.exp(v[1])/p["theta"]
            if ratio > max_ratio:
                max_ratio, peak_grad, peak_time = float(ratio), float(ratio*v[4]), float(t)
        # 加密样点只做额外防漏诊断，不替代事件定位。
        mids = (out.t[:-1]+out.t[1:])/2
        ratio_mid = np.exp(out.sol(mids)[1])/p["theta"] if len(mids) else []
        result = dict(u_inf_N=float(u), du_inf_dsq=float(y[3]+y[5]),
                      tail_bound_persons=float(bound_N*p["N"]),
                      tail_time=float(out.t[-1]), peak_ratio=max_ratio,
                      peak_grad=peak_grad, peak_time=peak_time,
                      dense_peak_ratio=float(max([1., *ratio_mid])), nfev=int(out.nfev))
        self.cache[key] = result
        return result


class ExactPlateau:
    """常lambda片段的精确状态传播及一阶敏感度。"""
    def __init__(self, p, start, n_segments, quadrature=4):
        self.p, self.start, self.n = p, start, n_segments
        nodes, weights = leggauss(quadrature)
        self.nodes, self.weights = (nodes+1)/2, weights/2
        beta, sc, gamma, theta = p["beta"], p["sc"], p["gamma"], p["theta"]
        r, k, omega = p["c0"]*theta, gamma*theta, p["omega"]
        a = (1-beta)/beta
        self.M0 = np.array([[0., omega, -r*sc+a*k],
                            [0., -omega, (1-beta)*r*sc-a*k],
                            [0., 0., 0.]])
        self.M1 = np.array([[-r, 0., r*sc],
                            [(1-beta)*r, 0., -(1-beta)*r*sc],
                            [0., 0., 0.]])
        self.cache_key, self.cache_value = None, None

    def __call__(self, z):
        z = np.asarray(z)
        key = z.tobytes()
        if key == self.cache_key:
            return self.cache_value
        T, us = z[0], z[1:]
        n, p = self.n, self.p
        h, sc = T/n, p["sc"]
        v = np.array([self.start["s_N"], self.start["sq_N"], 1.])
        grad = np.zeros((3, n+1))
        cost, cost_grad = 0., np.zeros(n+1)
        states, samples, sample_grads = [v[:2].copy()], [], []
        for k, u in enumerate(us):
            M = self.M0 + u*self.M1
            for xi, weight in zip(self.nodes, self.weights):
                E = expm(M*(h*xi))
                duE = expm_frechet(M*(h*xi), self.M1*(h*xi), compute_expm=False)
                qv = E@v
                qgrad = E@grad
                qgrad[:,0] += (M@qv)*xi/n
                qgrad[:,k+1] += duE@v
                s = qv[0]
                # 对优化器的试探性非物理解保持有限，约束会拒绝它。
                s_eval = max(s, 1e-10)
                w = max(u*s_eval+(1-u)*sc, 1e-10)
                aa, bb = (1-u)*(1-sc/s_eval), 1-sc/w
                g = aa*aa + p["wq"]*bb*bb
                gs = 2*aa*(1-u)*sc/s_eval**2 + 2*p["wq"]*bb*sc*u/w**2
                gu = -2*aa*(1-sc/s_eval) + 2*p["wq"]*bb*sc*(s_eval-sc)/w**2
                cost += h*weight*g
                cost_grad += h*weight*gs*qgrad[0]
                cost_grad[0] += weight*g/n
                cost_grad[k+1] += h*weight*gu
                samples.append(s-sc)
                sample_grads.append(qgrad[0].copy())
            E = expm(M*h)
            duE = expm_frechet(M*h, self.M1*h, compute_expm=False)
            old_v = v
            v = E@old_v
            grad = E@grad
            grad[:,0] += M@v/n
            grad[:,k+1] += duE@old_v
            states.append(v[:2].copy())
            if k < n-1:
                samples.append(v[0]-sc)
                sample_grads.append(grad[0].copy())
        result = dict(final=v, gradient=grad, J=cost, J_gradient=cost_grad,
                      states=np.asarray(states), inequalities=np.asarray(samples),
                      inequality_jac=np.asarray(sample_grads))
        self.cache_key, self.cache_value = key, result
        return result


def solve(case: str, objective: str, duration0: float, lambda0, *, n_segments=40,
          start_state=None, maxiter=400, log_dir=None, ftol=1e-11, seed_label="provided"):
    """返回分段常控制候选；所有目标均检查同一退出后阈值。"""
    if objective not in ("time", "cost", "infections"):
        raise ValueError(objective)
    p = parameters(case)
    start = starting_state(case) if start_state is None else dict(start_state)
    if "s_N" not in start:
        raise ValueError("start_state必须含s_N和sq_N")
    incoming = np.asarray(lambda0, dtype=float)
    if incoming.size != n_segments:
        incoming = np.interp((np.arange(n_segments)+0.5)/n_segments,
                             np.linspace(0,1,incoming.size), incoming)
    z0 = np.r_[duration0, np.clip(incoming,0,1)]
    plateau, tail = ExactPlateau(p,start,n_segments), TailMap(p,safety_only=objective!="infections")
    qcrit = p["c0"]*(p["beta"]+(1-p["beta"])*p["q0"])*p["sc"]*p["theta"]/p["omega"]
    Tbound = (start["s_N"]+start["sq_N"]-p["sc"])/(p["gamma"]*p["theta"]/(1-p["q0"]))
    total_u0 = (p["S0"]+p["Sq0"])/p["N"]

    def objective_fun(z):
        v = plateau(z)
        if objective == "time":
            return p["gamma"]*z[0]
        if objective == "cost":
            return p["gamma"]*v["J"]/(p["wc"]+p["wq"])
        out = tail(v["final"][1])
        return total_u0-out["u_inf_N"]

    def objective_jac(z):
        v = plateau(z)
        if objective == "time":
            g=np.zeros(n_segments+1); g[0]=p["gamma"]; return g
        if objective == "cost":
            return p["gamma"]*v["J_gradient"]/(p["wc"]+p["wq"])
        out = tail(v["final"][1])
        return -out["du_inf_dsq"]*v["gradient"][1]

    def eq(z):
        return np.array([plateau(z)["final"][0]-p["sc"]])

    def eqjac(z):
        return plateau(z)["gradient"][[0]]

    def inequalities(z):
        v=plateau(z)
        out=tail(v["final"][1])
        # 末端向下到达的必要条件，以及所有常规尾段内峰约束。
        return np.r_[v["inequalities"], v["final"][1], qcrit-v["final"][1], 1-out["peak_ratio"]]

    def ineqjac(z):
        v=plateau(z); out=tail(v["final"][1])
        return np.vstack([v["inequality_jac"], v["gradient"][1], -v["gradient"][1],
                          -out["peak_grad"]*v["gradient"][1]])

    t0=time.perf_counter()
    result=minimize(objective_fun,z0,jac=objective_jac,method="SLSQP",
                    bounds=[(1e-5,max(Tbound,1e-4))]+[(0.,1.)]*n_segments,
                    constraints=[dict(type="eq",fun=eq,jac=eqjac),
                                 dict(type="ineq",fun=inequalities,jac=ineqjac)],
                    options=dict(maxiter=maxiter,ftol=ftol,disp=False))
    v=plateau(result.x)
    final_tail=TailMap(p)
    t=final_tail(v["final"][1])
    output=dict(case=case,objective=objective,method="exact_expm_piecewise_constant_SLSQP",
                n_segments=n_segments,interpolation="constant",seed_label=seed_label,
                duration=float(result.x[0]),lambda_values=result.x[1:].tolist(),
                solver_success=bool(result.success),solver_status=int(result.status),
                solver_message=str(result.message),nit=int(result.nit),nfev=int(result.nfev),
                objective_scaled=float(result.fun),J=float(v["J"]),
                C_infty_estimate=float((total_u0-t["u_inf_N"])*p["N"]),
                Sq_exit=float(v["final"][1]*p["N"]),
                terminal_residual_N=float(eq(result.x)[0]),
                min_inequality=float(np.min(inequalities(result.x))),tail=t,
                wall_seconds=time.perf_counter()-t0,tail_integrations=tail.calls+final_tail.calls,
                initial_duration=float(z0[0]),initial_lambdas=z0[1:].tolist(),
                maxiter=maxiter,ftol=ftol,source_shooting_sha256=SOURCE_SHA256)
    if log_dir is not None:
        path=Path(log_dir); path.mkdir(parents=True,exist_ok=True)
        tag=f"{case}_{objective}_n{n_segments}_{seed_label}_{time.time_ns()}"
        (path/f"{tag}.json").write_text(json.dumps(output,indent=2,ensure_ascii=False),encoding="utf-8")
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case",choices=["base","xian"])
    parser.add_argument("--objective",choices=["time","infections","cost"])
    parser.add_argument("--initial",type=Path)
    parser.add_argument("--segments",type=int,default=40)
    parser.add_argument("--maxiter",type=int,default=400)
    parser.add_argument("--run",action="store_true")
    args=parser.parse_args()
    if not args.run:
        print("未指定--run，不启动优化。")
        return
    if not args.case or not args.objective or not args.initial:
        parser.error("--run需要--case、--objective和--initial")
    initial=json.loads(args.initial.read_text(encoding="utf-8"))
    output=solve(args.case,args.objective,initial["duration"],initial["lambda_values"],
                 n_segments=args.segments,maxiter=args.maxiter,
                 log_dir=HERE/"results"/"shooting_attempts")
    print(json.dumps({k:v for k,v in output.items() if k not in ("lambda_values","initial_lambdas")},
                     indent=2,ensure_ascii=False))


if __name__ == "__main__":
    main()
