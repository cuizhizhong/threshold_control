import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
def setup(N,S0,I0,beta,gam,c0,q0,eta):
    Sc=gam*N/(beta*c0*(1-q0)); Sbar=gam*N*(1-beta)/(beta*c0)
    # S* from first integral of baseline: I + (b2/b1)S - rho ln S = const
    b1=c0*(beta+q0*(1-beta))/N; b2=beta*c0*(1-q0)/N; rho=gam/b1
    C0=I0+b2/b1*S0-rho*np.log(S0)
    g=lambda S: eta+b2/b1*S-rho*np.log(S)-C0
    Sstar=brentq(g,Sc,S0)
    return Sc,Sbar,Sstar
def analyze(name,N,S0,I0,beta,gam,c0,q0,eta,wc=1,wq=2):
    Sc,Sbar,Sstar=setup(N,S0,I0,beta,gam,c0,q0,eta)
    f=lambda S,c: (wc*(1-c/c0)**2+wq*(1-c0*Sc/(c*S))**2)/(c*S-c0*Sbar)
    phi=lambda S,c: 1/(c*S-c0*Sbar)
    Ss=np.linspace(Sc*(1+1e-6),Sstar,400)
    cstar=[];nloc=[];xs=[]
    for S in Ss:
        lo=c0*Sc/S; cs=np.linspace(lo,c0,4001); v=f(S,cs)
        k=np.argmin(v); cstar.append(cs[k]); xs.append((cs[k]-lo)/(c0-lo))
        # count local minima
        d=np.diff(v); nloc.append(int(np.sum((d[:-1]<0)&(d[1:]>0)))+int(d[0]>0)+int(d[-1]<0))
    cstar=np.array(cstar); xs=np.array(xs)
    qstar=1-c0*(1-q0)*Sc/(cstar*Ss)
    print(f'== {name}: Sc={Sc:.4g}, Sstar={Sstar:.4g}, Sbar={Sbar:.4g}')
    print('  x=(c-lo)/(c0-lo) range:',xs.min().round(4),xs.max().round(4),' interior everywhere:',(xs>1e-3).all() and (xs<1-1e-3).all())
    print('  max #local minima in c:',max(nloc))
    print('  c* monotone decreasing in S:',np.all(np.diff(cstar)<=1e-9), ' q* increasing in S:', np.all(np.diff(qstar)>=-1e-9))
    print('  at S*: c*/c0=%.4f q*=%.4f  (q-only q=%.4f)'%(cstar[-1]/c0,qstar[-1],1-Sc*(1-q0)/Sstar))
    # normalized intensity ratio at S*
    rc=1-cstar[-1]/c0; rq=(qstar[-1]-q0)/(1-q0)
    print('  normalized intensities at S*: contact %.4f, quarantine %.4f, ratio %.3f'%(rc,rq,rc/rq))
    # frontier via scalarization
    out=[]
    for mu in np.concatenate([-np.logspace(1,-3,9),[0],np.logspace(-3,1,9)])*1.0:
        J=0;T=0
        Sg=np.linspace(Sc,Sstar,1201); 
        vals=[];tv=[]
        for S in Sg:
            lo=c0*Sc/S; cs=np.linspace(lo,c0,1501)
            v=f(S,cs)+mu*phi(S,cs); k=np.argmin(v)
            vals.append(f(S,cs[k])); tv.append(phi(S,cs[k]))
        J=N/eta*np.trapezoid(vals,Sg); T=N/eta*np.trapezoid(tv,Sg)
        out.append((mu,T,J))
    out=sorted(out,key=lambda r:r[1])
    print('  frontier (mu, duration, J):')
    for r in out: print('   %9.4g  %9.4f  %9.4f'%r)
analyze('baseline',763,762,1,0.155,0.3504,10,0.01526,0.05*763)
analyze('xian',13163000,13163000-1.00663e-3,1.00663e-3,0.1498,0.2953,12.8872,0.3230,0.002*13163000)
