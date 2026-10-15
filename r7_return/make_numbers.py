"""由 R7-3 的全精度结果生成稿件用数字宏 paper/generated/r7_numbers.tex（只含 \\newcommand）。

运行（仓库根目录，先运行 r7_3_numerics.py）：
    conda run --no-capture-output -n thesis python r7_return/make_numbers.py
输入：results/r7_3_{endpoint_immediate,exponential_return,release,noreturn_inf,convergence}.json
输出：
    paper/generated/r7_numbers.tex      展示值（\\newcommand，宏名前缀 \\rs，只用字母）
    results/r7_numbers_full.json        每个宏的全精度值、展示值、单位、来源文件与字段

只收 R7-3 新增的计算结果。日期、章节号、公式常数（如 ε_tail 的相对系数 1e-6、e 的容限 1e-8）、
文献数字不宏化。

展示位数（执行计划第 5 节数值判据：保存与判定用全精度；收紧容差后非零量相对变化 < 1e-3）：
- Δt、J：5 位有效数字（与执行计划第 5 节参考值的位数相同；实际收紧变化 ≤ 1e-9 量级）；
- 人数：基准以人计，1 位小数；西安以 10^6 人计，4 位小数（宏名以 Mil 结尾）；
- 百分数：3 位有效数字，不含 % 号；比值（S_q(t2)/S_c、R_e、切换位置、分担比例、I/η）：3 位小数；
- e = max I/η − 1（退出后内部极大）：3 位小数，负数用 \\ensuremath；
- 收敛量：1–2 位有效数字的科学记数，用 \\ensuremath；
- 文字宏：是／否／数值上未确定／未到达／满足／不满足。
指数回流的终点为退出后首次 I<1 截断（作者 2026-10-15 决定），只给 Δt、J、e、是否越过 η、截断时刻与
终止时累计感染；不给“超出下界幅度”与尾部误差（不截断的尾部判据结果只在 JSON 的 diagnostic_tail 中）。
"""
import hashlib
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(HERE, 'results')
OUT_TEX = os.path.join(ROOT, 'paper', 'generated', 'r7_numbers.tex')
OUT_JSON = os.path.join(RESULTS, 'r7_numbers_full.json')

INPUTS = {
    'endpoint': 'r7_3_endpoint_immediate.json',
    'return': 'r7_3_exponential_return.json',
    'release': 'r7_3_release.json',
    'noreturn': 'r7_3_noreturn_inf.json',
    'convergence': 'r7_3_convergence.json',
}

CASE = {'base': 'Base', 'xian': 'Xian'}
STAY_WORD = {7: 'Seven', 14: 'Fourteen', 30: 'Thirty', 60: 'Sixty', 120: 'Onetwenty', 365: 'Threesixtyfive'}
LAW_IR = {'q_only': 'Qonly', 'alpha': 'Alpha', 'opt_immediate': 'Opt', 'c_only': 'Conly'}
LAW_NR = {'q_only': 'Qonly', 'alpha': 'Alpha', 'opt_noreturn': 'Opt', 'c_only': 'Conly'}
LAW_RET = {'q_only': 'Qonly', 'c_only': 'Conly', 'opt_noreturn': 'Mig'}
CROSS_TEXT = {'crossed': '是', 'not_crossed': '否', 'undetermined': '数值上未确定'}
NAME_RE = re.compile(r'^rs[A-Za-z]+$')


# ---------------- 格式 ----------------
def sig(v, n=5):
    """n 位有效数字的定点写法（不用指数）。"""
    if v == 0:
        return '0'
    d = n - 1 - int(math.floor(math.log10(abs(v))))
    d = max(d, 0)
    s = f'{round(v, d):.{d}f}'
    return s


def fixed(v, d):
    s = f'{v:.{d}f}'
    if s.startswith('-'):
        return r'\ensuremath{' + s + '}'
    return s


def pct(v):
    """比例 v 写成百分数：3 位有效数字，不含 % 号。"""
    return sig(100 * v, 3)


def sci(v, n=2):
    """科学记数（n 位有效数字）；10^0 量级写成普通数。"""
    if v == 0:
        return '0'
    e = int(math.floor(math.log10(abs(v))))
    m = v / 10 ** e
    m = round(m, n - 1)
    if abs(m) >= 10:
        m /= 10
        e += 1
    ms = f'{m:.{n - 1}f}'
    if e == 0:
        return ms
    if e == 1:
        return sig(v, n)
    return r'\ensuremath{' + ms + r'\times10^{' + str(e) + '}}'


