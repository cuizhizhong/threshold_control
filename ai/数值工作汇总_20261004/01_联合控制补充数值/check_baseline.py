import csv, numpy as np
import joint_numerics as JN
p = JN.baseline_params()
ref = {r['strategy']: r for r in csv.DictReader(open(JN.ROOT/'reproducibility/results/20261003_release_final/joint/results.csv', encoding='utf-8-sig'))}
for ns in (4001, 8001, 16001):
    s = JN.s_grid(p, ns)
    x, nl = JN.allocate(p, s, 1, 2, nx=4001)
    q = JN.plateau_quantities(p, s, x)
    print(ns, 'min_cost dT=%.12f J=%.12f' % (q['dT'], q['J']))
s = JN.s_grid(p, 8001)
pols = {'contact_only': JN.x_policy('contact_only', s), 'alpha_0.5': JN.x_policy('alpha', s, 0.5),
        'quarantine_only': JN.x_policy('quarantine_only', s), 'minimum_cost': JN.allocate(p, s, 1, 2, nx=4001)[0]}
for k, x in pols.items():
    r = JN.full_run(p, s, x)
    R = ref[k]
    print(f"{k:16s} dT {r['dT']:.8f} ({float(R['duration']):.8f})  J {r['J']:.8f} ({float(R['cost']):.8f})  "
          f"tend {r['t_end']:.6f} ({float(R['t_end']):.6f})  inf {r['total_infections']:.4f} ({float(R['total_infections']):.4f})  "
          f"Sq {r['plateau_Sq']:.4f} ({float(R['new_Sq_control']):.4f}) drift {r['max_rel_drift']:.1e} I+Iq pk {r['peak_I_plus_Iq']:.2f}")
