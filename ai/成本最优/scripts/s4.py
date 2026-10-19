import numpy as np
from core import *
rng=np.random.default_rng(1)
N=400000
b=rng.uniform(0.01,0.99,N); Us=Usw(b)
u=1.5+(Us-1.5)*rng.uniform(0.001,0.999,N)
r=np.exp(rng.uniform(np.log(0.05),np.log(rinf(b)*0.999),N))
C=C_of(u,b,r); ok=C<u
b,u,r,C=b[ok],u[ok],r[ok],C[ok]
v=vs_of(u,b,r)
# Htilde=(1-v)F~_v - u F~_u, F~=u^2(u-2b)v^2-2u^2(u-b)v+r(u-1)(3u-u^2-2b)
Fv=2*u**2*(u-2*b)*v-2*u**2*(u-b)
Fu=(3*u**2-4*b*u)*v**2-2*(3*u**2-2*b*u)*v+r*((3*u-u**2-2*b)+(u-1)*(3-2*u))
H=(1-v)*Fv-u*Fu
s=np.sqrt(r); w=np.sqrt(2*u-3); X=u**3-6*u**2+6*u+2*b*(3*u-4)
F1=s*s*X+u**3-2*s*b*u*w
# 用有限差分直接核对 U_s 的单调方向
du=1e-7
dU=(Us_branch(u+du,b,r)-Us_branch(u-du,b,r))/(2*du)
m=np.isfinite(dU)&(np.abs(F1)>1e-6)&(np.abs(dU)>1e-6)
print("samples:",m.sum())
print("sign(H)==-sign(F1):",np.mean(np.sign(H[m])==-np.sign(F1[m])))
print("sign(dU_s/du)==sign(F1):",np.mean(np.sign(dU[m])==np.sign(F1[m])))
