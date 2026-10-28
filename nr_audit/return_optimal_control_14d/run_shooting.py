"""独立shooting互证任务，必须显式--run。"""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from shooting import solve, starting_state, parameters

HERE=Path(__file__).resolve().parent


def load_refs(case):
    out={}
    for name in ['q_only','c_only','opt_noreturn']:
        out[name]=json.loads((HERE/'results'/'references'/f'{case}_{name}.json').read_text(encoding='utf8'))
    return out


def seeds(case,n):
    refs=load_refs(case)
    Tq=refs['q_only']['duration']; Tc=refs['c_only']['duration']
    tau=(np.arange(n)+.5)/n
    rng=np.random.default_rng(20261027)
    migrated=np.interp(tau,np.linspace(0,1,len(refs['opt_noreturn']['lambda_values'])),
                       refs['opt_noreturn']['lambda_values'])
    return [
        ('q_only',Tq,np.ones(n)),('c_only',Tc,np.zeros(n)),
        ('migrated',refs['opt_noreturn']['duration'],migrated),
        ('mixed',.5*(Tq+Tc),np.full(n,.5)),
        ('q_then_c',.5*(Tq+Tc),(tau<.5).astype(float)),
        ('c_then_q',.5*(Tq+Tc),(tau>=.5).astype(float)),
        ('smooth_random1',.5*(Tq+Tc),np.clip(.5+.25*np.sin(2*np.pi*tau)+.08*rng.normal(size=n),0,1)),
        ('smooth_random2',.5*(Tq+Tc),np.clip(.5+.25*np.cos(2*np.pi*tau)+.08*rng.normal(size=n),0,1))]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--case',choices=['base','xian','both'],default='both')
    parser.add_argument('--segments',type=int,default=20)
    parser.add_argument('--maxiter',type=int,default=200)
    parser.add_argument('--starts',type=int,default=8)
    parser.add_argument('--objective',choices=['all','time','cost','infections'],default='all')
    args=parser.parse_args()
    if not args.run:
        print('未指定--run，不启动优化。'); return
    folder=HERE/'results'/'shooting_attempts'; folder.mkdir(parents=True,exist_ok=True)
    summary=[]
    for case in (['base','xian'] if args.case=='both' else [args.case]):
        start=starting_state(case)
        for obj in (['time','infections','cost'] if args.objective=='all' else [args.objective]):
            for label,T,controls in seeds(case,args.segments)[:args.starts]:
                try:
                    result=solve(case,obj,T,controls,n_segments=args.segments,start_state=start,
                                 maxiter=args.maxiter,log_dir=folder,seed_label=label)
                    compact={k:v for k,v in result.items() if k not in ('lambda_values','initial_lambdas')}
                    summary.append(compact)
                    print(json.dumps({k:result[k] for k in ['case','objective','seed_label','duration','J','C_infty_estimate','solver_success','nit','terminal_residual_N','min_inequality','wall_seconds']},ensure_ascii=False),flush=True)
                except Exception as exc:
                    result=dict(case=case,objective=obj,seed_label=label,error=repr(exc),n_segments=args.segments)
                    (folder/f'failure_{case}_{obj}_{label}_{time.time_ns()}.json').write_text(json.dumps(result,indent=2),encoding='utf8')
                    summary.append(result)
                    print(json.dumps(result,ensure_ascii=False),flush=True)
                (HERE/'results'/f'shooting_summary_{args.case}_{args.objective}_n{args.segments}.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf8')


if __name__=='__main__':
    main()
