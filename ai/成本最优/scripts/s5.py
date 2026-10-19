import sympy as sp
u,v,b,r=sp.symbols('u v b r',positive=True)
F=u**2*(u-2*b)*v**2-2*u**2*(u-b)*v+r*(u-1)*(3*u-u**2-2*b)
H=(1-v)*sp.diff(F,v)-u*sp.diff(F,u)
F2,H2=sp.expand(F.subs(u,2)),sp.expand(H.subs(u,2))
# H 对 F 取余，化为 v 的一次式
rem=sp.rem(sp.Poly(H2,v),sp.Poly(F2,v))
print("H mod F at u=2:",sp.factor(rem.as_expr()))
D=sp.expand((2-b)**2-r*(1-b)**2)
vs=((2-b)-sp.sqrt(D))/(2*(1-b))
val=sp.simplify(rem.as_expr().subs(v,vs))
print("H(2,v_s) =",sp.factor(val))
# 数值核对符号：H(2,v_s)>0 当且仅当 (1-b)r+b*sqrt(r)-2>0
import numpy as np
f=sp.lambdify((b,r),val,'numpy')
for bv in [0.1,0.5,0.8321053,0.95]:
    rA=16/(bv+np.sqrt(bv*bv-8*bv+8))**2
    for rv in [rA*0.9,rA*0.999,rA*1.001,rA*1.5, min(3.9/(1-bv),(2-bv)**2/(1-bv)**2)*0.99]:
        print(f"  b={bv} r={rv:.4f} H(2,v_s)={f(bv,rv):+.4e}  (1-b)r+b√r-2={(1-bv)*rv+bv*np.sqrt(rv)-2:+.4e}")
