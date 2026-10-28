"""有回流优化的代数身份与配点规则核验；不启动任何OCP。"""
import sys
import numpy as np
import pytest
sys.dont_write_bytecode=True
from collocation import radau
from evaluate import load_params


@pytest.mark.parametrize('case',['base','xian'])
def test_plateau_reduction_and_infection_flow(case):
    p=load_params(case)
    sc,theta=p['sc_N'],p['theta']
    for s in [sc,1.1*sc,.5*(sc+1),.99]:
        for lam in [0.,.17,.5,.93,1.]:
            c=p['c0']*(sc/s+lam*(1-sc/s))
            q=1-p['gamma']/(p['beta']*c*s)
            assert p['q0']-1e-14<=q<1
            assert abs(p['beta']*c*(1-q)*s-p['gamma'])<1e-14
            sq=.04
            F=p['beta']*c*s*theta
            A=(1-p['beta'])*c*q*s*theta
            original=np.array([-F-A+p['omega']*sq,A-p['omega']*sq])
            h=p['c0']*theta*lam*(s-sc)
            D=p['c0']*(p['beta']+(1-p['beta'])*p['q0'])*sc*theta
            B=(1-p['beta'])*p['c0']*p['q0']*sc*theta
            reduced=np.array([-D+p['omega']*sq-h,B-p['omega']*sq+(1-p['beta'])*h])
            np.testing.assert_allclose(original,reduced,atol=2e-16,rtol=1e-12)
            assert abs(sum(reduced)+F)<2e-16
            expected_cost=(1-c/p['c0'])**2+2*((q-p['q0'])/(1-p['q0']))**2
            x=c/p['c0']
            assert abs(expected_cost-((1-x)**2+2*(1-sc/(x*s))**2))<1e-13


def test_radau_polynomial_consistency():
    nodes,C,D,B=radau(3)
    for power in range(4):
        values=nodes**power
        expected=np.zeros(4) if power==0 else power*nodes**(power-1)
        np.testing.assert_allclose(values@C,expected,atol=2e-13)
        assert abs(values@D-1)<2e-13
        assert abs(values@B-1/(power+1))<2e-13


@pytest.mark.parametrize('case',['base','xian'])
def test_terminal_cumulative_includes_all_phases(case):
    p=load_params(case)
    u0=(p['S0']+p['Sq0'])/p['N']
    u1=.9*u0
    u2=p['sc_N']+.03
    uend=.9*p['sc_N']
    assert abs((u0-u1)+(u1-u2)+(u2-uend)-(u0-uend))<1e-15

