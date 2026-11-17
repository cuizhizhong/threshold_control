"""NEW-4w（N33）：西安设计阈值改为 η = 0.001N 后，稿件数字、图件与 results/new4w/ 的结果一致。"""
import hashlib
import json

import pytest

import params as PR
from conftest import SRC

ROOT = SRC.ROOT
RES = SRC.HERE / 'results' / 'new4w'
NEW4AP = SRC.HERE / 'results' / 'new4ap_scope.json'   # NEW-4ap（N44）：删去能力约束的收据
NEW4AQ = SRC.HERE / 'results' / 'new4aq_ch7.json'     # NEW-4aq（N45）：第 7 章逐句修订的收据
NEW4AT = SRC.HERE / 'results' / 'new4at_scope.json'   # NEW-4at（N48）：删去显式控制族的收据


@pytest.fixture(scope='module')
def w3():
    f = RES / 'xian_theta001.json'
    if not f.exists():
        pytest.skip('尚未运行 new4w_xian_threshold.py')
    return json.loads(f.read_text(encoding='utf-8'))


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def test_precheck_reproduces_old_manuscript(w3):
    pre = w3['precheck']
    assert pre['ok'] and all(x['ok'] for x in pre['table3']) and all(x['ok'] for x in pre['table4'])
    assert pre['phase']['max_abs_diff_y'] < 1e-10 and pre['region']['region_equal']


def test_threshold_value_from_supplement_inputs(w3):
    """补充 S6.3：C/N = 4.75e-5、p_ICU = 0.03 × 0.28、κ_I = 1 + (βc0S0/N − γ)/δq，上限向下取整为 0.001。"""
    X = PR.XIAN
    kappa = 1 + (X.beta * X.c0 * X.S0 / X.N - X.gamma) / X.delta_q
    theta_max = 4.75e-5 / (0.03 * 0.28 * kappa)
    assert abs(kappa - 5.63) < 0.005 and abs(theta_max - 1.004e-3) < 5e-7
    assert w3['settings']['theta'] == 0.001 <= theta_max and w3['settings']['eta'] == 0.001 * X.N
    s6 = text('paper/supplement_sections/S6_xian.tex')
    assert r'$\kappa_I\approx5.63$' in s6 and r'\approx1.004\times10^{-3}' in s6 and r'$\theta=0.001$' in s6
    s1 = text('paper/supplement_sections/S1_medical.tex')
    assert r'\label{lem:sup:infected-bound}' in s1 and r'\kappa_I=1+\frac{\beta c_0S_0/N-\gamma}{\delta_q}' in s1


def test_table3_and_text_match_results(w3):
    xt = text('paper/sections/07_xian.tex')
    names = dict(c_only='仅减少接触', alpha=r'显式族 $\alpha=0.5$', q_only='仅隔离控制', opt='成本最优控制')
    for law, name in names.items():
        r = w3['laws'][law]
        if law == 'alpha' and NEW4AT.exists():          # NEW-4at（N48）：表 3 删去 alpha = 0.5 一行，结果文件不变
            assert f'{name} &' not in xt
            continue
        row = (f"{name} & {r['dt']:.2f} & {r['t_end']:.2f} & {r['total_to_clearance'] / 1e6:.3f} & "
               f"{r['dSq'] / 1e6:.3f} & {r['J']:.2f} & {r['peak_ratio']:.2f}\\\\")
        assert row in xt, row
    assert rf"$S^*/S_c\approx {w3['start']['z_star']:.3f}$" in xt
    cap = w3['capacity']
    assert (not cap['q_only_feasible']) and (not cap['c_only_feasible']) and cap['joint_feasible']
    # NEW-4ap（N44）：删去能力约束后，能力代表点的结果不再入稿；结果文件中的值不变
    assert (rf"$J\approx {cap['J']:.2f}$ d、$\Delta t\approx {cap['dt']:.1f}$ d" in xt) == (not NEW4AP.exists())
    q = w3['laws']['q_only']
    # NEW-4am（N41）：第 7.3 节重写后的写法，数值不变
    assert rf"仅隔离控制约 ${q['total_to_clearance'] / 1e6:.2f}\times10^6$ 人" in xt
    if NEW4AQ.exists():
        # NEW-4aq（N45）：第 7.3 节第 2 段不再重复 7.2 节的控制时长，只留清零时间
        o = w3['laws']['opt']
        assert rf"清零约需 ${q['t_end']:.0f}$ d（仅隔离控制）至 ${o['t_end']:.0f}$ d（成本最优控制）" in xt
    else:
        assert rf"但要维持约 ${q['dt']:.0f}$ d，清零时间约 ${q['t_end']:.0f}$ d" in xt
    assert r'$0.001N=\num{13163}$' in xt and '0.002N' not in xt


