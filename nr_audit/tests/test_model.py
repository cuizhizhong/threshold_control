"""模型右端（式 2.1）的代数性质：守恒、无回流结构下的易感者流量、流量非负、阈值弧控制的平衡式。"""
import math
import random

import pytest

from conftest import PR
import model as M

random.seed(20261015)


def _samples(n=200):
    for _ in range(n):
        P = random.choice(list(PR.CASES.values()))
        s, i, sq, iq = (random.uniform(0, 1) for _ in range(4))
        r = random.uniform(0, 1)
        c, q = random.uniform(0, P.c0), random.uniform(0, 1)
        yield P, s, i, sq, iq, r, c, q


def test_mass_and_susceptible_flux():
    """五式之和为零；d(S+S_q)/dt = -β c S I/N = -(进入 I 与 I_q 的新增感染)。"""
    for P, s, i, sq, iq, r, c, q in _samples():
        ds, di, dsq, diq, dr = M.rhs_N(s, i, sq, iq, r, c, q, P)
        assert abs(ds + di + dsq + diq + dr) <= 1e-15 * (1 + abs(ds) + abs(di) + abs(dr))
        _, into_I, into_Iq, into_Sq = M.flows_N(s, i, c, q, P)
        assert math.isclose(ds + dsq, -(into_I + into_Iq), rel_tol=1e-14, abs_tol=1e-300)
        assert math.isclose(dsq, (1 - P.beta) / P.beta * into_Iq, rel_tol=1e-14, abs_tol=1e-300)
        assert min(into_I, into_Iq, into_Sq) >= 0.0
        assert math.isclose(di, into_I - P.gamma * i, rel_tol=1e-14, abs_tol=1e-300)


def test_no_return_term():
    """无回流：S_q 只有流入（ṡ_q ≥ 0），I = 0 时 S、S_q 都不变。"""
    for P, s, i, sq, iq, r, c, q in _samples(50):
        _, _, dsq, _, _ = M.rhs_N(s, i, sq, iq, r, c, q, P)
        assert dsq >= 0.0
        ds0, _, dsq0, _, _ = M.rhs_N(s, 0.0, sq, iq, r, c, q, P)
        assert ds0 == 0.0 and dsq0 == 0.0


@pytest.mark.parametrize('case', ['base', 'xian'])
def test_plateau_balance(case):
    """阈值弧控制 c = c0 x、q = 1-(1-q0)/(xz) 使 βc(1-q)S/N = γ（式 2.8），x = 1 时 q 为仅隔离控制的 q_c(S)。"""
    P = PR.CASES[case]
    for _ in range(200):
        z = random.uniform(1.0, 5.0)
        x = random.uniform(1.0 / z, 1.0)
        c, q = M.plateau_control(z, x, P)
        assert math.isclose(P.beta * c * (1 - q) * z * P.sc_N, P.gamma, rel_tol=1e-14)
        assert math.isclose(M.log_growth_rate(z * P.sc_N, c, q, P), 0.0, abs_tol=1e-15)
    for z in (1.0, 2.0, 4.0):
        c, q = M.plateau_control(z, 1.0, P)
        assert c == P.c0 and math.isclose(q, 1 - P.gamma * P.N / (P.beta * P.c0 * z * P.S_c), rel_tol=1e-14)


def test_intensities_and_cost():
    P = PR.BASE
    assert M.intensities(P.c0, P.q0, P) == (0.0, 0.0)
    uc, uq = M.intensities(0.5 * P.c0, 0.5, P)
    assert uc == 0.5 and math.isclose(uq, (0.5 - P.q0) / (1 - P.q0))
    assert M.intensities(1.1 * P.c0, 0.0, P) == (0.0, 0.0)          # (·)_+
    assert M.cost_rate(0.5, uq, 1.0, 2.0) == 0.25 + 2 * uq * uq
