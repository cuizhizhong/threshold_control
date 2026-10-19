"""尾界适用边界与显示方向，避免把数值约数当作上界。"""
import math
import pytest
import params as PR
from audit_return_endpoint import remaining_bound


def test_bound_requires_strict_subcritical_total():
    P=PR.BASE
    assert remaining_bound(P,P.S_c,1)['applicable'] is False
    assert remaining_bound(P,2*P.S_c,1)['B_persons'] is None
    v=remaining_bound(P,0.5*P.S_c,1)
    assert v['decay_rate'] == 0.5*P.gamma
    assert v['B_persons'] == pytest.approx(P.beta*P.c0*P.S_c/(P.N*P.gamma))


def test_zero_infection_has_zero_tail():
    assert remaining_bound(PR.BASE,PR.BASE.S_c/2,0)['B_persons']==0


@pytest.mark.parametrize('u,i', [(math.nan,1),(1,math.inf),(-1,1),(1,-1)])
def test_invalid_endpoint_rejected(u,i):
    with pytest.raises(ValueError):
        remaining_bound(PR.BASE,u,i)
