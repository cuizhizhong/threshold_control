"""数字来源：参数、初值、能力代表点、参照数据与复用代码的来源（路径、字段、SHA-256）。

运行（仓库根目录）：
    conda run --no-capture-output -n thesis python nr_audit/sources.py
写出 nr_audit/results/source_manifest.json。本脚本只读取下列来源文件，不写入它们所在的目录。
tests/test_sources.py 逐项核对：来源文件的 SHA-256 与清单一致；params.py 中的每个数值与来源字段逐位相等；
参照数据的列存在。参照数据（原 joint_extra 的全精度输出）只用于回归核对，不作为本模块的输入。
"""
import csv
import hashlib
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'results' / 'source_manifest.json'

JOINT_EXTRA = 'reproducibility/results/20261005_sec7_v2_refinement/joint_extra'
XIAN_DIR = 'reproducibility/results/20261003_release_final/xian'

# 参数与初值：params.py 中的字段 ← (来源 id, 字段路径)
PARAM_SOURCES = {
    'base': {
        'N': ('baseline_parameters', 'parameters.N'), 'S0': ('baseline_parameters', 'parameters.S0'),
        'I0': ('baseline_parameters', 'parameters.I0'), 'beta': ('baseline_parameters', 'parameters.beta'),
        'gamma': ('baseline_parameters', 'parameters.gamma'), 'delta_q': ('baseline_parameters', 'parameters.delta_q'),
        'c0': ('baseline_parameters', 'parameters.c0'), 'q0': ('baseline_parameters', 'parameters.q0'),
        'eta': ('baseline_parameters', 'parameters.eta'), 'wc': ('baseline_parameters', 'parameters.wc'),
        'wq': ('baseline_parameters', 'parameters.wq'), 'Sq0': ('baseline_parameters', 'other_initial_states.Sq0'),
        'Iq0': ('baseline_parameters', 'other_initial_states.Iq0'), 'R0': ('baseline_parameters', 'other_initial_states.R0'),
    },
    'xian': {
        'N': ('xian_reference', 'parameters.N'), 'beta': ('xian_reference', 'parameters.beta'),
        'gamma': ('xian_reference', 'parameters.gamma'), 'delta_q': ('xian_reference', 'parameters.delta_q'),
        'c0': ('xian_reference', 'parameters.c0'), 'q0': ('xian_reference', 'parameters.q0'),
        'I0': ('xian_reference', 'I0_abs'), 'S0': ('xian_fit', 'S0'), 'R0': ('xian_fit', 'R0_initial'),
    },
}
# 不在来源文件中逐字出现、由定义给出的量（记录规则，测试按规则核对）
DERIVED_RULES = {
    'base': {'eta': 'η = 0.05N（稿件表 1）；与 baseline_parameters.json 的 38.15 逐位相等'},
    'xian': {'eta': 'η = 0.002N = 26326（设计情景，稿件表 1；原 joint_extra 的 load_inputs 同此）',
             'S0': 'S0 = N - I0（稿件表 1；与 fit.json 的 S0 逐位相等）',
             'Sq0': 'S_q(0) = 0（稿件表 1）', 'Iq0': 'I_q(0) = 0（稿件表 1）',
             'wc': '默认权重 w_c = 1（稿件第 2.4 节）', 'wq': '默认权重 w_q = 2（稿件第 2.4 节）'},
}

