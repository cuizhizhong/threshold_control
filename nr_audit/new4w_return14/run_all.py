"""NEW-4w W5：14 天指数回流数值研究的调度入口（N33）。显式 --run 才执行。

设定：基准参数（eta = 0.05N）与西安参数（eta = 0.001N），平均停留 1/omega = 14 d；阈值策略的实施方式与正文相同
（首次 I = eta 启动，维持到 S 首次降到 S_c，此后永久常规措施，不释放、不重启）；累计新增感染计至退出后
首次 I = 1（T_cut）。
步骤：
1. 参照控制：仅隔离、仅减少接触、无回流成本最优状态反馈（w_c = 1、w_q = 2），完整五仓室 ODE 评价；
2. 配点优化：两个目标（最短控制时长、最低成本 J），n = 20/40/80/160 逐级加密；n = 20 用十个起点
   （仅隔离、仅减少接触、迁移律、一半、先隔离后接触、先接触后隔离、两个固定种子的平滑扰动，以及 lambda 恒为
   0.25、0.75），之后取前三个可行候选热启动；
3. 独立核验：每级最优候选用完整五仓室 ODE 回放（DOP853，rtol 1e-12），最终候选再用 Radau、rtol 1e-11 复核；
4. 打靶互证：从最终配点候选与仅隔离起点各做一次 80 段分段常控制 SLSQP，并回放核验；
5. 汇总写 nr_audit/results/new4w/return14_summary.json；原始尝试留在本目录 results/。
结论只是所采用离散化与起点下的数值最优，不称全局最优。

运行（仓库根目录）：python -X utf8 nr_audit/new4w_return14/run_all.py --run
"""
import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True

import evaluate as EV          # noqa: E402
import collocation as CO       # noqa: E402
import shooting as SH          # noqa: E402

CASES = ('base', 'xian')
OBJECTIVES = ('time', 'cost')
MESHES = (20, 40, 80, 160)
SUMMARY = REPO / 'nr_audit/results/new4w/return14_summary.json'
KEYS = ('duration', 't1', 't2', 'J', 'C_Tcut', 'T_cut', 'U_Tcut_over_Sc', 'Sq_exit', 'C_exit',
        'threshold_peak_ratio', 'threshold_numeric_status', 'platform_relative_deviation',
        'exit_residual_normalized', 'feasible', 'numeric_status', 'checks')


def brief(r):
    return {k: r.get(k) for k in KEYS}


def lam_profile(values):
    v = np.asarray(values, dtype=float)
    tau = np.linspace(0, 1, len(v))
    below = np.flatnonzero(v < 0.99)
    return dict(min=float(v.min()), max=float(v.max()), mean=float(v.mean()),
                first_tau_below_0p99=float(tau[below[0]]) if len(below) else None,
                head=v[:6].round(4).tolist(), tail=v[-6:].round(4).tolist())


def seeds(case, n):
    grid = np.linspace(0, 1, n + 1)
    out = CO.seeds(case, n)
    out += [('const0.25', np.full(n + 1, 0.25)), ('const0.75', np.full(n + 1, 0.75))]
    return out


def optimize(case, objective, log):
    previous, history = [], []
    for n in MESHES:
        problem = CO.Problem(case, objective, n)
        current = []
        if n == MESHES[0]:
            for label, values in seeds(case, n):
                current.append(problem.solve(problem.initial(values), label))
        else:
            for rank, item in enumerate(previous[:3]):
                current.append(problem.solve(problem.initial(item['lambda_values'], item['duration']),
                                             f"from{item['n']}_{rank}_{item['seed_label']}"))
        valid = [r for r in current if r.get('solver_success') and r.get('constraint_residual', 1) < 1e-8]
        valid.sort(key=lambda r: r['scaled_objective'])
        if not valid:
            raise RuntimeError(f'{case}/{objective}/n{n}: 当前方法未找到可用候选')
        best = valid[0]
        rep = EV.evaluate(case, best['duration'], best['lambda_values'], interpolation='linear')
        history.append(dict(n=n, attempts=len(current), valid=len(valid),
                            objectives=[(r['seed_label'], r['scaled_objective']) for r in valid],
                            best=dict(seed=best['seed_label'], duration=best['duration'], J=best['J'],
                                      scaled_objective=best['scaled_objective']),
                            replay=brief(rep)))
        log.append(dict(case=case, objective=objective, n=n, attempts=len(current), valid=len(valid)))
        previous = valid
        print(case, objective, n, 'valid', len(valid), 'best', best['seed_label'], round(best['duration'], 4),
              round(best['J'], 4), 'replay feasible', rep['feasible'], flush=True)
    final = previous[0]
    radau = EV.evaluate(case, final['duration'], final['lambda_values'], interpolation='linear',
                        method='Radau', rtol=1e-11)
    o80 = history[-2]['best']['scaled_objective']
    o160 = history[-1]['best']['scaled_objective']
    return dict(history=history, final=dict(duration=final['duration'], J=final['J'], seed=final['seed_label'],
                                            lambda_values=final['lambda_values'], profile=lam_profile(final['lambda_values'])),
                final_replay=history[-1]['replay'], final_radau=brief(radau),
                mesh_rel_change_80_160=abs(o160 - o80) / abs(o160))


