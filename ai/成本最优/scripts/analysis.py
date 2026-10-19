"""生成 LaTeX 稿的全部数值与图。独立实现：不调用仓库代码。"""
import json, numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad
from core import *

CASES = {
 "base": dict(N=763., I0=1., S0=762., beta=.155, gamma=.3504, c0=10., q0=.01526, th=.05,
              QO_total=285.7, label="Baseline"),
 "xian": dict(N=13163000., I0=1.00659e-3, S0=13163000.-1.00659e-3, beta=.1498, gamma=.2953,
              c0=12.8872, q0=.3230, th=.002, QO_total=2.3779e6, label="Xi'an"),
}
def setup(p):
    N,be,ga,c0,q0=p["N"],p["beta"],p["gamma"],p["c0"],p["q0"]
    eta=p["th"]*N; Sc=ga*N/(be*c0*(1-q0)); Sbar=(1-be)*ga*N/(be*c0)
    b1=c0*(be+q0*(1-be))/N; b2=be*c0*(1-q0)/N; rho=ga/b1
    Hf=lambda I,S: I+b2/b1*S-rho*np.log(S)
    Sstar=brentq(lambda S: Hf(eta,S)-Hf(p["I0"],p["S0"]), Sc*(1+1e-9), p["S0"])
    return dict(eta=eta,Sc=Sc,Sbar=Sbar,b=Sbar/Sc,Ustar=Sstar/Sc,th=p["th"],c0=c0,beta=be,gamma=ga,q0=q0,N=N)

rAc  = lambda b: 16/(b+np.sqrt(b*b-8*b+8))**2
Ucc  = lambda b: b+np.sqrt(b*b-8*b+8)

def locate_in(b, r, lo, hi, n=3000):
    Ug = np.linspace(lo, hi, n); us = np.array([argmin_exact(U,b,r)[0] for U in Ug])
    k = int(np.argmax(np.abs(np.diff(us))))
    UL, UR, uL, uR = Ug[k], Ug[k+1], us[k], us[k+1]
    for _ in range(70):
        Um = 0.5*(UL+UR); um = argmin_exact(Um,b,r)[0]
        if abs(um-uL) < abs(um-uR): UL, uL = Um, um
        else: UR, uR = Um, um
    return 0.5*(UL+UR), uL/UL, uR/UR, abs(uR-uL)

def jumpU(b, r):
    if r <= rAc(b)*(1+1e-9): return dict(U=np.nan, xl=np.nan, xr=np.nan)
    if r >= rhat(b):
        U0, uh = Uglob(r, b); return dict(U=U0, xl=uh/U0, xr=1.0)
    U0, xl, xr, gap = locate_in(b, r, Ucc(b)-0.01, Usw(b)-1e-9)
    return dict(U=U0, xl=xl, xr=xr)

def ustar(U, b, r): return argmin_exact(U, b, r)[0]

def metrics(d, r, wc=1.0):
    b, Us = d["b"], d["Ustar"]; scale = 1/(d["c0"]*d["th"])
    j = jumpU(b, r); pts = [1.0]
    for p_ in [Usw(b), j["U"]]:
        if np.isfinite(p_) and 1 < p_ < Us: pts.append(p_)
    pts = sorted(pts) + [Us]
    fT = lambda U: 1/(ustar(U,b,r)-b)
    fJ = lambda U: G(ustar(U,b,r),U,b,r)
    fJq = lambda U: (1-1/ustar(U,b,r))**2/(ustar(U,b,r)-b)
    T = sum(quad(fT,a,c,limit=200,epsabs=1e-11)[0] for a,c in zip(pts[:-1],pts[1:]))*scale
    J = sum(quad(fJ,a,c,limit=200,epsabs=1e-11)[0] for a,c in zip(pts[:-1],pts[1:]))*scale*wc
    Jq= sum(quad(fJq,a,c,limit=200,epsabs=1e-11)[0] for a,c in zip(pts[:-1],pts[1:]))*scale
    TQO = scale*np.log((Us-b)/(1-b))
    JQO = scale*wc*quad(lambda U: G(U,U,b,r),1,Us,limit=200)[0]
    eta=d["eta"]; be=d["beta"]; ga=d["gamma"]
    dI = (1-be)*ga*eta*(T-TQO)
    Sq = (1-be)*(d["Sc"]*(Us-1)-ga*eta*T)
    # 仅隔离段时长（若存在）
    Usw_ = Usw(b) if r <= rhat(b) else j["U"]
    front = scale*np.log((Us-b)/(Usw_-b)) if Usw_ < Us else 0.0
    x0 = ustar(Us,b,r)/Us
    return dict(r=r, dt=T, J=J, Jq=Jq, Jc=J/wc-r*Jq, dt_QO=TQO, J_QO=JQO, dI=dI, Sq=Sq,
                front=front, x_start=x0, jump=j)

if __name__ == "__main__":
    out = {}
    for k,p in CASES.items():
        d = setup(p); b = d["b"]; o = dict(setup=d)
        o["thr"] = dict(Usw=Usw(b), Uc=Ucc(b), rA=rAc(b), rhat=rhat(b), rloc=rloc(b), rinf=rinf(b),
                        rC=rg(d["Ustar"], b)[0], xhat_at_rhat=1/(Usw(b)-1), cusp_x=2/Ucc(b))
        # 跳跃曲线 Γ
        rs = np.concatenate([np.linspace(rAc(b)*(1+1e-4), rhat(b), 40)[:-1], np.geomspace(rhat(b), 200, 160)])
        o["gamma"] = [dict(r=float(r), **{kk: float(vv) for kk,vv in jumpU(b,r).items()}) for r in rs]
        # 指标随 r
        rs2 = np.unique(np.concatenate([np.geomspace(0.05, 200, 140), [0.5,1,2,rAc(b),rhat(b),5,10,o["thr"]["rC"],50]]))
        o["metrics"] = []
        for r in rs2:
            m = metrics(d, float(r)); m["jump"] = {kk: float(vv) for kk,vv in m["jump"].items()}
            o["metrics"].append({kk:(float(vv) if not isinstance(vv,dict) else vv) for kk,vv in m.items()})
        out[k] = o
        print(k, json.dumps(o["thr"], indent=0))
        for m in o["metrics"]:
            if abs(m["r"]-2) < 1e-12:
                print("  r=2:", {kk: round(m[kk],5) for kk in ["dt","J","J_QO","dt_QO","dI","Sq","front"]})
    json.dump(out, open("results.json","w"), indent=1, default=float)