class Book:
    def __init__(self):
        self.items = []          # (name, display, value, unit, rule, source, path, group)
        self.names = set()

    def add(self, name, display, value, unit, rule, source, path, group):
        if not NAME_RE.match(name):
            raise ValueError(f'宏名只能用字母：{name}')
        if name in self.names:
            raise ValueError(f'宏名重复：{name}')
        self.names.add(name)
        self.items.append(dict(name=name, display=display, value=value, unit=unit, rule=rule,
                               source=source, path=path, group=group))

    def persons(self, case, name, value, source, path, group):
        """人数：基准 1 位小数（人）；西安 4 位小数（10^6 人，宏名加 Mil）。"""
        if case == 'base':
            self.add(name, fixed(value, 1), value, '人', '1 位小数', source, path, group)
        else:
            self.add(name + 'Mil', fixed(value / 1e6, 4), value, '10^6 人', '以 10^6 人计，4 位小数', source, path, group)

    def five(self, name, value, unit, source, path, group):
        self.add(name, sig(value, 5), value, unit, '5 位有效数字', source, path, group)

    def text(self, name, text, value, source, path, group):
        self.add(name, text, value, '文字', '文字', source, path, group)


def load():
    data = {}
    for k, f in INPUTS.items():
        p = os.path.join(RESULTS, f)
        with open(p, encoding='utf-8') as fh:
            data[k] = json.load(fh)
        with open(p, 'rb') as fh:
            data[k + '_sha256'] = hashlib.sha256(fh.read()).hexdigest()
    return data


