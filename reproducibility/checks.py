"""对本次原始计算输出独立核查物理恒等式、事件和跨语言数值。"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
from bootstrap import dump
from xian import Params, structural


def trajectory(frame: pd.DataFrame, beta: float, gamma: float,
               N: float, c0: float, q0: float, *, eta=None, t1=None, t2=None) -> dict:
    states=frame[['S','I','Sq','Iq','R']].to_numpy(float)
    cc=frame.Cc.to_numpy(float); cq=frame.Cq.to_numpy(float)
    mass=float(np.max(abs(states.sum(axis=1)-N)))
    removal=float(np.max(abs(frame.S.iloc[0]-frame.S-cc-cq/beta)))
    sq=float(np.max(abs(frame.Sq-(1-beta)*cq/beta)))
    last=frame.iloc[-1]
    slope=float((beta*last.c*(1-last.q)*last.S/N-gamma)*last.I)
    time_increasing=bool(np.all(np.diff(frame.t)>0))
    bounds=bool(frame.c.min()>=-1e-9 and frame.c.max()<=c0+1e-8
                and frame.q.min()>=q0-1e-9 and frame.q.max()<=1+1e-9)
    platform=None
    if eta is not None:
        mid=frame[(frame.t>=t1)&(frame.t<=t2)]
        if mid.empty:raise RuntimeError('缺少平台采样，不能核查')
        platform=float(abs(mid.I-eta).max())
    values={'rows':len(frame),'mass_error':mass,'susceptible_removal_identity_error':removal,
            'quarantined_susceptible_identity_error':sq,'minimum_state':float(states.min()),
            'time_strictly_increasing':time_increasing,'controls_in_bounds':bounds,
            'clear_event_I_error':float(abs(last.I-1)), 'clear_event_direction_derivative':slope,
            'I_above_one_before_clear':bool(frame.I.max()>1),
            'cumulative_nondecreasing':bool(np.all(np.diff(cc)>=-1e-7) and np.all(np.diff(cq)>=-1e-7)),
            'platform_max_error':platform}
    values['passed']=bool(mass<1e-5 and removal<1e-4 and sq<1e-4
                          and states.min()>=-1e-7 and time_increasing and bounds
                          and abs(last.I-1)<1e-5 and slope<0 and frame.I.max()>1
                          and values['cumulative_nondecreasing']
                          and (platform is None or platform<1e-5))
    return values


def run(output_dir: Path, root: Path) -> dict:
    ref=json.loads((output_dir/'xian/reference.json').read_text(encoding='utf-8'))
    p=Params(**ref['parameters']); checks=[]
    xian=pd.read_csv(output_dir/'xian/timeseries.csv')
    for label,frame in xian.groupby('strategy',sort=False):
        threshold='阈值' in label
        d=next((r for r in ref['strategies'] if '阈值' in r['strategy']),None)
        item=trajectory(frame,p.beta,p.gamma,p.N,p.c0,p.q0,
                        **({'eta':d['eta'],'t1':d['t1'],'t2':d['t2']} if threshold else {}))
        checks.append({'source':'xian/timeseries.csv','group':label,**item})
    metadata=json.loads((output_dir/'population/metadata.json').read_text(encoding='utf-8'))
    cases=[x for group in metadata['cases'] for x in group]+metadata['fixed_eta']
    for case in cases:
        for suffix in ('','_routine'):
            path=output_dir/'population'/(case['stem']+suffix+'.csv')
            frame=pd.read_csv(path)
            item=trajectory(frame,p.beta,p.gamma,case['N'],p.c0,p.q0,
                  **({'eta':case['eta'],'t1':case['t1'],'t2':case['t2']} if not suffix else {}))
            checks.append({'source':str(path.relative_to(output_dir)),**item})
    c0=pd.read_csv(output_dir/'c0/timeseries.csv')
    summary=pd.read_csv(output_dir/'c0/representative_summary.csv')
    for role,frame in c0.groupby('role',sort=False):
        case=summary.loc[summary.role==role].iloc[0]
        item=trajectory(frame,p.beta,p.gamma,20000.,case.c0,p.q0,
                        eta=40.,t1=case.t1,t2=case.t2)
        checks.append({'source':'c0/timeseries.csv','group':role,**item})
    # MATLAB 原始 Lambert W /积分实现 vs 独立 Python 首次积分和求根实现。
    landscape_path=output_dir/'workspace/scenario1_threshold_landscape/current_run/output_csv/landscape_summary.csv'
    landscape=pd.read_csv(landscape_path)
    valid=landscape[landscape.valid.astype(bool)]
    selected=valid.iloc[np.unique(np.linspace(0,len(valid)-1,96,dtype=int))]
    cross=[]
    keys={'t1':'t1','Delta_t':'Delta_t','t_end':'t_end','q_max':'q_max','J':'J','I_t_cum':'Itcum'}
    for _,r in selected.iterrows():
        param=Params(N=r.N,beta=r.beta,gamma=r.gamma,delta_q=r.gamma,c0=r.c0,q0=r.q0)
        z=structural(param,r.I0,r.eta)
        if z['status']!='ok':raise RuntimeError('跨语言样本有效性不同')
        errors={k:abs(float(r[k])-z[v]) for k,v in keys.items()}
        cross.append({'c0':float(r.c0),'eta':float(r.eta),'errors':errors,
                      'passed':bool(max(errors[k] for k in keys if k!='q_max')<1e-5 and errors['q_max']<1e-10)})
    report={'passed':all(r['passed'] for r in checks+cross),'full_trajectory_count':len(checks),
            'trajectory_checks':checks,'matlab_python_independent_samples':cross,
            'scope':'逐轨迹仓室/计数恒等式和事件方向；96点跨语言误差。不替代数学证明或临床验证。'}
    dump(output_dir/'validation/independent_checks.json',report)
    if not report['passed']:raise RuntimeError('独立科学检查失败，见 independent_checks.json')
    return report


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();run(args.output,Path(__file__).resolve().parents[1])