FILES = {
    'baseline_parameters': ('joint_control/threshold_control_reproducible_release_20261002/numerics/inputs/'
                            'baseline_parameters.json', '基准参数与初值（原 joint_extra 的输入）'),
    'xian_reference': (f'{XIAN_DIR}/reference.json', '西安参数与未取整拟合初值 I0_abs'),
    'xian_fit': (f'{XIAN_DIR}/fit.json', '西安拟合输出（I0、S0 = N - I0、R0）'),
    'audit_notes': ('reproducibility/manuscript_audit_notes.md', '“拟合初值 I0=0.00100659188867187，计算不使用论文显示的取整数”'),
    'table1': ('paper/sections/06_numerics.tex', '稿件表 1（tab:xian_initial_fit）与图 6 图注（能力代表点）'),
    'model_section': ('paper/sections/02_model.tex', '默认权重 w_c = 1、w_q = 2（式 2.13 之后）'),
    'compare_baseline': (f'{JOINT_EXTRA}/compare_baseline.csv', '回归参照：基准四种控制（原表 2 的全精度来源）'),
    'compare_xian': (f'{JOINT_EXTRA}/compare_xian.csv', '回归参照：西安四种控制'),
    'input_manifest': (f'{JOINT_EXTRA}/input_manifest.json', '原 joint_extra 的输入与派生量'),
    'capacity': (f'{JOINT_EXTRA}/capacity.json', '能力代表点（point 字段）与其成本最优控制的指标'),
    'phase': (f'{JOINT_EXTRA}/phase.json', '权重网格上的切换位置（回归核对用的几个 r）'),
    'frontier': (f'{JOINT_EXTRA}/frontier_baseline.csv', 'J + κΔt 的最小化解（回归核对用的几个 κ；N1 的 11.09 d）'),
    # NR-3 增加
    'xian_raw_data': ('真实数据/Xianguankong.xlsx', 'N5：西安原始日报（社区、隔离发现的日新增）'),
    'xian_observed': (f'{XIAN_DIR}/observed.csv', 'N5：原程序处理后的观测序列（与原始表格逐项核对）'),
    'xian_code': ('reproducibility/xian.py', 'N5：拟合准则（fit_initial）与 TDINN 函数（controls）的原定义，只读'),
    'xian_loader': ('xian_control_comparison/xian_control_comparison.py', 'N5：观测数据的处理规则（load_observed_data），只读'),
    'c0_code': ('reproducibility/c0.py', 'N1：补充 S5 代表点 c0 的取法（触发边界 ×1.03、拐点边界 +0.05），只读'),
    'c0_representative': ('reproducibility/results/20261003_release_final/c0/representative_summary.csv',
                          'N1：补充 S5 代表点的原结果（核对用）'),
    # 证据 ID 与 use 的 NR 历史说明保持；NEW-4g 现行定位及分拆见独立路径迁移收据。
    'numerics_S1': ('paper/supplement_sections/S2_single_control.tex', 'N1：补充表 S1'),
    'numerics_S2': ('paper/supplement_sections/S3_inflection.tex', 'N1：补充 S2 的 q0†'),
    'xian_S3': ('paper/supplement_sections/S6_xian.tex', 'N1、N5：补充表 S2、S3'),
    'contact_S5': ('paper/supplement_sections/S2_single_control.tex', 'N1：补充 S5'),
    'numerics_S6': ('paper/supplement_sections/S8_numerics.tex', 'N1、N3：补充 S6 与表 S5'),
    'xian_chapter': ('paper/sections/07_xian.tex', 'N1：第 7 章与表 3'),
}

# 复用的代码：nr_audit 文件 ← 回流分支 research/return-effects 的提交 bb52b96（R7-3，G2 通过）
REUSE_COMMIT = 'bb52b965a8cd98dd07a5c41b9997dae433128756'
CODE_REUSE = [
    dict(file='params.py', source='r7_return/params.py', blob='b5467aae6b2bd824ad1d508ffb589e52f61eee21',
         change='删去回流专用的 L_bound、omega_from_stay；增加常规轨迹派生量与能力约束代表点；数值未改'),
    dict(file='model.py', source='r7_return/model.py', blob='810bf85c74350bb2cd78c43d70198857e1f0812f',
         change='只保留 ω = 0；成本被积函数改为式 (2.13) 的 (·)_+ 形式；增加线性强度'),
    dict(file='allocation.py', source='r7_return/alloc.py', blob='034e6207b6befb5dbc9755fc42c8f51bfbd07daa',
         change='只保留无回流；扩展为一般权重、κ、能力约束区间、缩放坐标 y、牛顿修正与重根诊断、'
                '带局部加密的 N_x 网格核对、异常括区（同类型跳变与陡峭点）与退出附近的对数网格'),
    dict(file='state_integrals.py', source='r7_return/endpoints.py', blob='345eb9f1895c0e4e9ed06c2d1b5b80244083ab1c',
         change='只保留无回流的启动状态与分段 Simpson/quad；增加 J_c、J_q、t1、退出后、闭式与 Policy 分段'),
    dict(file='simulate.py', source='r7_return/simulate.py', blob='c088330c9c532ebc28963657d861588b0e3219ec',
         change='只复用 ω = 0 的 analytic_tail；事件法（阈值弧上代数令 I ≡ η、状态反馈控制）未复用，'
                '改为新写的开环完整方程'),
]
# 参照但未复制、未运行的原代码
CODE_CONSULTED = [
    dict(path='reproducibility/joint_extra/core.py', use='缩放坐标 y 的驻点多项式写法、t1 的换元、名义时钟分段的思路'),
]


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def get_field(obj, dotted):
    for key in dotted.split('.'):
        obj = obj[key]
    return obj


