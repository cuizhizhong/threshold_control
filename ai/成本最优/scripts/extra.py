import json, numpy as np
from core import *
from analysis import setup, CASES, rAc, Ucc
res=json.load(open("results.json"))
for k in res:
    M=res[k]["metrics"]; r=np.array([m["r"] for m in M])
    for key in ["dt","J","Jq","Jc","dI","Sq"]:
        a=np.array([m[key] for m in M]); d=np.diff(a)
        print(k,key,"nondecr" if np.all(d>=-1e-9*np.abs(a[1:]).max()) else ("nonincr" if np.all(d<=1e-9*np.abs(a[1:]).max()) else "NOT monotone"))
    g=res[k]["gamma"]; U=np.array([x["U"] for x in g]); print(k,"Gamma U increasing:",np.all(np.diff(U)>0), " U range",U.min(),U.max())
    # 凹性：J_min(r)
    J=np.array([m["J"] for m in M]); 
    s=np.diff(J)/np.diff(r); print(k,"J slopes nonincreasing (concave):",np.all(np.diff(s)<=1e-7))

# ---------- 能力约束：截断规则 vs 精确有限比较 ----------
caps={"base":(0.5,0.6),"xian":(0.5,0.75)}
def exact_con(U,b,r,lo,hi):
    rts=stationary_roots(U,b,r); cand=np.concatenate([[lo,hi],rts[(rts>lo)&(rts<hi)]])
    v=G(cand,U,b,r); return cand[np.argmin(v)]
from scipy.integrate import quad
capout={}
for k,p in CASES.items():
    d=setup(p); b,Us=d["b"],d["Ustar"]; cm,qc=caps[k]; q0=p["q0"]; sc=1/(d["c0"]*d["th"])
    lo=lambda U:max(1.0,cm*U); hi=lambda U:min(U,(1-q0)/(1-qc))
    rows=[]
    for r in [0.5,1,2,rAc(b),3.0,rhat(b),5,10,20,50]:
        clip=lambda U:min(max(argmin_exact(U,b,r)[0],lo(U)),hi(U))
        ex=lambda U:exact_con(U,b,r,lo(U),hi(U))
        Ug=np.linspace(1.0001,Us,3000)
        diff=max(abs(clip(U)-ex(U)) for U in Ug)
        Jc=sc*quad(lambda U:G(clip(U),U,b,r),1,Us,limit=400)[0]; Je=sc*quad(lambda U:G(ex(U),U,b,r),1,Us,limit=400)[0]
        Te=sc*quad(lambda U:1/(ex(U)-b),1,Us,limit=400)[0]
        rows.append(dict(r=float(r),maxdiff=float(diff),J_clip=Jc,J_exact=Je,dt_exact=Te))
        print(k,f"r={r:.4f} max|clip-exact|={diff:.2e}  J_clip={Jc:.5f} J_exact={Je:.5f} dt={Te:.4f}")
    capout[k]=rows

# ---------- 时长约束：J+kappa*dt 的逐状态最小化，检验 V(T) 凸 ----------
import sympy as sp
_u,_U,_b,_r,_k=sp.symbols('u U b r k')
poly=sp.Poly(sp.expand((-2*(_U-_u)*_u**3+2*_r*_U**2*(_u-1))*(_u-_b)-(_U-_u)**2*_u**3-_r*_U**2*_u*(_u-1)**2-_k*_U**2*_u**3),_u)
cf=[sp.lambdify((_U,_b,_r,_k),c,'numpy') for c in poly.all_coeffs()]
def amin_k(U,b,r,kk):
    rt=np.roots([float(f(U,b,r,kk)) for f in cf]); rt=rt[np.abs(rt.imag)<1e-9].real; rt=rt[(rt>1)&(rt<U)]
    cand=np.concatenate([[1.0,U],rt]); val=G(cand,U,b,r)+kk/(cand-b); return cand[np.argmin(val)]
front={}
for k,p in CASES.items():
    d=setup(p); b,Us=d["b"],d["Ustar"]; sc=1/(d["c0"]*d["th"])
    pts=[]
    for kk in np.concatenate([-np.geomspace(1e3,1e-4,70),[0.0],np.geomspace(1e-4,1e3,70)]):
        Ug=np.linspace(1,Us,6001)[1:]; us=np.array([amin_k(U,b,2.0,kk) for U in Ug])
        T=sc*np.trapezoid(1/(us-b),Ug); J=sc*np.trapezoid(G(us,Ug,b,2.0),Ug)
        pts.append((float(kk),float(T),float(J)))
    a=np.array(pts); a=a[np.argsort(a[:,1])]
    sl=np.diff(a[:,2])/np.diff(a[:,1]); conv=np.all(np.diff(sl)>=-1e-6*np.abs(sl).max())
    print(k,"frontier points",len(a)," T range",a[:,1].min(),a[:,1].max()," convex:",conv)
    front[k]=pts
json.dump(dict(cap=capout,front=front),open("extra.json","w"),indent=1)
