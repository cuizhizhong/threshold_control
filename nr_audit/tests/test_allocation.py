"""逐状态最优选择（定理 5.1 的有限比较）：驻点多项式的代数、根法与 N_x 网格的交叉核对、重根与并列、
能力约束下的允许区间与可行性、结构变化点（命题 5.3 的 S_sw、表 S5 的结构类别）、退出附近的分担比例。
网格只作交叉核对，所有“全局”判断都只是在所检验的状态与网格上的数值结果。"""
import math
import random

import numpy as np
import pytest
import sympy as sp

from conftest import PR, SI, TOL, capacity_ref, policy, rel
import allocation as AL
import sources as SRC

random.seed(20261015)
x_, z_, zb_, wc_, wq_, ka_, y_ = sp.symbols('x z zbar w_c w_q kappa y', real=True)
PHI = (wc_ * (1 - x_) ** 2 + wq_ * (1 - 1 / (x_ * z_)) ** 2 + ka_) / (x_ * z_ - zb_)


def _rand_point():
    z = random.uniform(1.001, 5.0)
    return dict(z=z, zbar=random.uniform(0.05, 0.95), wc=random.uniform(0.1, 10), wq=random.uniform(0.1, 10),
                kappa=random.uniform(-1, 1))


def test_poly_x_is_derivative_numerator():
    """φ′(x)·x³(xz-z̄)²/z 恰为 stationary_poly_x 给出的五次多项式（随机参数点，系数逐项比较）。"""
    num = sp.Poly(sp.expand(sp.cancel(sp.diff(PHI, x_) * x_ ** 3 * (x_ * z_ - zb_) ** 2 / z_)), x_)
    assert num.degree() == 5
    for _ in range(20):
        pt = _rand_point()
        sub = {z_: pt['z'], zb_: pt['zbar'], wc_: pt['wc'], wq_: pt['wq'], ka_: pt['kappa']}
        ref = np.array([float(c.subs(sub)) for c in num.all_coeffs()])
        got = AL.stationary_poly_x(pt['z'], pt['zbar'], pt['wc'], pt['wq'], pt['kappa'])
        assert np.allclose(got, ref, rtol=1e-12, atol=1e-12 * np.max(np.abs(ref)))


def test_poly_x_matches_manuscript_eq_5_4():
    """κ = 0 时与稿件式 (5.4) 只差正因子 c0³（c = c0 x，S = z S_c，S̄ = z̄ S_c）。"""
    c, c0, S, Sc, Sb = sp.symbols('c c0 S S_c Sbar', positive=True)
    eq54 = (wc_ * c ** 3 / c0 ** 2 * (c - c0) * (c + c0 - 2 * c0 * Sb / S)
            + wq_ * (c - c0 * Sc / S) * (-c ** 2 + 3 * c0 * Sc / S * c - 2 * c0 ** 2 * Sb * Sc / S ** 2))
    r, b = 1 / z_, zb_ / z_
    P5 = (wc_ * x_ ** 5 - 2 * b * wc_ * x_ ** 4 + (wc_ * (2 * b - 1) - wq_) * x_ ** 3 + 4 * r * wq_ * x_ ** 2
          - r * (3 * r + 2 * b) * wq_ * x_ + 2 * b * r ** 2 * wq_)
    diff = sp.simplify(eq54.subs({c: c0 * x_, S: z_ * Sc, Sb: zb_ * Sc}) - c0 ** 3 * P5)
    assert diff == 0


