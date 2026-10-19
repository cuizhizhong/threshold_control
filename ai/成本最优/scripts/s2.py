import sympy as sp, numpy as np
u,b,r,s,w=sp.symbols('u b r s w',positive=True)
X=u**3-6*u**2+6*u+2*b*(3*u-4)
P=(r*X+u**3)**2-4*r*b**2*u**2*(2*u-3)
rA=16/(b+sp.sqrt(b**2-8*b+8))**2
print("P(2,b,rA) =",sp.simplify(P.subs({u:2,r:rA})))
print("P_u(2,b,rA) =",sp.simplify(sp.diff(P,u).subs({u:2,r:rA})))
# 以 s=sqrt(r_A') 为参数：b=(s^2-2)/(s(s-1))，s in (sqrt2,2)
bs=(s**2-2)/(s*(s-1))
print("check rA(bs)=s^2:",sp.simplify(rA.subs(b,bs)-s**2))
# F1 = s^2 X + u^3 - 2 s b u w，u=(w^2+3)/2
uw=(w**2+3)/2
F1=sp.together((s**2*X+u**3-2*s*b*u*w).subs(u,uw).subs(b,bs))
num=sp.factor(sp.numer(F1)); den=sp.factor(sp.denom(F1))
print("F1 numerator factored:",num)
print("F1 denominator:",den)
