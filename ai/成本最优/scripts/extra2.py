import json, numpy as np, sympy as sp
from core import *
from analysis import setup, CASES
_u,_U,_b,_r,_k=sp.symbols('u U b r k')
poly=sp.Poly(sp.expand((-2*(_U-_u)*_u**3+2*_r*_U**2*(_u-1))*(_u-_b)-(_U-_u)**2*_u**3-_r*_U**2*_u*(_u-1)**2-_k*_U**2*_u**3),_u)
cf=[sp.lambdify((_U,_b,_r,_k),c,'numpy') for c in poly.all_coeffs()]
def amin_k(U,b,r,kk):
    rt=np.roots([float(f(U,b,r,kk)) for f in cf]); rt=rt[np.abs(rt.imag)<1e-9].real; rt=rt[(rt>1)&(rt<U)]
    cand=np.concatenate([[1.0,U],rt]); val=G(cand,U,b,r)+kk/(cand-b); return cand[np.argmin(val)]
ext=json.load(open("extra.json"))
for k,p in CASES.items():
    d=setup(p); b,Us=d["b"],d["Ustar"]; sc=1/(d["c0"]*d["th"]); Ug=np.linspace(1,Us,3001)
    pts=[]
    for kk in np.concatenate([-np.geomspace(3e2,1e-4,160),[0.0],np.geomspace(1e-4,3e2,60)]):
        us=np.array([1.0]+[amin_k(U,b,2.0,kk) for U in Ug[1:]])
        pts.append((float(kk),float(sc*np.trapezoid(1/(us-b),Ug)),float(sc*np.trapezoid(G(us,Ug,b,2.0),Ug))))
    ext["front"][k]=pts; a=np.array(pts); print(k,"T range",a[:,1].min(),a[:,1].max())
json.dump(ext,open("extra.json","w"),indent=1)
