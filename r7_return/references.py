"""参考值（只读）。

1. 无回流（ω = 0）全精度参考：直接读取
   reproducibility/results/20261005_sec7_v2_refinement/joint_extra/compare_{baseline,xian}.csv
   与 input_manifest.json（稿件表 2 的计算来源；与 joint_integration_20261004 中同名文件逐字节相同）。
   计至清零的总累计感染（total_infections）与控制期感染（plateau_infections_state）是两个量，分开存。
2. 稿件表 2（tab:joint:compare，paper/sections/06_numerics.tex）的展示值：已按各列精度舍入，
   只用于检查舍入一致。
3. 执行计划第 5 节的参考数（立即返回 S 坐标求积、无回流 t→∞ 核算、旧反馈实现 1/ω = 14 d、
   释放用数）：照抄自 ai/R7_回流修订_分步执行计划.md，保留原有效位数。
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
JOINT_EXTRA = os.path.join(ROOT, 'reproducibility', 'results', '20261005_sec7_v2_refinement', 'joint_extra')

STRATEGY_TO_LAW = {'quarantine_only': 'q_only', 'alpha_0.5': 'alpha',
                   'minimum_cost': 'opt_noreturn', 'contact_only': 'c_only'}
CASE_FILE = {'base': 'baseline', 'xian': 'xian'}
LAWS_NORETURN = ('q_only', 'alpha', 'opt_noreturn', 'c_only')


def load_noreturn_refs():
    """返回 {(case, law): dict(dt, J, t1, t2, t_end, total_infections_to_clearance,
    plateau_infections, Sq_new)} 与 {case: 派生量(Sc, Sbar, Sstar, t1, S_end, tail)}。"""
    refs = {}
    for case, fname in CASE_FILE.items():
        path = os.path.join(JOINT_EXTRA, f'compare_{fname}.csv')
        with open(path, encoding='utf-8-sig', newline='') as fh:
            for row in csv.DictReader(fh):
                law = STRATEGY_TO_LAW[row['strategy']]
                refs[(case, law)] = dict(
                    dt=float(row['duration']), J=float(row['J']),
                    t1=float(row['t1']), t2=float(row['t2']), t_end=float(row['t_end']),
                    total_infections_to_clearance=float(row['total_infections']),
                    plateau_infections=float(row['plateau_infections_state']),
                    Sq_new=float(row['Sq_increment_plateau_state']))
    with open(os.path.join(JOINT_EXTRA, 'input_manifest.json'), encoding='utf-8') as fh:
        man = json.load(fh)
    derived = {case: man['cases'][fname]['derived'] for case, fname in CASE_FILE.items()}
    return refs, derived


# 稿件表 2 的展示值：(Δt, t_end, 总累计新增感染, 阈值控制期新增隔离易感者, J)
# 小数位：Δt 2，t_end 2，基准人数 1 位、西安以 10^6 人计 4 位，J 4 位。
TABLE2_DISPLAY = {
    ('base', 'c_only'): (36.26, 64.13, 628.6, 40.9, 11.9390),
    ('base', 'alpha'): (9.24, 37.11, 323.4, 346.2, 2.5462),
    ('base', 'q_only'): (5.90, 33.77, 285.7, 383.9, 2.2236),
    ('base', 'opt_noreturn'): (7.75, 35.62, 306.6, 363.0, 2.1183),
    ('xian', 'c_only'): (308.79, 481.83, 3.8566, 6.5004, 109.3648),
    ('xian', 'alpha'): (124.57, 297.60, 2.6390, 7.7180, 44.5286),
    ('xian', 'q_only'): (85.07, 258.10, 2.3779, 7.9791, 40.7686),
    ('xian', 'opt_noreturn'): (108.81, 281.84, 2.5348, 7.8222, 38.0209),
}
TABLE2_DECIMALS = {'base': (2, 2, 1, 1, 4), 'xian': (2, 2, 4, 4, 4)}
TABLE2_UNIT = {'base': 1.0, 'xian': 1e6}     # 人数列的单位


# 执行计划第 5 节：立即返回对照模型（S 坐标求积）
PLAN_IMMEDIATE = {
    ('base', 'q_only'): dict(dt=18.104, J=9.4077),
    ('base', 'alpha'): dict(dt=23.994, J=8.9893),
    ('base', 'opt_immediate'): dict(dt=23.551, J=8.2376),
    ('base', 'c_only'): dict(dt=39.584, J=13.106),
    ('xian', 'q_only'): dict(dt=384.26, J=213.18),
    ('xian', 'alpha'): dict(dt=515.36, J=211.14),
    ('xian', 'opt_immediate'): dict(dt=493.58, J=189.69),
    ('xian', 'c_only'): dict(dt=882.91, J=314.65),
}
PLAN_IMMEDIATE_STATE = {
    'base': dict(S_star_inf=712.512, S_c=175.160, infections=537.35),
    'xian': dict(S_star_inf=1.31127e7, S_c=2.97413e6, infections=1.01386e7),
}
PLAN_IMMEDIATE_SWITCH_Z = 3.000
PLAN_IMMEDIATE_TERMINAL_SHARE = 0.667

# 执行计划第 5 节：无回流全程对照（ω = 0）与 R2 下界
PLAN_NORETURN_INF = {'base': 286.590, 'xian': 2.37795e6}     # 仅隔离控制，t→∞
PLAN_NORETURN_INF_INCREMENT = {'base': 0.865, 'xian': 4.5}   # 清零之后的增量（约）
PLAN_L_BOUND = {'base': 586.840, 'xian': 1.01889e7}

# 执行计划第 5 节：旧反馈实现，平均停留 14 天（基准 dt=0.005、西安 dt=0.05，一次性退出）
PLAN_OMEGA14_OLD = {
    ('base', 'q_only'): dict(dt=19.21, J=2.823, C_end=619.5),
    ('base', 'opt_noreturn'): dict(dt=21.81, J=2.842, C_end=620.5),
    ('base', 'c_only'): dict(dt=38.48, J=12.58, C_end=665.8),
    ('xian', 'q_only'): dict(dt=425.25, J=192.89, C_end=1.045e7),
    ('xian', 'opt_noreturn'): dict(dt=484.65, J=176.88, C_end=1.045e7),
    ('xian', 'c_only'): dict(dt=857.25, J=299.48, C_end=1.045e7),
}
PLAN_XIAN_QONLY_DT_OTHER = {7: 407.1, 30: 452.1}      # 平均停留 7、30 天，西安仅隔离

# 执行计划第 5 节：在 t2 释放（ω = 0，仅隔离控制）
PLAN_RELEASE = {'base': dict(Sq_over_Sc=2.215, Re=3.22), 'xian': dict(Sq_over_Sc=2.714, Re=3.71)}
