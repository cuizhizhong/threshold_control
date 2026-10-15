"""pytest 公共设置：把 nr_audit/ 加入导入路径；缓存 Policy、状态路径与开环轨迹（同一组设置只算一次）；
读取回归参照（原 joint_extra 的全精度输出，只读）。容差集中在 TOL，README 第 6 节逐项说明。"""
import csv
import json
import os
import sys
from functools import lru_cache

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import params as PR  # noqa: E402
import simulate as SM  # noqa: E402
import sources as SRC  # noqa: E402
import state_integrals as SI  # noqa: E402

# ---------------------------------------------------------------- 容差（判据）
TOL = dict(
    reg_rel=1e-4,          # 与可追溯的旧全精度结果回归（NR 计划 5.2 节的验收目标）
    closed_rel=1e-9,       # 闭式与 S 坐标求积（Simpson，N_z = 4001）
    quad_rel=1e-10,        # Simpson 与 quad 互核
    path_rel=1e-8,         # 完整方程开环路径与状态路径
    ident_rel=1e-8,        # 累计量恒等式残差 / 初始易感者总数（NR 计划 5.2 节）
    mass_rel=1e-12,        # |S+I+S_q+I_q+R-N| / N
    min_comp=-1e-8,        # 仓室下限（人）
    plateau_rel=1e-8,      # 开环阈值弧上 max|I-η|/η
    feas_abs=1e-12,        # 控制界限（c/c0 与 q）的越界量
    balance=1e-12,         # 名义状态上 βc(1-q)S/(γN) - 1
    event_rel=1e-9,        # 触发、退出事件的相对残差；t1 与求积对照
    clear_abs=1e-8,        # |I(t_end) - 1|（人）
    grid_gap=1e-12,        # 网格值低于根法值的相对量（根法漏解的判据）
    root_rel=1e-12,        # Lambert W 与 brentq
)

CASES = ('base', 'xian')
LAWS = ('q_only', 'c_only', 'alpha', 'opt')
STRATEGY = {'q_only': 'quarantine_only', 'c_only': 'contact_only', 'alpha': 'alpha_0.5', 'opt': 'minimum_cost'}
CASE_FILE = {'base': 'compare_baseline', 'xian': 'compare_xian'}


def rel(a, b):
    return abs(a - b) / abs(b)


def key_args(cap=False, wq=None, kappa=0.0):
    return (bool(cap), wq, float(kappa))


@lru_cache(maxsize=None)
def policy(case, law, cap=False, wq=None, kappa=0.0):
    P = PR.CASES[case]
    return SI.Policy(P, law, cap=PR.REP_CAPACITY[case] if cap else None, wq=wq, kappa=kappa)


@lru_cache(maxsize=None)
def state(case, law, cap=False, wq=None, kappa=0.0):
    return SI.state_path(policy(case, law, cap, wq, kappa))


@lru_cache(maxsize=None)
def ode(case, law, cap=False, wq=None, kappa=0.0):
    return SM.run(policy(case, law, cap, wq, kappa))


@lru_cache(maxsize=None)
def compare_refs():
    out = {}
    for case, fid in CASE_FILE.items():
        for row in SRC.read_csv(fid):
            out[(case, row['strategy'])] = {k: float(v) for k, v in row.items()
                                            if k not in ('case', 'strategy', 'clearance_direction_ok', 'passed')
                                            and _isfloat(v)}
    return out


def _isfloat(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


@lru_cache(maxsize=None)
def capacity_ref():
    return SRC.load_json('capacity')


def slow_if_xian(case, law='', cap=False):
    """西安的成本最优控制与能力约束轨迹标为 slow。"""
    return [pytest.mark.slow] if case == 'xian' and (law == 'opt' or cap) else []


def case_law_params(laws=LAWS):
    return [pytest.param(c, l, marks=slow_if_xian(c, l), id=f'{c}-{l}') for c in CASES for l in laws]