def build(data):
    B = Book()

    # ---- 1. 端点小表：立即返回对照模型 ----
    src = INPUTS['endpoint']
    for case, c in data['endpoint']['cases'].items():
        C = CASE[case]
        g = '端点小表（立即返回对照模型，w_c=1、w_q=2）'
        for law, L in LAW_IR.items():
            d = c['laws'][law]
            pre = f'cases.{case}.laws.{law}'
            B.five(f'rs{C}{L}DtIr', d['dt'], 'd', src, pre + '.dt', g)
            B.five(f'rs{C}{L}JIr', d['J'], 'd', src, pre + '.J', g)
            B.persons(case, f'rs{C}{L}KqIr', d['Kq'], src, pre + '.Kq', g)
        B.persons(case, f'rs{C}InfIr', c['arc_infections_common'], src, f'cases.{case}.arc_infections_common', g)
        B.persons(case, f'rs{C}SstarIr', c['S_star_ir'], src, f'cases.{case}.S_star_ir', g)
        B.add(f'rs{C}IrCostGapConly', pct(c['cost_gap_vs_c_only']), c['cost_gap_vs_c_only'], '%',
              '百分数 3 位有效数字', src, f'cases.{case}.cost_gap_vs_c_only', g)
        B.add(f'rs{C}IrCostGapQonly', pct(c['cost_gap_vs_q_only']), c['cost_gap_vs_q_only'], '%',
              '百分数 3 位有效数字', src, f'cases.{case}.cost_gap_vs_q_only', g)
        opt = c['laws']['opt_immediate']
        B.add(f'rs{C}IrSwitchZ', fixed(opt['switch_z'], 3), opt['switch_z'], 'S/S_c', '3 位小数', src,
              f'cases.{case}.laws.opt_immediate.switch_z', g)
        B.add(f'rs{C}IrShare', fixed(opt['terminal_share_z=1+1e-6'], 3), opt['terminal_share_z=1+1e-6'], '比例',
              '3 位小数', src, f'cases.{case}.laws.opt_immediate.terminal_share_z=1+1e-6', g)

    # ---- 2. 指数回流表 ----
    src = INPUTS['return']
    runs = data['return']['runs']
    for key, d in runs.items():
        case, stay, law = key.split('|')
        C, W, L = CASE[case], STAY_WORD[int(stay)], LAW_RET[law]
        n = f'rs{C}Stay{W}{L}'
        g = f'指数回流（1/ω = {stay} d；终点：退出后首次 I<1 截断）'
        pre = f'runs.{key}'
        B.five(n + 'Dt', d['dt'], 'd', src, pre + '.dt', g)
        B.five(n + 'J', d['J'], 'd', src, pre + '.J', g)
        if d['e_interior'] is None:
            B.text(n + 'E', '—', None, src, pre + '.e_interior', g)
            B.text(n + 'PeakRatio', '—', None, src, pre + '.e_interior', g)
        else:
            B.add(n + 'E', fixed(d['e_interior'], 3), d['e_interior'], '无量纲', '3 位小数', src, pre + '.e_interior', g)
            B.add(n + 'PeakRatio', fixed(1 + d['e_interior'], 3), 1 + d['e_interior'], 'I/η', '3 位小数', src,
                  pre + '.e_interior', g)
        B.text(n + 'Crossed', CROSS_TEXT[d['crossing']], d['crossing'], src, pre + '.crossing', g)
        B.text(n + 'Reached', '是' if d['reached'] else '未到达', d['reached'], src, pre + '.reached', g)
        if d['reached']:
            B.five(n + 'Tend', d['t_end'], 'd', src, pre + '.t_end', g)
        else:
            B.text(n + 'Tend', '未到达', None, src, pre + '.t_end', g)
        B.persons(case, n + 'Cterm', d['C_term'], src, pre + '.C_term', g)
    # 汇总
    g = '指数回流（汇总）'
    vals = list(runs.values())
    B.add('rsReturnRunsTotal', str(len(vals)), len(vals), '条', '整数', src, 'runs', g)
    for crit, nm in (('crossed', 'Crossed'), ('undetermined', 'Undetermined')):
        k = sum(v['crossing'] == crit for v in vals)
        B.add(f'rsReturnRuns{nm}', str(k), k, '条', '整数', src, f'runs.*.crossing == {crit}', g)
    k = sum(not v['reached'] for v in vals)
    B.add('rsReturnRunsNotReached', str(k), k, '条', '整数', src, 'runs.*.reached == false', g)
    # 截断值低于命题 R2 的 t→∞ 下界 L 的条数（正文说明“R2 的下界针对不截断的 t→∞ 累计感染”时可用）
    k = sum(bool(v['C_term_below_L']) for v in vals)
    B.add('rsReturnRunsBelowL', str(k), k, '条', '整数', src, 'runs.*.C_term_below_L', g)
    for case in ('base', 'xian'):
        C = CASE[case]
        eint = [v['e_interior'] for k, v in runs.items() if k.startswith(case + '|') and v['e_interior'] is not None]
        if eint:
            B.add(f'rs{C}ReturnPeakRatioMax', fixed(1 + max(eint), 3), 1 + max(eint), 'I/η', '3 位小数', src,
                  f'max runs.{case}|*.e_interior + 1', g)

    # ---- 3. 释放用数 ----
    src = INPUTS['release']
    for case, r in data['release']['cases'].items():
        C = CASE[case]
        g = '释放（ω = 0，仅隔离，ξ = 1）'
        B.add(f'rs{C}ReleaseSqRatio', fixed(r['Sq_t2_over_Sc'], 3), r['Sq_t2_over_Sc'], 'S_q(t2)/S_c', '3 位小数',
              src, f'cases.{case}.Sq_t2_over_Sc', g)
        B.add(f'rs{C}ReleaseRe', fixed(r['Re_after_release'], 3), r['Re_after_release'], 'R_e(t2+)', '3 位小数',
              src, f'cases.{case}.Re_after_release', g)

    # ---- 4. 无回流 t→∞ 对照 ----
    src = INPUTS['noreturn']
    for case, c in data['noreturn']['cases'].items():
        C = CASE[case]
        g = '无回流 t→∞ 对照（ω = 0）'
        B.persons(case, f'rs{C}LBound', c['L'], src, f'cases.{case}.L', g)
        for law, L in LAW_NR.items():
            d = c['laws'][law]
            B.persons(case, f'rs{C}{L}CinfNr', d['C_inf'], src, f'cases.{case}.laws.{law}.C_inf', g)
            B.text(f'rs{C}{L}BelowL', '满足' if d['below_L'] else '不满足', d['below_L'], src,
                   f'cases.{case}.laws.{law}.below_L', g)

    # ---- 6、8. 收敛（汇总量） ----
    src = INPUTS['convergence']
    cv = data['convergence']
    g = '收敛与容差'
    ts = cv['tolerance_summary']
    B.add('rsTolMaxRelChange', sci(ts['max_rel_change_tight'], 1), ts['max_rel_change_tight'], '相对变化',
          '1 位有效数字', src, 'tolerance_summary.max_rel_change_tight', g)
    if ts['max_abs_e_change_tight'] is not None:
        B.add('rsTolMaxAbsEChange', sci(ts['max_abs_e_change_tight'], 1), ts['max_abs_e_change_tight'], '绝对变化',
              '1 位有效数字', src, 'tolerance_summary.max_abs_e_change_tight', g)
    B.add('rsTolRuns', str(ts['n_runs']), ts['n_runs'], '条', '整数', src, 'tolerance_summary.n_runs', g)
    B.add('rsIdentityResidualMax', sci(ts['max_identity_residual'], 1), ts['max_identity_residual'], '相对残差',
          '1 位有效数字', src, 'tolerance_summary.max_identity_residual', g)
    for nx, word in (('2001', 'TwoThousand'), ('4001', 'FourThousand'), ('8001', 'EightThousand')):
        v = max(cv['pointwise'][f'{case}|immediate']['result'][nx]['max_gap'] for case in ('base', 'xian'))
        B.add(f'rsIrNxGap{word}', sci(v, 2), v, 'S 坐标成本密度', '2 位有效数字', src,
              f'max pointwise.*|immediate.result.{nx}.max_gap', g)
    v = max(max(r['4001']['rel_dt_quad'], r['4001']['rel_J_quad']) for k, r in cv['quadrature_N_z'].items())
    B.add('rsIrNzQuadRelMax', sci(v, 1), v, '相对差', '1 位有效数字', src,
          'max quadrature_N_z.*.4001.rel_{dt,J}_quad', g)
    return B