def test_table4_matches_results(w3):
    xt = text('paper/sections/07_xian.tex')
    st = w3['strategies']
    assert round(st['TDINN']['total'], 2) == 2105.63 and round(st['TDINN']['t_end'], 2) == 45.29
    assert round(st['routine']['peak_I']) == 1377552 and round(st['routine']['total']) == 4587183
    for law, name in (('q_only', '仅隔离控制'), ('opt', '成本最优控制')):
        s = st[law]
        assert f"{name} & 13163 & {round(s['total'])} & {s['t_end']:.2f}\\\\" in xt
    q, o = st['q_only'], st['opt']
    if NEW4AQ.exists():
        # NEW-4aq（N45）：表 4 注删去与表 3 重复的控制时长，只留启动与退出时刻
        assert f"{q['t1']:.2f}" == f"{o['t1']:.2f}"
        assert (f"两种阈值控制都在 ${q['t1']:.2f}$ d 启动，仅隔离控制与成本最优控制分别在 "
                f"${q['t2']:.2f}$ d 与 ${o['t2']:.2f}$ d 退出") in xt
        return
    assert (f"分别为 ${q['t1']:.2f}$、${q['t2']:.2f}$、${q['dt']:.2f}$ d，成本最优控制分别为 "
            f"${o['t1']:.2f}$、${o['t2']:.2f}$、${o['dt']:.2f}$ d") in xt


def test_population_and_numerics_text(w3):
    pop = w3['population']
    xt, s6 = text('paper/sections/07_xian.tex'), text('paper/supplement_sections/S6_xian.tex')
    # NEW-4am（N41）：六个人口规模的数值经作者授权不再入稿（第 7.5 节与补充 S6.1 的两段数值删去）；
    # 结果文件只读保留，这里只核对结果本身与稿中不再出现相应文字。
    assert round(pop['dt_max'] - pop['dt_min'], 4) == 0 and f"{pop['t1_min']:.2f}" == '10.70'
    for t in (xt, s6):
        assert f"${pop['t1_min']:.2f}$ d" not in t and 'prop:reference-population' not in t and 'sec:dominance' not in t
    # NEW-4ax（N52）：补充命题 prop:scaling 删去
    if (SRC.HERE / 'results/new4ax_scope.json').exists():
        assert 'prop:scaling' not in s6 and '人口缩放' not in s6
    else:
        assert r'\label{prop:scaling}' in s6 and r'\lambda' not in s6.split(r'\end{proposition}')[0]
    # NEW-4ao（N43）：能力约束起作用的前一段时长由补充 S8 末段移入第 7.2 节，数值不变。
    s8 = text('paper/supplement_sections/S8_numerics.tex')
    seg = f"{w3['capacity']['segments'][0]['duration']:.2f}"
    # NEW-4ap（N44）：第 7.2 节能力区域一段删去，该时长只留在结果文件中
    assert seg == '61.64' and (f"启动后约 ${seg}$ d 内隔离比例停在上限" in xt) == (not NEW4AP.exists()) and seg not in s8
    assert not w3['post_exit_upcross']


def test_unchanged_weight_brackets(w3):
    ends = w3['weights']['unchanged_ends']
    assert (ends["A->A'"]['class_lo'], ends["A->A'"]['class_hi']) == ('A', "A'")
    assert (ends["A'->B"]['class_lo'], ends["A'->B"]['class_hi']) == ("A'", 'B')
    bc = w3['weights']['B_to_C']
    assert bc['width'] < 1e-3 and all(v == dict(lo='B', hi='C') for v in bc['check_fine'].values())


def test_return14_macros_trace_to_summary():
    f = RES / 'return14_summary.json'
    if not f.exists():
        pytest.skip('尚未运行 new4w_return14/run_all.py')
    d = json.loads(f.read_text(encoding='utf-8'))
    by = {m['macro']: m for m in json.loads((SRC.HERE / 'results/nr_numbers_map.json').read_text(encoding='utf-8'))['macros']}
    for case, tag, scale in (('base', 'Base', 1.0), ('xian', 'Xian', 1e6)):
        c = d['cases'][case]
        for ct, r in (('Q', c['references']['q_only']), ('C', c['references']['c_only']),
                      ('M', c['references']['opt_noreturn']), ('O', c['optimization']['cost']['final_replay'])):
            assert by[f'\\nrRw{tag}{ct}Dt']['value'] == r['duration']
            assert by[f'\\nrRw{tag}{ct}J']['value'] == r['J']
            assert by[f'\\nrRw{tag}{ct}Inf']['value'] == r['C_Tcut'] / scale
            assert r['feasible'] and r['U_Tcut_over_Sc'] < 1