def load_json(fid):
    return json.loads((ROOT / FILES[fid][0]).read_text(encoding='utf-8'))


def read_csv(fid):
    with open(ROOT / FILES[fid][0], encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def git_blob(path):
    """当前工作区文件的 git blob 哈希（与提交中的 blob 对照）。"""
    try:
        return subprocess.run(['git', 'hash-object', str(path)], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return None


def build():
    import params as PR
    # 只读目录中的数据文件固定 SHA-256（测试核对）；稿件文件会在后续步骤修改，只记录生成清单时的值
    files = {fid: dict(path=p, sha256=sha256(ROOT / p), use=u, pinned=not p.startswith('paper/'))
             for fid, (p, u) in FILES.items()}
    params = {}
    for case, P in PR.CASES.items():
        rows = {}
        for name in ('N', 'S0', 'I0', 'beta', 'gamma', 'delta_q', 'c0', 'q0', 'eta', 'Sq0', 'Iq0', 'R0', 'wc', 'wq'):
            val = getattr(P, name)
            src = PARAM_SOURCES[case].get(name)
            row = dict(value=val, unit=_unit(name))
            if src:
                fid, fld = src
                row.update(source=fid, field=fld, source_value=get_field(load_json(fid), fld))
            if name in DERIVED_RULES.get(case, {}):
                row['rule'] = DERIVED_RULES[case][name]
            rows[name] = row
        params[case] = rows
    cap = load_json('capacity')
    capacity = {case: dict(c_min=PR.REP_CAPACITY[case].c_min, q_cap=PR.REP_CAPACITY[case].q_cap,
                           source='capacity', field=f'{key}.point',
                           source_value=cap[key]['point'], caption='图 6 图注：c_min/c0 = 0.5、q_cap = '
                           + ('0.6' if case == 'base' else '0.75'))
                for case, key in (('base', 'baseline'), ('xian', 'xian'))}
    reuse = [dict(r, source_branch='research/return-effects', source_commit=REUSE_COMMIT) for r in CODE_REUSE]
    return dict(description='nr_audit 的数字来源清单（NR-2）。参数与初值逐位取自来源字段；参照数据只用于回归核对。',
                normalization='完整方程按 N 归一（s = S/N 等）；控制律与 S 坐标求积按 S_c 归一（z = S/S_c、x = c/c0）',
                units=dict(population='人', time='天', rates='d^-1', J='天（二次干预强度成本，式 2.13）'),
                files=files, parameters=params, capacity_points=capacity, code_reuse=reuse,
                code_consulted=CODE_CONSULTED)


def _unit(name):
    return {'N': '人', 'S0': '人', 'I0': '人', 'eta': '人', 'Sq0': '人', 'Iq0': '人', 'R0': '人',
            'gamma': 'd^-1', 'delta_q': 'd^-1', 'c0': 'd^-1'}.get(name, '无量纲')


def main():
    import sys
    sys.path.insert(0, str(HERE))
    man = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'写出 {OUT.relative_to(ROOT)}（{len(man["files"])} 个来源文件）')


if __name__ == '__main__':
    main()
