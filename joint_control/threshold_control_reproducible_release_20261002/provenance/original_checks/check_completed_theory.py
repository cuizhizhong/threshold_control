#!/usr/bin/env python3
"""Independent reproducible checks of the added theory. No Xi'an re-fitting.
Run from any directory: python validation/check_completed_theory.py
Requires numpy, scipy, sympy. Numerical tests supplement, not replace proofs.
"""
from pathlib import Path
import json, math
import numpy as np
import sympy as sp
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq, minimize_scalar

ROOT=Path(__file__).resolve().parents[1]
report={'scope':'Symbolic identities and independent model checks. Not a rerun of original Xi\'an experiments.','symbolic':{}}
c,c0,S,Sc,b,wc,wq=sp.symbols('c c0 S Sc b wc wq',positive=True)
f=(wc*(1-c/c0)**2+wq*(1-c0*Sc/(c*S))**2)/(c*S-c0*b)
poly=wc*c**3/c0**2*(c-c0)*(c+c0-2*c0*b/S)+wq*(c-c0*Sc/S)*(-c**2+3*c0*Sc*c/S-2*c0**2*b*Sc/S**2)
report['symbolic']['weighted_stationary_polynomial']=sp.cancel(sp.diff(f,c)*c**3*(c*S-c0*b)**2/S-poly)==0
report['symbolic']['quintic_degree']=sp.Poly(poly,c).degree()
quartic=c**4/c0**2-3*c**2+8*c0*Sc*c/S-6*(c0*Sc/S)**2
report['symbolic']['beta_one_quartic']=sp.cancel(poly.subs({b:0,wc:1,wq:2})/c-quartic)==0
z,x=sp.symbols('z x',real=True)
G=(wc*x*x+wq*(1-x)**2/(1-z*x)**2)/(c0*(Sc/(1-z)*(1-z*x)-b))
G0=(wc*x*x+wq*(1-x)**2)/(c0*(Sc-b))
report['symbolic']['terminal_limit']=sp.simplify(sp.limit(G,z,0)-G0)==0
report['symbolic']['terminal_weighted_minimizer']=sp.simplify(sp.diff(G0,x).subs(x,wq/(wc+wq)))==0
report['symbolic']['terminal_strict_convex_limit']=str(sp.simplify(sp.diff(G0,x,2)))

# Original model baseline: retain historical curves; do not silently replace their outputs.
N=763.;s0=762.;i0=1.;be=.155;ga=.3504;cv=10.;q0=.01526;eta=.05*N
B1=cv*(be+q0*(1-be))/N;B2=be*cv*(1-q0)/N
sc=ga/B2;bs=(1-be)*ga*N/(be*cv);rho=ga/B1
orbit=lambda u:i0+B2/B1*(s0-u)+rho*math.log(u/s0)
ss=brentq(lambda u:orbit(u)-eta,sc,s0,xtol=1e-11)
t1=quad(lambda u:1/(B1*u*orbit(u)),ss,s0,epsabs=1e-10,epsrel=1e-11)[0]
T=N/(cv*eta)*math.log((ss-bs)/(sc-bs))
peak=orbit(sc);tpeak=quad(lambda u:1/(B1*u*orbit(u)),sc,s0,epsabs=1e-10,epsrel=1e-11)[0]
report['baseline']={'S_c':sc,'S_bar':bs,'S_star':ss,'t1':t1,'duration':T,'t2':t1+T,'q_max':1-ga*N/(be*cv*ss),'continuous_routine_peak':peak,'continuous_routine_peak_time':tpeak,'legacy_reported_peak':300.3726,'legacy_reported_time':6.7065,'paper_action':'Historical trajectory retained; text reports routine peak approximately 300.4 at about 6.7 d; exact discrepancy disclosed in review.'}

