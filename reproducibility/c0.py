"""西安参数固定绝对初值下的 c0 响应、驻定曲线与 beta 拐点域。"""
from __future__ import annotations

from dataclasses import asdict, replace
from pathlib import Path
from types import SimpleNamespace
import json
import math
import numpy as np
import pandas as pd
from scipy.optimize import brentq, minimize_scalar

try:
    from .xian import Params, fit_initial, structural, threshold_strategy, source_module, dump, save_csv
    from .population import background_peak
except ImportError:
    from xian import Params, fit_initial, structural, threshold_strategy, source_module, dump, save_csv
    from population import background_peak


def boundaries(p,I0,theta=.002):
    trigger=brentq(lambda c:background_peak(replace(p,c0=c),I0)-theta,2.5,10.,xtol=1e-12)
    qi=1-1/(2*(1-p.beta))
    inf=brentq(lambda c:structural(replace(p,c0=c),I0,theta*p.N,times=False,costs=False)['q_max']-qi,
               trigger*(1+1e-7),14.,xtol=1e-12)
    opt=minimize_scalar(lambda c:-structural(replace(p,c0=c),I0,theta*p.N,times=False,costs=False)['Delta_t'],
                        bounds=(trigger*(1+1e-7),30.),method='bounded',options={'xatol':1e-11})
    if not opt.success:raise RuntimeError(opt.message)
    return {'c0_trigger':trigger,'c0_inflection_onset':inf,'c0_duration_max':float(opt.x),
            'duration_max':float(-opt.fun),'q_inf':qi}


def compatible_metrics(d,role,p,I0,df=None):
    s0=1-I0/p.N
    result={'role':role,'c0':p.c0,'initial_Re':p.beta*p.c0*(1-p.q0)*s0/p.gamma,
            'background_peak_fraction':d['background_peak_I']/p.N,'background_peak_I':d['background_peak_I'],
            't1':d['t1'],'t2':d['t2'],'control_duration':d['Delta_t'],'clear_time':d['t_end'],
            'post_control_tail':d['post_control_tail'],'cumulative_total':d['Itcum'],
            's_star':d['s_star'],'s_c':d['s_c'],'s_bar':d['s_bar'],'q_max':d['q_max'],
            'q_inf':d['q_inf'],'cost_J':d['J'],'has_internal_inflection':d['has_internal_inflection'],
            't_inf':d['t_inf'],'lambda_inf':d['lambda_inf'],
            't2_minus_tinf':d['t2']-d['t_inf'] if d['t_inf'] is not None else None,
            'plateau_max_abs_error_I':d.get('plateau_max_error'),
            'finite_difference_tinf':None,'finite_difference_qinf':None,
            'finite_difference_tinf_error':None,'finite_difference_qinf_error':None}
    if df is not None:
        result.update(cumulative_community=float(df.Cc.iloc[-1]),cumulative_quarantine=float(df.Cq.iloc[-1]))
    return result


