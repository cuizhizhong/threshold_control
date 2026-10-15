"""第二条路径（完整五仓室方程，输入按名义轨迹预先生成的时间开环控制）：守恒、正性、控制可行性、
触发/退出/清零事件、独立流量积分恒等式、阈值弧上 I 的偏离（不重置）、与状态路径及原结果的对照、
仅隔离控制的闭式轨迹、推论 4.7 的时间平移、退出后的单调性与 t→∞ 补尾。"""
import math

import numpy as np
import pytest

from conftest import (CASES, LAWS, PR, SI, SM, STRATEGY, TOL, capacity_ref, case_law_params, compare_refs,
                      ode, policy, rel, state)
import model as M


@pytest.mark.parametrize('case,law', case_law_params())
def test_conservation_positivity(case, law, record_property):
    o = ode(case, law)
    P = PR.CASES[case]
    record_property('mass_residual_persons', o['mass_residual_persons'])
    record_property('min_compartment_persons', o['min_compartment_persons'])
    assert o['mass_residual_persons'] / P.N <= TOL['mass_rel']
    assert o['min_compartment_persons'] >= TOL['min_comp']


@pytest.mark.parametrize('case,law', case_law_params())
def test_control_feasibility(case, law):
    """阈值弧上的名义控制：c ∈ [c⁻, c⁺]（不超过 c0），q ∈ [q0, 1)，且在名义状态上满足平衡式 (2.8)。"""
    f = ode(case, law)['feasibility']
    for k in ('c_below_lo', 'c_above_hi', 'c_above_c0', 'q_below_q0', 'q_above_cap'):
        assert f[k] <= TOL['feas_abs'], k
    assert f['balance'] <= TOL['balance']


@pytest.mark.parametrize('case,law', case_law_params())
def test_events(case, law, record_property):
    """启动：I 首次向上达到 η，且与首次积分的 S*、式 (3.2) 的 t1 一致；退出：名义 t2 时 S ≈ S_c、I ≈ η；
    清零：只在退出后、I 向下穿过 1，且只有一次。"""
    o, s, P = ode(case, law), state(case, law), PR.CASES[case]
    assert o['n_trigger_events'] == 1 and o['trigger_dlnI'] > 0
    assert rel(o['I_t1'], P.eta) <= TOL['event_rel']
    assert rel(o['S_t1'], s['S_star']) <= TOL['event_rel']
    assert rel(o['t1'], s['t1']) <= TOL['event_rel']
    assert abs(o['exit_S_error']) / P.S_c <= TOL['event_rel'] and abs(o['exit_I_error']) / P.eta <= TOL['event_rel']
    assert all(abs(t - o['t2']) <= 1e-6 for t in o['exit_actual_crossings'])
    assert o['n_clearance_events'] == 1 and o['clearance_dlnI'] < 0 and o['t_end'] > o['t2']
    assert abs(o['clearance_I_error']) <= TOL['clear_abs']
    assert o['post_upcross_eta'] == []
    record_property('t1_rel', rel(o['t1'], s['t1']))
    record_property('exit_S_error_persons', o['exit_S_error'])


@pytest.mark.parametrize('case,law', case_law_params())
def test_flux_identities(case, law, record_property):
    """独立积分的流量：(i) cI + cIq 与 S0+S_q(0)-S-S_q；(ii) cI 与 I - I0 + γ∫I；(iii) S_q - S_q(0) 与 (1-β)/β·cIq
    （残差除以初始易感者总数）；控制期的两条恒等式 (4.15)(4.16) 用完整方程的流量核对。"""
    o = ode(case, law)
    record_property('identity_residual_rel', o['identity_residual_rel'])
    for k in ('identity_residual_rel', 'Icum_identity_residual_rel', 'Sq_identity_residual_rel'):
        assert o[k] <= TOL['ident_rel'], k
    assert rel(o['arc_infections'], o['arc_infections_identity']) <= TOL['path_rel']
    assert rel(o['arc_Sq_new'], o['arc_Sq_new_identity']) <= TOL['path_rel']
    P = PR.CASES[case]
    assert rel(o['arc_into_I'], P.gamma * P.eta * o['dt']) <= TOL['path_rel']


@pytest.mark.parametrize('case,law', case_law_params())
def test_plateau_not_reset(case, law, record_property):
    """开环阈值弧上 I 自由演化：偏离 η 很小但不为零（实现中没有把 I 重置为 η）。"""
    o = ode(case, law)
    record_property('plateau_abs_dev_persons', o['plateau_abs_dev'])
    assert 0.0 < o['plateau_rel_dev'] <= TOL['plateau_rel']


