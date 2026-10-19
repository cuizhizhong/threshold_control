import sympy as sp, numpy as np
from scipy.optimize import minimize_scalar, brentq
u,v,b,r=sp.symbols('u v b r',real=True)
F=sp.expand(u**2*(u-2*b)*v**2-2*u**2*(u-b)*v+r*(u-1)*(3*u-u**2-2*b))
H=sp.expand((1-v)*sp.diff(F,v)-u*sp.diff(F,u))
Res=sp.factor(sp.resultant(F,H,v))
X=u**3-6*u**2+6*u+2*b*(3*u-4)
P=(r*X+u**3)**2-4*r*b**2*u**2*(2*u-3)
print("1) Res == 4u^4(u-b)^2 * P :", sp.expand(Res-4*u**4*(u-b)**2*P)==0)
print("   P at b=0 :", sp.factor(P.subs(b,0)))
# 2) 手工证明中的几个不等式
psi=-2*u**3+21*u**2-48*u+32
print("2) psi min on [1.5,3]:", min(float(psi.subs(u,x)) for x in np.linspace(1.5,3,30001)))
print("   identity W(r=2) =", sp.factor(sp.expand((r*X+u**3).subs(r,2)-4*b*(3*u-4))), "+ 4b(3u-4)")
print("   X+u^3/2 =", sp.factor(sp.expand(X+u**3/2-2*b*(3*u-4))), "+ 2b(3u-4)")
gap=sp.expand(u**2*(u-b)-2*(u-1)*(3*u-u**2-2*b))  # C(r=2)<u-b 的分子
print("   u^2(u-b)-2(u-1)(3u-u^2-2b) =", sp.collect(gap,b))
# 3) 随机抽样：P>0 于区域 1<u<U_sw(b), 0<b<1, 0<r<=2
rng=np.random.default_rng(0); Pf=sp.lambdify((u,b,r),P,'numpy')
bb=rng.uniform(1e-6,1-1e-6,2_000_000); Usw=(3+np.sqrt(9-8*bb))/2
uu=1+(Usw-1)*rng.uniform(0,1,bb.size); rr=rng.uniform(1e-6,2,bb.size)
vals=Pf(uu,bb,rr)/uu**6
print("3) min P/u^6 over 2e6 samples:", vals.min())
# 4) 尖点 r_A'(b) = 折叠曲线在 (1,U_sw) 上的最小 r；与上一会话 3.13582 / 2.54770 比较
def rfold_min(bv):
    Us=(3+np.sqrt(9-8*bv))/2; best=np.inf
    for uv in np.linspace(1+1e-6,Us-1e-6,4001):
        Xv=uv**3-6*uv**2+6*uv+2*bv*(3*uv-4)
        # P 关于 r 的二次方程 r^2 X^2 + r(2Xu^3-4b^2u^2(2u-3)) + u^6 = 0
        A=Xv**2; B=2*Xv*uv**3-4*bv**2*uv**2*(2*uv-3); C=uv**6
        disc=B*B-4*A*C
        if A>0 and disc>=0:
            rts=[(-B-np.sqrt(disc))/(2*A),(-B+np.sqrt(disc))/(2*A)]
            rts=[x for x in rts if x>0]
            if rts: best=min(best,min(rts))
    return best
for name,bv in [("base",0.8321053),("xian",0.5755854),("b=0.001",0.001),("b=0.5",0.5),("b=0.999",0.999)]:
    print(f"4) r_A'({name}) from P:", rfold_min(bv))
