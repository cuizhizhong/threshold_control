"""第一条路径（闭式与对 S 的一维积分）：启动与退出后状态、单控制闭式回归、Simpson 与 quad 互核、
控制期恒等式、时长排序、N_z 收敛、与原全精度结果（compare_*.csv、capacity.json、frontier）的回归。"""
import math

import numpy as np
import pytest

from conftest import (CASES, LAWS, PR, SI, STRATEGY, TOL, capacity_ref, case_law_params, compare_refs,
                      policy, rel, state)
import allocation as AL
import sources as SRC


@pytest.mark.parametrize('case', CASES)
def test_start_state(case, record_property):
    P = PR.CASES[case]
    st = SI.start_state(P)
    assert st['status'] == 'ok' and -math.exp(-1) < st['z_eta'] < 0 and st['lambertw_imag'] == 0.0
    assert P.S_c < st['S_star'] < P.S0
    assert st['lambertw_vs_brentq_rel'] <= TOL['root_rel']
    assert abs(st['residual_I']) <= 1e-9 * P.eta
    record_property('S_star', st['S_star'])


@pytest.mark.parametrize('case', CASES)
def test_post_exit(case):
    P = PR.CASES[case]
    po = SI.post_exit(P)
    assert 0 < po['S_inf'] < po['S_end'] < P.S_c
    assert po['S_end_lambertw_vs_brentq_rel'] <= TOL['root_rel'] and po['S_inf_lambertw_vs_brentq_rel'] <= TOL['root_rel']
    assert po['tail_time'] > 0


@pytest.mark.parametrize('case', CASES)
def test_closed_forms(case, record_property):
    """单控制与显式族的闭式（定理 3.2、3.6，式 4.11、4.14，附录 B）与 S 坐标求积一致。"""
    P = PR.CASES[case]
    cf = SI.closed_forms(P)
    q, c, a = state(case, 'q_only'), state(case, 'c_only'), state(case, 'alpha')
    pairs = dict(dt_q=(q['dt'], cf['dt_q_only']), dt_c=(c['dt'], cf['dt_c_only']), dt_a=(a['dt'], cf['dt_alpha']),
                 J_q=(q['J'], cf['J_q_only']), Jq_q=(q['Jq'], cf['Jq_q_only']), J_c=(c['J'], cf['J_c_only']),
                 Jc_c=(c['Jc'], cf['Jc_c_only']), arc_inf_q=(q['inf_flux'], cf['arc_inf_q_only']),
                 Itcum_q=(q['total_infections_to_clearance'], cf['Itcum_q_only_to_clearance']),
                 Itcum_q_inf=(q['total_infections_inf'], cf['Itcum_q_only_inf']), q_max=(q['q_max'], cf['q_max']))
    worst = max(rel(u, v) for u, v in pairs.values())
    record_property('max_rel', worst)
    for k, (u, v) in pairs.items():
        assert rel(u, v) <= TOL['closed_rel'], k
    assert abs(q['Jc']) <= 1e-12 and abs(c['Jq']) <= 1e-12      # 解析上为零，求积只剩舍入


@pytest.mark.parametrize('case,law', case_law_params())
def test_simpson_vs_quad(case, law, record_property):
    s = state(case, law)
    d = max(rel(s['dt'], s['dt_quad']), rel(s['J'], s['J_quad']))
    record_property('max_rel', d)
    assert d <= TOL['quad_rel']
    assert s['feasibility_violation'] <= TOL['feas_abs']


@pytest.mark.parametrize('case,law', case_law_params())
def test_arc_identities(case, law):
    """控制期累计新增感染与新增隔离易感者：流量求积与式 (4.15)(4.16) 一致。"""
    s = state(case, law)
    assert rel(s['inf_flux'], s['inf_identity']) <= 1e-12
    assert rel(s['sq_flux'], s['sq_identity']) <= 1e-12


@pytest.mark.parametrize('case', CASES)
def test_duration_ordering(case):
    """式 (4.14) 的两界与定理 4.5(ii)；成本最优控制与 α = 0.5 的次序只是这两组参数下的数值结果（N-1）。"""
    d = {l: state(case, l)['dt'] for l in LAWS}
    assert d['q_only'] < d['opt'] < d['alpha'] < d['c_only']
    P = PR.CASES[case]
    al = [SI.arc_integrals(SI.Policy(P, 'alpha', alpha=a), with_quad=False)['dt'] for a in (0.25, 0.5, 0.75)]
    assert d['c_only'] > al[0] > al[1] > al[2] > d['q_only']


REG_FIELDS = dict(dt='duration_state', J='J_state', t1='t1', t_end='t_end_state',
                  total_infections_to_clearance='total_infections_state', inf_identity='plateau_infections_state',
                  sq_identity='Sq_increment_plateau_state')


