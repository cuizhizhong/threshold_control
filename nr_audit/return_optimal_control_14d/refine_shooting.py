"""从主配点候选与另一形态初值启动独立shooting互证。"""
import argparse
import json
from pathlib import Path
import numpy as np
from shooting import solve, starting_state

HERE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--segments',type=int,default=80)
    parser.add_argument('--maxiter',type=int,default=300)
    parser.add_argument('--objective',choices=['all','time','cost','infections'],default='all')
    args=parser.parse_args()
    if not args.run:
        print('未指定--run，不启动。'); return
    rows=[]
    for case in ['base','xian']:
        start=starting_state(case)
        for obj in (['time','infections','cost'] if args.objective=='all' else [args.objective]):
            candidate=json.loads((HERE/'results'/'collocation'/f'{case}_{obj}_best.json').read_text(encoding='utf8'))
            alt='c_only' if obj=='time' else 'q_only'
            reference=json.loads((HERE/'results'/'references'/f'{case}_{alt}.json').read_text(encoding='utf8'))
            for label,seed in [('collocation_best',candidate),(alt,reference)]:
                result=solve(case,obj,seed['duration'],seed['lambda_values'],
                             n_segments=args.segments,start_state=start,maxiter=args.maxiter,
                             log_dir=HERE/'results'/'shooting_attempts',
                             seed_label=f'cross_{label}',ftol=3e-12)
                compact={k:v for k,v in result.items() if k not in ('lambda_values','initial_lambdas')}
                rows.append(compact)
                (HERE/'results'/f'shooting_cross_n{args.segments}.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')
                print(json.dumps({k:result[k] for k in ['case','objective','seed_label','duration','J','C_infty_estimate','solver_success','nit','terminal_residual_N','min_inequality','wall_seconds']},ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
