import sympy as sp
from sympy.polys.numberfields.galoisgroups import galois_group
u=sp.symbols('u')
def quintic(b,r,U):
    return sp.Poly(sp.expand((-2*(U-u)*u**3 + 2*r*U**2*(u-1))*(u-b) - (U-u)**2*u**3 - r*U**2*u*(u-1)**2),u)
R=sp.Rational
for (b,r,U) in [(R(1,2),2,2),(R(4,5),2,R(9,5)),(R(3,5),2,R(11,5)),(R(4,5),R(16,5),R(9,4)),(R(1,2),5,3)]:
    p=quintic(b,r,U)
    fl=sp.factor_list(p.as_expr())
    degs=[sp.Poly(f,u).degree() for f,_ in fl[1]]
    out=f"(b,r,U)=({b},{r},{U}) factor degrees={degs}"
    for f,_ in fl[1]:
        if sp.Poly(f,u).degree()==5:
            G,alt=galois_group(sp.Poly(f,u),by_name=True)
            out+=f"  Galois group: {G}"
    print(out)
