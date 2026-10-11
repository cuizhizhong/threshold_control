"""(1) 无回流模型平台期易感者减少的分解：新增感染 vs 进入 S_q 的未感染者；
(2) 快速返回极限 lambda->inf 的解析时长/成本，并与 lambda=1 的模拟对照。"""
import json
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import simpson
import joint_cost_optimal as M
from sq_return import XIAN, BASE, simulate

out = {"decomposition_no_return": {}, "fast_return_limit": {}}
for name, p in (("baseline", BASE), ("xian", XIAN)):
    for pol in ("q_only", "optimal", "c_only"):
        s = M.solve_allocation(p, 1, 2, policy=pol)
        d = s["Sstar"] - s["Sc"]
        out["decomposition_no_return"][f"{name}|{pol}"] = dict(
            plateau_S_drop=d, plateau_S_drop_over_N=d / p["N"], plateau_infections=s["infections"],
            plateau_new_Sq=s["Sq_new"], Sq_share=s["Sq_new"] / d, duration=s["dT"])
    # 快速返回极限：S' = -beta c S I/N，平台期 S' = -(eta/N) beta c S
    N, b, g, c0, q0, eta, S0, I0 = (p[k] for k in ("N", "beta", "gamma", "c0", "q0", "eta", "S0", "I0"))
    Sc = g * N / (b * c0 * (1 - q0))
    Ifun = lambda S: I0 + (1 - q0) * (S0 - S) + g * N / (b * c0) * np.log(S / S0)
    Sstar = brentq(lambda S: Ifun(S) - eta, Sc, S0)
    pref = N / (eta * b * c0)
    sg = np.linspace(1, Sstar / Sc, 20001)
    for pol, x in (("q_only", np.ones_like(sg)), ("c_only", 1 / sg)):
        dT = pref * simpson(1 / (x * sg), x=sg)
        J = pref * simpson(((1 - x) ** 2 + 2 * (1 - 1 / (x * sg)) ** 2) / (x * sg), x=sg)
        r = simulate(p, pol, lam=1.0, T=4000.0, dt=0.005)
        out["fast_return_limit"][f"{name}|{pol}"] = dict(
            Sstar_over_N=Sstar / N, duration_limit=dT, J_limit=J,
            duration_sim_lambda1=r["tctrl"], J_sim_lambda1=r["J"])
json.dump(out, open("results/decomposition_and_limit.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
