import json, numpy as np
from sq_return import simulate, XIAN, BASE, make_alloc
out = {}
for name, p, T in (('base', BASE, 3000.0), ('xian', XIAN, 4000.0)):
    allocs = {pol: make_alloc(p, pol) for pol in ('q_only', 'optimal', 'c_only')}
    for lam in (0.0, 1/21, 1/14, 1/7):
        for rule in ('oneshot', 'feedback'):
            if lam == 0 and rule == 'feedback':
                continue
            for pol in ('q_only', 'optimal', 'c_only'):
                r = simulate(p, pol, lam=lam, rule=rule, T=T, alloc=allocs[pol])
                key = f"{name}|{lam:.4f}|{rule}|{pol}"
                out[key] = dict(n_ep=r['n_ep'], tctrl=r['tctrl'], t1=r['t1'], t_last=r['t_last'],
                                t_end=r['t_end'], inf=r['inf'], sq_in=r['sq_in'], J=r['J'],
                                Imax_eta=r['Imax_over_eta'], Iafter_eta=r['pk']['I_after_exit']/p['eta'],
                                Sq_pk=r['pk']['Sq'], Iq_pk=r['pk']['Iq'], IIq_pk=r['pk']['Iq_plus_I'],
                                P_end=r['P_end'], Sc=r['Sc'], seg=r['seg'][:6], nseg=len(r['seg']))
                d = out[key]
                print(f"{key:32s} ep={d['n_ep']:3d} tctrl={d['tctrl']:8.2f} tlast={d['t_last'] or 0:8.1f} "
                      f"tend={d['t_end'] or -1:8.1f} inf={d['inf']:.4g} sqin={d['sq_in']:.4g} J={d['J']:8.2f} "
                      f"Imax/eta={d['Imax_eta']:.3f} Iafter/eta={d['Iafter_eta']:.3f} Sqpk={d['Sq_pk']:.4g} "
                      f"(I+Iq)pk/eta={d['IIq_pk']/p['eta']:.2f} P_end/Sc={d['P_end']/d['Sc']:.3f}", flush=True)
json.dump(out, open('results/sq_return_results.json', 'w'), indent=1, default=float)
