"""(e) 逐状态最小化：根法最小值 ≤ 网格最小值 + tol_abs + tol_rel·|网格最小值|，
且两者差距随 N_x 加密缩小。退出点附近成本接近零，只用绝对判据，不做除零比较。"""
import numpy as np
import pytest

import alloc as AL
import endpoints as E
from params import CASES

TOL_ABS = 1e-14
TOL_REL = 1e-12
NX = (2001, 4001, 8001)


def _setup(case, model):
    P = CASES[case]
    if model == 'noreturn':
        zs = E.start_state_noreturn(P)['z_star']
        am = lambda z: AL.argmin_noreturn(z, P.z_bar, 1.0, 2.0)
        dens = lambda z: (lambda x: AL.density_noreturn(x, z, P.z_bar, 1.0, 2.0))
    else:
        zs = E.start_state_immediate(P)['z_star']
        am = lambda z: AL.argmin_immediate(z, 1.0, 2.0)
        dens = lambda z: (lambda x: AL.density_immediate(x, z, 1.0, 2.0))
    zgrid = np.concatenate([[1 + 1e-9, 1 + 1e-6, 1 + 1e-4], np.linspace(1.001, zs, 300)])
    return zgrid, am, dens


@pytest.mark.parametrize('case,model', [(c, m) for c in ('base', 'xian') for m in ('noreturn', 'immediate')])
def test_root_vs_grid(case, model):
    zgrid, am, dens = _setup(case, model)
    gaps = {n: [] for n in NX}
    for z in zgrid:
        z = float(z)
        x_r, v_r, _ = am(z)
        lo, hi = AL.x_bounds(z)
        assert lo - 1e-15 <= x_r <= hi + 1e-15
        for n in NX:
            _, v_g = AL.grid_min(dens(z), z, n)
            assert v_r <= v_g + TOL_ABS + TOL_REL * abs(v_g)
            gaps[n].append(v_g - v_r)
    g = {n: np.array(gaps[n]) for n in NX}
    # 逐点：嵌套网格加密后差距不增大（容许舍入）
    assert np.all(g[4001] <= g[2001] + 1e-15 + 1e-13 * np.abs(g[2001]))
    assert np.all(g[8001] <= g[4001] + 1e-15 + 1e-13 * np.abs(g[4001]))
    # 整体：最大差距随 N_x 严格缩小
    assert g[8001].max() < g[4001].max() < g[2001].max()


def test_sympy_quintic_matches_quartic_at_zbar0():
    """SymPy 导出的无回流五次式在 z̄ = 0 处应等于 z³·x·(立即返回四次式)。"""
    for z in (1.3, 2.0, 2.9, 4.1):
        p5 = AL.stationary_poly_noreturn(z, 0.0, 1.0, 2.0)
        p4 = AL.stationary_poly_immediate(z, 1.0, 2.0)
        for x in (0.3, 0.55, 0.8, 1.0):
            assert abs(np.polyval(p5, x) - z ** 3 * x * np.polyval(p4, x)) < 1e-12


@pytest.mark.parametrize('case', ['base', 'xian'])
def test_noreturn_switch_matches_formula(case):
    """ω = 0、默认权重：逐状态全局最小的切换位置与 S_sw/S_c = (3+√(9-8z̄))/2 一致。"""
    P = CASES[case]
    r = E.arc_noreturn(P, 'opt_noreturn')
    bps = r['structure']['breakpoints']
    assert len(bps) == 1 and bps[0]['continuous']
    assert abs(bps[0]['z'] - AL.z_sw_noreturn_formula(P.z_bar)) < 1e-10