def test_return14_claims_in_text():
    """补充 S7 与第 8.3 节所写的仍成立的结论：仅隔离最快、仅减少接触最慢，成本最优控制先仅隔离，退出后不越过阈值。"""
    f = RES / 'return14_summary.json'
    if not f.exists():
        pytest.skip('尚未运行 new4w_return14/run_all.py')
    d = json.loads(f.read_text(encoding='utf-8'))
    for case in ('base', 'xian'):
        a = d['cases'][case]['answers']
        assert a['Q1_time_optimal_vs_q_only']['rel_diff'] < 1e-8 and a['Q1_time_optimal_vs_q_only']['c_only_slowest']
        prof = a['Q3_cost']['profile']
        assert prof['head'][0] > 0.999 and 0 < prof['first_tau_below_0p99'] < 0.5 and prof['min'] < 0.5
        assert 0 < a['Q3_cost']['gap_noreturn_law_percent'] < 5
        assert all(v in ('satisfied', 'boundary_roundoff') for v in a['Q4_threshold'].values())
    s7 = text('paper/supplement_sections/S7_return.tex')
    for gone in ('lem:return:U', 'prop:return:final-size', 'cor:return:right-discontinuity', 'eq:return:tail',
                 'tab:sup:return:cinf', 'nrRetTerm', '7,14,30'):
        assert gone not in s7
    assert r'\label{tab:sup:return:term}' in s7 and r'\label{eq:return:cut}' in s7 and r'\nrRwXianQDt' in s7
    # NEW-4x：重新优化在退出后尾段网格上施加 I <= eta（collocation.py 的 postcap），S7 须写明
    assert '尾段的积分网格上作为约束施加' in s7
    d83 = text('paper/sections/08_discussion.tex')
    if (ROOT / 'paper/sections/09_conclusion.tex').exists():
        assert '仅隔离控制仍是控制时长最短的数值解' in d83 and 'eq:return:tail' not in d83
    else:
        # NEW-4av（N50）：第 8、9 章合并，回流数值一段改写为两句，排序结论不变
        assert '仅隔离控制的控制时长仍最短，仅减少接触仍最长' in d83 and 'eq:return:tail' not in d83


def test_new_figures_used_and_registered():
    f = RES / 'figures.json'
    if not f.exists():
        pytest.skip('尚未运行 plot_new4w_figures.py')
    rec = json.loads(f.read_text(encoding='utf-8'))
    for key, stem, tex in (('Main8', 'Main8', 'paper/sections/07_xian.tex'),
                           ('strategy_process', 'xian_strategy_process', 'paper/sections/07_xian.tex'),
                           ('S8', 'S8', 'paper/supplement_sections/S6_xian.tex')):
        pdf = ROOT / f'paper/figures/new4w/{stem}.pdf'
        assert hashlib.sha256(pdf.read_bytes()).hexdigest() == rec[key]['pdf_sha256']
        new4al = ROOT / 'nr_audit/results/new4al_notation.json'
        if key == 'Main8' and NEW4AP.exists():
            # NEW-4ap（N44）：图 8 改为权重相图加剖面，正式引用改为 figures/new4ap/Main8.pdf；new4w、new4al 图件只读保留
            rep = json.loads(NEW4AP.read_text(encoding='utf-8'))['replaced_figures']['Main8']
            assert '{figures/new4ap/Main8.pdf}' in text(tex) and '{figures/new4al/Main8.pdf}' not in text(tex)
            assert hashlib.sha256((ROOT / rep['new_pdf']).read_bytes()).hexdigest() == rep['new_pdf_sha256']
            continue
        if key == 'Main8' and new4al.exists():
            # NEW-4al（N40）：图 8 只把纵轴记号 q_cap 改为 q_max 后重绘，正式引用改为 figures/new4al/Main8.pdf
            r4 = json.loads(new4al.read_text(encoding='utf-8'))['figures']['fig:xian:joint']
            assert r4['current_pdf'] == 'paper/figures/new4w/Main8.pdf' and r4['reproduced_sha256'] == rec[key]['pdf_sha256']
            assert '{figures/new4al/Main8.pdf}' in text(tex)
            continue
        new4am = ROOT / 'nr_audit/results/new4am_scope.json'
        if key == 'S8' and new4am.exists():
            # NEW-4am（N41）：补充图 fig:xian_heatmaps 经作者授权不再入稿；图件字节只读保留
            g = json.loads(new4am.read_text(encoding='utf-8'))['removed_figures']['S8']
            assert g['pdf'] == f'paper/figures/new4w/{stem}.pdf' and g['pdf_sha256'] == rec[key]['pdf_sha256']
            assert f'{{figures/new4w/{stem}.pdf}}' not in text(tex) and g['label'] not in text(tex)
            continue
        assert f'{{figures/new4w/{stem}.pdf}}' in text(tex)
    sp = rec['strategy_process']
    assert sp['q_only']['I_dev_max'] < 1e-9 and sp['cost_optimal']['I_dev_max'] < 1e-9
    assert sp['eta'] == 13163.0 and rec['S8']['reference_positions'][1] == 13163.0
