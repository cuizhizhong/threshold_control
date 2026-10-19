import sympy as sp
u,v,b,r=sp.symbols('u v b r',real=True)
# 驻点方程乘 u^2 后的多项式形式
F=sp.expand(u**2*(u-2*b)*v**2-2*u**2*(u-b)*v+r*(u-1)*(3*u-u**2-2*b))
# 核对：F/u^2 等于 G_u 的分子（v=1-u/U）
U=sp.symbols('U',positive=True)
Gf=((1-u/U)**2+r*(1-1/u)**2)/(u-b)
num=sp.together(sp.diff(Gf,u)*(u-b)**2)
chk=sp.simplify(num*u - (F/u**2).subs(v,1-u/U)*1)  # 比例核对
print("check proportional:", sp.simplify(sp.factor(num)/sp.factor((F/u**2).subs(v,1-u/U))))
H=sp.expand((1-v)*sp.diff(F,v)-u*sp.diff(F,u))
P=sp.factor(sp.resultant(F,H,v))
print("resultant factored:")
print(P)
