"""由 NR-3 的结果 JSON 生成 paper/generated/nr_numbers.tex（只含 \\newcommand，宏名前缀 \\nr、只用字母）与
results/nr_numbers_map.json（每个宏的全精度值、显示格式、单位、来源文件与字段）。

只为 NR-3 新增的数字生成宏（初值诊断 N2、权重转折括区 N3、收敛与残差 N4、拟合误差 N5），
NR-5 为正文取整显示与补充 S6 收敛表追加的宏（括区的两位小数取整值 `...Apx`、`nrConvNzAllMaxRel` 等、`nrTdinnTolChange`），
NR-6 为补充 S3.1 的初值诊断表追加的宏（`nrICtab…`，六条轨迹各四个量），NR-7 为补充“隔离易感者回流”一节追加的宏（`nrRet…`：L、无回流 t→∞ 值、指数回流的终止时累计感染）。既有数字经 N1 核对与显示一致，
不为统一格式改宏。科学记数的宏写成 a\\times10^{b}，须在数学模式中使用。本步不在稿件中 \\input 本文件。

运行：conda run --no-capture-output -n thesis python nr_audit/make_numbers.py
"""
import json
import math
import re

from audit_common import RESULTS, ROOT, dump

OUT_TEX = ROOT / 'paper' / 'generated' / 'nr_numbers.tex'
MACROS = []


def load(name):
    return json.loads((RESULTS / name).read_text(encoding='utf-8'))


def fixed(v, d):
    return f'{v:.{d}f}'


def sci(v, sig=2):
    if v == 0:
        return '0'
    e = int(math.floor(math.log10(abs(v))))
    m = v / 10 ** e
    ms = f'{m:.{sig - 1}f}'
    if float(ms) >= 10:
        e += 1
        ms = f'{m / 10:.{sig - 1}f}'
    return f'{ms}\\times10^{{{e}}}'


def sci_up(v, sig=2):
    """科学记数，向上取整到 sig 位有效数字（用于“不超过”的上界）。"""
    e = int(math.floor(math.log10(abs(v))))
    m = math.ceil(round(v / 10 ** (e - sig + 1), 9))
    ms_val = m / 10 ** (sig - 1)
    if ms_val >= 10:
        e += 1
        ms_val /= 10
    return f'{ms_val:.{sig - 1}f}\\times10^{{{e}}}'


def add(name, value, text, unit, src_file, field, meaning):
    assert re.fullmatch(r'nr[A-Za-z]+', name), name
    MACROS.append(dict(macro='\\' + name, value=value, display=text, unit=unit, source=f'nr_audit/results/{src_file}',
                       field=field, meaning=meaning))


