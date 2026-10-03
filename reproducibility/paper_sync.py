"""由本次计算结果同步新稿；冻结稿、历史计算和正式稿均不在写入范围内。

仅替换有变量来源绑定的数字或完整数据行，不遍历全文猜测小数含义。
返回主稿、补充稿及逐项记录；数字一致不等于理论证明或版面验收。
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import re


RELEASE = Path('ai/threshold_control_reproducible_release_20261002/latex')


def _json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def _csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def _f(value, places=2):
    return f'{float(value):.{places}f}'


def _i(value):
    return str(int(math.floor(float(value) + .5)))


def _sci(value, places=2):
    value = float(value)
    exponent = math.floor(math.log10(abs(value)))
    return f'{value / 10**exponent:.{places}f}' + r'\times10^{' + str(exponent) + '}'


class _Editor:
    def __init__(self, main, si):
        self.documents = {'main': main, 'supplement': si}
        self.changes = []
        self.cells = []

    def replace(self, document, old, new, source, anchor, *, expected=1, raw=None):
        text = self.documents[document]
        count = text.count(old)
        if count == 0 or (expected is not None and count != expected):
            raise ValueError(f'{document}: {anchor}: 预期 {expected} 处，实际 {count} 处: {old[:90]}')
        self.documents[document] = text.replace(old, new)
        self.changes.append(dict(document=document, anchor=anchor, old=old, new=new,
                                 source=source, occurrences=count, changed=old != new,
                                 unrounded_value=raw))

    def token(self, document, old, new, source, anchor, *, raw=None):
        # 西安数值及其应用附录内的独有参照值；不会触及证明中同名小数。
        text = self.documents[document]
        if document == 'main':
            split = text.index(r'\section{西安疫情背景下的策略比较}') if r'\section{西安疫情背景下的策略比较}' in text else text.index(r'\label{sec:xian}')
            prefix, text = text[:split], text[split:]
            # 后续理论证明中的示例参数不得成为替换目标。
            end = text.find('% ===== theory_appendices')
            if end < 0:
                end = text.find(r'\section{常规阶段首次积分')
            body, tail = (text[:end], text[end:]) if end >= 0 else (text, '')
        else:
            prefix, body, tail = '', text, ''
        pattern = r'(?<![\d.])' + re.escape(old) + r'(?![\d.])'
        count = len(re.findall(pattern, body))
        if not count:
            raise ValueError(f'未找到绑定参照值 {anchor}: {old}')
        body = re.sub(pattern, lambda _: new, body)
        self.documents[document] = prefix + body + tail
        self.changes.append(dict(document=document, anchor=anchor, old=old, new=new,
                                 source=source, occurrences=count, changed=old != new,
                                 unrounded_value=raw, scope='xian_numeric_and_application_appendices'))

    def line(self, document, starts, new, source, anchor, *, raw=None):
        lines = self.documents[document].splitlines()
        selected = [line for line in lines if line.startswith(starts)]
        if len(selected) != 1:
            raise ValueError(f'完整行定位 {anchor}: {len(selected)} 处')
        self.replace(document, selected[0], new, source, anchor, raw=raw)

    def row(self, document, label, prefix, values, raw, keys, source, *, prefix_value=None, prefix_key=None):
        text = self.documents[document]
        label_pos = text.index(r'\label{' + label + '}')
        end = text.index(r'\end{table}', label_pos)
        block = text[label_pos:end]
        lines = [line for line in block.splitlines() if line.startswith(prefix + ' &')]
        if len(lines) != 1:
            raise ValueError(f'数据行 {label} {prefix}: {len(lines)} 处')
        old_line = lines[0]
        old_cells = [x.strip() for x in old_line.removesuffix(r'\\').split('&')]
        new_line = prefix + ' & ' + ' & '.join(values) + r'\\'
        self.replace(document, old_line, new_line, source, f'{label}:{prefix}', raw=raw)
        if prefix_key is not None:
            self.cells.append(dict(document=document,label=label,row=prefix,column=0,
                                   variable=prefix_key,old=old_cells[0],new=prefix,
                                   unrounded_value=prefix_value,source=source,passed=True,status='reproduced'))
        if len(old_cells) != len(values) + 1:
            raise ValueError(f'表格列数不符 {label}:{prefix}')
        for index, (old, new, number, key) in enumerate(zip(old_cells[1:], values, raw, keys), 1):
            self.cells.append(dict(document=document, label=label, row=prefix, column=index,
                                   variable=key, old=old, new=new, unrounded_value=number,
                                   source=source, passed=True, status='reproduced'))

    def styles(self):
        for document in self.documents:
            pattern = re.compile(r'\\begin\{table\}.*?\\end\{table\}', re.S)
            blocks = pattern.findall(self.documents[document])
            for index, old in enumerate(blocks, 1):
                new = re.sub(r'\\setlength\{\\tabcolsep\}\{[^}]+\}',
                             lambda _: r'\setlength{\tabcolsep}{3.5pt}', old)
                if r'\setlength{\tabcolsep}' not in new:
                    new = new.replace(r'\centering\small', r'\centering\small' + '\n' + r'\setlength{\tabcolsep}{3.5pt}', 1)
                if r'\renewcommand{\arraystretch}' not in new:
                    new = new.replace(r'\setlength{\tabcolsep}{3.5pt}', r'\setlength{\tabcolsep}{3.5pt}' + '\n' + r'\renewcommand{\arraystretch}{1.25}', 1)
                else:
                    new = re.sub(r'\\renewcommand\{\\arraystretch\}\{[^}]+\}', lambda _: r'\renewcommand{\arraystretch}{1.25}', new)
                self.replace(document, old, new, 'approved-local-table-style', f'table-style-{index}')


def prepare_manuscript(root: Path, output_dir: Path):
    root, output_dir = Path(root), Path(output_dir)
    frozen = root / RELEASE
    main = (frozen / 'flatten_curve_analysis_cn.tex').read_text(encoding='utf-8-sig')
    si = (frozen / 'flatten_curve_supplement_cn.tex').read_text(encoding='utf-8-sig')
    edit = _Editor(main, si)
    reference = _json(output_dir / 'xian/reference.json')
    fit = _json(output_dir / 'xian/fit.json')
    difference = _json(output_dir / 'xian/S2_difference.json')
    xd = _json(output_dir / 'xian/diagnostics.json')
    critical = _json(output_dir / 'population/critical.json')
    metadata = _json(output_dir / 'population/metadata.json')
    pd = _json(output_dir / 'population/diagnostics.json')
    supplemental = _json(output_dir / 'population/supplementary_anchors.json')
    beta_summary = _json(output_dir / 'population/beta_summary.json')
    c0params = _json(output_dir / 'c0/parameters.json')
    c0extrema = _json(output_dir / 'c0/extrema.json')
    joint = _json(output_dir / 'joint/results.json')
    if not all([xd['passed'], pd['passed'], _json(output_dir / 'c0/diagnostics.json')['passed'], joint['passed']]):
        raise ValueError('数值阶段未通过，不生成同步稿')
    strategies = {row['strategy']: row for row in reference['strategies']}
    td, flat, routine = [strategies[name] for name in ['TDINN控制', '情景一阈值控制', '常规控制']]
    eta_rows = _csv(output_dir / 'xian/eta_scan.csv')
    pop_rows = _csv(output_dir / 'population/representative_summary.csv')
    fixed_rows = [row for row in pop_rows if row['stem'].startswith('dominance_fixed_eta')]
    cases = [[row for row in pop_rows if row['stem'].startswith(f'dominance_case{n}_')] for n in range(4)]
    arcs = _csv(output_dir / 'population/arcs.csv')
    scale = _csv(output_dir / 'population/fixed_absolute_scale.csv')
    beta_rows = _csv(output_dir / 'population/beta_scan.csv')
    c0_rows = _csv(output_dir / 'c0/representative_summary.csv')
    baseline_path = output_dir / 'workspace/scenario1_threshold_landscape/current_run/output_csv'

    # 主表三：每个数值单元来自同一精度的三策略输出。
    for title, row in [('TDINN 控制', td), ('隔离率阈值控制', flat), ('常规控制', routine)]:
        keys = ['peak_I', 'cum_total_infections', 'clear_time', 'J']
        raw = [row[key] for key in keys]
        edit.row('main', 'tab:xian_summary', title,
                 [_i(raw[0]), _i(raw[1]), _f(raw[2]), _f(raw[3])], raw, keys, 'xian/reference.json:strategies')

    # 主表二的固定参数与定义也核对；并非所有不变单元都是新增结果。
    table2 = main[main.index(r'\label{tab:xian_initial_fit}'):main.index(r'\end{table}', main.index(r'\label{tab:xian_initial_fit}'))]
    for symbol, value, displayed in [('N', reference['parameters']['N'], r'\num{13163000}'),
                                     ('beta', reference['parameters']['beta'], '0.1498'),
                                     ('gamma', reference['parameters']['gamma'], '0.2953'),
                                     ('delta_q', reference['parameters']['delta_q'], '0.3531'),
                                     ('c0', reference['parameters']['c0'], '12.8872'),
                                     ('q0', reference['parameters']['q0'], '0.3230')]:
        if displayed not in table2:
            raise ValueError(f'表二参数 {symbol} 不一致')
        edit.cells.append(dict(document='main', label='tab:xian_initial_fit', variable=symbol,
                               old=displayed, new=displayed, unrounded_value=value,
                               source='xian/reference.json:parameters', passed=True, status='reproduced'))
    i0display = f'{fit["I0"] * 1e3:.5f}'
    edit.replace('main', '1.00663' + r'\times10^{-3}', i0display + r'\times10^{-3}',
                 'xian/fit.json:I0', 'fixed_absolute_I0', expected=None, raw=fit['I0'])
    edit.cells.append(dict(document='main', label='tab:xian_initial_fit', variable='I0',
                           old=r'1.00663\times10^{-3}', new=i0display + r'\times10^{-3}',
                           unrounded_value=fit['I0'], source='xian/fit.json', passed=True, status='reproduced'))
    for variable, definition in [('S0', 'N-I_0'), ('R0_initial', '$0$'), ('eta', r'0.002N=\num{26326}')]:
        if definition not in table2:
            raise ValueError(f'表二定义 {variable} 不一致')
        edit.cells.append(dict(document='main', label='tab:xian_initial_fit', variable=variable,
                               old=definition, new=definition, source='model_definition_and_xian/reference.json',
                               passed=True, status='static_and_reproduced'))

    table4_values = [('N_floor', r'1.06\times10^4', 2), ('N_star45', r'4.04\times10^4', 2),
                     ('N_star_inf', r'9.17\times10^4', 2), ('N_star_cum_inf', r'1.18\times10^4', 2)]
    # 限定到相关整行，不改变其他公式中数字相同的参数。
    for key, old, digits in table4_values:
        new = _sci(critical[key], digits).replace('^{4}', '^4')
        text = edit.documents['main']
        pos = text.index(r'\label{tab:dom:thresholds}')
        end = text.index(r'\end{table}', pos)
        matching = [line for line in text[pos:end].splitlines() if old in line]
        if len(matching) != 1:
            raise ValueError(f'表四 {key} 无唯一匹配')
        edit.replace('main', matching[0], matching[0].replace(old, new), 'population/critical.json', 'tab:dom:thresholds:' + key, raw=critical[key])
        edit.cells.append(dict(document='main', label='tab:dom:thresholds', variable=key, old=old, new=new,
                               source='population/critical.json', unrounded_value=critical[key], passed=True, status='reproduced'))
    edit.line('main', r'清零时间等值条件 &',
              r'清零时间等值条件 & \makecell{$N_{\rm clr}(\eta)$\\的最大取值} & ' + _i(critical['N_star_clear_peak']) + ' & 扫描范围内仍低于下界' + r'\\',
              'population/critical.json', 'tab:dom:thresholds:N_star_clear_peak', raw=critical['N_star_clear_peak'])
    edit.cells.append(dict(document='main', label='tab:dom:thresholds', variable='N_star_clear_peak', old='5166',
                           new=_i(critical['N_star_clear_peak']), unrounded_value=critical['N_star_clear_peak'],
                           source='population/critical.json', passed=True, status='reproduced'))

    # 三份补表完全由新输出重建数据行；原表头、分组、说明和样式保留。
    baseline_keys = ['t1', 'Delta_t', 't_end', 'q_max', 'J', 'I_t_cum']
    for source_name, prefix_function in [('main_c0_summary.csv', lambda r, j: '$c_0' + (r'\approx' + _f(r['c0'], 4) if j == 0 else '=' + _i(r['c0'])) + '$'),
                                         ('main_eta_summary.csv', lambda r, j: r'$\eta/N=' + f'{float(r["eta_percent"]):g}' + r'\%$')]:
        for j, row in enumerate(_csv(baseline_path / source_name)):
            prefix = prefix_function(row, j)
            raw = [float(row[key]) for key in baseline_keys]
            edit.row('supplement', 'tab:sup:baseline', prefix, [_f(n, 4) for n in raw], raw, baseline_keys,
                     'workspace/scenario1_threshold_landscape/current_run/output_csv/' + source_name,
                     prefix_key='c0' if source_name.startswith('main_c0') else 'eta_fraction',
                     prefix_value=float(row['c0'] if source_name.startswith('main_c0') else row['eta_frac']))
    s2rows = _csv(output_dir / 'xian/S2_window.csv')
    for prefix, row in zip(['观测数据', '最小二乘拟合', '$I_0=1$'], s2rows):
        if prefix == '$I_0=1$':
            prefix = '固定 $I_0=1$'
        raw = [None if row['I0'] == '' else float(row['I0'])] + [float(row[k]) for k in ['cumulative_40', 'community_daily_peak', 'quarantine_daily_peak']]
        values = ['{---}' if raw[0] is None else (_f(raw[0], 6) if prefix == '最小二乘拟合' else '1'), _i(raw[1]),
                  _i(raw[2]) if prefix == '观测数据' else _f(raw[2]), _i(raw[3]) if prefix == '观测数据' else _f(raw[3])]
        edit.row('supplement', 'tab:sup:initial', prefix, values, raw,
                 ['I0', 'cumulative_40', 'community_daily_peak', 'quarantine_daily_peak'], 'xian/S2_window.csv')
    eta_keys = ['q_max', 'Delta_t', 't_end', 'J', 'Itcum']
    for row in eta_rows:
        raw = [float(row[key]) for key in eta_keys]
        edit.row('supplement', 'tab:sup:eta', _f(row['eta_fraction'], 4),
                 [_f(raw[0], 4)] + [_f(n) for n in raw[1:4]] + [_i(raw[4])], raw, eta_keys, 'xian/eta_scan.csv',
                 prefix_key='eta_fraction',prefix_value=float(row['eta_fraction']))

    # 有名字绑定的四个 TDINN 参照及其重复图注统一更新。
    for old, value, anchor, places in [('151.90', td['peak_I'], 'TDINN_peak_I', 2),
                                       ('2096.76', td['cum_total_infections'], 'TDINN_cumulative_total', 2),
                                       ('49.35', td['J'], 'TDINN_J', 2),
                                       ('45.27', td['clear_time'], 'TDINN_clear_time', 2),
                                       ('258.11', flat['clear_time'], 'threshold_clear_time', 2)]:
        edit.token('main', old, _f(value, places), 'xian/reference.json', anchor, raw=value)
    edit.replace('main', '分别约为 $152$ 和 $2097$', '分别约为 $' + _i(td['peak_I']) + '$ 和 $' + _i(td['cum_total_infections']) + '$',
                 'xian/reference.json', 'rounded_TDINN_body', raw=[td['peak_I'], td['cum_total_infections']])
    edit.replace('main', '达到约 $2097$ 的累计感染参照', '达到约 $' + _i(td['cum_total_infections']) + '$ 的累计感染参照',
                 'xian/reference.json', 'exit_lower_bound_reference', raw=td['cum_total_infections'])
    edit.replace('main', r'最大数值偏差约为 $2.89\times10^{-8}$',
                 '最大数值偏差约为 $' + _sci(xd['threshold_diagnostics']['plateau_max_error'], 2) + '$',
                 'xian/diagnostics.json:threshold_diagnostics.plateau_max_error', 'openloop_plateau_error', raw=xd['threshold_diagnostics']['plateau_max_error'])
    for old, key, row in [('18.55', 't1', eta_rows[-1]), ('13.93', 't1', eta_rows[0]),
                           ('16.61', 'Delta_t', eta_rows[-1]), ('1710.66', 'Delta_t', eta_rows[0]), ('2209.55', 't_end', eta_rows[0])]:
        edit.replace('main', '$' + old + '$', '$' + _f(row[key]) + '$', 'xian/eta_scan.csv', f'eta_endpoint:{old}:{key}', raw=float(row[key]))
    edit.line('main', r'图\ref{fig:xian:observed-fit}使用',
              r'图\ref{fig:xian:observed-fit}与三策略比较、补充表\ref*{tab:sup:initial}使用统一归一化方程、求解器和容差的轨迹输出。旧拟合与旧事件积分的差异已按统一设置重算核对，其来源和历史数值见该补充表注。',
              'xian/S2_difference.json', 'S2_body_resolution')
    note = (r'\item 注：观测窗口为 2021 年 12 月 9 日至 2022 年 1 月 17 日的 40 个日区间。本表、主稿和三策略比较采用统一的归一化方程、DOP853 求解器和容差，并重新估计 $I_0$；仅隔离控制按常规、平台和退出后三阶段连接。统一计算在 $t=40$ 的总累计为 $'
            + _f(difference['unified_refit_40_cumulative'], 4) + r'$，在动态清零时刻 $' + _f(td['clear_time'], 4)
            + r'$ d 为 $' + _f(td['cum_total_infections'], 4) + r'$。历史拟合与事件积分在相同旧初值下分别给出 $'
            + _f(difference['legacy_fit_40_cumulative'], 4) + r'$ 和 $' + _f(difference['legacy_event_40_cumulative'], 4)
            + r'$；统一设置在该旧初值下给出 $' + _f(difference['unified_at_legacy_I0_40_cumulative'], 4)
            + r'$。差异主要来自旧绝对容差相对于约 $10^{-3}$ 的初始感染量过大；初值重新估计与积分设置改变是两个不同步骤。统一结果再收紧容差后，总累计变化为 $'
            + _sci(difference['reference_tolerance_differences']['cum_total_infections'], 2)
            + r'$ 人，本表所列精度不受影响。历史输出仅用于说明差异来源，不再作为当前参照。日新增峰值不等于社区现存感染者峰值。')
    edit.line('supplement', r'\item 注：观测窗口为', note, 'xian/S2_difference.json + xian/reference.json', 'S2_diagnosis_resolved', raw=difference)
    edit.line('supplement', '本文件保留原主稿中的',
              r'本文件列出仅隔离控制的基准参数分析、初值设定比较和西安阈值敏感性。表内数值由本次独立复现输出生成；基准结果位于 \texttt{workspace/scenario1\_threshold\_landscape/current\_run/output\_csv/}，西安结果位于 \texttt{xian/}。阈值为给定的社区感染人数上限，表中结果不用于验证实际 ICU 容量。',
              'fresh-run outputs', 'SI_data_location')
    edit.replace('supplement', '数值取自基准实验的保存结果', '数值取自本次重新计算的基准实验结果', 'fresh baseline MATLAB outputs', 'S1_source_note')
    edit.replace('supplement', '数值取自西安阈值敏感性保存结果', '数值取自统一积分设置下重新计算的西安阈值敏感性结果', 'xian/eta_scan.csv', 'S3_source_note')

    # 全市峰值阈值的时长：使用新参照参数作公式回代，不重新拟合。
    from xian import Params, structural
    city_peak = structural(Params(**reference['parameters']), fit['I0'], td['peak_I'], costs=False)
    log_factor = math.log((city_peak['S_star'] - city_peak['Sbar']) / (city_peak['Sc'] - city_peak['Sbar']))
    edit.replace('main', '对数因子约为 $2.205$', '对数因子约为 $' + _f(log_factor, 3) + '$', 'xian.structural(fresh reference parameters)', 'city_peak_log_factor', raw=log_factor)
    # 参照峰值已更新，因此采用当前显示值定位，不匹配其他年数。
    old_city_line = r'\Delta t(\eta=' + _f(td['peak_I']) + r')\approx1.48\times10^{4}\ \text{d}\approx 40.6\ \text{年}.'
    edit.replace('main', old_city_line, r'\Delta t(\eta=' + _f(td['peak_I']) + r')\approx' + _sci(city_peak['Delta_t'], 2) + r'\ \text{d}\approx ' + _f(city_peak['Delta_t']/365, 1) + r'\ \text{年}.',
                 'xian.structural(fresh reference parameters)', 'city_peak_duration', raw=city_peak['Delta_t'])

    # 人口边界、两种初值约定及轨迹数字分别绑定各自输出。
    edit.line('main', '由首次积分，$i_0$ 通过',
              r'由首次积分，$i_0$ 通过 $\theta-i_0$ 和 $s_0=1-i_0$ 影响启动点。在 $N\ge N_{\rm floor}$、$\theta\ge\theta_{\rm dur150}$ 时，$i_0/\theta$ 不超过约 $'
              + _sci(fit['I0']/(critical['N_floor']*critical['theta_dur150']), 1)
              + r'$；该比例本身不是控制指标的严格误差上界。本次固定 $\theta=0.002$ 的六个人口规模测试中，$\Delta t$ 和 $J$ 的相对极差分别为 $'
              + _sci(pd['fixed_absolute_duration_relative_range'], 2) + r'$ 和 $'
              + _sci((max(float(r['J']) for r in scale)-min(float(r['J']) for r in scale))/max(float(r['J']) for r in scale), 2)
              + r'$。这些是本次有限参数测试的数值结果，不给出所有初值或人口下统一的误差认证。',
              'population/fixed_absolute_scale.csv + population/critical.json', 'finite_scale_test', raw={'scale':scale, 'critical':critical})
    edit.replace('main', r'N_{\rm floor}=605.40+\frac{1491.36}{0.1498}', r'N_{\rm floor}=' + _f(td['cum_community_infections']) + r'+\frac{' + _f(td['cum_quarantined_infections']) + r'}{0.1498}',
                 'xian/reference.json:strategies', 'N_floor_components', raw=[td['cum_community_infections'], td['cum_quarantined_infections']])
    edit.replace('main', r'=1.0561\times10^4\approx1.06\times10^4.', '=' + _sci(critical['N_floor'], 4).replace('^{4}', '^4') + r'\approx1.06\times10^4.', 'population/critical.json', 'N_floor_unrounded_intermediate', raw=critical['N_floor'])
    edit.replace('main', r'相对极差为 $2.4\times10^{-7}$', '相对极差为 $' + _sci(pd['fixed_absolute_duration_relative_range'], 2) + '$',
                 'population/fixed_absolute_scale.csv', 'six_population_duration_spread', raw=pd['fixed_absolute_duration_relative_range'])
    edit.line('main', r'固定 $\beta=0.1498$，在 $\eta\in',
              r'固定 $\beta=0.1498$，在 $\eta\in\{80,100,150\}$、$N_{\rm eff}\in\{4,5,6\}\times10^4$ 的九组参数中，将解析拐点时刻回代开环控制，所得隔离率均约为 $0.4119$，与理论值的最大绝对差为 $'
              + _sci(supplemental['max_inflection_q_error'], 2)
              + r'$。这只是解析公式的浮点回代核对，不是独立 ODE 误差认证。当 $q_0=0.3230$ 时，$\qinf=q_0$ 给出 $\beta_{\max}='
              + _f(supplemental['beta_max'], 6) + r'$；超过该值后控制区间内不再有内部拐点。',
              'population/inflection_invariance.csv + population/supplementary_anchors.json', 'inflection_backsubstitution', raw=supplemental['max_inflection_q_error'])
    for old, new, key in [(r'9.17\times10^{4}', _sci(critical['N_star_inf'], 2), 'N_star_inf'),
                          ('5166', _i(critical['N_star_clear_peak']), 'N_star_clear_peak'),
                          ('102.83', _f(critical['duration_at_cost_boundary']), 'duration_at_cost_boundary'),
                          ('2439', _i(pd['fixed_normalized_clear_arc_max']), 'fixed_normalized_clear_arc_max')]:
        edit.token('main', old, new, 'population/critical.json or diagnostics.json', key, raw=critical.get(key, pd.get(key)))
    intersection = '(' + _i(critical['N_star_cum_inf']) + ',' + _f(critical['eta_at_cumulative_cost_intersection']) + ')'
    edit.replace('main', '(11762,19.48)', intersection, 'population/critical.json', 'cumulative_cost_intersection', expected=None, raw=[critical['N_star_cum_inf'],critical['eta_at_cumulative_cost_intersection']])
    old_fixed_N = '3970,10102,26584,60381,87944'
    new_fixed_N = ','.join(_i(row['N']) for row in fixed_rows)
    edit.replace('main', old_fixed_N, new_fixed_N, 'population/representative_summary.csv', 'figure14_populations', raw=[float(r['N']) for r in fixed_rows])
    edit.replace('main', r'$\eta=22.7,33.1,75.2$', r'$\eta='+','.join(_f(row['eta'],1) for row in cases[0])+'$',
                 'population/representative_summary.csv','figure14_thresholds',raw=[float(row['eta']) for row in cases[0]])
    edit.replace('main', '3970,10102,26584,60381', ','.join(_i(row['N']) for row in fixed_rows[:4]), 'population/representative_summary.csv', 'figure17_populations', raw=[float(r['N']) for r in fixed_rows[:4]])
    edit.line('main', r'图~\ref{fig:dom:levers}(b,d) 固定',
              r'图~\ref{fig:dom:levers}(b,d) 固定 $\eta=100$。随 $N_{\rm eff}$ 增大，感染人数维持的阈值保持不变，持续时间增加；在本节参数范围内，$\Delta t\approx0.170N/\eta$。附录图~\ref{fig:panel_N_decomp} 中，人口从 $'
              + _i(fixed_rows[0]['N']) + '$ 增至 $' + _i(fixed_rows[3]['N']) + '$ 时，常规控制的感染峰值由 $'
              + _i(fixed_rows[0]['routine_peak_I']) + '$ 增至 $' + _i(fixed_rows[3]['routine_peak_I']) + '$，清零时间由 $'
              + _f(fixed_rows[0]['routine_clear_time'],1) + '$ 天增至 $' + _f(fixed_rows[3]['routine_clear_time'],1) + '$ 天；阈值控制的控制持续时间由 $'
              + _f(fixed_rows[0]['Delta_t'],1) + '$ 天增至 $' + _f(fixed_rows[3]['Delta_t'],1) + '$ 天，清零时间由 $'
              + _f(fixed_rows[0]['t_end'],1) + '$ 天增至 $' + _f(fixed_rows[3]['t_end'],1) + r'$ 天。较低的固定感染峰值因此可能伴随明显延长的疫情持续时间。',
              'population/representative_summary.csv', 'fixed_eta_trajectory_narrative', raw=fixed_rows)
    edit.line('main', '五个人口规模对应的总累计感染',
              '五个人口规模对应的总累计感染依次约为 $' + ','.join(_i(r['Itcum']) for r in fixed_rows)
              + '$，可与固定 TDINN 参照 $' + _f(td['cum_total_infections']) + r'$ 比较。前两个人口规模低于 $N_{\rm floor}$，不属于施加人口相容下界后的比较区域。',
              'population/representative_summary.csv + xian/reference.json', 'fixed_eta_cumulative_all5', raw=[float(r['Itcum']) for r in fixed_rows])
    new_cases_N = ','.join(_i(rows[0]['N']) for rows in cases[1:])
    edit.replace('main', '11763,40382,91721', new_cases_N, 'population/representative_summary.csv', 'figure18_populations', raw=[float(rows[0]['N']) for rows in cases[1:]])
    edit.replace('main', r'\theta_{\rm cost}=1.656\times10^{-3}', r'\theta_{\rm cost}=' + _sci(critical['theta_cost'],3), 'population/critical.json', 'appendix_theta_cost', raw=critical['theta_cost'])
    for key,texname,old in [('theta_dur150',r'\theta_{\rm dur150}',r'1.137\times10^{-3}'),
                           ('theta_dur45',r'\theta_{\rm dur45}',r'3.762\times10^{-3}')]:
        edit.replace('main',texname+'='+old,texname+'='+_sci(critical[key],3),'population/critical.json',
                     'appendix_'+key,raw=critical[key])
    narrative = []
    for n, rows in enumerate(cases[1:], 1):
        text = r'当 $N_{\rm eff}=' + _i(rows[0]['N']) + '$ 时，三个阈值为 $' + ','.join(_f(r['eta'],3) for r in rows) + '$'
        if n == 1:
            text += '，清零时间分别约为 $' + ','.join(_f(r['t_end'],1) for r in rows) + '$ d；成本条件下累计感染约为 TDINN 参照 $' + _f(td['cum_total_infections']) + '$，另外两个阈值的结果分别低于和高于该参照。'
        elif n == 2:
            text += '，最后一个约等于 TDINN 峰值。'
        else:
            text += '，分别低于、约等于和高于 TDINN 峰值。'
        narrative.append(text)
    edit.line('main', r'当 $N_{\rm eff}=11763$ 时', ''.join(narrative), 'population/representative_summary.csv', 'appendix_critical_cases_all', raw=cases[1:])
    edit.replace('main', '约 $368$ 天', '约 $' + _i(c0extrema['time_at_near_trigger']) + '$ 天', 'c0/extrema.json:time_at_near_trigger', 'c0_near_trigger_clearance', raw=c0extrema['time_at_near_trigger'])
    edit.replace('main', '两套既有西安积分设置也仍需统一核对', '既有西安积分设置的差异已按统一归一化方程、求解器和容差重算核对', 'xian/S2_difference.json', 'discussion_unified_integration')
    edit.replace('main', r'西安重构在这一终点的状态需要另行检验 $\beta c_0(1-q_0)S/(\gamma N)$。',
                 r'在西安重构的这一终点，若直接恢复常规接触率和隔离率，状态回代给出 $\beta c_0(1-q_0)S/(\gamma N)\approx'
                 + _f(td['post_restore_Re']) + r'>1$，因此不能据 $I=1$ 保证恢复常规后的继续下降。该值只是名义参数下的终点状态核查，不是新的后续反弹轨迹模拟。',
                 'xian/reference.json:TDINN控制.post_restore_Re','TDINN_clearance_restore_state',raw=td['post_restore_Re'])
    # 字面取整未变化的 c0 结果也留下独立的来源记录。
    derived=c0params['derived']
    for old,new,anchor,raw in [
        (r'$c_0\approx6.61$',r'$c_0\approx'+_f(derived['c0_duration_max'])+'$','c0_duration_argmax',derived['c0_duration_max']),
        ('$103.2$ 天','$'+_f(derived['duration_max'],1)+'$ 天','c0_duration_max',derived['duration_max']),
        (r'$c_0\approx18.12$ 和 $13.88$',r'$c_0\approx'+_f(c0extrema['J']['c0'])+'$ 和 $'+_f(c0extrema['Itcum']['c0'])+'$','c0_cost_and_cumulative_argmax',[c0extrema['J']['c0'],c0extrema['Itcum']['c0']]),
        (r'$J\approx42.80$ 和 $\Itcum\approx3610$',r'$J\approx'+_f(c0extrema['J']['value'])+r'$ 和 $\Itcum\approx'+_i(c0extrema['Itcum']['value'])+'$','c0_cost_and_cumulative_max',[c0extrema['J']['value'],c0extrema['Itcum']['value']]),
        ('$c_0=30$ 时约 $102$ 天','$c_0=30$ 时约 $'+_i(c0extrema['time_at_c0_30']['t_end'])+'$ 天','c0_30_clearance',c0extrema['time_at_c0_30']['t_end']),
        (r'触发边界 $3.334$、拐点边界 $3.543$ 和时长极大值位置 $6.607$',
         '触发边界 $'+_f(derived['c0_trigger'],3)+'$、拐点边界 $'+_f(derived['c0_inflection_onset'],3)+'$ 和时长极大值位置 $'+_f(derived['c0_duration_max'],3)+'$',
         'c0_scan_boundaries',[derived['c0_trigger'],derived['c0_inflection_onset'],derived['c0_duration_max']])]:
        edit.replace('main',old,new,'c0/parameters.json + c0/extrema.json',anchor,expected=None,raw=raw)

    # 传播概率扫描与两条弧：更新完整成组数字，不只改端点的峰值。
    edit.replace('main', r'\in[8.669,\,8.688]', r'\in[' + _f(beta_summary['N_star_over_floor_min'],3) + r',\,' + _f(beta_summary['N_star_over_floor_max'],3) + ']', 'population/beta_summary.json', 'beta_ratio_range', raw=beta_summary)
    selected_beta = [next(r for r in beta_rows if abs(float(r['beta']) - b) < 1e-9) for b in [.10,.1498,.20,.30]]
    edit.line('main', r'$N^\ast_\infty=13.48/',
              r'$N^\ast_\infty=' + '/'.join(_f(float(r['N_star_inf'])/1e4) for r in selected_beta) + r'\times10^4$、$N_{\rm floor}='
              + '/'.join(_f(float(r['N_floor'])/1e4) for r in selected_beta) + r'\times10^4$）。',
              'population/beta_scan.csv', 'beta_scan_grouped_endpoints', raw=selected_beta)
    cumulative_fixed = next(r for r in fixed_rows if r['role'] == 'cum')
    edit.line('main', r'在 $\eta\in[10,' + _f(td['peak_I']) + ']$ 内，累计感染等值曲线',
              r'在 $\eta\in[10,' + _f(td['peak_I']) + r']$ 内，累计感染等值曲线 $\Itcum(\eta,N)=\Itcum^{\rm T}$ 从 $('
              + _i(arcs[-1]['N_cum']) + ',' + _f(td['peak_I']) + ')$ 延伸至 $(' + _i(arcs[0]['N_cum']) + r',10)$，$\eta=100$ 时 $N_{\rm cum}\approx'
              + _sci(cumulative_fixed['N'],3).replace('^{4}','^4') + '$。它与成本线的交点为 $' + intersection + r'$，给出 $N_{\rm cum,\infty}^\ast\approx1.18\times10^4$，约为 $N^\ast_\infty$ 的 $'
              + _f(critical['N_star_cum_inf']/critical['N_star_inf']) + r'$。现有 $16$ 个计算点及其插值仅显示一次交点，尚不能据此确定一般参数下交点的唯一性。',
              'population/arcs.csv + critical.json + representative_summary.csv', 'cumulative_arc_complete', raw={'arcs':arcs,'fixed':cumulative_fixed})
    edit.line('main', r'$t_{\rm end}=t_{\rm end}^{\rm T}$ 在同一阈值范围内',
              r'$t_{\rm end}=t_{\rm end}^{\rm T}$ 在同一阈值范围内从 $(' + _f(arcs[0]['N_clear'],1) + r',\,10)$ 延伸到 $('
              + _f(arcs[-1]['N_clear'],1) + r',\,' + _f(td['peak_I']) + r')$，', 'population/arcs.csv', 'clearance_arc_endpoints', raw=[arcs[0],arcs[-1]])

    # 联合算例保留论文四位精度；全精度积分与真正开环核查单独留档。
    joint_rows = {row['strategy']:row for row in _csv(output_dir/'joint/results.csv')}
    for strategy, key, old in [('minimum_cost','cost','2.1183'), ('minimum_cost','duration','7.7536'),
                                ('quarantine_only','cost','2.2236'), ('contact_only','cost','11.9390'),
                                ('quarantine_only','duration','5.9026')]:
        value = float(joint_rows[strategy][key])
        # 仅定位联合算例说明段；这些数值在其他基准表中可重复出现。
        paragraph = next(line for line in edit.documents['main'].splitlines() if line.startswith(r'在图\ref{fig:scenario1:single-sim}所列基准参数下'))
        token = old if old in paragraph else _f(value,4)
        new = _f(value,4)
        edit.replace('main', paragraph, paragraph.replace(token,new), 'joint/results.csv + openloop_check.json', f'joint:{strategy}.{key}', raw=value)
    edit.styles()

    # 保留原稿结构；供构建步骤核对表号、标签及受保护理论内容。
    labels = lambda t: re.findall(r'\\label\{([^}]+)\}', t)
    if labels(main) != labels(edit.documents['main']) or labels(si) != labels(edit.documents['supplement']):
        raise ValueError('同步过程改变了标签及其顺序')
    table_counts = {doc:len(re.findall(r'\\begin\{table\}', text)) for doc,text in edit.documents.items()}
    if table_counts != {'main':4,'supplement':3}:
        raise ValueError(f'表格计数不符 {table_counts}')
    if any(ord(char)<32 and char not in '\n\t' for text in edit.documents.values() for char in text):
        raise ValueError('生成 TeX 中出现非法控制字符')
    stale = ['151.90','2096.76','49.35','45.27','258.11','11762,19.48','11763,40382,91721','1.00663', '尚未通过统一积分设置消除']
    stale_present = [value for value in stale if re.search(r'(?<![\d.])'+re.escape(value)+r'(?![\d.])',edit.documents['main'])]
    if stale_present:
        raise ValueError('当前主稿仍有旧绑定数字: ' + ', '.join(stale_present))
    inputs = ['xian/reference.json','xian/fit.json','xian/S2_difference.json','xian/S2_window.csv','xian/eta_scan.csv',
              'population/critical.json','population/representative_summary.csv','population/arcs.csv','population/beta_scan.csv',
              'population/fixed_absolute_scale.csv','population/inflection_invariance.csv','population/supplementary_anchors.json',
              'population/beta_summary.json','population/diagnostics.json','c0/parameters.json','c0/extrema.json','c0/representative_summary.csv',
              'joint/results.json','joint/results.csv','joint/openloop_check.json']
    report = dict(schema='manuscript-sync-v1', passed=True, source_main=(RELEASE/'flatten_curve_analysis_cn.tex').as_posix(),
                  source_supplement=(RELEASE/'flatten_curve_supplement_cn.tex').as_posix(),
                  source_sha256={'main':hashlib.sha256((frozen/'flatten_curve_analysis_cn.tex').read_bytes()).hexdigest(),
                                 'supplement':hashlib.sha256((frozen/'flatten_curve_supplement_cn.tex').read_bytes()).hexdigest()},
                  changes=edit.changes, numerical_cells=edit.cells, table_counts=table_counts,
                  input_sha256={name:hashlib.sha256((output_dir/name).read_bytes()).hexdigest() for name in inputs},
                  full_precision_sources=dict(xian_reference=reference, population_critical=critical, population_metadata=metadata,
                                              population_supplementary=supplemental, c0_parameters=c0params,c0_extrema=c0extrema,joint=joint,
                                              city_peak_formula=city_peak),
                  evidence_boundary='passed 仅表示按 fresh 结果完成逐单元同步及标签保持，不是所有理论证明、所有图曲线或版面验收。',
                  unchanged_table1=dict(label='tab:sensitivity',status='static',note='公式符号及理论依据原样保留，未当成新的数值检查。'),
                  remaining_verification=['完整编译与页面视觉核查由构建阶段完成。','未将有限参数扫描推广为一般参数的唯一性或全局误差认证。'])
    anchors_path = output_dir/'paper_anchor_updates.json'
    if anchors_path.exists():
        report['numeric_anchor_records'] = _json(anchors_path)['records']
    destination=output_dir/'manuscript'
    destination.mkdir(exist_ok=True)
    (destination/'staged.tex').write_text(edit.documents['main'],encoding='utf-8')
    (destination/'staged_supplement.tex').write_text(edit.documents['supplement'],encoding='utf-8')
    (output_dir/'manuscript_changes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return edit.documents['main'], edit.documents['supplement'], report
