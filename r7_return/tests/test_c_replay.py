"""(c) 事件法与反馈重放（旧实现的复制）的 Δt、J 相对差 < 1e-2；退出后控制不再开启。
这是两种实现的交叉核对，不是真值。"""
import pytest

import alloc as AL
import replay_feedback as RF
from params import CASES

RUNS = [(c, l, w) for c in ('base', 'xian') for w in (0.0, 1 / 14)
        for l in ('q_only', 'opt_noreturn', 'c_only')]


@pytest.mark.parametrize('case,law,omega', RUNS)
def test_event_vs_replay(case, law, omega, sim):
    P = CASES[case]
    ev = sim(case, law, omega)
    rp = RF.replay(P, AL.get_law(law, P), omega)
    assert ev['status'] == 'ok' and rp['t2'] is not None
    assert abs(rp['dt_ctrl'] - ev['dt']) / ev['dt'] < 1e-2
    assert abs(rp['J'] - ev['J']) / ev['J'] < 1e-2
    # 退出后控制不再开启：事件法只有一个阈值弧阶段，此后为常规阶段；重放只有一段控制
    assert ev['phases'] == ['routine', 'plateau', 'post']
    assert rp['n_episodes'] == 1
