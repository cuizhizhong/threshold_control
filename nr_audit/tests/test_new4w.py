"""NEW-4w（N33）：西安设计阈值改为 η = 0.001N 后，稿件数字、图件与 results/new4w/ 的结果一致。"""
import hashlib
import json

import pytest

import params as PR
from conftest import SRC

ROOT = SRC.ROOT
RES = SRC.HERE / 'results' / 'new4w'


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
    """补充 S6.3：C/N = 4.77e-5、p_ICU = 21/699 × 0.28、κ_I = 1 + (βc0S0/N − γ)/δq，上限向下取整为 0.001。"""
    X = PR.XIAN
    kappa = 1 + (X.beta * X.c0 * X.S0 / X.N - X.gamma) / X.delta_q
    theta_max = 4.77e-5 / (21 / 699 * 0.28 * kappa)
    assert abs(kappa - 5.63) < 0.005 and abs(theta_max - 1.007e-3) < 5e-7
    assert w3['settings']['theta'] == 0.001 <= theta_max and w3['settings']['eta'] == 0.001 * X.N
    s6 = text('paper/supplement_sections/S6_xian.tex')
    assert r'$\kappa_I\approx5.63$' in s6 and r'\approx1.007\times10^{-3}' in s6 and r'$\theta=0.001$' in s6
    s1 = text('paper/supplement_sections/S1_medical.tex')
    assert r'\label{lem:sup:infected-bound}' in s1 and r'\kappa_I=1+\frac{\beta c_0S_0/N-\gamma}{\delta_q}' in s1


def test_table3_and_text_match_results(w3):
    xt = text('paper/sections/07_xian.tex')
    names = dict(c_only='仅减少接触', alpha=r'显式族 $\alpha=0.5$', q_only='仅隔离控制', opt='成本最优控制')
    for law, name in names.items():
        r = w3['laws'][law]
        row = (f"{name} & {r['dt']:.2f} & {r['t_end']:.2f} & {r['total_to_clearance'] / 1e6:.3f} & "
               f"{r['dSq'] / 1e6:.3f} & {r['J']:.2f} & {r['peak_ratio']:.2f}\\\\")
        assert row in xt, row
    assert rf"$S^*/S_c\approx {w3['start']['z_star']:.3f}$" in xt
    cap = w3['capacity']
    assert (not cap['q_only_feasible']) and (not cap['c_only_feasible']) and cap['joint_feasible']
    assert rf"$J\approx {cap['J']:.2f}$ d、$\Delta t\approx {cap['dt']:.1f}$ d" in xt
    q = w3['laws']['q_only']
    assert rf"约为 ${q['total_to_clearance'] / 1e6:.2f}\times10^6$ 人、清零时间约为 ${q['t_end']:.1f}$ d" in xt
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
    assert (f"分别为 ${q['t1']:.2f}$、${q['t2']:.2f}$、${q['dt']:.2f}$ d，成本最优控制分别为 "
            f"${o['t1']:.2f}$、${o['t2']:.2f}$、${o['dt']:.2f}$ d") in xt


def test_population_and_numerics_text(w3):
    pop = w3['population']
    xt, s6 = text('paper/sections/07_xian.tex'), text('paper/supplement_sections/S6_xian.tex')
    for t in (xt, s6):
        assert f"${pop['dt_min']:.2f}$ d" in t and f"${pop['t1_min']:.2f}$ d" in t and f"${pop['t1_max']:.2f}$ d" in t
    assert round(pop['dt_max'] - pop['dt_min'], 4) == 0
    s8 = text('paper/supplement_sections/S8_numerics.tex')
    assert f"隔离比例停在上限约 ${w3['capacity']['segments'][0]['duration']:.2f}$ d" in s8
    assert not w3['post_exit_upcross']


def test_unchanged_weight_brackets(w3):
    ends = w3['weights']['unchanged_ends']
    assert (ends["A->A'"]['class_lo'], ends["A->A'"]['class_hi']) == ('A', "A'")
    assert (ends["A'->B"]['class_lo'], ends["A'->B"]['class_hi']) == ("A'", 'B')
    bc = w3['weights']['B_to_C']
    assert bc['width'] < 1e-3 and all(v == dict(lo='B', hi='C') for v in bc['check_fine'].values())


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
        assert f'{{figures/new4w/{stem}.pdf}}' in text(tex)
    sp = rec['strategy_process']
    assert sp['q_only']['I_dev_max'] < 1e-9 and sp['cost_optimal']['I_dev_max'] < 1e-9
    assert sp['eta'] == 13163.0 and rec['S8']['reference_positions'][1] == 13163.0
