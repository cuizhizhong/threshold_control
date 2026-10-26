"""NEW-4p：数值部分重排所需图件的收据（results/new4p_figures.json）。
核对输入数据的身份未变、入库图件即收据登记的输出、图内字体为 Computer Modern、印刷尺寸与稿件中的宽度一致，
以及图中成本最优控制与能力代表点的数据与稿件表格、正文数字一致。"""
import hashlib
import json
import re

import pytest

from conftest import SRC

RES = SRC.HERE / 'results' / 'new4p_figures.json'
ROOT = SRC.HERE.parent
TEXT_WIDTH_MM = 452.9679 / 72 * 25.4
# 图件 → (稿件文件, includegraphics 宽度写法, 印刷宽度 mm)
USES = {
    'joint_capacity_baseline': ('paper/sections/06_numerics.tex', r'0.8\textwidth', 0.8 * TEXT_WIDTH_MM),
    'joint_phase_baseline': ('paper/sections/06_numerics.tex', r'\textwidth', TEXT_WIDTH_MM),
    'xian_joint': ('paper/sections/07_xian.tex', r'\textwidth', TEXT_WIDTH_MM),
    'xian_strategy_process': ('paper/sections/07_xian.tex', '135mm', 135.0),
}


@pytest.fixture(scope='module')
def receipt():
    if not RES.exists():
        pytest.skip('尚未运行 plot_new4p_figures.py')
    return json.loads(RES.read_text(encoding='utf-8'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def test_inputs_unchanged(receipt):
    # 冻结的计算结果按原字节核对；nr_audit 中的文本结果按 CRLF→LF 后的内容核对（跨平台换行不影响内容身份）
    for rel, rec in receipt['inputs'].items():
        raw = (ROOT / rel).read_bytes()
        if rel.startswith('nr_audit/') and 'content_sha256' in rec:
            assert sha(raw.replace(b'\r\n', b'\n')) == rec['content_sha256'], rel
        else:
            assert sha(raw) == rec['sha256'], rel


@pytest.mark.parametrize('name', sorted(USES))
def test_outputs_registered_and_used(receipt, name):
    rel = f'paper/figures/new4p/{name}.pdf'
    out = receipt['outputs'][rel]
    assert sha((ROOT / rel).read_bytes()) == out['sha256']
    assert out['fonts'] and all(re.search(r'Cm(r|mi|sy|ex)10', f) for f in out['fonts'])
    tex, width, width_mm = USES[name]
    assert abs(out['size_mm'][0] - width_mm) < 0.05
    text = (ROOT / tex).read_text(encoding='utf-8')
    assert f'\\includegraphics[width={width}]{{figures/new4p/{name}.pdf}}' in text


def test_cost_optimal_trajectory_matches_tables(receipt):
    sp = receipt['checks']['xian_strategy_process']
    assert all(v < 1e-12 for v in sp['Re_formula_max_rel_err'].values())
    qo = sp['quarantine_only_cross_check']
    assert abs(qo['t1_diff']) < 1e-9 and abs(qo['t2_diff']) < 1e-9 and abs(qo['Itcum_end_rel_diff']) < 1e-12
    co = sp['cost_optimal']
    xian = (ROOT / 'paper/sections/07_xian.tex').read_text(encoding='utf-8')
    assert f"成本最优控制 & 26326 & {round(co['Itcum_end'])} & {co['t_end']:.2f}\\\\" in xian
    assert f"成本最优控制 & {co['duration']:.2f} & {co['t_end']:.2f} & {co['Itcum_end'] / 1e6:.3f}" in xian
    assert f"{co['t1']:.2f}$、${co['t2']:.2f}$、${co['duration']:.2f}$ d" in xian
    assert round(co['I_max']) == 26326 and abs(co['I_end'] - 1) < 1e-9
    assert f"{100 * (1 - co['c_min'] / 12.8872):.1f}" == '28.2'


def test_capacity_points_match_text(receipt):
    base = receipt['checks']['joint_capacity_baseline']
    xian = receipt['checks']['xian_joint']['capacity']
    assert (base['point']['u_max'], base['point']['q_cap']) == (0.5, 0.6)
    assert (xian['point']['u_max'], xian['point']['q_cap']) == (0.5, 0.75)
    num = (ROOT / 'paper/sections/06_numerics.tex').read_text(encoding='utf-8')
    xt = (ROOT / 'paper/sections/07_xian.tex').read_text(encoding='utf-8')
    assert f"J\\approx {base['J']:.3f}$ d、$\\Delta t\\approx {base['duration']:.2f}$ d" in num
    assert f"J\\approx {xian['J']:.2f}$ d、$\\Delta t\\approx {xian['duration']:.1f}$ d" in xt
    assert base['q_required_quarantine_only'] > base['point']['q_cap'] and xian['q_required_quarantine_only'] > xian['point']['q_cap']
    assert base['u_required_contact_only'] > base['point']['u_max'] and xian['u_required_contact_only'] > xian['point']['u_max']


def test_phase_panels_reuse_new4d_cache(receipt):
    ph = receipt['checks']
    assert ph['joint_phase_baseline']['gamma_points'] > 0 and ph['xian_joint']['phase']['gamma_points'] > 0
    assert 2 < ph['xian_joint']['phase']['r_cont'] < 4 and 2 < ph['joint_phase_baseline']['r_cont'] < 4
    render = json.loads((SRC.HERE / 'results' / 'new4d_figure7_render.json').read_text(encoding='utf-8'))
    assert ph['joint_phase_baseline']['profile_jumps'] == render['profile_jumps']
