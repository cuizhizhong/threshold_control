"""显式启动六类配点优化；保留每次尝试及逐级加密结果。"""
import argparse
import json
import pathlib
import sys
sys.dont_write_bytecode=True
from collocation import Problem,seeds,dump,RESULTS


def run(case,objective):
    previous=[]
    history=[]
    for n in [20,40,80,160]:
        problem=Problem(case,objective,n)
        current=[]
        if n==20:
            for label,values in seeds(case,n):
                current.append(problem.solve(problem.initial(values),label))
        else:
            for rank,item in enumerate(previous[:3]):
                current.append(problem.solve(problem.initial(item['lambda_values'],item['duration']),
                    f"from{item['n']}_{rank}_{item['seed_label']}"))
        valid=[r for r in current if r.get('solver_success') and r.get('constraint_residual',1)>-1
               and r.get('constraint_residual',1)<1e-8]
        valid.sort(key=lambda r:r['scaled_objective'])
        history.append({'n':n,'best':valid[0] if valid else None,'attempt_count':len(current)})
        if not valid:
            dump(RESULTS/'collocation'/f'{case}_{objective}_progress.json',history)
            raise RuntimeError(f'{case}/{objective}/n{n}: 无可用候选')
        previous=valid
        dump(RESULTS/'collocation'/f'{case}_{objective}_progress.json',history)
    dump(RESULTS/'collocation'/f'{case}_{objective}_best.json',previous[0])


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--case',choices=['base','xian'],required=True)
    parser.add_argument('--objectives',nargs='+',choices=['time','infections','cost'],default=['time','infections','cost'])
    args=parser.parse_args()
    for objective in args.objectives:
        run(args.case,objective)