def write(B, data):
    os.makedirs(os.path.dirname(OUT_TEX), exist_ok=True)
    lines = ['% 由 r7_return/make_numbers.py 自动生成，请勿手改。只含 \\newcommand。',
             '% 来源（r7_return/results/ 下的全精度 JSON 及其 SHA-256）：']
    for k, f in INPUTS.items():
        lines.append(f'%   {f}  {data[k + "_sha256"]}')
    lines += ['% 全精度值、单位与字段路径见 r7_return/results/r7_numbers_full.json。',
              '% 单位：Δt、J 以天计；基准人数以人计；西安人数宏名以 Mil 结尾，以 10^6 人计；百分数不含 % 号。',
              '% 含 \\ensuremath 的宏（负数、科学记数）在正文与数学模式中均可用；放进 siunitx 的 S 列时加花括号。',
              '% 宏名：\\rs + 参数（Base/Xian）+ 情景或控制 + 量。控制：Qonly 仅隔离、Alpha α=0.5、Opt 成本最优、',
              '%   Conly 仅减少接触、Mig 无回流最优律迁移；后缀 Ir 为立即返回对照模型，Nr 为无回流模型 t→∞；',
              '%   Stay{Seven,Fourteen,Thirty,Sixty,Onetwenty,Threesixtyfive} 为平均停留 1/ω（天）；',
              '%   指数回流的终点为退出后首次 I<1 截断，Tend 为截断时刻，Cterm 为截断时的累计新增感染。', '']
    group = None
    for it in B.items:
        if it['group'] != group:
            group = it['group']
            lines.append(f'% ---- {group} ----')
        lines.append(f"\\newcommand{{\\{it['name']}}}{{{it['display']}}}")
    with open(OUT_TEX, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lines) + '\n')
    full = dict(generated_by='r7_return/make_numbers.py', output='paper/generated/r7_numbers.tex',
                inputs={k: dict(file=f, sha256=data[k + '_sha256']) for k, f in INPUTS.items()},
                n_macros=len(B.items), macros={it['name']: {k: v for k, v in it.items() if k != 'name'} for it in B.items})
    with open(OUT_JSON, 'w', encoding='utf-8') as fh:
        json.dump(full, fh, indent=1, ensure_ascii=False, allow_nan=False)
    return len(B.items)


def main():
    data = load()
    B = build(data)
    n = write(B, data)
    print(f'make_numbers：{n} 个宏 → {os.path.relpath(OUT_TEX, ROOT)}；全精度 → {os.path.relpath(OUT_JSON, ROOT)}')


if __name__ == '__main__':
    sys.exit(main())
