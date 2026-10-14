"""(a) ω = 0：四种控制的 Δt 与 J 对照全精度参考值（相对误差 < 1e-4）；
控制期累计感染用解析恒等式与独立的流量积分交叉核验；计至清零的总累计感染另行对照；
稿件表 2 的展示值只检查舍入一致。"""
import pytest

import endpoints as E
import references as REF
from params import CASES

REFS, DERIVED = REF.load_noreturn_refs()
REL = 1e-4
CASES_LAWS = [(c, l) for c in ('base', 'xian') for l in REF.LAWS_NORETURN]


def rel(a, b):
    return abs(a - b) / abs(b)


@pytest.mark.parametrize('case', ['base', 'xian'])
def test_start_state_noreturn(case):
    st = E.start_state_noreturn(CASES[case])
    assert st['status'] == 'ok'
    assert st['lambertw_vs_brentq_rel'] < 1e-12          # Lambert W（k=-1）与 brentq 交叉核对
    assert rel(st['S_star'], DERIVED[case]['Sstar']) < 1e-10
    assert rel(CASES[case].S_c, DERIVED[case]['Sc']) < 1e-12


@pytest.mark.parametrize('case,law', CASES_LAWS)
def test_quadrature_vs_reference(case, law):
    r = E.arc_noreturn(CASES[case], law)
    ref = REFS[(case, law)]
    assert rel(r['dt'], ref['dt']) < REL
    assert rel(r['J'], ref['J']) < REL
    # S 坐标求积的 Simpson（N_z）与自适应 quad 相互核对
    assert rel(r['dt'], r['dt_quad']) < 1e-8 and rel(r['J'], r['J_quad']) < 1e-8
    # 控制期累计感染与新增隔离易感者：解析恒等式 vs 独立的流量求积
    assert rel(r['infections_identity'], r['infections_quad']) < 1e-8
    assert rel(r['Sq_new_identity'], r['Sq_new_quad']) < 1e-8
    assert rel(r['infections_quad'], ref['plateau_infections']) < REL
    assert rel(r['Sq_new_quad'], ref['Sq_new']) < REL


@pytest.mark.parametrize('case,law', CASES_LAWS)
def test_event_method_vs_reference(case, law, sim):
    r = sim(case, law)
    ref = REFS[(case, law)]
    assert r['status'] == 'ok' and r['phases'] == ['routine', 'plateau', 'post']
    assert rel(r['dt'], ref['dt']) < REL
    assert rel(r['J'], ref['J']) < REL
    assert rel(r['t1'], ref['t1']) < 1e-6
    # 控制期累计感染：独立积分的流量 vs 解析恒等式 β(S*-S_c)+(1-β)γηΔt
    assert rel(r['arc_infections'], r['arc_infections_identity']) < 1e-8
    assert rel(r['arc_Kq'], r['arc_Sq_new_identity']) < 1e-8
    assert rel(r['arc_infections'], ref['plateau_infections']) < REL
    # 计至清零（I = 1，退出后向下穿越）的总累计感染：另一个量，单独对照
    assert r['termination'] == 'clearance'
    assert rel(r['C_t_end'], ref['total_infections_to_clearance']) < REL
    assert rel(r['t_end'], ref['t_end']) < REL
    # t→∞（定理 3.5 的 S_∞ 解析补尾）不小于计至清零的值
    assert r['C_inf'] > r['C_t_end']


def _rounds_to(value, shown, decimals):
    return abs(value - shown) <= 0.5 * 10 ** (-decimals) * (1 + 1e-9)


@pytest.mark.parametrize('case,law', CASES_LAWS)
def test_table2_rounding(case, law, sim):
    """稿件表 2 展示值只检查舍入一致（不作精度参考）。"""
    r = sim(case, law)
    a = E.arc_noreturn(CASES[case], law)
    shown = REF.TABLE2_DISPLAY[(case, law)]
    dec = REF.TABLE2_DECIMALS[case]
    unit = REF.TABLE2_UNIT[case]
    vals = (r['dt'], r['t_end'], r['C_t_end'] / unit, a['Sq_new_quad'] / unit, r['J'])
    for v, s, d in zip(vals, shown, dec):
        assert _rounds_to(v, s, d), (v, s, d)
