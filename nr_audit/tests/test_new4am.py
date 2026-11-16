"""NEW-4am（N41）：范围收紧后，删去的内容不再入稿，新写出的西安读数与论断都能追溯到已登记的结果。"""
import json
import math
import re

import pytest

import params as PR
import tdinn as TD
from conftest import SRC
from text_identity import content_sha256

ROOT = SRC.ROOT
RES = SRC.HERE / 'results'


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


@pytest.fixture(scope='module')
def scope():
    return json.loads((RES / 'new4am_scope.json').read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def w3():
    return json.loads((RES / 'new4w/xian_theta001.json').read_text(encoding='utf-8'))


def test_removed_content_absent_and_archive_intact(scope):
    supp = scope['current_inputs']['paper/flatten_curve_supplement_cn.tex']
    arch = scope['archived_source']
    assert arch['path'] not in supp and 'S3_inflection' not in text('paper/flatten_curve_supplement_cn.tex')
    assert content_sha256((ROOT / arch['path']).read_bytes()) == arch['content_sha256']
    # NEW-4av（N50）：第 9 章并入第 8 章，09_conclusion.tex 删去
    current = ''.join(text(f) for fs in scope['current_inputs'].values() for f in fs
                      if f != 'paper/sections/09_conclusion.tex' or (ROOT / f).exists())
    for lab in scope['removed_labels']:
        assert f'\\label{{{lab}}}' not in current and f'{{{lab}}}' not in current, lab
    for gone in ('N_{\\rm floor}', 'N_{\\rm eff}', '40.5', '低阈值极限'):
        assert gone not in current, gone
    assert scope['scientific_activity'] == dict(ode_solves=0, optimization_solves=0, fits=0, redraws=0)


def test_chapter7_structure():
    xt = text('paper/sections/07_xian.tex')
    assert re.findall(r'\\subsection\{([^}]*)\}', xt) == ['数据与参数', '控制组合', '与实际干预的对照']
    for lab in ('sec:xian:data', 'sec:xian:joint', 'sec:xian:threshold-scale', 'fig:xian:observed-fit',
                'fig:xian:joint', 'fig:xian:strategy-process', 'tab:xian:joint-compare', 'tab:xian_summary'):
        assert xt.count(f'\\label{{{lab}}}') == 1, lab
    d = text('paper/sections/08_discussion.tex')
    if (ROOT / 'paper/sections/09_conclusion.tex').exists():
        assert 'sec:xian:threshold-scale' in d and 'prop:scaling' in d
    else:
        # NEW-4av（N50）：第 8、9 章合并，原 8.1 节第 3 段（退出下界，回指 7.3 节）删去，有效人口一句仍引 prop:scaling
        assert 'sec:xian:threshold-scale' not in d and 'prop:scaling' in d


def test_new_macros_trace_to_results(scope, w3):
    by = {m['macro']: m for m in json.loads((RES / 'nr_numbers_map.json').read_text(encoding='utf-8'))['macros']}
    assert set(scope['new_macros']) <= set(by)
    cut = by['\\nrXianCutContactPct']
    assert cut['value'] == 100 * w3['region']['contact_line'] and cut['display'] == '77.3'
    assert abs(w3['region']['contact_line'] - (1 - 1 / w3['start']['z_star'])) < 1e-12
    laws = w3['laws']
    diff = by['\\nrXianSingleDiffM']
    d_inf = (laws['c_only']['total_to_clearance'] - laws['q_only']['total_to_clearance']) / 1e6
    d_sq = (laws['q_only']['dSq'] - laws['c_only']['dSq']) / 1e6
    assert diff['value'] == d_inf and abs(d_inf - d_sq) < 1e-6 and diff['display'] == '1.49'
    xt = text('paper/sections/07_xian.tex')
    assert xt.count('\\nrXianCutContactPct') == 2 and xt.count('\\nrXianSingleDiffM') == 1


def test_new_readings_match_tables(w3):
    xt, s6 = text('paper/sections/07_xian.tex'), text('paper/supplement_sections/S6_xian.tex')
    laws = w3['laws']
    assert rf"约 ${laws['c_only']['dSq'] / 1e6:.2f}\times10^6$ 名未感染者" in xt
    assert rf"未感染者约 ${laws['q_only']['dSq'] / 1e6:.2f}\times10^6$ 人" in xt
    assert rf"约为 $\eta$ 的 ${laws['q_only']['peak_ratio']:.2f}$ 倍" in xt
    assert abs(laws['q_only']['peak_ratio'] - laws['opt']['peak_ratio']) < 1e-9
    for name, law in (('仅隔离控制', 'q_only'), ('成本最优控制', 'opt'), ('仅减少接触', 'c_only')):
        assert f"{name}约 ${laws[law]['dt']:.0f}$ d" in xt
    # 阈值扫描两端（补充表 tab:sup:eta，数值不变）
    assert '0.0001 & 0.8470 & 1710.66 & 2209.55 & 826.4066 & 2155649' in s6
    assert '0.0100 & 0.8382 & 16.61 & 123.89 & 7.6781 & 2737382' in s6
    assert r'$2.74\times10^6$ 人降到约 $2.16\times10^6$ 人，控制时长却由 $16.6$ d 增至 $1711$ d' in xt
    X = PR.XIAN
    Sc = X.gamma * X.N / (X.beta * X.c0 * (1 - X.q0))
    assert f'{X.beta * (X.S0 - Sc) / 1e6:.2f}' == '1.53' and r'\approx1.53\times10^6' in xt
    assert f'{(1 - X.beta) / X.beta:.1f}' == '5.7' and r'(1-\beta)/\beta\approx5.7' in xt
    assert f'{X.N / Sc:.2f}' == '4.43' and f"{w3['start']['z_star']:.2f}" == '4.40'


def test_tdinn_intensity_claim(w3):
    """第 7.2 节：以 TDINN 达到的强度为能力上限，仅隔离控制与成本最优控制可行，仅减少接触所需的降幅略高。"""
    c_inf, q_inf = TD.c_tdinn(1e6), TD.q_tdinn(1e6)          # 控制函数的极限值
    X = PR.XIAN
    cut_tdinn = 1 - c_inf / X.c0
    assert f'{100 * cut_tdinn:.0f}' == '73' and f'{q_inf:.2f}' == '0.98'
    xt = text('paper/sections/07_xian.tex')
    assert r'隔离比例趋向约 $0.98$、接触率降低约 $73\%$' in xt
    q1 = w3['start']['q_max']                    # 结果文件沿用旧字段名，即仅隔离控制启动时的隔离比例 q_1
    assert f'{q1:.2f}' == '0.85' and q1 < q_inf
    opt_cut = float(re.search(r'后段接触率最多降低约 \$([0-9.]+)\\%\$', xt)[1]) / 100
    assert opt_cut < cut_tdinn < w3['region']['contact_line']


def test_weight_bounds_depend_only_on_b(w3):
    """第 7.2 节：r_cont 与 r̂ 只通过 b = (1-β)(1-q0) 依赖参数。"""
    case = w3['phase']['case']
    X = PR.XIAN
    b = (1 - X.beta) * (1 - X.q0)
    assert abs(b - case['b']) < 1e-12
    z_sw = (3 + math.sqrt(9 - 8 * b)) / 2
    assert abs(z_sw - case['z_sw']) < 1e-12
    assert abs((z_sw / (z_sw - 1)) ** 2 - case['r_hat']) < 1e-10
    assert abs(16 / (b + math.sqrt(b * b - 8 * b + 8)) ** 2 - case['r_cont']) < 1e-10
    B = PR.BASE
    bb = (1 - B.beta) * (1 - B.q0)
    assert b < bb and 16 / (b + math.sqrt(b * b - 8 * b + 8)) ** 2 < 16 / (bb + math.sqrt(bb * bb - 8 * bb + 8)) ** 2
