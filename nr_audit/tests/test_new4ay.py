"""NEW-4ay（N53）：第 7.3 节每日追踪隔离人数的上下界由参数、控制函数与表 4 按公式算出；第 7.1 节数据来源不再用“这些”指代。"""
import json

import numpy as np
import pytest

import params as PR
from conftest import SRC

ROOT = SRC.ROOT
RES = SRC.HERE / 'results'


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


@pytest.fixture(scope='module')
def rec():
    return json.loads((RES / 'new4ay_scope.json').read_text(encoding='utf-8'))


def test_workload_bounds(rec):
    X = PR.XIAN.with_(eta=0.001 * PR.XIAN.N)
    low = X.c0 * X.q0 * X.S_c * X.eta / X.N
    t = np.linspace(0.0, 46.0, 200001)
    c = (12.8872 - 3.4625) * np.exp(-(0.0463 * t) ** 2) + 3.4625
    q = (0.3230 - 0.9844) * np.exp(-(0.0452 * t) ** 2) + 0.9844
    cq = float((c * q).max())
    peak = json.loads((RES / 'new4w/xian_theta001.json').read_text(encoding='utf-8'))['strategies']['TDINN']['peak_I']
    up = cq * peak
    vals = {r['text']: r.get('value') for r in rec['new_readings']}
    assert f'{low:.3g}' == '1.24e+04' and abs(vals['c0 q0 S_c eta/N ≈ 1.24e4'] - low) < 0.01
    assert f'{cq:.2f}' == '5.28' and up < 810 and int(low / up) == 15
    assert rec['scientific_activity'] == dict(ode_solves=0, optimization_solves=0, fits=0, redraws=0)
    xt = text('paper/sections/07_xian.tex')
    for s in ('c_0q_0S_c\\eta/N\\approx1.24\\times10^4', '$cq\\le5.28$', '不超过约 $810$', '至少是 TDINN 的 $15$ 倍'):
        assert s in xt, s
    assert '的 $86$ 倍' not in xt and '与 $I$ 成正比' not in xt


def test_data_source_wording():
    xt = text('paper/sections/07_xian.tex')
    assert '从西安的病例数据重构' in xt and '从这些数据重构' not in xt
