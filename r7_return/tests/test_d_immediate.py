"""(d) 立即返回对照模型的端点数与执行计划第 5 节一致（相对误差 < 1e-3）。"""
import pytest

import alloc as AL
import endpoints as E
import references as REF
from params import CASES

REL = 1e-3
LAWS = ('q_only', 'alpha', 'opt_immediate', 'c_only')


def rel(a, b):
    return abs(a - b) / abs(b)


@pytest.mark.parametrize('case', ['base', 'xian'])
def test_start_state_immediate(case):
    P = CASES[case]
    st = E.start_state_immediate(P)
    assert st['status'] == 'ok'
    assert 0 < P.I0 < P.eta < st['I_peak_ir']             # R3 的触发条件
    assert st['A'] > 1
    assert st['lambertw_vs_brentq_rel'] < 1e-12
    ref = REF.PLAN_IMMEDIATE_STATE[case]
    assert rel(st['S_star'], ref['S_star_inf']) < REL
    assert rel(P.S_c, ref['S_c']) < REL
    assert rel(st['S_star'] - P.S_c, ref['infections']) < REL


@pytest.mark.parametrize('case,law', [(c, l) for c in ('base', 'xian') for l in LAWS])
def test_immediate_endpoint_table(case, law):
    r = E.arc_immediate(CASES[case], law)
    ref = REF.PLAN_IMMEDIATE[(case, law)]
    assert rel(r['dt'], ref['dt']) < REL
    assert rel(r['J'], ref['J']) < REL
    assert rel(r['dt'], r['dt_quad']) < 1e-8 and rel(r['J'], r['J_quad']) < 1e-8
    assert rel(r['Kq_identity'], r['Kq_quad']) < 1e-8
    if law == 'q_only':
        assert rel(r['dt'], r['dt_closed_q_only']) < 1e-10
    if law == 'c_only':
        assert rel(r['dt'], r['dt_closed_c_only']) < 1e-10


@pytest.mark.parametrize('case', ['base', 'xian'])
def test_immediate_structure(case):
    r = E.arc_immediate(CASES[case], 'opt_immediate')
    bps = r['structure']['breakpoints']
    assert len(bps) == 1 and bps[0]['continuous']
    assert rel(bps[0]['z'], REF.PLAN_IMMEDIATE_SWITCH_Z) < REL
    z = 1.0 + 1e-6
    share = AL.terminal_share(AL.argmin_immediate(z, 1.0, 2.0)[0], z)
    assert rel(share, REF.PLAN_IMMEDIATE_TERMINAL_SHARE) < REL


@pytest.mark.parametrize('case,law', [(c, l) for c in ('base', 'xian')
                                      for l in ('q_only', 'opt_immediate', 'c_only')])
def test_immediate_event_vs_quadrature(case, law, sim):
    """事件法（时间积分）与 S 坐标求积相互核对；控制期感染恒为 S*_∞ - S_c。"""
    r = sim(case, law, 0.0, 'immediate')
    a = E.arc_immediate(CASES[case], law)
    assert rel(r['dt'], a['dt']) < 1e-7 and rel(r['J'], a['J']) < 1e-7
    assert rel(r['arc_infections'], a['infections']) < 1e-8
    assert rel(r['arc_Kq'], a['Kq_quad']) < 1e-7


def test_degenerate_branch_skips_lambertw(monkeypatch):
    """触发条件不满足时走退化分支，不调用 Lambert W。"""
    def boom(*a, **k):
        raise AssertionError('不应调用 lambertw')
    monkeypatch.setattr(E, 'lambertw', boom)
    P = CASES['base'].with_(eta=400.0)                       # η > I_peak,ir ≈ 325
    st = E.start_state_immediate(P)
    assert st['status'] == 'degenerate' and P.eta >= st['I_peak_ir']
    P2 = CASES['base'].with_(eta=0.5)                        # I0 = 1 ≥ η
    assert E.start_state_immediate(P2)['status'] == 'degenerate'
