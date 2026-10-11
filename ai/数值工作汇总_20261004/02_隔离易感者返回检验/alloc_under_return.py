"""返回模型（lambda=1/14）下，用不同权重比推出的无回流最优分配作为反馈分配规则，按权重 1:2 计成本，
检验"存在比仅隔离更便宜的混合分配"是否仍成立（这些分配不是返回模型下的最优分配）。"""
import json
from sq_return import simulate, XIAN, BASE, make_alloc
out = {}
for name, p, T in (("baseline", BASE, 3000.0), ("xian", XIAN, 4000.0)):
    r = simulate(p, "q_only", lam=1 / 14, T=T)
    out[f"{name}|q_only"] = dict(J=r["J"], duration=r["tctrl"])
    for wq in (0.25, 0.5, 1.0, 2.0, 4.0):
        r = simulate(p, "optimal", lam=1 / 14, T=T, alloc=make_alloc(p, "optimal", wc=1.0, wq=wq))
        out[f"{name}|alloc_from_r={wq}"] = dict(J=r["J"], duration=r["tctrl"])
json.dump(out, open("results/alloc_under_return.json", "w"), indent=1)
for k, v in out.items():
    print(f"{k:28s} J(1:2)={v['J']:.3f}  duration={v['duration']:.1f}")
