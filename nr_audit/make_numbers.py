"""由 NR-3 的结果 JSON 生成 paper/generated/nr_numbers.tex（只含 \\newcommand，宏名前缀 \\nr、只用字母）与
results/nr_numbers_map.json（每个宏的全精度值、显示格式、单位、来源文件与字段）。

只为 NR-3 新增的数字生成宏（初值诊断 N2、权重转折括区 N3、收敛与残差 N4、拟合误差 N5）。既有数字经 N1 核对与显示一致，
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
    idr = max(max(t['identity_residual_rel'] for t in r['residuals'].values()) for r in cv['tolerance_tiers'])
    add('nrIdentityMaxRel', idr, sci(idr, 1), '', 'convergence.json', 'max tolerance_tiers[].residuals[*].identity_residual_rel',
        '累计新增感染恒等式残差/初始易感者总数的最大值')

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