def test_poly_y_is_derivative_numerator():
    """缩放坐标：dφ/dy·u³(uz-z̄)²/(ζz) 恰为 stationary_poly_y（x = 1-ζy，u = 1-ζy，ζ = 1-1/z）。"""
    zeta = 1 - 1 / z_
    u = 1 - zeta * y_
    phi_y = (zeta ** 2 * (wc_ * y_ ** 2 + wq_ * (1 - y_) ** 2 / u ** 2) + ka_) / (u * z_ - zb_)
    # 先核对 φ(y) 就是 φ(x) 在 x = 1-ζy 处的值
    assert sp.simplify(phi_y - PHI.subs(x_, u)) == 0
    num = sp.Poly(sp.expand(sp.cancel(sp.diff(phi_y, y_) * u ** 3 * (u * z_ - zb_) ** 2 / (zeta * z_))), y_)
    for _ in range(10):
        pt = _rand_point()
        sub = {z_: pt['z'], zb_: pt['zbar'], wc_: pt['wc'], wq_: pt['wq'], ka_: pt['kappa']}
        ref = np.array([float(c.subs(sub)) for c in num.all_coeffs()])
        got = AL.stationary_poly_y(pt['z'], pt['zbar'], pt['wc'], pt['wq'], pt['kappa'])
        assert len(got) == len(ref)
        assert np.allclose(got, ref, rtol=1e-11, atol=1e-11 * np.max(np.abs(ref)))


GRID_CASES = [(c, r, k, cap) for c in ('base', 'xian') for r in (0.1, 0.5, 2.0, 5.0, 20.0)
              for k in (-0.4, 0.0, 0.3) for cap in (False, True)]


@pytest.mark.parametrize('case,r,kappa,cap', GRID_CASES,
                         ids=[f'{c}-r{r}-k{k}-{"cap" if cp else "free"}' for c, r, k, cp in GRID_CASES])
def test_roots_vs_grid(case, r, kappa, cap, record_property):
    """在 25 个状态上，N_x = 2001/4001/8001 的网格（含局部极小处的有界搜索加密）都找不到比根法更低的值。"""
    P = PR.CASES[case]
    x_min, h = AL.cap_factors(P, PR.REP_CAPACITY[case] if cap else None)
    z_star = SI.start_state(P)['z_star']
    worst = -math.inf
    for z in np.r_[1.0 + 1e-6, 1.0 + 1e-3, np.linspace(1.01, z_star, 23)]:
        for N_x in (2001, 4001, 8001):
            g = AL.grid_check(float(z), P.z_bar, 1.0, r, kappa, x_min, h, N_x)
            worst = max(worst, g['gap_rel'])
    record_property('max_gap_rel', worst)
    assert worst <= TOL['grid_gap']


def test_argmin_triple_root_minimum():
    """f = (x-0.3)⁴：f′ 有三重根，numpy.roots 给出相距约 1e-5 的根簇；候选仍包含最小点。"""
    f = lambda x: (np.asarray(x) - 0.3) ** 4
    x, v, info = AL._argmin_on(4 * np.poly([0.3, 0.3, 0.3]), 0.0, 1.0, f)
    assert abs(x - 0.3) < 1e-4 and v < 1e-15 and info['kind'] == 'root'


def test_argmin_double_root_saddle():
    """f = (x-0.3)³：f′ 在 0.3 有重根（不变号，不是极小），最小值在左端点。"""
    f = lambda x: (np.asarray(x) - 0.3) ** 3
    x, v, info = AL._argmin_on(3 * np.poly([0.3, 0.3]), 0.0, 1.0, f)
    assert x == 0.0 and info['kind'] == 'lo' and info['near_double_root']


def test_argmin_tie():
    """f = (x-0.2)²(x-0.8)²：两个相等的极小，近并列个数为 2，选中其中之一。"""
    f = lambda x: (np.asarray(x) - 0.2) ** 2 * (np.asarray(x) - 0.8) ** 2
    coeffs = 2 * np.polymul(np.poly([0.2, 0.8]), [2.0, -1.0])
    x, v, info = AL._argmin_on(coeffs, 0.0, 1.0, f)
    assert info['near_ties'] == 2 and min(abs(x - 0.2), abs(x - 0.8)) < 1e-12 and v < 1e-28


def test_capacity_bounds_formula():
    """x_lo、x_hi 即式 (4.8) 的 c⁻/c0、c⁺/c0。"""
    for case in ('base', 'xian'):
        P, C = PR.CASES[case], PR.REP_CAPACITY[case]
        x_min, h = AL.cap_factors(P, C)
        for S in np.linspace(P.S_c * 1.0001, SI.start_state(P)['S_star'], 50):
            lo, hi, _, _ = AL.x_bounds_raw(S / P.S_c, x_min, h)
            assert math.isclose(lo * P.c0, max(C.c_min, P.c0 * P.S_c / S), rel_tol=1e-14)
            assert math.isclose(hi * P.c0, min(P.c0, P.c0 * (1 - P.q0) * P.S_c / ((1 - C.q_cap) * S)), rel_tol=1e-14)


