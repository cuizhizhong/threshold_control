"""NEW-4m：跳变结构入稿的派生核验结果（results/new4m_jump_structure.json）与补充 S5.3 的恒等式。
符号部分只核对代数；图件与求解器部分是命题结论的抽查，不代替证明。"""
import json
import math

import pytest

from conftest import SRC

RES = SRC.HERE / 'results' / 'new4m_jump_structure.json'


@pytest.fixture(scope='module')
def js():
    if not RES.exists():
        pytest.skip('尚未运行 audit_jump_structure.py')
    return json.loads(RES.read_text(encoding='utf-8'))


def test_all_checks(js):
    assert js['all_symbolic_ok'] and js['all_checks_ok']


@pytest.mark.parametrize('case', ['base', 'xian'])
def test_stored_internal_jumps_match_closed_form(js, case):
    c = js['figures']['cases'][case]
    for fig in ('figure7', 'figureS10'):
        assert c[fig]['n'] > 0 and c[fig]['max_abs_dz'] < 1e-10 and c[fig]['max_abs_dx'] < 1e-8
    assert c['internal_r_inside_Aprime']


@pytest.mark.parametrize('case', ['base', 'xian'])
def test_jump_count_by_weight(js, case):
    o = js['solver'][case]
    for key, v in o['scans'].items():
        r = float(key)
        assert v['n_jumps'] == (0 if r <= o['r_cont'] * (1 + 1e-6) else 1), key
        assert v['ok'], key


def test_square_identity_and_factorization():
    sp = pytest.importorskip('sympy')
    p, b, s, t = sp.symbols('p b s t', positive=True)
    r = s ** 2
    zj = 2 * (b + (1 - b) * s)
    k = s * zj
    G = ((1 - p / zj) ** 2 + r * (1 - 1 / p) ** 2) / (p - b)
    assert sp.simplify(sp.together(G - 2 * (s - 1) / zj - (p ** 2 - k * p + k) ** 2 / (zj ** 2 * p ** 2 * (p - b)))) == 0
    lhs = (s - (s - 1) * zj).subs(b, t * (3 - t) / 2)
    assert sp.expand(lhs - (t - (t - 1) * s) * ((t - 2) * s + 3 - t)) == 0


@pytest.mark.parametrize('b', [0.05, 0.575585, 0.832105, 0.95])
def test_closed_form_ordering(b):
    """r_cont < r < r̂ 时 1 < p_- < 2 < p_+ < ζ_j < ζ_sw，且 ζ_j 在两端取尖点状态与 ζ_sw。"""
    rc = 16 / (b + math.sqrt(b * b - 8 * b + 8)) ** 2
    t = (3 + math.sqrt(9 - 8 * b)) / 2
    rh = (t / (t - 1)) ** 2
    zj = lambda r: 2 * (b + (1 - b) * math.sqrt(r))
    assert abs(zj(rc) - (b + math.sqrt(b * b - 8 * b + 8))) < 1e-12 and abs(zj(rh) - t) < 1e-12
    for r in [rc + (rh - rc) * f for f in (0.01, 0.3, 0.7, 0.99)]:
        k = math.sqrt(r) * zj(r)
        d = math.sqrt(k * (k - 4))
        pm, pp = (k - d) / 2, (k + d) / 2
        assert 1 < pm < 2 < pp < zj(r) < t
