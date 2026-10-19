import numpy as np, sympy as sp
from core import *
bb=np.linspace(1e-6,1-1e-6,200001)
rA=16/(bb+np.sqrt(bb**2-8*bb+8))**2; Uc=bb+np.sqrt(bb**2-8*bb+8)
print("min(rhat-rA') =",(rhat(bb)-rA).min()," min(Usw-Uc) =",(Usw(bb)-Uc).min(),
      " min(rloc-rhat) =",(rloc(bb)-rhat(bb)).min(), " min(rinf-rloc)=",(rinf(bb)-rloc(bb)).min())
print("rA' increasing:",np.all(np.diff(rA)>0)," rhat increasing:",np.all(np.diff(rhat(bb))>0))
# 尝试证明 U_c<U_sw：两边都是 b 的显式函数
b=sp.symbols('b',positive=True)
Ucs=b+sp.sqrt(b**2-8*b+8); Usws=(3+sp.sqrt(9-8*b))/2
print("U_c at b->0,1:",sp.limit(Ucs,b,0),sp.limit(Ucs,b,1),"; U_sw:",sp.limit(Usws,b,0),sp.limit(Usws,b,1))
