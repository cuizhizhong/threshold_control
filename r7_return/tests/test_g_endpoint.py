"""(g) R7-3：ω > 0 的“退出后首次 I<1 截断”终点（Config.return_endpoint = 'first_below_one'）。
截断前与不截断（尾部判据）是同一条轨迹：截断时刻与累计感染应等于不截断轨迹首次 I<1 时的值。
默认终点仍为尾部判据（R7-1 的测试与记录不变）。"""
import pytest

import simulate as S
from params import CASES


def _pair(case, law, omega):
    P = CASES[case]
    tr = S.run(P, law, omega=omega, cfg=S.Config(return_endpoint='first_below_one'))
    tl = S.run(P, law, omega=omega, cfg=S.Config(return_endpoint='tail'))
    return tr, tl


def test_default_is_tail():
    assert S.Config().return_endpoint == 'tail'


@pytest.mark.parametrize('case,law,omega', [('base', 'q_only', 1 / 14), ('base', 'opt_noreturn', 1 / 365),
                                            ('xian', 'c_only', 1 / 30)])
def test_truncation_matches_first_below_one(case, law, omega):
    tr, tl = _pair(case, law, omega)
    assert tr['termination'] == 'first_below_one'
    assert abs(tr['t_end'] - tl['below_one_time']) <= 1e-9 * tl['below_one_time']
    assert abs(tr['C_term'] - tl['C_below_one']) <= 1e-9 * tl['C_below_one']
    assert abs(tr['clearance_event_abs']) < 1e-8
    assert tr['crossing'] == 'not_crossed'


def test_truncation_after_tail_when_I_above_one():
    # 西安 1/ω = 7 d：尾部判据先满足（此时 I > 1），截断终点在其后，且累计感染只多出不超过 ε_tail
    tr, tl = _pair('xian', 'q_only', 1 / 7)
    assert tl['termination'] == 'tail' and tl.get('below_one_time') is None
    assert tr['t_end'] > tl['T_term']
    assert 0.0 <= tr['C_term'] - tl['C_term'] <= tl['eps_tail']
