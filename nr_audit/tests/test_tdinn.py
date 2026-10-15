"""TDINN 控制与常规控制（时间开环，NR-3）：控制函数在 t = 0 取常规水平；与原参照值（xian/reference.json）回归；
拟合窗口的观测算子与原拟合准则一致（fit.json 的 objective 与 raw_rmse）；质量与流量恒等式。"""
import math

import numpy as np
import pytest

from conftest import PR, TOL, rel
import sources as SRC
import tdinn as TD


@pytest.fixture(scope='module')
def runs():
    X = PR.XIAN
    return dict(tdinn=TD.run(X, TD.tdinn)[0], routine=TD.run(X, TD.routine_of(X))[0])


def test_controls_at_origin():
    c, q = TD.tdinn(0.0)
    assert c == PR.XIAN.c0 and abs(q - PR.XIAN.q0) <= 1e-15
    assert TD.c_tdinn(1e3) == pytest.approx(3.4625) and TD.q_tdinn(1e3) == pytest.approx(0.9844)


def test_reference_regression(runs, record_property):
    ref = SRC.load_json('xian_reference')
    td = runs['tdinn']
    d = dict(peak=rel(td['peak_I'], ref['I_peak_T']), total=rel(td['total'], ref['Itcum_T']),
             t_end=rel(td['t_end'], ref['t_end_T']), J=rel(td['J'], ref['J_T']), cI=rel(td['cI'], ref['Ic_cum_T']),
             cIq=rel(td['cIq'], ref['Iq_cum_T']))
    rt = next(s for s in ref['strategies'] if s['strategy'] == '常规控制')
    d.update(r_peak=rel(runs['routine']['peak_I'], rt['peak_I']), r_total=rel(runs['routine']['total'], rt['cum_total_infections']),
             r_t_end=rel(runs['routine']['t_end'], rt['clear_time']))
    record_property('max_rel', max(d.values()))
    assert max(d.values()) <= TOL['reg_rel']
    assert runs['routine']['J'] == 0.0


def test_conservation(runs):
    for o in runs.values():
        assert o['mass_residual_persons'] / PR.XIAN.N <= TOL['mass_rel']
        assert o['identity_residual_rel'] <= TOL['ident_rel']
        assert o['n_clearance_events'] == 1 and abs(o['clearance_I_error']) <= TOL['clear_abs']


def test_fit_objective_reconstruction(record_property):
    """在给定 I0 下按原定义（日区间 [k, k+1] 上的流量积分与 k+1 时刻的累计，四项均方误差等权相加）重算拟合准则。"""
    import audit_fit as AF
    obs = AF.load_raw()
    e = AF.errors(PR.XIAN, obs)
    fit = SRC.load_json('xian_fit')
    record_property('objective_rel', rel(e['objective'], fit['objective']))
    assert rel(e['objective'], fit['objective']) <= 1e-8
    assert rel(e['raw_rmse_daily'], fit['raw_rmse']) <= 1e-8
    assert len(obs) == 40 and str(obs['date'].iloc[0].date()) == '2021-12-09'
