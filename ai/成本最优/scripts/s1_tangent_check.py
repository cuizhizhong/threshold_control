import sympy as sp, numpy as np
u,U,b,r,v=sp.symbols('u U b r v',positive=True)
G=((1-u/U)**2+r*(1-1/u)**2)/(u-b)
GQ=r*(1-1/U)**2/(U-b)
Gu=sp.together(sp.diff(G,u))
rr=u**3/((2*U-1)*u-2*U)
bb=U-(U-1)**2*u**3/(2*((2*U-1)*u**2-U*(U+1)*u+U**2))
e1=sp.simplify(sp.numer(Gu).subs({r:rr,b:bb}))
e2=sp.simplify(sp.numer(sp.together(G-GQ)).subs({r:rr,b:bb}))
print("tangent param: G_u ->",e1,"; G-G_QO ->",e2)
# 在切换点处的 x=u/U 极限 r->rhat: U=U_sw, 接触点 u_hat
Usw=(3+sp.sqrt(9-8*b))/2
# 二阶条件：在相切点 D_uu>=0（核对数值）
# r_inf(b)：C(u)<u 对一切 u in (1,U_sw) 成立的最大 r
for bv in [0.8321053,0.5755854,0.3,0.05,0.95]:
    Us=float(Usw.subs(b,bv)); us=np.linspace(1,Us,200001)[1:-1]
    phi=(us-1)*(3*us-us**2-2*bv)/us**3
    rinf=1/phi.max(); s=np.sqrt(9-8*bv); rhat=((3+s)/(1+s))**2
    print(f"b={bv}: r_inf={rinf:.5f} at u={us[phi.argmax()]:.4f};  rhat={rhat:.5f}")