def test_capacity_infeasible_and_equality():
    """式 (4.7)：c_min/c0 = 0.9、q_cap = 0.6（NR-1 的 G5 算例）时类为空；取等号时允许区间只在 S* 一点退化。"""
    P = PR.BASE
    with pytest.raises(AL.Infeasible):
        SI.Policy(P, 'opt', cap=PR.Capacity(c_min=0.9 * P.c0, q_cap=0.6))
    q_max = SI.start_state(P)['q_max']
    C = PR.Capacity(c_min=0.5 * P.c0, q_cap=1 - (1 - q_max) / 0.5)       # c_min(1-q_cap) = c0(1-q_max)
    pol = SI.Policy(P, 'opt', cap=C)
    lo, hi, _, _ = AL.x_bounds_raw(pol.z_star, pol.x_min, pol.h)
    assert abs(hi - lo) <= 1e-12
    lo2, hi2, _, _ = AL.x_bounds_raw(pol.z_star * (1 - 1e-3), pol.x_min, pol.h)
    assert hi2 - lo2 > 1e-4


@pytest.mark.parametrize('case', ['base', 'xian'])
def test_switch_equals_S_sw(case, record_property):
    """默认权重：成本最优控制唯一的结构变化点是连续切换，位置与式 (5.6) 的 S_sw 一致（命题 5.3 的局部分界；
    其左右的全局选择是所检验网格上的数值结果）。"""
    pol = policy(case, 'opt')
    bps = pol.structure['breakpoints']
    assert len(bps) == 1 and bps[0]['continuous'] and not pol.structure['steep_points']
    zf = AL.z_sw_formula(pol.P.z_bar)
    record_property('z_switch', bps[0]['z'])
    record_property('z_sw_formula', zf)
    assert abs(bps[0]['z'] - zf) <= 1e-12 * zf
    assert (bps[0]['label_left'], bps[0]['label_right']) == ('int', 'hi')


STRUCT = [('base', 1.0, 'cont'), ('base', 5.0, 'jump'), ('base', 20.0, 'none'),
          ('xian', 1.0, 'cont'), ('xian', 5.0, 'jump'), ('xian', 20.0, 'none')]


@pytest.mark.parametrize('case,r,kind', STRUCT, ids=[f'{c}-r{r}' for c, r, _ in STRUCT])
def test_structure_classes(case, r, kind):
    """表 S5 的三类结构（所算网格上）：r 小时在 S_sw 处连续切换；中等 r 时切换提前并跳变；r 大时没有仅隔离段。"""
    pol = policy(case, 'opt', wq=r)
    bps = pol.structure['breakpoints']
    zf = AL.z_sw_formula(pol.P.z_bar)
    top = pol.law.full(pol.z_star * (1 - 1e-12))[2]['label']
    if kind == 'cont':
        assert len(bps) == 1 and bps[0]['continuous'] and abs(bps[0]['z'] - zf) <= 1e-12 * zf and top == 'hi'
    elif kind == 'jump':
        assert len(bps) == 1 and not bps[0]['continuous'] and bps[0]['z'] > zf and top == 'hi'
        assert (bps[0]['label_left'], bps[0]['label_right']) == ('int', 'hi')
    else:
        assert bps == [] and top == 'int'


def _phase_switches(key, r_target):
    sw = SRC.load_json('phase')[key]['switches']
    r = min({s['r'] for s in sw}, key=lambda v: abs(v - r_target))
    return r, [s for s in sw if s['r'] == r]


@pytest.mark.parametrize('case,key,r_target', [('base', 'baseline', 4.977), ('base', 'baseline', 12.17),
                                                ('xian', 'xian', 3.131), ('xian', 'xian', 4.977)])
