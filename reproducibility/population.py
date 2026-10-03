"""固定绝对初值的有效人口边界与代表轨迹；不读取历史数值缓存。"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import json
import math
import numpy as np
import pandas as pd
from scipy.optimize import brentq

try:
    from .xian import Params, structural, threshold_strategy, time_strategy, dump, save_csv
except ImportError:
    from xian import Params, structural, threshold_strategy, time_strategy, dump, save_csv


def background_peak(p, I0):
    s0=1-I0/p.N; i0=I0/p.N
    A=p.beta+p.q0*(1-p.beta)
    k=p.beta*(1-p.q0)/A; rho=p.gamma/(p.c0*A)
    sc=p.gamma/(p.beta*p.c0*(1-p.q0))
    return i0 if sc>=s0 else i0+k*(s0-sc)+rho*np.log(sc/s0)


def theta_root(p, I0, key, target):
    upper=background_peak(p,I0)*(1-1e-9)
    return brentq(lambda th:structural(p,I0,th*p.N,times=False)[key]-target,
                  max(2/p.N,1e-7),upper,xtol=1e-15,rtol=1e-13)


def population_arc(p, I0, eta, key, target):
    # 下端只用于数值求根，不作人口可行性主张；随后与 N_floor 相交。
    lo=eta/background_peak(replace(p,N=1e8),I0)*1.0001
    hi=max(1e6,lo*10)
    return brentq(lambda N:structural(replace(p,N=N),I0,eta)[key]-target,
                  lo,hi,xtol=1e-7,rtol=1e-12)


def main_critical(p, I0, ref):
    tc=theta_root(p,I0,'J',ref['J_T'])
    d45=theta_root(p,I0,'Delta_t',45.)
    d150=theta_root(p,I0,'Delta_t',150.)
    floor=ref['Ic_cum_T']+ref['Iq_cum_T']/p.beta
    # 固定绝对 I0 后主边界与纯 theta 近似相差约 1e-5，两者都保留。
    def critical(key,target):
        return brentq(lambda N:structural(replace(p,N=N),I0,ref['I_peak_T'],times=False)[key]-target,
                      5000.,2e6,xtol=1e-7,rtol=1e-12)
    ns=critical('J',ref['J_T']); n45=critical('Delta_t',45.)
    def cum_at_cost(N):
        pn=replace(p,N=N)
        th=theta_root(pn,I0,'J',ref['J_T'])
        return structural(pn,I0,N*th)['Itcum']-ref['Itcum_T']
    nc=brentq(cum_at_cost,2000.,1e5,xtol=1e-7,rtol=1e-12)
    nclr_at_peak=population_arc(p,I0,ref['I_peak_T'],'t_end',ref['t_end_T'])
    return {'theta_cost':tc,'theta_dur45':d45,'theta_dur150':d150,
            'theta_inflection_limit':float(I0/p.N + p.beta*(1-p.q0)/(p.beta+p.q0*(1-p.beta))*(1-I0/p.N-2*p.gamma*(1-p.beta)/(p.beta*p.c0))
                +p.gamma/(p.c0*(p.beta+p.q0*(1-p.beta)))*np.log(2*p.gamma*(1-p.beta)/(p.beta*p.c0)/(1-I0/p.N))),
            'N_floor':floor,'N_star_inf':ns,'N_star45':n45,'N_star_cum_inf':nc,
            'N_star_clear_peak':nclr_at_peak,'i_max_no':background_peak(p,I0),
            'N_star_inf_theta_approx':ref['I_peak_T']/tc,'N_star45_theta_approx':ref['I_peak_T']/d45}


def draw_original(root, figdir, critical, ref, arcs):
    """原 dom_pretty 的绘制逻辑不动，只注入本次重新计算的边界。"""
    path=root/'xian_dom/dom_pretty.py'
    code=path.read_text(encoding='utf-8-sig')
    begin=code.index('OUT = '); end=code.index('def sort_unique')
    names={'IPEAK':ref['I_peak_T'],'IMAX_NO':critical['i_max_no'],
           'th_cost':critical['theta_cost'],'th_d45':critical['theta_dur45'],
           'th_d150':critical['theta_dur150'],'th_int':critical['theta_inflection_limit'],
           'Nstar_45':critical['N_star45'],'N_FLOOR':critical['N_floor'],
           'N_FLOOR_OLD':ref['Itcum_T']}
    block='OUT = Path('+repr(str(figdir))+')\nOUT.mkdir(parents=True, exist_ok=True)\n'
    block+='\n'.join(f'{k} = {v!r}' for k,v in names.items())+'\n'
    for key,col in [('cum_eta','eta'),('cum_N','N_cum'),('clr_eta','eta'),('clr_N','N_clear')]:
        block+=f'{key} = np.array({arcs[col].tolist()!r}, float)\n'
    # 交点从重新计算的累计弧求根，不保留原图硬编码 70.16。
    block+='ETA_CUM_FLOOR = '+repr(critical['eta_cum_floor'])+'\n\n'
    env={'__file__':str(path),'__name__':'repro_dom_original'}
    exec(compile(code[:begin]+block+code[end:],str(path),'exec'),env)


def run_population(output_dir: Path, root: Path) -> dict:
    out=output_dir/'population';out.mkdir(parents=True,exist_ok=True)
    ref=json.loads((output_dir/'xian/reference.json').read_text(encoding='utf-8'))
    p=Params(**ref['parameters']); I0=ref['I0_abs']
    crit=main_critical(p,I0,ref)
    crit['eta_cum_floor']=brentq(lambda eta:structural(replace(p,N=crit['N_floor']),I0,eta)['Itcum']-ref['Itcum_T'],
                               1.01,ref['I_peak_T'],xtol=1e-10)
    cost_at_boundary=structural(p,I0,p.N*crit['theta_cost'])
    crit['duration_at_cost_boundary']=cost_at_boundary['Delta_t']
    crit['eta_at_cumulative_cost_intersection']=crit['N_star_cum_inf']*theta_root(
        replace(p,N=crit['N_star_cum_inf']),I0,'J',ref['J_T'])
    etas=np.geomspace(10.,ref['I_peak_T'],16)
    arc_rows=[]
    for eta in etas:
        nc=population_arc(p,I0,float(eta),'Itcum',ref['Itcum_T'])
        nz=population_arc(p,I0,float(eta),'t_end',ref['t_end_T'])
        arc_rows.append({'eta':eta,'N_cum':nc,'N_clear':nz,
                         'cum_residual':structural(replace(p,N=nc),I0,eta)['Itcum']-ref['Itcum_T'],
                         'clear_residual':structural(replace(p,N=nz),I0,eta)['t_end']-ref['t_end_T']})
    arcs=pd.DataFrame(arc_rows);save_csv(arcs,out/'arcs.csv')
    dump(out/'critical.json',crit)
    # beta 扫描保持 beta*c0 不变；实际 TDINN 四参照和 I0 不随反事实 beta 重拟合。
    beta_rows=[]
    for beta in [.10,.12,.1498,.20,.25,.30]:
        pb=replace(p,beta=beta,c0=p.beta*p.c0/beta)
        cb=main_critical(pb,I0,ref)
        beta_rows.append({'beta':beta,'c0':pb.c0,**cb,'main_width':cb['N_star_inf']-cb['N_floor'],
                          'cumulative_width':cb['N_star_cum_inf']-cb['N_floor']})
    save_csv(pd.DataFrame(beta_rows),out/'beta_scan.csv')
    beta_df=pd.DataFrame(beta_rows)
    ratios=beta_df.N_star_inf/beta_df.N_floor
    beta_summary={'N_star_over_floor_min':float(ratios.min()),'N_star_over_floor_max':float(ratios.max()),
                  'ratio_relative_range':float((ratios.max()-ratios.min())/ratios.mean()),
                  'beta_N_star_relative_range':float((beta_df.beta*beta_df.N_star_inf).max()/(beta_df.beta*beta_df.N_star_inf).min()-1),
                  'beta_N_floor_relative_range':float((beta_df.beta*beta_df.N_floor).max()/(beta_df.beta*beta_df.N_floor).min()-1)}
    dump(out/'beta_summary.json',beta_summary)
    limits=[]
    for limit in [45.,60.,90.,150.,None]:
        td=theta_root(p,I0,'Delta_t',limit) if limit is not None else 0.
        N=crit['N_star_inf'] if not limit or td<crit['theta_cost'] else brentq(
            lambda n:structural(replace(p,N=n),I0,ref['I_peak_T'],times=False)['Delta_t']-limit,
            5000.,2e6,xtol=1e-7)
        limits.append({'T_max':limit,'theta_dur':td,'theta_cost':crit['theta_cost'],
                       'theta_bind':max(td,crit['theta_cost']),'N_star':N})
    save_csv(pd.DataFrame(limits),out/'duration_limits.csv')
    inflection_tests=[]
    for N in [40000.,50000.,60000.]:
        for eta in [80.,100.,150.]:
            d=structural(replace(p,N=N),I0,eta)
            si=d['s_bar']+(d['s_star']-d['s_bar'])*np.exp(-p.c0*eta/N*(d['t_inf']-d['t1']))
            qi=1-p.gamma/(p.beta*p.c0*si)
            inflection_tests.append({'N':N,'eta':eta,'q_at_t_inf':qi,'q_inf':d['q_inf'],'error':abs(qi-d['q_inf'])})
    save_csv(pd.DataFrame(inflection_tests),out/'inflection_invariance.csv')
    supplementary={'example_N50000_eta100':structural(replace(p,N=50000.),I0,100.),
                   'city_eta100':structural(p,I0,100.),'beta_max':1-1/(2*(1-p.q0)),
                   'growth_rate':p.beta*p.c0*(1-p.q0)-p.gamma,
                   'tenfold_initial_time_shift':math.log(10)/(p.beta*p.c0*(1-p.q0)-p.gamma),
                   'log_factor_low':structural(replace(p,N=20000.),I0,.0005*20000.,times=False)['Delta_t']*p.c0*.0005,
                   'log_factor_high':structural(replace(p,N=20000.),I0,.008*20000.,times=False)['Delta_t']*p.c0*.008,
                   'beta_summary':beta_summary,'max_inflection_q_error':max(r['error'] for r in inflection_tests)}
    dump(out/'supplementary_anchors.json',supplementary)
    # 固定归一化初值检验理论规模不变性；主轨迹仍固定绝对 I0。
    scale=[]
    for N in [10000.,20000.,100000.]:
        for theta in [crit['theta_dur150'],crit['theta_cost'],crit['theta_dur45']]:
            d=structural(replace(p,N=N),I0*N/p.N,N*theta,times=False)
            scale.append({'N':N,'theta':theta,'I0':I0*N/p.N,'Delta_t':d['Delta_t'],'J':d['J'],'q_max':d['q_max']})
    scaled=pd.DataFrame(scale);save_csv(scaled,out/'scale_invariance.csv')
    absolute=[]
    for N in [5e4,1e5,5e5,1e6,5e6,p.N]:
        d=structural(replace(p,N=N),I0,.002*N)
        absolute.append({'N':N,'I0':I0,'theta':.002,**d})
    abs_frame=pd.DataFrame(absolute);save_csv(abs_frame,out/'fixed_absolute_scale.csv')
    normalized_clear=[]
    for eta in etas:
        lo=eta/background_peak(p,I0)*1.0001
        N=brentq(lambda n:structural(replace(p,N=n),I0*n/p.N,float(eta))['t_end']-ref['t_end_T'],
                 lo,1e6,xtol=1e-7,rtol=1e-12)
        normalized_clear.append({'eta':eta,'N_clear_fixed_normalized':N,'I0':I0*N/p.N})
    save_csv(pd.DataFrame(normalized_clear),out/'clear_arc_fixed_normalized_diagnostic.csv')
    datadir=output_dir/'workspace/latex/revision_v4/data';datadir.mkdir(parents=True,exist_ok=True)
    metadata={'cases':[],'fixed_eta':[],'N_floor':crit['N_floor'],
              'theta':[crit['theta_dur150'],crit['theta_cost'],crit['theta_dur45']],
              'critical':crit,'reference':ref,'fixed_absolute_I0':I0}
    rows=[]; errors=[]
    def case(N,eta,stem,role):
        pn=replace(p,N=float(N))
        df,d=threshold_strategy(pn,I0,float(eta))
        routine,rd=time_strategy(pn,I0,'常规控制')
        # 原组合代码读取 I/q/Ccum，并以 metadata 的时刻绘制内嵌与投影。
        df=df.assign(Itcum=df.Cc+df.Cq,It_cum=df.Cc+df.Cq)
        routine=routine.assign(Itcum=routine.Cc+routine.Cq,It_cum=routine.Cc+routine.Cq)
        save_csv(df,datadir/(stem+'.csv'));save_csv(routine,datadir/(stem+'_routine.csv'))
        save_csv(df,out/(stem+'.csv'));save_csv(routine,out/(stem+'_routine.csv'))
        rec={'N':float(N),'eta':float(eta),'stem':stem,'role':role,'t1':d['t1'],'t2':d['t2'],
             't_end':d['t_end'],'ti':d['t_inf'],'qi':d['q_inf'],'Itcum':d['Itcum'],
             'J':d['J'],'I0':I0,'Delta_t':d['Delta_t']}
        rows.append({**rec,**{k:d[k] for k in ['q_max','lambda_inf','plateau_max_error','mass_residual','analytic_ode_cumulative_error']},
                     'routine_peak_I':rd['peak_I'],'routine_clear_time':rd['clear_time'],
                     'routine_Itcum':rd['cum_total_infections']})
        errors.append(max(d['plateau_max_error'],d['analytic_ode_cumulative_error'],d['mass_residual']))
        return rec
    # 图14及图18：四人口×三个阈值角色，旧stem保留但所有数值重算。
    for j,N in enumerate([20000.,crit['N_star_cum_inf'],crit['N_star45'],crit['N_star_inf']]):
        group=[]
        for k,(role,key,target) in enumerate([('dur150','Delta_t',150.),('cost','J',ref['J_T']),('dur45','Delta_t',45.)]):
            th=theta_root(replace(p,N=N),I0,key,target)
            group.append(case(N,N*th,f'dominance_case{j}_{k}',role))
        metadata['cases'].append(group)
        print('POPULATION_CASE',j,N,flush=True)
    fixed_eta=100.
    fixedNs=[population_arc(p,I0,fixed_eta,'t_end',ref['t_end_T']),
             population_arc(p,I0,fixed_eta,'Itcum',ref['Itcum_T'])]
    for key,target in [('Delta_t',45.),('J',ref['J_T']),('Delta_t',150.)]:
        fixedNs.append(brentq(lambda N:structural(replace(p,N=N),I0,fixed_eta,times=False)[key]-target,
                             2000.,2e5,xtol=1e-7,rtol=1e-12))
    for j,(N,role) in enumerate(zip(fixedNs,['clear','cum','dur45','cost','dur150'])):
        metadata['fixed_eta'].append(case(N,fixed_eta,f'dominance_fixed_eta{j}',role))
    save_csv(pd.DataFrame(rows),out/'representative_summary.csv')
    dump(datadir/'dominance_metadata.json',metadata);dump(out/'metadata.json',metadata)
    figdir=output_dir/'workspace/latex/figures';figdir.mkdir(parents=True,exist_ok=True)
    draw_original(root,figdir,crit,ref,arcs)
    spread=scaled.groupby('theta')[['Delta_t','J','q_max']].agg(lambda x:float(x.max()-x.min())).to_numpy().max()
    report={'passed':bool(max(errors)<1e-4 and spread<1e-8 and np.max(abs(arcs.cum_residual))<1e-4 and np.max(abs(arcs.clear_residual))<1e-6),
            'critical':crit,'fixed_absolute_I0':I0,'arc_points':16,'trajectory_count':17,
            'max_trajectory_error':max(errors),'scale_invariance_spread':spread,
            'fixed_absolute_duration_relative_range':float((abs_frame.Delta_t.max()-abs_frame.Delta_t.min())/abs_frame.Delta_t.mean()),
            'fixed_absolute_t1_min':float(abs_frame.t1.min()),'fixed_absolute_t1_max':float(abs_frame.t1.max()),
            'fixed_normalized_clear_arc_max':float(max(r['N_clear_fixed_normalized'] for r in normalized_clear)),
            'clear_region_empty_numerically':bool(arcs.N_clear.max()<crit['N_floor']),
            'artifacts':[str(f.relative_to(output_dir)) for f in out.iterdir() if f.is_file()]}
    dump(out/'diagnostics.json',report)
    return report
