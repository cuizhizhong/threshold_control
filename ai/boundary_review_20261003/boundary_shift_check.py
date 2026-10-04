#!/usr/bin/env python3
"""Independent high-precision review of fixed-I0 cost/duration boundaries.

Not part of the repository's accepted reproducibility run. Does not modify paper,
figures or repository data. Zero initial fraction means analytic continuation of
first-integral/plateau formulas, NOT an epidemic generated from zero infectives.

Usage: python boundary_shift_check.py
       python boundary_shift_check.py --inputs inputs.json --output-dir results
Requires mpmath 1.3.0. All reported numerical results condition on the decimal
input values in inputs.json. A finite scan is not a certified uniform bound.
"""
from __future__ import annotations
import argparse
import csv
import json
import platform
from pathlib import Path
import mpmath as mp


def evaluate(data: dict, dps: int, ngrid: int = 41) -> dict:
    mp.mp.dps = dps
    m = mp.mpf
    p = data['parameters']
    beta, gamma, c0, q0 = (m(p[k]) for k in ('beta','gamma','c0','q0'))
    seed, Nref = m(data['I0_abs']), m(p['N'])
    Nmin = m(data['N_floor'])
    peak = m(data['I_peak_T'])
    if not (0 < beta <= 1 and gamma > 0 and c0 > 0 and 0 <= q0 < 1 and seed > 0 and Nref > Nmin > seed):
        raise ValueError('Invalid model parameters or population range')
    A = beta + (1-beta)*q0
    a = beta*(1-q0)/A
    b = gamma/(c0*A)
    sc, sb = b/a, (1-beta)*gamma/(beta*c0)
    hp0 = 1-a+b
    tol = mp.power(10, -dps+12)
    def orbit(s):
        return a*(1-s)+b*mp.log(s)
    def initial_shift(e):
        return (1-a)*e-b*mp.log1p(-e)
    def primitive(s, kind):
        if kind == 'duration':
            return mp.log((s-sb)/(sc-sb))/c0
        if sb == 0:
            return 2/c0*(mp.log(s/sc)+2*sc*(1/s-1/sc)-sc**2/2*(1/s**2-1/sc**2))
        return 2/c0*(sc*(2*sb-sc)/sb**2*mp.log(s/sc)
                      +sc**2/sb*(1/s-1/sc)
                      +(1-sc/sb)**2*mp.log((s-sb)/(sc-sb)))
    def density(s, kind):
        return (1 if kind == 'duration' else 2*(1-sc/s)**2)/(c0*(s-sb))
    def solve(e, kind, target):
        lo, hi = sc, 1-e
        shift = initial_shift(e)
        def f(s): return primitive(s,kind)-target*(orbit(s)+shift)
        if not (hi > lo and f(lo) < 0 and f(hi) > 0):
            raise ValueError('No interior threshold root for these inputs')
        s = (lo+hi)/2
        for _ in range(4*dps+40):
            val = f(s)
            if abs(val) < tol:
                theta = primitive(s,kind)/target
                return theta, s, val
            if val > 0: hi = s
            else: lo = s
            candidate = s-val/(density(s,kind)+target*(a-b/s))
            s = candidate if lo < candidate < hi else (lo+hi)/2
        raise RuntimeError('Safeguarded Newton iteration did not converge')
    scenarios = [('cost','cost',m(data['J_T'])),
                 ('duration45','duration',m(45)),
                 ('duration150','duration',m(150))]
    nodes = [Nmin*mp.exp(mp.log(Nref/Nmin)*j/(ngrid-1)) for j in range(ngrid)]
    nodes[0], nodes[-1] = Nmin, Nref
    result = {'precision_dps':dps, 'grid_size':ngrid, 'scope':'Finite high-precision diagnostic; not interval certification.', 'cases':{}, 'scan':[]}
    sf = lambda v: mp.nstr(v, min(45,dps-10))
    for name,kind,target in scenarios:
        th0,s0,res0=solve(m(0),kind,target)
        gp=density(s0,kind); D=a-b/s0
        kappa=hp0*gp/(gp+target*D)
        # Check the analytic coefficient by high-precision central differences.
        step=mp.power(10,-dps//3)
        central=(solve(step,kind,target)[0]-solve(-step,kind,target)[0])/(2*step)
        thref,sref,_=solve(seed/Nref,kind,target)
        record={'target':sf(target),'theta_zero_limit':sf(th0),'s_star_zero_limit':sf(s0),
                'kappa':sf(kappa),'intercept_people':sf(kappa*seed),
                'derivative_central_difference_error':sf(abs(central-kappa)),
                'theta_at_reference_population':sf(thref),
                'stored_plot_slope':data['stored_slopes'][name],
                'stored_plot_slope_minus_limit':sf(m(data['stored_slopes'][name])-th0)}
        # Verify closed primitive against direct quadrature at the zero-limit root.
        direct=mp.quad(lambda s:density(s,kind),[sc,(sc+s0)/2,s0])
        record['primitive_quadrature_error']=sf(abs(direct-primitive(s0,kind)))
        relative_errors=[]; remainders=[]; exact_plot_differences=[]
        for N in nodes:
            th,s,res=solve(seed/N,kind,target)
            eta=N*th
            dz=eta-N*th0
            rem=dz-kappa*seed
            dp=eta-N*m(data['stored_slopes'][name])
            # The saved number of digits in a display table is not an input slope.
            dr=eta-N*m(data['rounded_user_slopes'][name])
            relative_errors.append(abs(dz/(N*th0)))
            remainders.append(abs(rem));exact_plot_differences.append(abs(dp))
            result['scan'].append({'case':name,'N':sf(N),'initial_fraction':sf(seed/N),
                'theta_exact':sf(th),'eta_exact':sf(eta),'offset_from_zero_limit_line':sf(dz),
                'first_order_remainder_people':sf(rem),'offset_from_stored_plot_line':sf(dp),
                'offset_from_rounded_user_line':sf(dr),'relative_to_zero_limit_line':sf(dz/(N*th0)),
                'equation_residual':sf(res)})
        record['max_sampled_relative_error_to_zero_limit_line']=sf(max(relative_errors))
        record['max_sampled_first_order_remainder_people']=sf(max(remainders))
        record['max_sampled_offset_from_stored_plot_line']=sf(max(exact_plot_differences))
        # Solve eta_boundary(N)=fixed reference peak; no straight-line substitution.
        N=peak/th0
        for _ in range(30):
            e=seed/N;theta,s,res=solve(e,kind,target)
            g=density(s,kind);d=a-b/s;hp=1-a+b/(1-e)
            theta_prime=hp*g/(g+target*d)
            val=N*theta-peak
            if abs(val)<tol:break
            N-=val/(theta-e*theta_prime)
        else: raise RuntimeError('Population intersection did not converge')
        record['N_star_exact']=sf(N)
        record['N_star_zero_limit_line']=sf(peak/th0)
        record['N_star_first_order_line']=sf((peak-kappa*seed)/th0)
        record['N_star_stored_plot_line']=sf(peak/m(data['stored_slopes'][name]))
        record['N_star_relative_zero_limit_error']=sf((peak/th0-N)/N)
        if name in data['stored_N_star']:
            record['N_star_minus_repository_result']=sf(N-m(data['stored_N_star'][name]))
        result['cases'][name]=record
    result['constants']={k:sf(v) for k,v in {'a':a,'b':b,'s_c':sc,'s_bar':sb,'hprime0':hp0}.items()}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',type=Path,default=Path(__file__).with_name('inputs.json'))
    parser.add_argument('--output-dir',type=Path,default=Path(__file__).with_name('results'))
    args=parser.parse_args()
    data=json.loads(args.inputs.read_text(encoding='utf-8'))
    low=evaluate(data,60);high=evaluate(data,90)
    mp.mp.dps=90
    convergence={name:{key:mp.nstr(abs(mp.mpf(high['cases'][name][key])-mp.mpf(low['cases'][name][key])),30)
         for key in ['theta_zero_limit','kappa','intercept_people','N_star_exact']}
         for name in high['cases']}
    output={'metadata':{'python':platform.python_version(),'mpmath':mp.__version__,
             'provenance':data,'precision_comparison':convergence,
             'warning':'These are independent conditional numerical checks; not the accepted repository pipeline and not rigorous interval error bounds.'},
             'results':high}
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'boundary_shift_results.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    with (args.output_dir/'boundary_scan.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(high['scan'][0]));writer.writeheader();writer.writerows(high['scan'])
    for name,item in high['cases'].items():
        print(name, json.dumps(item,ensure_ascii=False))
    print('Precision comparison:',json.dumps(convergence))

if __name__=='__main__':
    main()