def main():
    ic = load('initial_condition.json')
    rows = {(r['law'], r['factor']): r for r in ic['rows']}
    for f, tag in ((0.1, 'Low'), (1.0, 'Fit'), (10.0, 'High')):
        r = rows[('q_only', f)]
        add(f'nrICtOne{tag}', r['state']['t1'], fixed(r['state']['t1'], 2), 'd', 'initial_condition.json',
            f'rows[law=q_only,factor={f}].state.t1', f'西安仅隔离控制的启动时刻 t1，I0 为拟合值的 {f:g} 倍')
    sh = max(abs(r['change_vs_fit']['t1_abs_days']) for r in ic['rows'])
    add('nrICtOneShift', sh, fixed(sh, 2), 'd', 'initial_condition.json', 'max |rows[].change_vs_fit.t1_abs_days|',
        'I0 改为 0.1 或 10 倍时 t1 的最大变化（两种控制相同）')
    span = ic['max_abs_relative_change']
    for key, tag in (('S_star', 'Sstar'), ('dt', 'Dt'), ('J', 'J')):
        v = max(span[l][key] for l in span)
        add(f'nrICMaxRel{tag}', v, sci(v), '', 'initial_condition.json', f'max over laws of max_abs_relative_change[*].{key}',
            f'六条轨迹中 {key} 相对拟合初值的最大相对变化')
    v = max(span[l]['total_infections_to_clearance'] for l in span)
    add('nrICMaxRelTotal', v, sci(v), '', 'initial_condition.json',
        'max over laws of max_abs_relative_change[*].total_infections_to_clearance', '六条轨迹中计至清零的总累计新增感染的最大相对变化')

    # NR-6：六条固定人口初值诊断的表（补充 S3.1）：t1、Δt、J、清零时间
    for law, lt in (('q_only', 'Q'), ('opt', 'O')):
        for f, tag in ((0.1, 'Low'), (1.0, 'Fit'), (10.0, 'High')):
            st = rows[(law, f)]['state']
            for key, kt, d, unit in (('t1', 'TOne', 2, 'd'), ('dt', 'Dt', 4, 'd'), ('J', 'J', 3, 'd'), ('t_end', 'Tend', 2, 'd')):
                add(f'nrICtab{lt}{tag}{kt}', st[key], fixed(st[key], d), unit, 'initial_condition.json',
                    f'rows[law={law},factor={f}].state.{key}', f'西安固定人口初值诊断表：{law}，I0 为拟合值的 {f:g} 倍，{key}')

    fit = load('fit_reconstruction.json')['at_fit_I0']
    for key, tag in (('community_new', 'CommNew'), ('quarantine_new', 'QuarNew'), ('community_cum', 'CommCum'),
                     ('quarantine_cum', 'QuarCum')):
        add(f'nrFitMse{tag}', fit['mse'][key], fixed(fit['mse'][key], 2), '例²', 'fit_reconstruction.json',
            f'at_fit_I0.mse.{key}', f'拟合初值下 {key} 的均方误差')
    add('nrFitObjective', fit['objective'], fixed(fit['objective'], 2), '例²', 'fit_reconstruction.json',
        'at_fit_I0.objective', '四项均方误差之和（拟合准则）')

    wb = load('weight_brackets.json')['cases']
    code = {'A': 'A', "A'": 'Ap', 'B': 'B', 'C': 'C', '?': 'Q'}
    for case, res in wb.items():
        cname = case.capitalize()
        for c in res['changes']:
            for b in c['brackets']:
                if b['status'] != 'resolved':
                    continue
                base = f"nrWt{cname}{code[b['from_']]}To{code[b['to']]}"
                for end in ('lo', 'hi'):
                    add(base + end.capitalize(), b[end], fixed(b[end], 4), '', 'weight_brackets.json',
                        f"cases.{case}.changes[grid {c['grid'][1]:.6f}–{c['grid'][2]:.6f}].brackets[{b['from_']}->{b['to']}].{end}",
                        f"{case}：结构由 {b['from_']} 变为 {b['to']} 的 r 括区{'下' if end == 'lo' else '上'}端（宽度 < 1e-3，所检验网格上）")
                mid = 0.5 * (b['lo'] + b['hi'])
                rd = round(mid, 2)
                assert b['lo'] - 0.005 <= rd <= b['hi'] + 0.005, (case, b)
                add(base + 'Apx', rd, fixed(rd, 2), '', 'weight_brackets.json',
                    f"cases.{case}.changes[grid {c['grid'][1]:.6f}–{c['grid'][2]:.6f}].brackets[{b['from_']}->{b['to']}].(lo+hi)/2 取两位小数",
                    f"{case}：结构由 {b['from_']} 变为 {b['to']} 的 r 括区中点取两位小数（正文用语“约”，不是括区端点）")

    cv = load('convergence.json')
    tol = max(max(r['max_rel_change_vs_base'].values()) for r in cv['tolerance_tiers'] if r['law'] not in ('tdinn', 'routine'))
    add('nrConvTolMaxRel', tol, sci(tol, 1), '', 'convergence.json', 'max tolerance_tiers[阈值策略].max_rel_change_vs_base',
        '积分容差三档间核心量的最大相对变化（阈值策略的全部轨迹）')
    nz = max(max(r['vs_8001']['4001']['dt_rel'], r['vs_8001']['4001']['J_rel']) for r in cv['state_grid'])
    add('nrConvNzMaxRel', nz, sci(nz, 1), '', 'convergence.json', 'max state_grid[].vs_8001[4001].{dt_rel,J_rel}',
        'N_z = 4001 与 8001 的 Δt、J 最大相对差')
    gap = max(max(r['max_gap_rel'].values()) for r in cv['control_grid'])
    add('nrConvNxMaxGap', gap, sci(gap, 1), '', 'convergence.json', 'max control_grid[].max_gap_rel',
        '控制网格上网格值低于根法值的最大相对量')
    for case, tag in (('base', 'Base'), ('xian', 'Xian')):
        r = next(r for r in cv['tolerance_tiers'] if r['case'] == case and r['law'] == 'q_only' and not r['capacity'])
        v = r['residuals']['base']['plateau_abs_dev']
        add(f'nrPlateauDev{tag}', v, sci(v), '人', 'convergence.json',
            f'tolerance_tiers[{case},q_only].residuals.base.plateau_abs_dev', f'{case} 仅隔离控制开环完整方程阈值控制期的 max|I-η|（基准档）')
    nzall = max(max(r['vs_8001'][k]['dt_rel'], r['vs_8001'][k]['J_rel']) for r in cv['state_grid'] for k in ('1001', '2001', '4001'))
    add('nrConvNzAllMaxRel', nzall, sci_up(nzall), '', 'convergence.json', 'max state_grid[].vs_8001[1001,2001,4001].{dt_rel,J_rel}',
        'N_z = 1001、2001、4001 与 8001 的 Δt、J 最大相对差')
    nzq = max(max(abs(r['values']['8001']['dt'] - r['values']['8001']['dt_quad']) / abs(r['values']['8001']['dt_quad']),
                  abs(r['values']['8001']['J'] - r['values']['8001']['J_quad']) / abs(r['values']['8001']['J_quad']))
              for r in cv['state_grid'])
    add('nrConvNzQuadMaxRel', nzq, sci_up(nzq), '', 'convergence.json', 'max state_grid[].values[8001] 与 quad 的 Δt、J 相对差',
        'N_z = 8001 的 Simpson 与分段 quad 的 Δt、J 最大相对差')
    thr = [r for r in cv['tolerance_tiers'] if r['law'] not in ('tdinn', 'routine')]
    pl = max(t['plateau_abs_dev'] for r in thr for t in r['residuals'].values())
    add('nrConvPlateauMax', pl, sci_up(pl), '人', 'convergence.json', 'max tolerance_tiers[阈值策略].residuals[*].plateau_abs_dev',
        '积分容差三档下阈值控制期 max|I-η| 的最大值')
    ex = max(abs(t['exit_S_error']) for r in thr for t in r['residuals'].values())
    add('nrConvExitMax', ex, sci_up(ex), '人', 'convergence.json', 'max |tolerance_tiers[阈值策略].residuals[*].exit_S_error|',
        '积分容差三档下退出时刻 S 与 S_c 之差的最大值')
    ms = max(t['mass_residual_persons'] for r in cv['tolerance_tiers'] for t in r['residuals'].values())
    add('nrConvMassMax', ms, sci_up(ms), '人', 'convergence.json', 'max tolerance_tiers[].residuals[*].mass_residual_persons',
        '积分容差三档下人口守恒残差的最大值（含常规控制与 TDINN）')
    reg = load('regression.json')
    tv = reg['old_implementation_numbers']['S6_tdinn_tolerance']['nr_audit']
    add('nrTdinnTolChange', tv, sci_up(tv), '人', 'regression.json', 'old_implementation_numbers.S6_tdinn_tolerance.nr_audit',
        '本模块收紧容差并把最大步长减半后，TDINN 总累计新增感染（清零时间）的变化')
    idr = max(max(t['identity_residual_rel'] for t in r['residuals'].values()) for r in cv['tolerance_tiers'])
    add('nrIdentityMaxRel', idr, sci(idr, 1), '', 'convergence.json', 'max tolerance_tiers[].residuals[*].identity_residual_rel',
        '累计新增感染恒等式残差/初始易感者总数的最大值')

    # NR-7（G-N3 方案 B）：补充材料“隔离易感者回流”一节的数字。
    # 无回流 t→∞ 值、L 与计至清零值来自本模块的独立复核（noreturn_inf_crosscheck.json）；
    # 指数回流的终止时累计感染自回流分支固定提交导入（return_import.json，不重算）。西安的人数以 10^6 人为单位。
    cc = load('noreturn_inf_crosscheck.json')
    crow = {(r['case'], r['law']): r for r in cc['rows']}
    for case, tag, scale, dec in (('base', 'Base', 1.0, 2), ('xian', 'Xian', 1e6, 4)):
        L0 = crow[(case, 'q_only')]['L']
        add(f'nrRetL{tag}', L0 / scale, fixed(L0 / scale, dec), '人' if scale == 1 else '10^6 人', 'noreturn_inf_crosscheck.json',
            f'rows[case={case}].L', f'{case}：L = U(0) − S_c = S_0 + S_q(0) − S_c')
        for law, lt in (('q_only', 'Q'), ('alpha', 'A'), ('opt', 'O'), ('c_only', 'C')):
            r = crow[(case, law)]
            add(f'nrRetCinf{tag}{lt}', r['C_inf'] / scale, fixed(r['C_inf'] / scale, dec), '人' if scale == 1 else '10^6 人',
                'noreturn_inf_crosscheck.json', f'rows[case={case},law={law}].C_inf',
                f'{case}：无回流（ω=0）{law} 的 t→∞ 累计新增感染 C_π(0)')
            if law in ('q_only', 'opt', 'c_only'):
                add(f'nrRetClr{tag}{lt}', r['C_to_clearance'] / scale, fixed(r['C_to_clearance'] / scale, 1 if scale == 1 else 4),
                    '人' if scale == 1 else '10^6 人', 'noreturn_inf_crosscheck.json', f'rows[case={case},law={law}].C_to_clearance',
                    f'{case}：无回流 {law} 计至清零时间的累计新增感染（表 2）')
    ri = load('return_import.json')
    for case, tag, scale, dec in (('base', 'Base', 1.0, 2), ('xian', 'Xian', 1e6, 4)):
        for s, st in ((7, 'Seven'), (14, 'Fourteen'), (30, 'Thirty')):
            for law, lt in (('q_only', 'Q'), ('opt_noreturn', 'M'), ('c_only', 'C')):
                v = ri['runs'][f'{case}|{s}|{law}']['C_term']
                add(f'nrRetTerm{tag}{st}{lt}', v / scale, fixed(v / scale, dec), '人' if scale == 1 else '10^6 人',
                    'return_import.json', f'runs[{case}|{s}|{law}].C_term',
                    f'{case}：指数回流 1/ω={s} d，{law}，终止时（退出后首次 I<1）累计新增感染；来源见 source')

    # 宏名不得与稿件中已有的定义重名
    existing = set()
    for f in list((ROOT / 'paper').glob('*.tex')) + list((ROOT / 'paper').glob('*/*.tex')) + list((ROOT / 'paper').glob('*.cls')):
        if f.resolve() == OUT_TEX.resolve():
            continue
        existing |= set(re.findall(r'\\(?:newcommand|def|renewcommand)\s*\{?\\([A-Za-z]+)', f.read_text(encoding='utf-8', errors='ignore')))
    clash = [m['macro'] for m in MACROS if m['macro'][1:] in existing]
    assert not clash, clash
    assert len({m['macro'] for m in MACROS}) == len(MACROS)
    OUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    lines = ['% 由 nr_audit/make_numbers.py 生成，勿手改。字段映射见 nr_audit/results/nr_numbers_map.json。',
             '% 含 \\times 的宏须在数学模式中使用。']
    lines += [f"\\newcommand{{{m['macro']}}}{{{m['display']}}}  % {m['meaning']}" for m in MACROS]
    OUT_TEX.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    dump('nr_numbers_map.json', dict(tex='paper/generated/nr_numbers.tex', n_macros=len(MACROS), macros=MACROS))
    print(f'写出 {OUT_TEX.relative_to(ROOT)}：{len(MACROS)} 个宏')


if __name__ == '__main__':
    main()
