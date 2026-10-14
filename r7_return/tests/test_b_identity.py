"""(b) 独立积分的累计新增感染与 U(0) - U(t) 之差除以 U(0) 小于 1e-8（在全部求解步上）。
累计感染是单独积分的状态 ∫F dt，不由 U(0) - U 定义。"""
import pytest

SETTINGS = [('q_only', 0.0, 'return', 0.0), ('opt_noreturn', 0.0, 'return', 0.0),
            ('c_only', 0.0, 'return', 0.0),
            ('q_only', 1 / 14, 'return', 0.0), ('opt_noreturn', 1 / 14, 'return', 0.0),
            ('c_only', 1 / 14, 'return', 0.0), ('q_only', 1 / 120, 'return', 0.0),
            ('q_only', 0.0, 'return', 1.0),
            ('q_only', 0.0, 'immediate', 0.0), ('opt_immediate', 0.0, 'immediate', 0.0)]
RUNS = [(c,) + s for c in ('base', 'xian') for s in SETTINGS]


@pytest.mark.parametrize('case,law,omega,model,xi', RUNS)
def test_U_identity(case, law, omega, model, xi, sim):
    r = sim(case, law, omega, model, xi)
    assert r['status'] == 'ok'
    assert r['identity_residual_rel'] < 1e-8
    assert r['mass_residual_abs'] < 1e-10