@pytest.mark.parametrize('case,law', case_law_params())
def test_regression_compare_state(case, law, record_property):
    """状态路径与原全精度结果（compare_*.csv 的 state 字段）回归。"""
    s, r = state(case, law), compare_refs()[(case, STRATEGY[law])]
    diffs = {k: rel(s[k], r[f]) for k, f in REG_FIELDS.items()}
    record_property('max_rel', max(diffs.values()))
    for k, v in diffs.items():
        assert v <= TOL['reg_rel'], (k, v)


CAP_FIELDS = dict(dt='duration_state', J='J_state', t_end='t_end_state', total_infections_to_clearance='total_infections_state',
                  inf_identity='plateau_infections_state', sq_identity='Sq_increment_plateau_state', q_max='q_max',
                  c_min='c_min')


@pytest.mark.parametrize('case', [pytest.param('base'), pytest.param('xian', marks=pytest.mark.slow)])
def test_capacity_state(case, record_property):
    """能力代表点：成本最优控制与原结果回归；推论 4.6 的时长两界；命题 5.2 的“放宽能力不增大最小成本”。"""
    key = 'baseline' if case == 'base' else 'xian'
    s, r = state(case, 'opt', cap=True), capacity_ref()[key]['metrics']
    diffs = {k: rel(s[k], r[f]) for k, f in CAP_FIELDS.items()}
    record_property('max_rel', max(diffs.values()))
    for k, v in diffs.items():
        assert v <= TOL['reg_rel'], (k, v)
    up, lo = state(case, 'cap_upper', cap=True), state(case, 'cap_lower', cap=True)
    assert up['dt'] < s['dt'] < lo['dt']
    assert s['J'] <= min(up['J'], lo['J'])
    assert s['J'] > state(case, 'opt')['J']
    assert s['feasibility_violation'] <= TOL['feas_abs'] and rel(s['dt'], s['dt_quad']) <= TOL['quad_rel']


@pytest.mark.parametrize('case', CASES)
def test_Nz_convergence(case, record_property):
    """成本最优控制：N_z = 1001/2001/4001 的 Δt、J 与切换位置（控制网格 N_x 不参与求积，另见 test_allocation）。"""
    P = PR.CASES[case]
    ref = state(case, 'opt')
    worst = 0.0
    for N_z in (1001, 2001):
        pol = SI.Policy(P, 'opt', N_z=N_z)
        a = SI.arc_integrals(pol, N_z=N_z, with_quad=False)
        worst = max(worst, rel(a['dt'], ref['dt']), rel(a['J'], ref['J']))
        assert pol.breaks == pytest.approx(policy(case, 'opt').breaks, rel=1e-12)
        assert pol.structure['steep_points'] == []
    record_property('max_rel', worst)
    assert worst <= 1e-8


@pytest.mark.slow
def test_frontier_regression(record_property):
    """J + κΔt 的最小化解（注记 5.5）与原乘子曲线（frontier_baseline.csv）回归：每隔 47 行取一点，另加
    κ ≈ -0.246…-0.240 的 5 行（成本最优控制律在 z ≈ 2.82 处由跳变变为陡峭的连续变化）。"""
    rows = SRC.read_csv('frontier')
    worst = 0.0
    for row in rows[::47] + rows[296:301]:
        k = float(row['kappa'])
        a = SI.arc_integrals(SI.Policy(PR.BASE, 'opt', kappa=k), with_quad=False)
        worst = max(worst, rel(a['dt'], float(row['duration'])), rel(a['J'], float(row['J'])))
    record_property('max_rel', worst)
    assert worst <= 1e-6


@pytest.mark.parametrize('case', CASES)
def test_exit_lower_bound(case):
    """命题 4.9 的数值一致性：到 S 首次到达 S_c 时（t2）的累计新增感染不小于 β(S0 - S_c)；
    能力约束下不小于 β(S0 - S_c)/(β + (1-β)q_cap)（这里 q ≤ q_cap 在全程成立）。"""
    P = PR.CASES[case]
    lb = P.beta * (P.S0 - P.S_c)
    for law in ('q_only', 'c_only', 'alpha'):
        s = state(case, law)
        assert s['pre_infections'] + s['inf_identity'] >= lb
    C = PR.REP_CAPACITY[case]
    if case == 'base':
        s = state(case, 'opt', cap=True)
        assert s['pre_infections'] + s['inf_identity'] >= P.beta / (P.beta + (1 - P.beta) * C.q_cap) * (P.S0 - P.S_c)


def test_minimum_cost_decreases_with_threshold():
    """命题 5.2 的数值一致性（基准参数、三个阈值）：最小成本随 η 严格下降。"""
    J = [SI.arc_integrals(SI.Policy(PR.BASE.with_(eta=f * PR.BASE.N), 'opt'), with_quad=False)['J']
         for f in (0.03, 0.05, 0.08)]
    assert J[0] > J[1] > J[2]
