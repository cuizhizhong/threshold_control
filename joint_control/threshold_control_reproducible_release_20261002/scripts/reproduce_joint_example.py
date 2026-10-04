#!/usr/bin/env python3
"""本轮新增的复现入口，不冒充历史计算程序。

计算核心为 numerics/joint_comparison.py（从此前已交付包恢复，字节未改）。
读取明确的输入配置，导出未按论文小数位取整的结果，并从论文的t=0初值
进行三阶段完整ODE核对和轨迹导出。输出不自动写入论文、不重画已有图表。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
from dataclasses import fields
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'numerics'))
try:
    import numpy as np
    import scipy
    from scipy.integrate import solve_ivp
    import joint_comparison as original
except ImportError as exc:
    raise SystemExit('Missing dependency: install requirements-numerics.txt. ' + str(exc))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def write_csv(path: Path, rows: list[dict]) -> None:
    """17 significant digits preserve round-trip binary64 values; not an accuracy claim."""
    if not rows:
        raise ValueError('No output rows.')
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: format(v, '.17g') if isinstance(v, float) else v for k, v in row.items()})


def read_configuration(path: Path) -> tuple[dict, original.Parameters]:
    obj = json.loads(path.read_text(encoding='utf-8'))
    raw = obj['parameters']
    if set(raw) != {x.name for x in fields(original.Parameters)}:
        raise ValueError('Configuration must contain exactly the Parameters fields.')
    if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in raw.values()):
        raise ValueError('All parameters must be finite numbers.')
    p = original.Parameters(**raw)
    if not (0 < p.beta <= 1 and 0 <= p.q0 < 1 and
            min(p.N, p.S0, p.I0, p.gamma, p.delta_q, p.c0, p.wc, p.wq) > 0):
        raise ValueError('Parameter outside the model domain.')
    if abs(p.N - p.S0 - p.I0) > 1e-10:
        raise ValueError('This reproduction assumes Sq0=Iq0=R0=0 and N=S0+I0.')
    if any(float(x) != 0 for x in obj['other_initial_states'].values()):
        raise ValueError('This specific baseline requires zero other initial compartments.')
    if not p.I0 < p.eta < p.routine_I(p.Sc) or p.eta <= 1:
        raise ValueError('An upward interior trigger and eta>1 are required.')
    return obj, p


def full_ode_check(p: original.Parameters, scalar: dict, options: dict) -> tuple[dict, list[dict]]:
    """Full path verification, additional to the legacy control-period-only ODE test.

    The model's closed S,I subsystem allows earlier code to use a synthetic
    Sq,Iq,R distribution at entry. Here we also propagate the real initial state
    through the pre-control stage. Control is the recovered state function, not
    an independent optimal-control solver. Medical occupancy is not modeled.
    """
    rtol = float(options['rtol']); atol = float(options['atol'])
    method = options['method']; samples = int(options['samples_per_phase'])
    if samples < 2 or not (0 < rtol < 1 and 0 < atol < 1):
        raise ValueError('Invalid ODE configuration.')

    def rhs(y: np.ndarray, c: float, q: float, controlled: bool) -> list[float]:
        S, I, Sq, Iq, R, cumulative, J = y
        inf = p.beta * c * S * I / p.N
        to_sq = (1 - p.beta) * c * q * S * I / p.N
        extra = (p.wc * (1-c/p.c0)**2 + p.wq*((q-p.q0)/(1-p.q0))**2) if controlled else 0.0
        return [-inf-to_sq, inf*(1-q)-p.gamma*I, to_sq,
                inf*q-p.delta_q*Iq, p.gamma*I+p.delta_q*Iq, inf, extra]

    def regular(t: float, y: np.ndarray) -> list[float]:
        return rhs(y, p.c0, p.q0, False)

    def trigger(t: float, y: np.ndarray) -> float:
        return float(y[1]-p.eta)
    trigger.direction = 1
    trigger.terminal = True

    pre = solve_ivp(regular, (0, max(2*scalar['t1'], 1.0)),
                    [p.S0, p.I0, 0., 0., 0., 0., 0.],
                    events=trigger, dense_output=True, method=method,
                    rtol=rtol, atol=atol, max_step=max(scalar['t1']/100, 1e-4))
    if not pre.success or len(pre.t_events[0]) != 1:
        raise RuntimeError('Full ODE did not reach the upward trigger.')
    t1 = float(pre.t_events[0][0]); entry = pre.y_events[0][0]
    profiles = {
        'contact_only': lambda S: p.Sc/S,
        'alpha_0.5': lambda S: .5+.5*p.Sc/S,
        'quarantine_only': lambda S: 1.,
        'minimum_cost': lambda S: original.optimal_x(S, p),
    }
    result = {'description': '本轮从t=0真实初始仓室状态积分；控制取自原逐状态候选比较程序。',
              'entry_time_ode': t1, 'entry_state_ode': entry[:5].tolist(),
              'entry_time_abs_error': abs(t1-scalar['t1']),
              'entry_S_abs_error': abs(float(entry[0])-scalar['Sstar']), 'strategies': []}
    traces: list[dict] = []

    for expected in scalar['rows']:
        name = expected['strategy']; profile = profiles[name]
        def controls(S: float) -> tuple[float, float]:
            # Extension only for ODE trial steps past the terminal event.
            s_eval = max(float(S), p.Sc)
            c = p.c0 * profile(s_eval)
            q = 1 - p.gamma*p.N/(p.beta*c*s_eval)
            return float(c), float(q)
        def controlled(t: float, y: np.ndarray) -> list[float]:
            c,q = controls(y[0]); return rhs(y,c,q,True)
        def exit_event(t: float, y: np.ndarray) -> float:
            return float(y[0]-p.Sc)
        exit_event.direction = -1; exit_event.terminal = True
        mid = solve_ivp(controlled, (t1, t1+1.3*expected['duration']), entry,
                        events=exit_event, dense_output=True, method=method,
                        rtol=rtol, atol=atol, max_step=expected['duration']/150)
        if not mid.success or len(mid.t_events[0]) != 1:
            raise RuntimeError(name + ': no S=Sc exit event.')
        t2 = float(mid.t_events[0][0]); exit_state = mid.y_events[0][0]
        def clearance(t: float, y: np.ndarray) -> float:
            return float(y[1]-1.)
        clearance.direction = -1; clearance.terminal = True
        post = solve_ivp(regular, (t2, t2+2*scalar['post_control_duration']+1), exit_state,
                         events=clearance, dense_output=True, method=method,
                         rtol=rtol, atol=atol,
                         max_step=scalar['post_control_duration']/150)
        if not post.success or len(post.t_events[0]) != 1:
            raise RuntimeError(name + ': no descending I=1 event.')
        tend = float(post.t_events[0][0]); final = post.y_events[0][0]
        errors = {
            'duration_days': abs((t2-t1)-expected['duration']),
            'cost_days': abs(float(final[6])-expected['cost']),
            'total_new_infections_persons': abs(float(final[5])-expected['total_infections']),
            'control_new_infections_persons': abs(float(exit_state[5]-entry[5])-expected['new_infections_control']),
            'control_new_Sq_persons': abs(float(exit_state[2]-entry[2])-expected['new_Sq_control']),
            'clearance_time_days': abs(tend-expected['t_end']),
            'exit_S_persons': abs(float(exit_state[0])-p.Sc),
            'control_I_max_abs_error_persons': float(np.max(np.abs(mid.y[1]-p.eta))),
            'population_max_abs_error_persons': max(float(np.max(np.abs(np.sum(sol.y[:5],axis=0)-p.N))) for sol in (pre,mid,post)),
        }
        result['strategies'].append({'strategy': name, 't1_ode': t1, 't2_ode':t2,
            't_end_ode':tend, 'duration_ode':t2-t1, 'cost_ode':float(final[6]),
            'total_new_infections_ode':float(final[5]), 'absolute_errors':errors})
        for phase,sol,start,stop in [('before',pre,0.,t1),('control',mid,t1,t2),('after',post,t2,tend)]:
            tt=np.linspace(start,stop,samples); yy=sol.sol(tt)
            for t,y in zip(tt,yy.T):
                c,q=controls(y[0]) if phase=='control' else (p.c0,p.q0)
                traces.append({'strategy':name,'phase':phase,'time_days':float(t),
                  'S':float(y[0]),'I':float(y[1]),'Sq':float(y[2]),'Iq':float(y[3]),
                  'R':float(y[4]),'total_new_infections':float(y[5]),'J':float(y[6]),
                  'c':float(c),'q':float(q)})
        if max(errors.values()) > 5e-5:
            raise RuntimeError(name + ': independent integration exceeds baseline tolerance.')
    result['all_baseline_absolute_errors_below_5e_minus_5'] = True
    result['notes'] = ['ODE核对使用相同控制函数，检验积分实现一致性，不构成全局最优性的独立证明。',
                       '重复切换时刻按phase保留左右控制值；未将采样轨迹积分代替高精度标量结果。',
                       '没有计算ICU占用；没有重新拟合或重跑西安结果。']
    return result, traces


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parameters',type=Path,default=ROOT/'numerics/inputs/baseline_parameters.json')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'numerics/results')
    args=parser.parse_args()
    try:
        config,p=read_configuration(args.parameters)
        out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
        fine=original.compute(p,float(config['quadrature']['fine_eps']),ode_check=True)
        coarse=original.compute(p,float(config['quadrature']['coarse_eps']),ode_check=False)
        fine['convergence']={r['strategy']:{k:abs(r[k]-s[k]) for k in
            ['duration','cost','total_infections','new_Sq_control','t_end']}
            for r,s in zip(fine['rows'],coarse['rows'])}
        fine['software']={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__}
        fine['provenance']={'core':'numerics/joint_comparison.py','core_sha256':sha256(ROOT/'numerics/joint_comparison.py'),
            'input_sha256':sha256(args.parameters),'runner_sha256':sha256(Path(__file__)),
            'manuscript_sha256':sha256(ROOT/'latex/flatten_curve_analysis_cn.tex'),
            'role':'本轮实际复现；旧程序原样恢复，新增配置和导出入口。',
            'precision_note':'JSON保留binary64可往返显示位数；CSV用17位有效数字；不表示所有位数均已得到误差认证。'}
        write_json(out/'joint_comparison_results.json',fine)
        write_csv(out/'joint_comparison_results.csv', [{k:v for k,v in row.items() if k!='ode_errors'} for row in fine['rows']])
        ode,traces=full_ode_check(p,fine,config['full_ode'])
        write_json(out/'full_three_stage_ode_check.json',ode)
        write_csv(out/'full_three_stage_trajectories.csv',traces)
        chosen=next(x for x in fine['rows'] if x['strategy']=='minimum_cost')
        if f"{chosen['cost']:.4f}"!='2.1183' or f"{chosen['duration']:.4f}"!='7.7536':
            if config['case_id']=='baseline_N763_same_threshold_full_class':
                raise RuntimeError('Baseline no longer matches the unchanged manuscript.')
        print(json.dumps({'case_id':config['case_id'],'J_min':chosen['cost'],
           'duration_days':chosen['duration'],'output_dir':str(out),
           'full_ode_check_passed':ode['all_baseline_absolute_errors_below_5e_minus_5']},ensure_ascii=False,indent=2))
    except (ValueError,KeyError,RuntimeError,OSError,json.JSONDecodeError) as exc:
        parser.exit(1,f'ERROR: {exc}\n')


if __name__=='__main__':
    main()
