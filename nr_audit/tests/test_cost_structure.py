"""NEW-4d：成本结构定理入稿的派生核验结果（results/new4d_cost_structure.json）与闭式阈值。
符号部分只核对代数；数值部分是定理结论在两组参数上的抽查，不代替证明。"""
import json
import math

import pytest

from conftest import SRC

RES = SRC.HERE / 'results' / 'new4d_cost_structure.json'


@pytest.fixture(scope='module')
def cs():
    if not RES.exists():
        pytest.skip('尚未运行 audit_cost_structure.py')
    return json.loads(RES.read_text(encoding='utf-8'))


def test_all_checks(cs):
    assert cs['all_symbolic_ok'] and cs['all_checks_ok']


@pytest.mark.parametrize('case', ['base', 'xian'])
def test_closed_forms_inside_nr3_brackets(cs, case):
    o = cs['cases'][case]
    b = o['b']
    rc = 16 / (b + math.sqrt(b * b - 8 * b + 8)) ** 2
    t = (3 + math.sqrt(9 - 8 * b)) / 2
    assert abs(o['r_cont'] - rc) < 1e-14 and abs(o['r_hat'] - (t / (t - 1)) ** 2) < 1e-14
    assert 2 < o['r_cont'] < o['r_hat'] < 4
    assert o['bracket_A_Ap'][0] <= o['r_cont'] <= o['bracket_A_Ap'][1]
    assert o['bracket_Ap_B'][0] <= o['r_hat'] <= o['bracket_Ap_B'][1]


@pytest.mark.parametrize('case', ['base', 'xian'])
def test_clip_and_monotonicity(cs, case):
    o = cs['cases'][case]
    assert max(o['clip_max_abs_diff_x'].values()) < 1e-9
    for m in o['monotonicity'].values():
        assert m['max_increase_in_r'] < 1e-9 and m['max_decrease_of_u_in_z'] < 1e-9
    assert all(not v for v in o['unimodal_violations'].values())


def test_E_derivative_identity():
    sp = pytest.importorskip('sympy')
    p, z, b, r = sp.symbols('p zeta b r', positive=True)
    E = (p ** 2 - 2 * b * p) / z ** 2 + 2 * b / z - 1 + r * (p - 1) * (3 * p - p ** 2 - 2 * b) / p ** 3
    assert sp.simplify(sp.diff(E, p) - 2 * (p - b) * (1 / z ** 2 - r * (2 * p - 3) / p ** 4)) == 0