# Finite candidates are complete analytically. Numerically cross-check against a dense grid.
rng=np.random.default_rng(20261002)
def dim_fun(xx,r,bb,w1=1.,w2=2.):
 return (w1*(1-xx)**2+w2*(1-r/xx)**2)/(xx-bb)
def candidates(r,bb,lo=None,hi=1.,w1=1.,w2=2.):
 lo=r if lo is None else lo
 X=np.polynomial.Polynomial([0.,1.])
 P=w1*X**3*(X-1)*(X+1-2*bb)+w2*(X-r)*(-X**2+3*r*X-2*bb*r)
 rr=P.roots();pts=[lo,hi]
 for y in rr:
  if abs(y.imag)<2e-7 and lo-2e-9<=y.real<=hi+2e-9:pts.append(float(np.clip(y.real,lo,hi)))
 vals=[float(dim_fun(y,r,bb,w1,w2)) for y in pts]
 k=int(np.argmin(vals));return pts[k],vals[k]
max_excess=0.;strict_gaps=[];feas_tests=0;root_checks=0
for _ in range(320):
 r=float(rng.uniform(.04,.999));d=float(rng.uniform(.005,.99));bb=d*r
 q0v=float(rng.uniform(0,.65));cap=q0v+float(rng.uniform(0,.999))*(1-q0v);m=float(rng.uniform(0,1))
 lo=max(r,m);hi=min(1,(1-q0v)*r/(1-cap))
 condition=m<=((1-q0v)*r/(1-cap))
 alow=max(0,(m-r)/(1-r));ahigh=min(1,r*(cap-q0v)/((1-cap)*(1-r)))
 assert condition==(alow<=ahigh+1e-13);feas_tests+=1
 if lo<=hi:
  root_checks+=1
  a,best=candidates(r,bb,lo,hi)
  grid=float(np.min(dim_fun(np.linspace(lo,hi,10001),r,bb)))
  max_excess=max(max_excess,best-grid)
  assert best<=grid+2e-7*max(1,abs(grid))
report['candidate_tests']={'drawn_cases':320,'finite_candidate_checks_on_feasible_intervals':root_checks,'capability_vs_alpha_interval_tests':feas_tests,'largest_candidate_cost_above_grid':max_excess}

# Terminal allocation: exhaustive grid identifies all local minima, each locally refined.
terminal=[]
for z0 in [1e-1,1e-2,1e-3,1e-4,1e-5]:
 for d in [.0,.2,.7,.95]:
  def h(xx):return (xx*xx+2*(1-xx)**2/(1-z0*xx)**2)/((1-z0*xx)/(1-z0)-d)
  grid=np.linspace(0,1,2001);vv=h(grid)
  local=np.where((vv[1:-1]<=vv[:-2])&(vv[1:-1]<=vv[2:]))[0]+1
  pts=[(0.,float(vv[0])),(1.,float(vv[-1]))]
  for j in local:
   res=minimize_scalar(h,bounds=(grid[j-1],grid[j+1]),method='bounded',options={'xatol':1e-13})
   pts.append((float(res.x),float(res.fun)))
  xm,vm=min(pts,key=lambda t:t[1]);qratio=(1-xm)/(1-z0*xm)
  assert 0<xm<1 and vm<min(h(0),h(1))
  terminal.append({'z':z0,'bar_over_Sc':d,'contact_fraction':xm,'quarantine_fraction':qratio,'contact_limit_error':abs(xm-2/3)})
assert max(t['contact_limit_error'] for t in terminal if t['z']==1e-5)<2e-5
report['terminal_allocation']=terminal

# Integrating statewise minima at varying thresholds, with the same model and control capacities.
def state_min(Sv):
 rv=sc/Sv;bb=bs/Sv
 if 1-rv<1e-5:
  zv=1-rv
  def h(xx):return (xx*xx+2*(1-xx)**2/(1-zv*xx)**2)/(cv*(Sv*(1-zv*xx)-bs))
  res=minimize_scalar(h,bounds=(0,1),method='bounded',options={'xatol':1e-12})
  return zv*zv*res.fun
 return candidates(rv,bb)[1]/(cv*Sv)
