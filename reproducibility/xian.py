"""从西安原始日报计算统一精度的拟合、策略参照与阈值响应。

方程及 TDINN 函数沿用现有 xian_control_comparison.py；归一化积分避免
绝对初值约 1e-3 时旧绝对容差 1e-4 对早期传播的影响。旧文件保持不变。
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path
import importlib.util
import json
import math
import sys
import hashlib
import ast
import io
import re

import numpy as np
import pandas as pd
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq, minimize_scalar


@dataclass(frozen=True)
class Params:
    N: float = 13_163_000.0
    beta: float = .1498
    gamma: float = .2953
    delta_q: float = .3531
    c0: float = 12.8872
    q0: float = .3230


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False,
                              default=lambda v: v.item() if hasattr(v, 'item') else str(v))+'\n', encoding='utf-8')


def save_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding='utf-8-sig', float_format='%.17g')


def source_module(root: Path, rel: str, name: str):
    source = root / rel
    old_path = list(sys.path)
    sys.path.insert(0, str(source.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, source)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = old_path
    return module


def controls(t):
    # 原科学源文件 c_real / q_real 的表达式；两个参数函数不重新拟合。
    t = np.asarray(t)
    return ((12.8872-3.4625)*np.exp(-(.0463*t)**2)+3.4625,
            (.3230-.9844)*np.exp(-(.0452*t)**2)+.9844)


def initial(p: Params, I0: float):
    y = np.zeros(10)
    y[:2] = [1-I0/p.N, I0/p.N]
    return y


def rhs(p: Params, cfun, qfun):
    """[s,i,sq,iq,r,cc,cq,Jc,Jq,J]；前七项为人口比例。"""
    def f(t, y):
        s, i, sq, iq, r, cc, cq = y[:7]
        c, q = float(cfun(t)), float(qfun(t))
        force = c*s*i
        fc, fq, fs = p.beta*(1-q)*force, p.beta*q*force, (1-p.beta)*q*force
        uc, uq = max((p.c0-c)/p.c0, 0.), max((q-p.q0)/(1-p.q0), 0.)
        return np.array([-fc-fq-fs, fc-p.gamma*i, fs, fq-p.delta_q*iq,
                         p.gamma*i+p.delta_q*iq, fc, fq, uc, uq, uc*uc+2*uq*uq])
    return f


def integrate(p, I0, cfun, qfun, end, *, y0=None, start=0., event=None, tight=False):
    atol = np.array([1e-14, 1e-21, 1e-15, 1e-21, 1e-15, 1e-21, 1e-21, 1e-12, 1e-12, 1e-12])
    if tight:
        atol *= .1
    sol = solve_ivp(rhs(p, cfun, qfun), (start, end), initial(p, I0) if y0 is None else y0,
                    method='DOP853', dense_output=True, events=event,
                    rtol=2e-12 if tight else 2e-11, atol=atol,
                    max_step=.2 if tight else .4)
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol


def fit_initial(observed, p=Params()):
    edges = np.arange(len(observed)+1, dtype=float)
    data = [observed[k].to_numpy(float) for k in ['community_new','quarantine_new','community_cum','quarantine_cum']]
    calls = 0
    def objective(log_i):
        nonlocal calls
        calls += 1
        sol = integrate(p, math.exp(log_i), lambda t: controls(t)[0], lambda t: controls(t)[1], edges[-1])
        arr = sol.sol(edges)*p.N
        pred = [np.diff(arr[5]), np.diff(arr[6]), arr[5,1:], arr[6,1:]]
        return float(sum(np.mean((a-b)**2) for a,b in zip(pred,data)))
    opt = minimize_scalar(objective, bounds=(-15., 0.), method='bounded', options={'xatol':1e-11})
    if not opt.success:
        raise RuntimeError(opt.message)
    I0 = math.exp(opt.x)
    sol = integrate(p,I0,lambda t:controls(t)[0],lambda t:controls(t)[1],edges[-1])
    arr = sol.sol(edges)*p.N
    pred = np.r_[np.diff(arr[5]),np.diff(arr[6])]
    return {'I0':I0,'S0':p.N-I0,'R0_initial':0.,'objective':float(opt.fun),
            'raw_rmse':float(np.sqrt(np.mean((pred-np.r_[data[0],data[1]])**2))),
            'residual_type':'paper_mse_unified','optimizer_calls':calls,'N':p.N}


def structural(p: Params, I0: float, eta: float, *, costs=True, times=True):
    """原首次积分的稳定 x=s0-s 坐标；所得 q(t) 仍为时间开环。"""
    s0,i0=1-I0/p.N,I0/p.N
    A=p.beta+p.q0*(1-p.beta)
    k=p.beta*(1-p.q0)/A
    rho=p.gamma/(p.c0*A)
    sc=p.gamma/(p.beta*p.c0*(1-p.q0))
    sb=p.gamma*(1-p.beta)/(p.beta*p.c0)
    theta=eta/p.N
    def ix(x): return i0+k*x+rho*np.log1p(-x/s0)
    ip=float(ix(s0-sc)) if sc<s0 else i0
    if theta<=i0 or ip<=theta or sc>=s0:
        return {'status':'threshold_not_reached','eta':eta,'eta_fraction':theta,'c0':p.c0,'peak_I':ip*p.N}
    xx=brentq(lambda x:ix(x)-theta,0.,s0-sc,xtol=1e-15,rtol=1e-14)
    ss=s0-xx
    dt=math.log((ss-sb)/(sc-sb))/(p.c0*theta)
    t1=0.
    if times:
        scale=i0/(k-rho/s0)
        zmax=math.log1p(xx/scale)
        def t_integrand(z):
            x=scale*math.expm1(z)
            return scale*math.exp(z)/(p.c0*A*(s0-x)*ix(x))
        t1=quad(t_integrand,0.,zmax,epsabs=2e-10,epsrel=2e-11,limit=150)[0]
    # 退出后的常规轨道在下降支求 I=1，使用 log(s/sc) 保持极限精度。
    def tail_i(s):return theta+k*(sc-s)+rho*math.log(s/sc)
    se=brentq(lambda s:tail_i(s)-1/p.N,sc*1e-8,sc*(1-1e-14),xtol=1e-15,rtol=1e-14)
    tail=quad(lambda s:1/(p.c0*A*s*tail_i(s)),se,sc,epsabs=2e-9,epsrel=2e-10,limit=150)[0] if times else 0.
    cum_pre=(s0-ss)*p.beta/A
    # 正确恒等式：S差=(1-beta)/beta*Cq + Cc+Cq；Cc=gamma*theta*dt。
    cc_plat=p.gamma*theta*dt
    cq_plat=p.beta*((ss-sc)-cc_plat)
    cum_platform=cc_plat+cq_plat
    cum_tail=(sc-se)*p.beta/A
    Itcum=(cum_pre+cum_platform+cum_tail)*p.N
    qm=1-p.gamma/(p.beta*p.c0*ss)
    qi=1-1/(2*(1-p.beta)) if p.beta<1 else None
    inf=bool(sc<2*sb<ss)
    ti=t1+math.log((ss-sb)/sb)/(p.c0*theta) if inf else None
    linear=square=0.
    if costs:
        rel=lambda s:(1-p.gamma/(p.beta*p.c0*s)-p.q0)/(1-p.q0)
        linear=quad(lambda s:rel(s)/(s-sb),sc,ss,epsabs=1e-12,epsrel=1e-11)[0]/(p.c0*theta)
        square=2*quad(lambda s:rel(s)**2/(s-sb),sc,ss,epsabs=1e-12,epsrel=1e-11)[0]/(p.c0*theta)
    return {'status':'ok','N':p.N,'I0':I0,'eta':eta,'eta_fraction':theta,'c0':p.c0,
            'S_star':ss*p.N,'Sc':sc*p.N,'Sbar':sb*p.N,'s_star':ss,'s_c':sc,'s_bar':sb,
            't1':t1,'t2':t1+dt,'control_duration':dt,'Delta_t':dt,'delta_t':dt,
            'clear_time':t1+dt+tail,'t_end':t1+dt+tail,'post_control_tail':tail,
            'q_start':qm,'q_max_control':qm,'q_max':qm,'q_inf':qi,'has_internal_inflection':inf,
            't_inf':ti,'lambda_inf':((ti-t1)/dt if inf else None),
            'J_c':0.,'J_q':linear,'J':square,'cost_J':square,'peak_I':eta,
            'cum_total_infections':Itcum,'Itcum':Itcum,'background_peak_I':ip*p.N,
            'q_end':p.q0,'control_start':t1,'control_end':t1+dt,
            'Delta_t_formula':dt,'t2_formula':t1+dt,'t2_numeric':t1+dt,
            'Delta_t_numeric':dt,'q_min_control':p.q0,'S_end':se*p.N,'s_end':se,
            'cum_community_infections':(p.beta*(1-p.q0)/A*(xx+sc-se)+cc_plat)*p.N,
            'cum_quarantined_infections':(p.beta*p.q0/A*(xx+sc-se)+cq_plat)*p.N}


def frame_from_stages(stages,p,I0,name,cfun,qfun,*,points=2400):
    frames=[]
    total=sum(b-a for a,b,sol in stages)
    for j,(a,b,sol) in enumerate(stages):
        n=max(350,int(points*(b-a)/total))
        tt=np.unique(np.r_[np.linspace(a,b,n), np.arange(math.ceil(a),math.floor(b)+1)])
        if j:tt=tt[tt>a+1e-12]
        y=sol.sol(tt)
        c=np.asarray(cfun(tt))+np.zeros_like(tt);q=np.asarray(qfun(tt))+np.zeros_like(tt)
        df=pd.DataFrame({'strategy':name,'t':tt,'S':y[0]*p.N,'I':y[1]*p.N,'Sq':y[2]*p.N,
                         'Iq':y[3]*p.N,'R':y[4]*p.N,'Cc':y[5]*p.N,'Cq':y[6]*p.N,
                         'J_c':y[7],'J_q':y[8],'J':y[9],'c':c,'q':q,
                         'Rt':p.beta*c*(1-q)*y[0]/p.gamma})
        frames.append(df)
    return pd.concat(frames,ignore_index=True)


def time_strategy(p,I0,name='TDINN控制',tight=False):
    td=name in ('TDINN','TDINN控制')
    cfun=(lambda t:controls(t)[0]) if td else (lambda t:p.c0+np.asarray(t)*0)
    qfun=(lambda t:controls(t)[1]) if td else (lambda t:p.q0+np.asarray(t)*0)
    def clear(t,y):return y[1]-1/p.N
    clear.direction=-1;clear.terminal=True
    sol=integrate(p,I0,cfun,qfun,600.,event=clear,tight=tight)
    if not sol.t_events[0].size:raise RuntimeError('未找到下降清零事件 '+name)
    end=float(sol.t_events[0][0]);ye=sol.y_events[0][0]
    peak=minimize_scalar(lambda t:-float(sol.sol(t)[1]),bounds=(0,end),method='bounded',options={'xatol':1e-10})
    summary={'strategy':name,'peak_I':-float(peak.fun)*p.N,'peak_time':float(peak.x),
             'clear_time':end,'cum_community_infections':ye[5]*p.N,'cum_quarantined_infections':ye[6]*p.N,
             'cum_total_infections':(ye[5]+ye[6])*p.N,'final_I':ye[1]*p.N,'final_S':ye[0]*p.N,
             'J_c':ye[7],'J_q':ye[8],'J':ye[9], 'control_start':0.,'control_end':end if td else 0.,
             'control_duration':end if td else 0., 'mass_residual':float(np.max(np.abs(sol.y[:5].sum(axis=0)-1))*p.N),
             'post_restore_Re':p.beta*p.c0*(1-p.q0)*ye[0]/p.gamma}
    df=frame_from_stages([(0,end,sol)],p,I0,name,cfun,qfun)
    return df,summary


def threshold_strategy(p,I0,eta,name='情景一阈值控制',tight=False):
    d=structural(p,I0,eta)
    if d['status']!='ok':raise ValueError('未触发阈值')
    c=lambda t:p.c0+np.asarray(t)*0
    q0=lambda t:p.q0+np.asarray(t)*0
    pre=integrate(p,I0,c,q0,d['t1'],tight=tight)
    def q(t):
        t=np.asarray(t)
        ss=d['s_bar']+(d['s_star']-d['s_bar'])*np.exp(-p.c0*eta/p.N*(t-d['t1']))
        return 1-p.gamma/(p.beta*p.c0*ss)
    middle=integrate(p,I0,c,q,d['t2'],start=d['t1'],y0=pre.y[:,-1],tight=tight)
    def clear(t,y):return y[1]-1/p.N
    clear.direction=-1;clear.terminal=True
    end_guess=d['clear_time']+max(10.,.03*d['post_control_tail'])
    tail=integrate(p,I0,c,q0,end_guess,start=d['t2'],y0=middle.y[:,-1],event=clear,tight=tight)
    if not tail.t_events[0].size:raise RuntimeError('开环核对未找到清零事件')
    end=float(tail.t_events[0][0]);ye=tail.y_events[0][0]
    qfull=lambda t:np.where((np.asarray(t)>=d['t1'])&(np.asarray(t)<=d['t2']),q(t),p.q0)
    df=frame_from_stages([(0,d['t1'],pre),(d['t1'],d['t2'],middle),(d['t2'],end,tail)],p,I0,name,c,qfull)
    d.update(strategy=name,cum_community_infections=ye[5]*p.N,cum_quarantined_infections=ye[6]*p.N,
             ode_cumulative_total=(ye[5]+ye[6])*p.N,ode_cost=ye[9],ode_clear_time=end,
             plateau_max_error=float(np.max(abs(middle.y[1]*p.N-eta))),
             mass_residual=float(max(np.max(abs(s.y[:5].sum(axis=0)-1))*p.N for s in [pre,middle,tail])),
             analytic_ode_cumulative_error=float(abs((ye[5]+ye[6])*p.N-d['Itcum'])),
             analytic_ode_time_error=float(abs(end-d['clear_time'])))
    return df,d


def render_native_figures(output_dir: Path, root: Path, *, eta_frame=None,
                          heat_frame=None, tds=None, xcc=None, tla=None):
    """原函数重绘图11/12；局部隔离 rc，允许复用本轮新算出的 CSV。

    Matplotlib 原 rc 字典没有列出所有刻度颜色。若上一阶段设置过灰色刻度，
    原上下文会继承这些设置；先在局部恢复默认项，再让原论文上下文设置字体、
    配色、线型和尺寸。退出后恢复调用方状态，不改变其他图的 rc 设置。
    """
    import matplotlib as mpl
    xcc=xcc or source_module(root,'xian_control_comparison/xian_control_comparison.py','repro_original_xcc_figures')
    tla=tla or source_module(root,'xian_control_comparison/threshold_landscape_analysis/threshold_landscape_analysis.py','repro_original_tla_figures')
    if eta_frame is None:eta_frame=pd.read_csv(output_dir/'xian/eta_scan.csv',float_precision='round_trip')
    if heat_frame is None:heat_frame=pd.read_csv(output_dir/'xian/heatmap.csv',float_precision='round_trip')
    if tds is None:
        ref=json.loads((output_dir/'xian/reference.json').read_text(encoding='utf-8'))
        tds=next(r for r in ref['strategies'] if r['strategy']=='TDINN控制')
    figdir=output_dir/'workspace/latex/figures';figdir.mkdir(parents=True,exist_ok=True)
    xcc.OUT_DIR=figdir;tla.HEATMAP_DIR=figdir
    eta_plot=eta_frame.assign(flat_J=lambda d:d.J,
        flat_cum_total=lambda d:d.cum_total_infections,flat_control_duration=lambda d:d.control_duration,
        flat_clear_time=lambda d:d.clear_time,flat_cleared=1.)
    etas=np.sort(heat_frame.eta.unique());c0s=np.sort(heat_frame.c0.unique())
    metric_values={k:heat_frame.pivot(index='c0',columns='eta',values=k).reindex(index=c0s,columns=etas).to_numpy()
                   for k in ['control_duration','clear_time','cum_total_infections','J']}
    # 不切换绘图后端；原函数内部仍使用其认可的 PAPER_RC_PARAMS。
    rc={k:v for k,v in mpl.rcParamsDefault.items() if k!='backend'}
    rc.update({'text.color':'black','axes.labelcolor':'black','xtick.color':'black','ytick.color':'black',
               'xtick.labelcolor':'black','ytick.labelcolor':'black'})
    with mpl.rc_context(rc=rc):
        xcc.plot_eta_sensitivity(eta_plot,tds)
        tla.plot_combined_heatmaps(etas,c0s,metric_values)
    return [figdir/'xian_eta_sensitivity.pdf',figdir/'xian_heatmaps.pdf']


def run_xian(output_dir: Path, root: Path) -> dict:
    out=output_dir/'xian';out.mkdir(parents=True,exist_ok=True)
    xcc=source_module(root,'xian_control_comparison/xian_control_comparison.py','repro_original_xcc')
    observed=xcc.load_observed_data()
    save_csv(observed,out/'observed.csv')
    p=Params(); fit=fit_initial(observed,p);dump(out/'fit.json',fit)
    I0=fit['I0'];print('XIAN_FIT',I0,fit['objective'],flush=True)
    td,tds=time_strategy(p,I0); routine,routs=time_strategy(p,I0,'常规控制')
    flat,flats=threshold_strategy(p,I0,.002*p.N)
    ref={'parameters':asdict(p),'fit':fit,'I0_abs':I0,'I_peak_T':tds['peak_I'],'J_T':tds['J'],
         'Itcum_T':tds['cum_total_infections'],'t_end_T':tds['clear_time'],
         'Ic_cum_T':tds['cum_community_infections'],'Iq_cum_T':tds['cum_quarantined_infections'],
         'strategies':[tds,flats,routs],'implementation':'normalized-DOP853-unified-v1',
         'numerical_settings':{'rtol':2e-11,'early_infection_atol':1e-21,'max_step':.4},
         'data_sha256':hashlib.sha256((root/'真实数据/Xianguankong.xlsx').read_bytes()).hexdigest()}
    dump(out/'reference.json',ref)
    series=pd.concat([td,flat,routine],ignore_index=True);save_csv(series,out/'timeseries.csv')
    summary=pd.DataFrame([tds,flats,routs]);save_csv(summary,out/'summary.csv')
    # 在旧代码上实算旧拟合与旧事件轨迹，分开报告数值算法差异和重新拟合影响。
    oldfit=xcc.fit_initial_conditions(observed)
    old40=xcc.solve_with_initials(oldfit.S0,oldfit.I0,40.,xcc.c_real,xcc.q_real,t_eval=np.array([0.,40.]))
    oldevent=xcc.solve_time_control('TDINN',oldfit,xcc.c_real,xcc.q_real)
    oldevent40=float(np.interp(40.,oldevent.t,oldevent.Cc+oldevent.Cq))
    unified_old=integrate(p,oldfit.I0,lambda t:controls(t)[0],lambda t:controls(t)[1],40.)
    check,checks=time_strategy(p,I0,tight=True)
    _,routine_checks=time_strategy(p,I0,'常规控制',tight=True)
    _,flat_checks=threshold_strategy(p,I0,.002*p.N,tight=True)
    def window_metrics(i0):
        sol=integrate(p,i0,lambda t:controls(t)[0],lambda t:controls(t)[1],40.)
        daily=sol.sol(np.arange(41.))*p.N
        return {'I0':i0,'cumulative_40':float(daily[5:7,-1].sum()),
                'community_daily_peak':float(np.diff(daily[5]).max()),
                'quarantine_daily_peak':float(np.diff(daily[6]).max())}
    window=[{'type':'observed','I0':None,'cumulative_40':float(observed.community_cum.iloc[-1]+observed.quarantine_cum.iloc[-1]),
             'community_daily_peak':float(observed.community_new.max()),'quarantine_daily_peak':float(observed.quarantine_new.max())},
            {'type':'fitted',**window_metrics(I0)},{'type':'fixed_I0_1',**window_metrics(1.)}]
    save_csv(pd.DataFrame(window),out/'S2_window.csv')
    def first_event(t,y):return y[1]-1.
    first_event.direction=1;first_event.terminal=True
    early,first=xcc.solve_event_stage(xcc.c_real,xcc.q_real,0.,np.array([oldfit.S0,oldfit.I0,0.,0.,0.,0.]),first_event,'diagnostic_first')
    old40full=xcc.solve_with_initials(oldfit.S0,oldfit.I0,40.,xcc.c_real,xcc.q_real,t_eval=None,dense_output=True)
    early_t=np.linspace(0.,first,101)
    early_true=unified_old.sol(early_t)[1]*p.N
    early_event=early.sol(early_t)[1]
    early_fit=old40full.sol(early_t)[1]
    early_error={'legacy_event_first_crossing_time':first,'unified_I_at_legacy_first_crossing':float(unified_old.sol(first)[1]*p.N),
        'event_max_relative_I_error':float(np.max(abs(early_event/early_true-1))),
        'fit_solver_max_relative_I_error':float(np.max(abs(early_fit/early_true-1))),
        'legacy_event_initial_atol_over_I0':1e-4/oldfit.I0,'legacy_fit_initial_atol_over_I0':1e-5/oldfit.I0,
        'event_minus_fit_40_cumulative':oldevent40-float(old40.y[4:6,-1].sum())}
    save_csv(pd.DataFrame({'t':early_t,'I_unified':early_true,'I_legacy_event':early_event,'I_legacy_fit':early_fit}),out/'early_tolerance.csv')
    difference={'legacy_fit':asdict(oldfit),'legacy_fit_40_cumulative':float(old40.y[4:6,-1].sum()),
                'legacy_event_40_cumulative':oldevent40,'unified_at_legacy_I0_40_cumulative':float(unified_old.y[5:7,-1].sum()*p.N),
                'unified_refit_40_cumulative':window[1]['cumulative_40'],'unified_S2_rows':window,'early_tolerance':early_error,
                'explanation':'旧拟合使用rtol=1e-7/atol=1e-5；旧事件使用1e-8/1e-4。相同初值并不能保证相同数值轨道。新计算统一使用归一化方程、DOP853求解器和分量容差；TDINN控制连续积分，情景一阈值控制按启动前、平台期、解除后三阶段积分。',
                'reference_tolerance_differences':{k:abs(float(tds[k])-float(checks[k])) for k in ['peak_I','J','clear_time','cum_total_infections']},
                'routine_tolerance_differences':{k:abs(float(routs[k])-float(routine_checks[k])) for k in ['peak_I','J','clear_time','cum_total_infections']},
                'threshold_tolerance_differences':{k:abs(float(flats[k])-float(flat_checks[k])) for k in ['ode_cost','ode_clear_time','ode_cumulative_total']}}
    dump(out/'S2_difference.json',difference)
    eta_fracs=[.0001,.0002,.0005,.001,.0015,.002,.003,.004,.005,.0075,.01]
    eta_rows=[structural(p,I0,f*p.N) for f in eta_fracs]
    save_csv(pd.DataFrame(eta_rows),out/'eta_scan.csv')
    tla=source_module(root,'xian_control_comparison/threshold_landscape_analysis/threshold_landscape_analysis.py','repro_original_tla')
    etas=np.unique(np.r_[np.geomspace(50.,40000.,90),tla.REPRESENTATIVE_ETAS])
    c0s=np.unique(np.r_[np.linspace(6.,13.,45),tla.REPRESENTATIVE_C0_VALUES])
    heat=[]
    for j,c0 in enumerate(c0s):
        for eta in etas:heat.append(structural(replace(p,c0=float(c0)),I0,float(eta)))
        if j%10==0:print('XIAN_HEATMAP',j,len(c0s),flush=True)
    save_csv(pd.DataFrame(heat),out/'heatmap.csv')
    compat=output_dir/'workspace/archive_unused/generated_snapshots/xian_control_comparison_main'
    save_csv(series,compat/'xian_control_comparison_timeseries.csv')
    save_csv(observed,compat/'xian_observed_data_processed.csv')
    save_csv(summary,compat/'xian_control_comparison_summary.csv')
    save_csv(pd.DataFrame(eta_rows),compat/'xian_eta_sensitivity.csv')
    save_csv(pd.DataFrame({'metric':list(flats),'value':list(flats.values())}),compat/'xian_flat_control_details.csv')
    save_csv(pd.DataFrame(heat),output_dir/'workspace/xian_control_comparison/threshold_landscape_analysis/eta_c0_heatmap/eta_c0_heatmap_summary.csv')
    # 原绘图函数只绑定新数值和新输出目录，不修改原代码或历史结果。
    render_native_figures(output_dir,root,eta_frame=pd.DataFrame(eta_rows),
                          heat_frame=pd.DataFrame(heat),tds=tds,xcc=xcc,tla=tla)
    passed=(flats['plateau_max_error']<1e-5 and flats['mass_residual']<1e-5
            and flats['analytic_ode_cumulative_error']<1e-4
            and max(difference['reference_tolerance_differences'].values())<1e-4
            and max(difference['routine_tolerance_differences'].values())<1e-4
            and max(difference['threshold_tolerance_differences'].values())<1e-4)
    report={'passed':bool(passed),'fit':fit,'heatmap_shape':[len(c0s),len(etas)],'rows':len(heat),
            'threshold_diagnostics':{k:flats[k] for k in ['plateau_max_error','mass_residual','analytic_ode_cumulative_error','analytic_ode_time_error']},
            'artifacts':[str(f.relative_to(output_dir)) for f in out.iterdir() if f.is_file()]}
    dump(out/'diagnostics.json',report)
    return report


def write_anchor_updates(output_dir: Path, root: Path):
    """历史对照可缺失；新值仅取本轮结果，不以旧值作为科学通过判据。"""
    records=[];sources={};history=[]
    def clean(v):
        if isinstance(v,(float,np.floating)) and not np.isfinite(v):return None
        return v.item() if hasattr(v,'item') else v
    def record(group,anchor,old,new,source,old_source=None):
        if isinstance(new,(bool,int,float,np.number)) or new is None:
            before=clean(old)
            records.append({'group':group,'anchor':anchor,'old':before,'new':clean(new),'source':source,
                            'old_source':old_source,'old_status':'available' if before is not None else 'unknown'})
    def old_input(rel,parser):
        # 实际读取的每份对照都记录哈希；缺失/不可解析只降低历史对照覆盖率。
        path=root/rel
        try:
            raw=path.read_bytes()
        except OSError as exc:
            history.append({'file':rel,'status':'unavailable','reason':type(exc).__name__,
                            'sha256':None,'role':'optional_historical_comparison_only'})
            return None
        sources[rel]=hashlib.sha256(raw).hexdigest()
        try:
            value=parser(raw)
        except (ValueError,UnicodeError,SyntaxError) as exc:
            history.append({'file':rel,'status':'unparseable','reason':type(exc).__name__,
                            'sha256':sources[rel],'role':'optional_historical_comparison_only'})
            return None
        history.append({'file':rel,'status':'available','sha256':sources[rel],
                        'role':'optional_historical_comparison_only'})
        return value
    def old_csv(rel):
        value=old_input(rel,lambda raw:pd.read_csv(io.BytesIO(raw)))
        return value if value is not None else pd.DataFrame()
    def old_json(rel):
        value=old_input(rel,lambda raw:json.loads(raw.decode('utf-8-sig')))
        return value if isinstance(value,dict) else {}
    def old_row(frame,key,value):
        if key not in frame.columns:return {}
        matches=frame.loc[frame[key]==value]
        return matches.iloc[0].to_dict() if len(matches) else {}
    def item(rows,index):
        return rows[index] if index<len(rows) and isinstance(rows[index],dict) else {}
    def new_json(rel):return json.loads((output_dir/rel).read_text(encoding='utf-8'))
    def new_csv(rel):return pd.read_csv(output_dir/rel)
    xr=new_json('xian/reference.json');xd=new_json('xian/S2_difference.json')
    for k,v in xr['fit'].items():record('xian_fit',k,xd['legacy_fit'].get(k),v,'xian/fit.json','xian/S2_difference.json:legacy_fit')
    oldpath='archive_unused/generated_snapshots/xian_control_comparison_main/xian_control_comparison_summary.csv'
    old=old_csv(oldpath)
    new=new_csv('xian/summary.csv')
    for row in new.to_dict('records'):
        before=old_row(old,'strategy',row['strategy'])
        for k,v in row.items():
            if pd.notna(v):record('xian_strategies',row['strategy']+'.'+k,before.get(k),v,'xian/summary.csv',oldpath)
    oldpath='archive_unused/generated_snapshots/xian_control_comparison_main/xian_eta_sensitivity.csv'
    old=old_csv(oldpath)
    new=new_csv('xian/eta_scan.csv')
    aliases={'Delta_t':'flat_control_duration','t_end':'flat_clear_time','Itcum':'flat_cum_total','J':'flat_J',
             'J_q':'flat_J_q','t1':'t1','t2':'t2_formula','q_max':'q_max_window','q_start':'q_start'}
    for j,row in enumerate(new.to_dict('records')):
        before=old.iloc[j].to_dict() if j<len(old) else {}
        for k,oldkey in aliases.items():record('xian_eta',f'row{j}.{k}',before.get(oldkey),row[k],'xian/eta_scan.csv',oldpath)
    metapath='latex/revision_v4/data/dominance_metadata.json'
    oldmeta=old_json(metapath)
    meta=new_json('population/metadata.json');critical=new_json('population/critical.json')
    oldcrit={'N_floor':oldmeta.get('N_floor')}
    for j,key in enumerate(['theta_dur150','theta_cost','theta_dur45']):
        values=oldmeta.get('theta',[])
        oldcrit[key]=values[j] if j<len(values) else None
    for j,key in enumerate(['N_star_cum_inf','N_star45','N_star_inf'],1):
        groups=oldmeta.get('cases',[])
        oldcrit[key]=item(groups[j],0).get('N') if j<len(groups) else None
    for k,v in critical.items():record('population_critical',k,oldcrit.get(k),v,'population/critical.json',metapath)
    for group in ['cases','fixed_eta']:
        before=[r for rows in oldmeta.get(group,[]) for r in rows] if group=='cases' else oldmeta.get(group,[])
        after=[r for rows in meta[group] for r in rows] if group=='cases' else meta[group]
        for j,row in enumerate(after):
            for k,v in row.items():record('population_'+group,f'row{j}.{k}',item(before,j).get(k),v,'population/metadata.json',metapath)
    # 原图内嵌的16点只作为对照清单；新弧始终由求根重新生成。
    def embedded_arrays(raw):
        arrays={}
        for node in ast.parse(raw.decode('utf-8-sig')).body:
            if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ['cum_eta','cum_N','clr_N']:
                if isinstance(node.value,ast.Call):arrays[node.targets[0].id]=ast.literal_eval(node.value.args[0])
        return arrays
    arcpath='xian_dom/dom_pretty.py'
    oldarrays=old_input(arcpath,embedded_arrays) or {}
    arcs=new_csv('population/arcs.csv')
    for j,row in enumerate(arcs.to_dict('records')):
        for key,before in [('eta','cum_eta'),('N_cum','cum_N'),('N_clear','clr_N')]:
            values=oldarrays.get(before,[])
            record('population_arcs',f'row{j}.{key}',values[j] if j<len(values) else None,row[key],'population/arcs.csv',arcpath)
    oldpath='archive_unused/generated_snapshots/c0_sensitivity_outputs/c0_representative_summary.csv'
    old=old_csv(oldpath)
    new=new_csv('c0/representative_summary.csv')
    for row in new.to_dict('records'):
        before=old_row(old,'role',row['role'])
        for k,v in row.items():
            if k!='role':record('c0_cases',row['role']+'.'+k,before.get(k),v,'c0/representative_summary.csv',oldpath)
    parpath='archive_unused/generated_snapshots/c0_sensitivity_outputs/experiment_parameters.json'
    oldpars=old_json(parpath)
    pars=new_json('c0/parameters.json')
    for k,v in pars['derived'].items():record('c0_boundaries',k,oldpars.get('derived',{}).get(k),v,'c0/parameters.json',parpath)
    # S2旧值来自冻结补表/表注，不用硬编码数字冒充已读取的历史证据。
    sipath='joint_control/threshold_control_reproducible_release_20261002/latex/flatten_curve_supplement_cn.tex'
    sitext=old_input(sipath,lambda raw:raw.decode('utf-8-sig')) or ''
    s2old={}
    for kind,prefix in [('observed','观测数据'),('fitted','最小二乘拟合'),('fixed_I0_1','固定 $I_0=1$')]:
        line=next((line for line in sitext.splitlines() if line.startswith(prefix+' &')),'')
        cells=line.removesuffix(r'\\').split('&')
        if len(cells)==5:
            try:s2old[kind]=[float(value.strip()) for value in cells[2:]]
            except ValueError:pass
    oldcum=re.search(r'总累计为\s*\$([-+\d.eE]+)\$',sitext)
    if oldcum and 'fitted' in s2old:s2old['fitted'][0]=float(oldcum[1])
    for row in new_csv('xian/S2_window.csv').to_dict('records'):
        previous=s2old.get(row['type'],[None]*3)
        for j,key in enumerate(['cumulative_40','community_daily_peak','quarantine_daily_peak']):
            record('S2',row['type']+'.'+key,previous[j],row[key],'xian/S2_window.csv',sipath)
    payload={'schema':'paper-anchor-updates-v1','records':records,'old_sources_sha256':sources,
             'historical_inputs':history,'unknown_old_value_count':sum(r['old_status']=='unknown' for r in records),
             'scientific_results_depend_on_historical_inputs':False,
             'full_precision_sources':{'xian':'xian/reference.json','S2':'xian/S2_window.csv',
                'population_critical':'population/critical.json','population_beta':'population/beta_scan.csv',
                'population_beta_summary':'population/beta_summary.json','population_arcs':'population/arcs.csv',
                'population_cases':'population/representative_summary.csv','population_extra':'population/supplementary_anchors.json',
                'scale_absolute':'population/fixed_absolute_scale.csv','scale_normalized':'population/scale_invariance.csv',
                'normalized_clear_arc':'population/clear_arc_fixed_normalized_diagnostic.csv',
                'c0_cases':'c0/representative_summary.csv','c0_parameters':'c0/parameters.json','c0_extrema':'c0/extrema.json'},
             'xian_reference':xr,'population_critical':critical,'population_beta_summary':new_json('population/beta_summary.json'),
             'population_supplementary':new_json('population/supplementary_anchors.json'),
             'population_cases':new_csv('population/representative_summary.csv').where(pd.notnull(new_csv('population/representative_summary.csv')),None).to_dict('records'),
             'c0_parameters':pars,'c0_extrema':new_json('c0/extrema.json'),
             'S2':xd['unified_S2_rows']}
    dump(output_dir/'paper_anchor_updates.json',payload)
    return payload