def test_switch_regression_phase(case, key, r_target, record_property):
    """跳变切换的位置与两侧取值，与原权重网格结果（phase.json）回归。"""
    r, ref = _phase_switches(key, r_target)
    pol = SI.Policy(PR.CASES[case], 'opt', wq=r)
    bps = pol.structure['breakpoints']
    assert len(ref) == 1 and len(bps) == 1 and ref[0]['jump'] and not bps[0]['continuous']
    S = bps[0]['z'] * pol.P.S_c
    record_property('S_rel_diff', rel(S, ref[0]['S']))
    assert rel(S, ref[0]['S']) <= 1e-8
    assert abs(bps[0]['x_left'] - ref[0]['x_low_S']) <= 1e-6 and abs(bps[0]['x_right'] - ref[0]['x_high_S']) <= 1e-6


@pytest.mark.parametrize('case', ['base', 'xian'])
@pytest.mark.parametrize('r', [0.1, 1.0, 2.0, 5.0, 20.0])
def test_contact_only_never_selected(case, r):
    """命题 5.3(i) 的数值一致性：不考虑能力约束时，所检验状态上从不选仅减少接触的取值。"""
    P = PR.CASES[case]
    for z in np.linspace(1.0005, SI.start_state(P)['z_star'], 400):
        assert AL.argmin_state(float(z), P.z_bar, 1.0, r)[2]['label'] != 'lo'


@pytest.mark.parametrize('case', ['base', 'xian'])
def test_default_weight_labels(case):
    """默认权重：S > S_sw 的所检验状态上选仅隔离控制，S_c < S < S_sw 上两者并用（数值结果，N-3）。"""
    P = PR.CASES[case]
    zf, zs = AL.z_sw_formula(P.z_bar), SI.start_state(P)['z_star']
    for z in np.linspace(1.0005, zs, 800):
        lab = AL.argmin_state(float(z), P.z_bar, 1.0, 2.0)[2]['label']
        if z > zf * (1 + 1e-6):
            assert lab == 'hi'
        elif z < zf * (1 - 1e-6):
            assert lab == 'int'


@pytest.mark.parametrize('r', [0.5, 2.0, 7.0])
def test_terminal_share(r):
    """退出附近接触减少的分担比例 y → w_q/(w_c+w_q)（命题 5.4，一般权重按 NR-1 R6 批准的陈述）。"""
    for P in PR.CASES.values():
        for zeta in (1e-5, 1e-7, 1e-9, 1e-11):
            z = 1.0 / (1.0 - zeta)
            x, v, info = AL.argmin_state(z, P.z_bar, 1.0, r)
            assert info['coordinate'] == 'y' and info['label'] == 'int'
            assert abs(info['y'] - r / (1 + r)) <= 10 * zeta


def test_capacity_structure_matches_reference():
    """能力代表点上成本最优控制的允许区间端点与折点：q 在启动后停在上限（x = x_hi = h/z）直到 z = h。"""
    for case, key in (('base', 'baseline'), ('xian', 'xian')):
        pol = policy(case, 'opt', cap=True)
        P = pol.P
        assert pol.kinks == sorted([1.0 / pol.x_min, pol.h]) or pol.kinks == [pol.h]
        x, v, info = pol.law.full(pol.z_star * (1 - 1e-9))
        assert info['label'] == 'hi' and info['hi_kind'] == 'qcap'
        q = 1 - (1 - P.q0) / (x * pol.z_star)
        assert abs(q - capacity_ref()[key]['point']['q_cap']) <= 1e-8


@pytest.mark.parametrize('case,r', [('base', 3.2143), ('base', 3.17), ('xian', 2.7137), ('xian', 2.70)])
def test_continuous_switch_is_endpoint(case, r):
    """NR-3 中修正的问题：用端点驻点式的 brentq 定位的连续切换点，该处的选择必须就是该端点
    （A→B 转折附近，端点驻点处两侧都已选内部解时，真正的切换是别处的跳变）。"""
    pol = SI.Policy(PR.CASES[case], 'opt', wq=r)
    for b in pol.structure['breakpoints']:
        if b['method'] == 'brentq_endpoint_stationary':
            x, v, info = pol.law.full(b['z'])
            assert abs(x - info['x_hi']) <= 1e-6 or abs(x - info['x_lo']) <= 1e-6
            assert 'hi' in (b['label_left'], b['label_right']) or 'lo' in (b['label_left'], b['label_right'])
