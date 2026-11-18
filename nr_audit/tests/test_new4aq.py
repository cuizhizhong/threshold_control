"""NEW-4aq（N45）：第 7 章与补充西安一节逐句修订后，新写出的读数与表 4 同源，删去的图不再入稿。"""
import hashlib
import json
import re

import pytest

from conftest import SRC

ROOT = SRC.ROOT
RES = SRC.HERE / 'results'


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


@pytest.fixture(scope='module')
def rec():
    return json.loads((RES / 'new4aq_ch7.json').read_text(encoding='utf-8'))


def test_routine_readings_match_table4(rec):
    """第 7.3 节新补的常规控制一句：峰值、阈值倍数、总累计与“约为一半”都由表 4 同源的结果得到。"""
    src = rec['readings_source']
    assert hashlib.sha256((ROOT / src['path']).read_bytes()).hexdigest() == src['sha256']
    r = rec['readings']
    xt = text('paper/sections/07_xian.tex')
    # 表 4 中的整数与正文的取整
    assert f"常规控制 & {round(r['routine_peak_I'])} & {round(r['routine_total'])} &" in xt
    sentence = (rf"常规控制下 $I$ 的峰值约 ${r['routine_peak_I'] / 1e6:.2f}\times10^6$ 人，约为阈值的 "
                rf"${r['routine_peak_over_eta']:.0f}$ 倍，总累计新增感染约 ${r['routine_total'] / 1e6:.2f}\times10^6$ 人")
    assert sentence in xt
    assert rf"仅隔离控制约 ${r['q_only_total'] / 1e6:.2f}\times10^6$ 人、成本最优控制约 ${r['opt_total'] / 1e6:.2f}\times10^6$ 人，约为常规控制的一半" in xt
    assert 0.45 < r['q_only_over_routine'] < 0.55 and 0.45 < r['opt_over_routine'] < 0.55
    assert rf"约 ${r['tdinn_t_end']:.0f}$ d 清零" in xt
    assert rf"清零约需 ${r['q_only_t_end']:.0f}$ d（仅隔离控制）至 ${r['opt_t_end']:.0f}$ d（成本最优控制）" in xt


def test_section73_no_longer_repeats_72_numbers():
    xt = text('paper/sections/07_xian.tex')
    s72, s73 = xt.split('\\subsection{控制组合}')[1].split('\\subsection{与实际干预的对照}')
    # NEW-4bb（N56）：171 d、218 d 不再写在第 7.2 节，只留在表 3
    bb = (ROOT / 'paper/revision_notes/NEW_4bb_ch7.md').exists()
    for s in ('约 $0.85$', '约 $171$ d', '约 $218$ d'):
        assert (bb and s != '约 $0.85$' or s in s72) and s not in s73, s
    assert '170.63' not in s73.split('\\begin{table}')[1].split('\\end{table}')[0].split('tablenotes')[1]
    # ⑫ 拆为两段：下界式之后另起一段
    assert '\\]\n\n这一下界是在 $S_c$ 退出必须付出的感染。' in s73


def test_supplement_order_and_removed_figure(rec):
    s6 = text('paper/supplement_sections/S6_xian.tex')
    # NEW-4ax（N52）：“人口缩放”一节（prop:scaling、sec:sup:xian:settings）删去
    cut = (ROOT / 'nr_audit/results/new4ax_scope.json').exists()
    subs = ['设计阈值的取值', '阈值扫描'] + ([] if cut else ['人口缩放'])
    assert re.findall(r'\\subsection\{([^}]*)\}', s6) == subs
    labs = ('sec:sup:threshold-scale', 'sec:sup:xian:threshold-scan', 'tab:sup:eta')
    for lab in labs + (() if cut else ('sec:sup:xian:settings', 'prop:scaling')):
        assert s6.count('\\label{' + lab + '}') == 1, lab
    fig = rec['removed_figure']
    assert hashlib.sha256((ROOT / fig['pdf']).read_bytes()).hexdigest() == fig['pdf_sha256']
    assert fig['label'] not in s6 and '\\begin{figure}' not in s6
    # NEW-4bb（N56）：下界来自正文推导，扫描只与它一致
    bb = (ROOT / 'paper/revision_notes/NEW_4bb_ch7.md').exists()
    assert ('的下界一致：降低阈值不能把感染降到下界以下' if bb else '据此说明，降低阈值不能把感染降到下界以下') in s6
    assert rec['scientific_activity'] == dict(ode_solves=0, optimization_solves=0, fits=0, redraws=0)
