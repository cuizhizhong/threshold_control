#!/usr/bin/env python3
"""Reproduce the new same-initial-state joint-control table.

Uses the paper's SIQR equations; no re-fitting or replacement of the Xi'an data.
At each state all real stationary roots and both admissible endpoints are compared.
The calculations in x=c/c0 are algebraically equivalent to the paper's c variable.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import csv, json, platform
import numpy as np
import scipy
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq
from numpy.polynomial import Polynomial

@dataclass(frozen=True)
class Parameters:
    N: float = 763.0
    S0: float = 762.0
    I0: float = 1.0
    beta: float = 0.155
    gamma: float = 0.3504
    delta_q: float = 0.3504
    c0: float = 10.0
    q0: float = 0.01526
    eta: float = 38.15
    wc: float = 1.0
    wq: float = 2.0
    @property
    def Sc(self) -> float:
        return self.gamma*self.N/(self.beta*self.c0*(1-self.q0))
    @property
    def barS(self) -> float:
        return (1-self.beta)*self.gamma*self.N/(self.beta*self.c0)
    @property
    def beta1(self) -> float:
        return self.c0*(self.beta+self.q0*(1-self.beta))/self.N
    @property
    def ratio(self) -> float:
        return self.beta*(1-self.q0)/(self.beta+self.q0*(1-self.beta))
    @property
    def rho1(self) -> float:
        return self.gamma/self.beta1
    def routine_I(self,S:float) -> float:
        return self.I0+self.ratio*(self.S0-S)+self.rho1*np.log(S/self.S0)

X=Polynomial([0.,1.])
def stationary_candidates(r:float,b:float,wc:float=1.,wq:float=2.,
                          lower:float|None=None,upper:float=1.) -> list[float]:
    """Finite candidates on x=c/c0; r=Sc/S, b=barS/S."""
    lo=r if lower is None else max(r,lower)
    hi=upper
    if lo>hi+1e-11 or lo<=0 or hi>1+1e-11 or b>=lo:
        raise ValueError(f'Invalid admissible interval: {lo}, {hi}, b={b}')
    if hi-lo<1e-12:
        return [(lo+hi)/2]
    poly=wc*X**3*(X-1)*(X+1-2*b)+wq*(X-r)*(-X*X+3*r*X-2*b*r)
    candidates=[lo,hi]
    for root in poly.roots():
        if abs(root.imag)<=1e-8*(1+abs(root.real)) and lo-1e-10<=root.real<=hi+1e-10:
            candidates.append(float(np.clip(root.real,lo,hi)))
    return sorted(set(candidates))

def dimensionless_cost(x:float|np.ndarray,r:float,b:float,wc:float=1.,wq:float=2.):
    return (wc*(1-x)**2+wq*(1-r/x)**2)/(x-b)

def optimal_x(S:float,p:Parameters, cmin:float=0.,qcap:float=1.) -> float:
    # Endpoint extension is used only by event root-finding outside the interval.
    if S<=p.Sc:
        return 1.
    r=p.Sc/S; b=p.barS/S
    upper=min(1.,(1-p.q0)*r/(1-qcap)) if qcap<1. else 1.
    candidates=stationary_candidates(r,b,p.wc,p.wq,cmin/p.c0,upper)
    return min(candidates,key=lambda x:dimensionless_cost(x,r,b,p.wc,p.wq))

def compute(p:Parameters,eps:float=1e-9,ode_check:bool=False) -> dict:
    if not (p.I0<p.eta<p.routine_I(p.Sc) and p.eta>1):
        raise ValueError('This table requires an interior trigger and eta>1.')
    Sstar=brentq(lambda S:p.routine_I(S)-p.eta,p.Sc,p.S0,xtol=1e-11)
    t1=quad(lambda S:1/(p.beta1*S*p.routine_I(S)),Sstar,p.S0,
            epsabs=eps*.1,epsrel=eps*.1,limit=500)[0]
    def after_I(S):
        return p.eta+p.ratio*(p.Sc-S)+p.rho1*np.log(S/p.Sc)
    Send=brentq(lambda S:after_I(S)-1,p.Sc*1e-10,p.Sc,xtol=1e-11)
    tail=quad(lambda S:1/(p.beta1*S*after_I(S)),Send,p.Sc,
              epsabs=eps*.1,epsrel=eps*.1,limit=500)[0]
    peak_time=quad(lambda S:1/(p.beta1*S*p.routine_I(S)),p.Sc,p.S0,
                   epsabs=eps*.1,epsrel=eps*.1,limit=500)[0]
    profiles={
      'contact_only':lambda S:p.Sc/S,
      'alpha_0.5':lambda S:.5+.5*p.Sc/S,
      'quarantine_only':lambda S:1.,
      'minimum_cost':lambda S:optimal_x(S,p),
    }
    rows=[]
    for name,profile in profiles.items():
        def denom(S):return p.c0*(profile(S)*S-p.barS)
        duration=quad(lambda S:p.N/(p.eta*denom(S)),p.Sc,Sstar,
                      epsabs=eps,epsrel=eps*.1,limit=500)[0]
        def integrand(S):
            x=profile(S)
            return p.N/(p.eta*denom(S))*(p.wc*(1-x)**2+p.wq*(1-p.Sc/(x*S))**2)
        cost=quad(integrand,p.Sc,Sstar,epsabs=eps,epsrel=eps*.1,limit=500)[0]
        inc=p.beta*(Sstar-p.Sc)+p.gamma*p.eta*(1-p.beta)*duration
        sq=(1-p.beta)*(Sstar-p.Sc-p.gamma*p.eta*duration)
        total=p.beta/(p.beta+p.q0*(1-p.beta))*(p.S0-Sstar+p.Sc-Send)+inc
        row={'strategy':name,'duration':duration,'cost':cost,'t_end':t1+duration+tail,
             'new_infections_control':inc,'new_Sq_control':sq,'total_infections':total,
             'initial_c':p.c0*profile(Sstar),
             'initial_q':1-(1-p.q0)*p.Sc/(profile(Sstar)*Sstar)}
        if ode_check:
            # S,I,Sq,Iq,R,cumulative-new-infections,cost.
            # The arbitrary *control-period* initial Sq/Iq/R is common for this
            # independent test, and does not alter the closed S,I dynamics.
            def rhs(t,y):
                S,I,Sq,Iq,R,C,J=y
                c=p.c0*profile(max(S,p.Sc))
                q=1-p.gamma*p.N/(p.beta*c*S)
                inf=p.beta*c*S*I/p.N
                qi=(1-p.beta)*c*q*S*I/p.N
                return [-inf-qi,inf*(1-q)-p.gamma*I,qi,
                        inf*q-p.delta_q*Iq,p.gamma*I+p.delta_q*Iq,
                        inf,p.wc*(1-c/p.c0)**2+p.wq*((q-p.q0)/(1-p.q0))**2]
            def exit_event(t,y):return y[0]-p.Sc
            exit_event.terminal=True;exit_event.direction=-1
            y0=[Sstar,p.eta,0,0,p.N-Sstar-p.eta,0,0]
            sol=solve_ivp(rhs,[0,1.3*duration],y0,method='DOP853',rtol=2e-11,
                          atol=2e-12,events=exit_event,max_step=duration/100)
            if not sol.success or len(sol.t_events[0])!=1:
                raise RuntimeError('ODE verification failed to reach exit.')
            yy=sol.y_events[0][0]; te=sol.t_events[0][0]
            row['ode_errors']={'duration':float(abs(te-duration)),
               'new_infections_control':float(abs(yy[5]-inc)),
               'new_Sq_control':float(abs(yy[2]-sq)),
               'cost':float(abs(yy[6]-cost)),
               'constant_I':float(np.max(np.abs(sol.y[1]-p.eta))),
               'population':float(np.max(np.abs(np.sum(sol.y[:5],axis=0)-p.N)))}
        rows.append(row)
    return {'parameters':asdict(p),'Sstar':Sstar,'Sc':p.Sc,'barS':p.barS,
            't1':t1,'Send':Send,'post_control_duration':tail,
            'routine_peak_exact':p.routine_I(p.Sc),'routine_peak_time':peak_time,
            'quadrature_tolerance':eps,'rows':rows}

if __name__=='__main__':
    out=Path(__file__).resolve().parent
    fine=compute(Parameters(),eps=1e-9,ode_check=True)
    coarse=compute(Parameters(),eps=1e-7)
    convergence={r['strategy']:{k:abs(r[k]-s[k]) for k in
        ['duration','cost','total_infections','new_Sq_control','t_end']}
        for r,s in zip(fine['rows'],coarse['rows'])}
    fine['convergence']=convergence
    fine['software']={'python':platform.python_version(),'numpy':np.__version__,
                      'scipy':scipy.__version__}
    (out/'joint_comparison_results.json').write_text(json.dumps(fine,ensure_ascii=False,indent=2),encoding='utf-8')
    fields=[k for k in fine['rows'][0] if k!='ode_errors']
    with (out/'joint_comparison_results.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        w.writerows({k:r[k] for k in fields} for r in fine['rows'])
    print(json.dumps(fine,ensure_ascii=False,indent=2))