thresholds=[]
for ev in [4.,10.,20.,38.15,70.,110.]:
 st=brentq(lambda u:orbit(u)-ev,sc,s0,xtol=1e-10)
 j=N/ev*quad(state_min,sc,st,epsabs=1e-9,limit=150)[0]
 jq=N/ev*quad(lambda u:2*(1-sc/u)**2/(cv*(u-bs)),sc,st,epsabs=1e-10)[0]
 jc=N/(cv*ev*(sc-bs))*(st-sc*sc/st-2*sc*math.log(st/sc))
 dsdeta=1/(rho*(1/st-1/sc));dj=-j/ev+N/ev*state_min(st)*dsdeta
 assert 0<j<min(jq,jc) and dj<0
 thresholds.append({'eta':ev,'J_min':j,'J_only_quarantine':jq,'J_only_contact':jc,'dJ_min_deta':dj})
assert all(thresholds[k+1]['J_min']<thresholds[k]['J_min'] for k in range(len(thresholds)-1))
report['minimum_cost_thresholds']=thresholds
# One reproducible illustration cited in section 6.4; original figures and Xi'an data are untouched.
def baseline_optimal_c(Sv):
 rv=sc/Sv;bb=bs/Sv
 if 1-rv<1e-5:
  zv=1-rv
  if zv<=0:return cv
  def h(xx):return (xx*xx+2*(1-xx)**2/(1-zv*xx)**2)/(cv*(Sv*(1-zv*xx)-bs))
  xx=minimize_scalar(h,bounds=(0,1),method='bounded',options={'xatol':1e-12}).x
  return cv*(1-zv*xx)
 return cv*candidates(rv,bb)[0]
topt=N/eta*quad(lambda u:1/(baseline_optimal_c(u)*u-cv*bs),sc,ss,epsabs=1e-9,limit=160)[0]
report['new_baseline_joint_illustration']={'eta':eta,'J_min':next(t['J_min'] for t in thresholds if t['eta']==eta),'T_cost_min':topt,'T_only_quarantine':T,'T_only_contact':N*(ss-sc)/(cv*eta*(sc-bs)),'J_only_quarantine':next(t['J_only_quarantine'] for t in thresholds if t['eta']==eta),'J_only_contact':next(t['J_only_contact'] for t in thresholds if t['eta']==eta),'method':'all real stationary roots plus both endpoints at each state; numerical integration; near the shrinking endpoint interval use a scaled local coordinate with grid cross-checks'}
assert topt>T