def test_open_loop_sensitivity(record_property):
    """把阈值弧上的接触率乘以 1+ε（ε = 1e-6，隔离比例不变）：ln I 的增长率起初偏离 γε，I 随即离开 η
    （S 也随之下降得更快，偏离不再是简单的 γεΔt）。若实现中把 I 重置到 η，这一偏离不会出现。"""
    eps = 1e-6
    pol = policy('base', 'q_only')
    o = SM.run(pol, c_scale=1 + eps)
    base = ode('base', 'q_only')
    record_property('perturbed_plateau_rel_dev', o['plateau_rel_dev'])
    record_property('unperturbed_plateau_rel_dev', base['plateau_rel_dev'])
    assert o['plateau_rel_dev'] >= 0.1 * eps and o['plateau_rel_dev'] >= 1e4 * base['plateau_rel_dev']


PATH_FIELDS = ('dt', 'J', 'Jc', 'Jq', 't_end', 'total_infections_to_clearance', 'total_infections_inf', 't2')
STATE_KEY = dict(dt='dt', J='J', Jc='Jc', Jq='Jq', t_end='t_end', total_infections_to_clearance='total_infections_to_clearance',
                 total_infections_inf='total_infections_inf', t2='t2')


@pytest.mark.parametrize('case,law', case_law_params())
def test_ode_vs_state_path(case, law, record_property):
    o, s = ode(case, law), state(case, law)
    # 解析上为零的分项（仅隔离控制的 J_c、仅减少接触的 J_q）只比较绝对值
    zero = {'q_only': 'Jc', 'c_only': 'Jq'}.get(law)
    if zero:
        assert abs(o[zero]) <= 1e-12 and abs(s[zero]) <= 1e-12
    diffs = {k: rel(o[k], s[STATE_KEY[k]]) for k in PATH_FIELDS if k != zero}
    diffs['arc_Sq_new'] = rel(o['arc_Sq_new'], s['sq_identity'])
    diffs['arc_infections'] = rel(o['arc_infections'], s['inf_identity'])
    record_property('max_rel', max(diffs.values()))
    for k, v in diffs.items():
        assert v <= TOL['path_rel'], (k, v)


ODE_REG = dict(dt='duration_time', J='J_time', t1='t1', t2='t2', t_end='t_end',
               total_infections_to_clearance='total_infections_to_clearance', arc_infections='plateau_infections_time',
               arc_Sq_new='Sq_increment_plateau', peak_I_plus_Iq_over_eta='peak_I_plus_Iq_over_eta')


@pytest.mark.parametrize('case,law', case_law_params())
def test_regression_compare_ode(case, law, record_property):
    """完整方程路径与原全精度结果（compare_*.csv 的 time 字段与现存感染峰值）回归。"""
    o, r = ode(case, law), compare_refs()[(case, STRATEGY[law])]
    diffs = {k: rel(o[k], r[f]) for k, f in ODE_REG.items()}
    record_property('max_rel', max(diffs.values()))
    for k, v in diffs.items():
        assert v <= TOL['reg_rel'], (k, v)


@pytest.mark.parametrize('case', CASES)
def test_q_only_closed_form_trajectory(case, record_property):
    """仅隔离控制：完整方程的 S(t) 与式 (3.5)、名义控制 q(t) 与式 (3.8)、最大隔离比例与式 (3.10)。"""
    o = ode(case, 'q_only')
    R = o['_runner']
    P = PR.CASES[case]
    (label, sol, control, ta, tb), = [ph for ph in R.phases if ph[0] == 'plateau']
    tt = np.linspace(ta, tb, 401)
    S = sol.sol(tt)[0] * P.N
    S_cf = SI.q_only_S_of_t(P, tt - ta)
    q = np.array([control(t)[1] for t in tt])
    q_cf = SI.q_only_q_of_t(P, tt - ta)
    record_property('S_max_rel', float(np.max(np.abs(S / S_cf - 1))))
    assert np.max(np.abs(S / S_cf - 1)) <= 1e-9
    assert np.max(np.abs(q - q_cf)) <= 1e-12
    assert abs(q[0] - SI.closed_forms(P)['q_max']) <= 1e-12 and abs(q[-1] - P.q0) <= 1e-12