def shoot(case, objective, final, q_only_duration):
    out = {}
    for label, d0, lam0 in (('from_collocation', final['duration'], final['lambda_values']),
                            ('from_q_only', q_only_duration, [1.0] * 80)):
        s = SH.solve(case, objective, d0, lam0, n_segments=80, maxiter=600,
                     log_dir=HERE / 'results' / 'shooting_attempts', seed_label=label)
        rep = EV.evaluate(case, s['duration'], s['lambda_values'], interpolation='piecewise_constant')
        out[label] = dict(duration=s['duration'], J=s['J'], success=s['solver_success'], message=s['solver_message'],
                          terminal_residual_N=s['terminal_residual_N'], min_inequality=s['min_inequality'],
                          profile=lam_profile(s['lambda_values']), replay=brief(rep))
    return out


def noreturn_reference():
    """无回流（正文模型）的对应值：基准参数与西安 eta = 0.001N，状态路径。"""
    sys.path.insert(0, str(REPO / 'nr_audit'))
    import params as PR
    import state_integrals as SI
    out = {}
    for case, P in (('base', PR.BASE), ('xian', PR.XIAN.with_(eta=0.001 * PR.XIAN.N))):
        rows = {}
        for law in ('q_only', 'c_only', 'opt'):
            st = SI.state_path(SI.Policy(P, law))
            rows[law] = dict(dt=st['dt'], J=st['J'], total_to_clearance=st['total_infections_to_clearance'],
                             dSq=st['sq_identity'], t_end=st['t_end'], t1=st['t1'])
        out[case] = dict(rows=rows, L=P.S0 + P.Sq0 - P.S_c)
    return out


def answers(case, refs, opt):
    q, c, m = refs['q_only'], refs['c_only'], refs['opt_noreturn']
    t, k = opt['time'], opt['cost']
    return dict(
        Q1_time_optimal_vs_q_only=dict(dt_time_opt=t['final_replay']['duration'], dt_q_only=q['duration'],
                                       rel_diff=(t['final_replay']['duration'] - q['duration']) / q['duration'],
                                       lambda_min_time_opt=t['final']['profile']['min'],
                                       c_only_slowest=c['duration'] > max(q['duration'], m['duration'],
                                                                         k['final_replay']['duration'])),
        Q2_infections=dict(order_by_duration=sorted([('q_only', q['duration'], q['C_Tcut']),
                                                     ('cost_opt', k['final_replay']['duration'], k['final_replay']['C_Tcut']),
                                                     ('opt_noreturn', m['duration'], m['C_Tcut']),
                                                     ('c_only', c['duration'], c['C_Tcut'])], key=lambda x: x[1]),
                           Sq_exit=dict(q_only=q['Sq_exit'], cost_opt=k['final_replay']['Sq_exit'],
                                        opt_noreturn=m['Sq_exit'], c_only=c['Sq_exit'])),
        Q3_cost=dict(J_cost_opt=k['final_replay']['J'], J_opt_noreturn=m['J'], J_q_only=q['J'], J_c_only=c['J'],
                     gap_noreturn_law_percent=100 * (m['J'] / k['final_replay']['J'] - 1),
                     profile=k['final']['profile']),
        Q4_threshold=dict({n: r['threshold_numeric_status'] for n, r in refs.items()},
                          time_opt=t['final_replay']['threshold_numeric_status'],
                          cost_opt=k['final_replay']['threshold_numeric_status']),
        Q5_U_Tcut_over_Sc=dict({n: r['U_Tcut_over_Sc'] for n, r in refs.items()},
                               time_opt=t['final_replay']['U_Tcut_over_Sc'], cost_opt=k['final_replay']['U_Tcut_over_Sc']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--cases', nargs='+', choices=CASES, default=list(CASES))
    args = parser.parse_args()
    if not args.run:
        print('未指定 --run，不启动计算。')
        return
    t0 = time.time()
    code = {p.name: hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
            for p in sorted(HERE.glob('*.py'))}
    log, out = [], dict(script='nr_audit/new4w_return14/run_all.py', authorization='AGENTS.md N33（NEW-4w）',
                        omega=EV.OMEGA, code_sha256=code, cases={})
    for case in args.cases:
        p = EV.load_params(case)
        start = EV.prepare_start(case)
        refs = {kind: brief(EV.reference(case, kind)) for kind in ('q_only', 'c_only', 'opt_noreturn')}
        print(case, 'references', {k: (round(v['duration'], 3), round(v['C_Tcut'], 2)) for k, v in refs.items()}, flush=True)
        opt = {obj: optimize(case, obj, log) for obj in OBJECTIVES}
        shots = {obj: shoot(case, obj, opt[obj]['final'], refs['q_only']['duration']) for obj in OBJECTIVES}
        out['cases'][case] = dict(params=dict(N=p['N'], eta=p['eta'], theta=p['theta'], S_c=p['S_c'],
                                              source=p['source'], source_sha256=p['source_sha256']),
                                  start=dict(t1=start['t1'], state=start['state_persons']),
                                  L=p['S0'] + p['Sq0'] - p['S_c'],
                                  references=refs, optimization=opt, shooting=shots,
                                  answers=answers(case, refs, opt))
    out['noreturn'] = noreturn_reference()
    out['log'] = log
    out['elapsed_s'] = time.time() - t0
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(EV._clean(out), ensure_ascii=False, indent=1), encoding='utf-8', newline='\n')
    print(json.dumps(EV._clean({c: out['cases'][c]['answers'] for c in out['cases']}), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
