"""pytest 公共设置：把 r7_return/ 加入导入路径，并缓存事件法轨迹（同一组参数只算一次）。"""
import os
import sys
from functools import lru_cache

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import params  # noqa: E402
import simulate  # noqa: E402


@lru_cache(maxsize=None)
def _run_cached(case, law, omega, model, xi):
    return simulate.run(params.CASES[case], law, omega=omega, model=model, xi=xi)


@pytest.fixture(scope='session')
def sim():
    """sim(case, law, omega=0.0, model='return', xi=0.0) -> 事件法结果（会话内缓存）。"""
    def f(case, law, omega=0.0, model='return', xi=0.0):
        return _run_cached(case, law, float(omega), model, float(xi))
    return f