def run_c0(output_dir: Path, root: Path) -> dict:
    out=output_dir/'c0';out.mkdir(parents=True,exist_ok=True)
    ref=json.loads((output_dir/'xian/reference.json').read_text(encoding='utf-8'))
    p=replace(Params(**ref['parameters']),N=20000.)
    I0=ref['I0_abs'];eta=.002*p.N
    observed=pd.read_csv(output_dir/'xian/observed.csv')
    # 20k 重拟合仅作初值敏感性诊断，主实验始终使用全市一次拟合的绝对 I0。
    fit20k=fit_initial(observed,p)
    b=boundaries(p,I0)
    post=b['c0_inflection_onset']*1.05
    if b['c0_inflection_onset']*.95<b['c0_trigger']*1.03:
        post=b['c0_inflection_onset']+.05
    reps=[('near-trigger',b['c0_trigger']*1.03),('post-inflection',post),
          ('max-duration',b['c0_duration_max']),('post-ridge',9.),('baseline',p.c0)]
    scenarios=[];rows=[];frames=[];errors=[]
    mod=source_module(root,'c0_sensitivity/run_c0_sensitivity.py','repro_original_c0')
    mod.P=replace(mod.P,full_city_I0_reference=I0)
    for role,c in reps:
        pc=replace(p,c0=float(c));df,d=threshold_strategy(pc,I0,eta)
        m=compatible_metrics(d,role,pc,I0,df)
        tt=np.linspace(d['t1'],d['t2'],4001)
        ss=d['s_bar']+(d['s_star']-d['s_bar'])*np.exp(-c*.002*(tt-d['t1']))
        qq=1-p.gamma/(p.beta*c*ss)
        # 独立差分诊断，不把解析拐点当作差分结果。
        if d['has_internal_inflection']:
            q2=np.gradient(np.gradient(qq,tt),tt)
            j=int(np.argmin(abs(q2[8:-8])))+8
            m.update(finite_difference_tinf=float(tt[j]),finite_difference_qinf=float(qq[j]),
                     finite_difference_tinf_error=abs(tt[j]-d['t_inf']),finite_difference_qinf_error=abs(qq[j]-d['q_inf']))
        ts=df.assign(role=role,c0=c,I_cum=df.Cc,Iq_cum=df.Cq,It_cum=df.Cc+df.Cq,
                     phase=np.where(df.t<d['t1'],'pre-control',np.where(df.t<=d['t2'],'threshold-control','post-control')))
        scenarios.append(mod.Scenario(SimpleNamespace(**m),ts,tt,qq,(tt-d['t1'])/d['Delta_t']))
        rows.append(m);frames.append(ts)
        errors.append({k:d[k] for k in ['plateau_max_error','mass_residual','analytic_ode_cumulative_error','analytic_ode_time_error']})
    values=np.unique(np.r_[np.linspace(b['c0_trigger']*(1+1e-6),4.5,260),np.linspace(4.5,22.,360),
                          [b['c0_inflection_onset']*(1+1e-7),b['c0_duration_max']],[c for role,c in reps]])
    scan=[]
    for c in values:
        pc=replace(p,c0=float(c));d=structural(pc,I0,eta)
        scan.append(compatible_metrics(d,'scan',pc,I0))
    scan=pd.DataFrame(scan);save_csv(scan,out/'scan.csv')
    summary=pd.DataFrame(rows);ts=pd.concat(frames,ignore_index=True)
    save_csv(summary,out/'representative_summary.csv');save_csv(ts,out/'timeseries.csv')
    cumvalues=np.linspace(b['c0_trigger']*1.01,22.,48)
    cum=np.array([[c,d['Itcum'],d['t_end'],d['post_control_tail']]
                  for c in cumvalues for d in [structural(replace(p,c0=float(c)),I0,eta)]])
    save_csv(pd.DataFrame(cum,columns=['c0','Itcum','t_end','tail']),out/'cumulative_curve.csv')
    extrema={}
    for key in ['J','Itcum']:
        opt=minimize_scalar(lambda c:-structural(replace(p,c0=c),I0,eta)[key],
                            bounds=(b['c0_trigger']*(1+1e-6),30.),method='bounded',options={'xatol':1e-9})
        if not opt.success:raise RuntimeError(opt.message)
        extrema[key]={'c0':float(opt.x),'value':float(-opt.fun)}
    extrema['time_at_c0_30']=structural(replace(p,c0=30.),I0,eta)
    extrema['time_at_near_trigger']=rows[0]['clear_time']
    clearance=[]
    for c in np.linspace(reps[0][1],30.,200):
        d=structural(replace(p,c0=float(c)),I0,eta)
        clearance.append({'c0':c,'t_end':d['t_end'],'Delta_t':d['Delta_t'],'J':d['J'],'Itcum':d['Itcum']})
    save_csv(pd.DataFrame(clearance),out/'extended_scan.csv')
    extrema['clearance_decreasing_on_grid']=bool(np.all(np.diff([r['t_end'] for r in clearance])<0))
    dump(out/'extrema.json',extrema)
    # 70点三边界 + 140×120全网格，全部从固定绝对初值及解析首次积分计算。
    theta=np.geomspace(.0005,.008,70)
    curves=[]
    for th in theta:
        z=boundaries(p,I0,float(th));curves.append([z['c0_trigger'],z['c0_inflection_onset'],z['c0_duration_max']])
    caxis=np.linspace(3.,14.,140);thaxis=np.geomspace(.0005,.008,120)
    duration=np.full((len(thaxis),len(caxis)),np.nan)
    for j,th in enumerate(thaxis):
        for k,c in enumerate(caxis):
            d=structural(replace(p,c0=float(c)),I0,float(th*p.N),times=False,costs=False)
            if d['status']=='ok':duration[j,k]=d['Delta_t']
    phase={'theta':theta,'curves':np.array(curves),'c':caxis,'th':thaxis,'duration':duration,'initial':I0}
    np.savez(out/'phase.npz',**phase)
    # beta 域保存精确数值网格，不仅交付图片。
    ca=np.linspace(3.,14.,220);ba=np.linspace(.05,.30,220)
    exists=np.zeros((len(ba),len(ca)),dtype=np.uint8);margin=np.full(exists.shape,np.nan)
    for j,beta in enumerate(ba):
        for k,c in enumerate(ca):
            d=structural(replace(p,beta=float(beta),c0=float(c)),I0,eta,times=False,costs=False)
            if d['status']=='ok':
                margin[j,k]=d['s_star']-2*d['s_bar'];exists[j,k]=d['has_internal_inflection']
    np.savez(out/'beta_existence.npz',c=ca,beta=ba,exists=exists,margin=margin)
    parameters={'parameters':asdict(mod.P),'derived':{'eta':eta,'I0_fixed_absolute':I0,
                    'I0_refit_at_N_eff':fit20k['I0'],'I0_refit_objective':fit20k['objective'],
                    'full_city_I0_reproduction':I0,'full_city_objective_reproduction':ref['fit']['objective'],**b},
                'initial_convention':'主实验固定全市一次拟合的绝对I0；20k重拟合仅诊断，不替换主实验。',
                'fit_at_20k_diagnostic':fit20k,'representative_c0':[{'role':r,'c0':c} for r,c in reps]}
    dump(out/'parameters.json',parameters)
    dirs=[output_dir/'workspace/c0_sensitivity/outputs',
          output_dir/'workspace/archive_unused/generated_snapshots/c0_sensitivity_outputs']
    for compat in dirs:
        dump(compat/'experiment_parameters.json',parameters)
        save_csv(summary,compat/'c0_representative_summary.csv');save_csv(ts,compat/'c0_representative_timeseries.csv')
        save_csv(scan,compat/'c0_continuous_scan.csv')
    datadir=output_dir/'workspace/latex/revision_v4/data';datadir.mkdir(parents=True,exist_ok=True)
    np.savez(datadir/'phase_curves.npz',**phase)
    figdir=output_dir/'workspace/latex/figures';figdir.mkdir(parents=True,exist_ok=True)
    mod.OUTPUT_DIR=figdir;mod.configure_plot_style()
    mod.plot_scan(scan,scenarios,b,cum)
    mod.plot_beta_existence(I0)
    # 代表点收紧容差核对，对末位拟合差异与数值误差分别记录。
    _,tight=threshold_strategy(p,I0,eta,tight=True)
    base=rows[-1]
    convergence={'clear_time':abs(tight['ode_clear_time']-base['clear_time']),
                 'cumulative_total':abs(tight['ode_cumulative_total']-base['cumulative_total'])}
    report={'passed':bool(max(e['plateau_max_error'] for e in errors)<1e-5
                 and max(e['analytic_ode_cumulative_error'] for e in errors)<1e-4
                 and max(convergence.values())<1e-4),
            'boundaries':b,'representative_count':5,'scan_rows':len(scan),'phase_shape':list(duration.shape),
            'beta_shape':list(exists.shape),'primary_I0':I0,'fit20k_diagnostic':fit20k,
            'trajectory_checks':errors,'tight_comparison':convergence,
            'artifacts':[str(f.relative_to(output_dir)) for f in out.iterdir() if f.is_file()]}
    dump(out/'diagnostics.json',report)
    try:
        from .xian import write_anchor_updates
    except ImportError:
        from xian import write_anchor_updates
    write_anchor_updates(output_dir,root)
    return report