# Full five-compartment ODE plus total incident infections; joint family is predetermined in time.
ODE_results=[];maxima={'state_residual_relative':0.,'plateau_infection_identity_relative':0.,'plateau_quarantine_identity_relative':0.,'whole_clearance_difference':0.,'whole_cumulative_identity_relative':0.}
for be0 in [.12,.35,.8,1.]:
 pop=1500.;cv0=8.;q00=.12;ga0=.3;dq=.35;init=np.array([pop-3,3.,0.,0.,0.,0.]);e0=30.
 sc0=ga0*pop/(be0*cv0*(1-q00));bar=(1-be0)*ga0*pop/(be0*cv0)
 if sc0>=init[0]:continue
 def rhs(t,y,cval,qval):
  S0,I0,Q0,Iq0,R0,C0=y
  infection=be0*cval*S0*I0/pop
  sq=(1-be0)*cval*qval*S0*I0/pop
  return [-infection-sq, infection*(1-qval)-ga0*I0,sq,infection*qval-dq*Iq0,ga0*I0+dq*Iq0,infection]
 def regular(t,y):return rhs(t,y,cv0,q00)
 def trigger(t,y):return y[1]-e0
 trigger.terminal=True;trigger.direction=1
 pre=solve_ivp(regular,(0,500),init,rtol=2e-11,atol=1e-11,method='DOP853',events=trigger)
 assert len(pre.t_events[0])==1
 entry=pre.y_events[0][0];entry_t=pre.t_events[0][0];start=entry[0];rows=[]
 for av in [0.,.2,.5,.8,1.]:
  dur=pop/(cv0*e0)*(start-sc0)/(sc0-bar) if av==0 else pop/(cv0*e0*av)*math.log1p(av*(start-sc0)/(sc0-bar))
  def analytic(tt):
   if av==0:return start-cv0*e0/pop*(sc0-bar)*tt
   decay=math.exp(-cv0*e0*av*tt/pop)
   return sc0+(start-sc0)*decay+(sc0-bar)/av*math.expm1(-cv0*e0*av*tt/pop)
  def controlled(t,y):
   st=analytic(t);ct=cv0*(av+(1-av)*sc0/st);qt=1-(1-q00)*sc0/(sc0+av*(st-sc0));return rhs(t,y,ct,qt)
  mid=solve_ivp(controlled,(0,dur),entry,rtol=2e-11,atol=1e-11,method='DOP853',dense_output=True)
  ev=mid.y[:,-1];predC=be0*(start-sc0)+ga0*e0*(1-be0)*dur;predQ=(1-be0)*(start-sc0-ga0*e0*dur)
  st_error=np.max(np.abs(mid.sol(np.linspace(0,dur,301))[0]-[analytic(t) for t in np.linspace(0,dur,301)]))/pop
  maxima['state_residual_relative']=max(maxima['state_residual_relative'],st_error)
  maxima['plateau_infection_identity_relative']=max(maxima['plateau_infection_identity_relative'],abs(ev[5]-entry[5]-predC)/pop)
  maxima['plateau_quarantine_identity_relative']=max(maxima['plateau_quarantine_identity_relative'],abs(ev[2]-entry[2]-predQ)/pop)
  def end(t,y):return y[1]-1
  end.terminal=True;end.direction=-1
  post=solve_ivp(regular,(0,1500),ev,rtol=2e-11,atol=1e-11,method='DOP853',events=end)
  assert len(post.t_events[0])==1
  final=post.y_events[0][0];total_t=entry_t+dur+post.t_events[0][0]
  rows.append({'beta':be0,'alpha':av,'duration':dur,'t_end':total_t,'cumulative':float(final[5]),'entry_S':float(start)})
 for row in rows:
  ref=rows[-1]
  maxima['whole_clearance_difference']=max(maxima['whole_clearance_difference'],abs((row['t_end']-ref['t_end'])-(row['duration']-ref['duration'])))
  maxima['whole_cumulative_identity_relative']=max(maxima['whole_cumulative_identity_relative'],abs(row['cumulative']-ref['cumulative']-ga0*e0*(1-be0)*(row['duration']-ref['duration']))/pop)
 ODE_results.extend(rows)
assert max(v for k,v in maxima.items() if 'relative' in k)<1e-7
assert maxima['whole_clearance_difference']<1e-5
report['full_ODE']={'cases':len(ODE_results),'maximum_residuals':maxima,'results':ODE_results}
report['xi_an_exit_bound']={'N':13163000,'S0':13163000-0.00100663,'S_c':2974125.41,'beta':0.1498,'C_lower_bound':.1498*(13163000-.00100663-2974125.41),'computed_from':'existing rounded SIQR parameters; not new fitted data'}
assert all(v for k,v in report['symbolic'].items() if k not in ['quintic_degree','terminal_strict_convex_limit'])
report['passed']=True
out=ROOT/'validation/completed_theory_checks.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'passed':True,'output':str(out),'ODE':maxima,'threshold_cost_values':thresholds,'terminal_error_at_1e_5':max(t['contact_limit_error'] for t in terminal if t['z']==1e-5)},ensure_ascii=False,indent=2))