@pytest.mark.parametrize('case', [pytest.param('base'), pytest.param('xian', marks=pytest.mark.slow)])
def test_whole_epidemic_shift(case, record_property):
    """推论 4.7 的数值一致性：各控制的清零时间之差等于控制时长之差，总累计新增感染之差等于 γη(1-β)ΔΔt。"""
    P = PR.CASES[case]
    runs = {l: ode(case, l) for l in LAWS}
    base = runs['q_only']
    worst = 0.0
    for l in ('c_only', 'alpha', 'opt'):
        d_dt = runs[l]['dt'] - base['dt']
        worst = max(worst, abs((runs[l]['t_end'] - base['t_end']) - d_dt) / d_dt)
        d_c = runs[l]['total_infections_to_clearance'] - base['total_infections_to_clearance']
        worst = max(worst, rel(d_c, P.gamma * P.eta * (1 - P.beta) * d_dt))
        d_inf = runs[l]['total_infections_inf'] - base['total_infections_inf']
        worst = max(worst, rel(d_inf, P.gamma * P.eta * (1 - P.beta) * d_dt))
    record_property('max_rel', worst)
    assert worst <= TOL['path_rel']


@pytest.mark.parametrize('case,law', case_law_params())
def test_post_exit_monotone(case, law):
    """定理 3.5 的数值一致性：退出后（保持常规、不释放）S 严格下降，I 不越过 η、此后单调下降到清零。"""
    o = ode(case, law)
    R = o['_runner']
    (label, sol, control, ta, tb), = [ph for ph in R.phases if ph[0] == 'post']
    tt = np.linspace(ta, o['t_end'], 2001)
    Y = sol.sol(tt)
    assert np.all(np.diff(Y[0]) < 0)
    I = np.exp(Y[1]) * PR.CASES[case].N
    assert o['max_I_over_eta_minus_1'] <= 1e-8
    k = int(np.argmax(I))
    assert np.all(np.diff(I[k:]) < 0) and tt[k] - ta <= 1e-3


@pytest.mark.parametrize('case,law', case_law_params())
def test_infinite_time_tail(case, law):
    """t→∞ 的解析补尾（定理 3.5 的首次积分）：Lambert W 与 brentq 一致；补尾增量为正；
    仅隔离控制的 t→∞ 总累计与定理 3.6 的闭式一致。"""
    o = ode(case, law)
    P = PR.CASES[case]
    assert o['tail_lambertw_vs_brentq_rel'] <= TOL['root_rel'] and o['tail_increment'] > 0
    assert rel(o['S_inf'], SI.post_exit(P)['S_inf']) <= TOL['path_rel']
    if law == 'q_only':
        assert rel(o['total_infections_inf'], SI.closed_forms(P)['Itcum_q_only_inf']) <= TOL['path_rel']


CAPS = [pytest.param(c, l, marks=([pytest.mark.slow] if c == 'xian' else []), id=f'{c}-{l}')
        for c in CASES for l in ('opt', 'cap_upper', 'cap_lower')]


@pytest.mark.parametrize('case,law', CAPS)
def test_capacity_ode(case, law, record_property):
    """能力代表点：完整方程上满足 c ≥ c_min、q ≤ q_cap；与状态路径一致；成本最优控制与原结果回归。"""
    o, s = ode(case, law, cap=True), state(case, law, cap=True)
    P, C = PR.CASES[case], PR.REP_CAPACITY[case]
    f = o['feasibility']
    assert max(f.values()) <= TOL['feas_abs']
    assert o['plateau_rel_dev'] <= TOL['plateau_rel'] and o['identity_residual_rel'] <= TOL['ident_rel']
    for k in ('dt', 'J', 't_end', 'total_infections_to_clearance'):
        assert rel(o[k], s[k]) <= TOL['path_rel'], k
    if law == 'opt':
        r = capacity_ref()['baseline' if case == 'base' else 'xian']['metrics']
        diffs = dict(dt=rel(o['dt'], r['duration_time']), J=rel(o['J'], r['J_time']), t_end=rel(o['t_end'], r['t_end']),
                     tot=rel(o['total_infections_to_clearance'], r['total_infections_to_clearance']),
                     peak=rel(o['peak_I_plus_Iq_over_eta'], r['peak_I_plus_Iq_over_eta']),
                     sq=rel(o['arc_Sq_new'], r['Sq_increment_plateau']))
        record_property('max_rel', max(diffs.values()))
        for k, v in diffs.items():
            assert v <= TOL['reg_rel'], (k, v)
