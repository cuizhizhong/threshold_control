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
    'xian_observed_fit': ('paper/sections/07_xian.tex', r'\textwidth', TEXT_WIDTH_MM),
}
ADOPTED_NEW4T = {'joint_phase_baseline': 'Main6', 'xian_joint': 'Main8'}
# NEW-4w（N33）：西安设计阈值改为 0.001N，图 8、图 9 由 plot_new4w_figures.py 重绘；历史图件与收据只读保留。
NEW4W = SRC.HERE / 'results' / 'new4w' / 'figures.json'
SUPERSEDED_NEW4W = {'xian_joint': ('Main8', 'Main8'), 'xian_strategy_process': ('xian_strategy_process', 'strategy_process')}
PRE_NEW4W = 'ebb7df5'
# NEW-4al（N40）：隔离比例两个记号调换后，图 5 与图 8 只改纵轴记号重绘到 figures/new4al/；被取代图件与收据只读保留。
NEW4AL = SRC.HERE / 'results' / 'new4al_notation.json'
SUPERSEDED_NEW4AL = {'joint_capacity_baseline': 'fig:joint:capacity', 'xian_joint': 'fig:xian:joint'}
# NEW-4ap（N44）：删去能力约束，图 5 不再入稿，图 8 改为权重相图加剖面（figures/new4ap/）；NEW-4al 图件只读保留。
NEW4AP = SRC.HERE / 'results' / 'new4ap_scope.json'
SUPERSEDED_NEW4AP = SUPERSEDED_NEW4AL


def xian_text():
    """NEW-4p 收据记录的是 η = 0.002N 的数值；NEW-4w 之后与改表前的稿件对照。"""
    if NEW4W.exists():
        import subprocess
        return subprocess.run(['git', 'show', f'{PRE_NEW4W}:paper/sections/07_xian.tex'], cwd=ROOT,
                              capture_output=True, check=True).stdout.decode('utf-8')
    return (ROOT / 'paper/sections/07_xian.tex').read_text(encoding='utf-8')


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
    adopted = SRC.HERE / 'results/new4t_figures.json'
    if name in SUPERSEDED_NEW4AP and NEW4AP.exists():
        scope = json.loads(NEW4AP.read_text(encoding='utf-8'))
        rec = json.loads(NEW4AL.read_text(encoding='utf-8'))['figures'][SUPERSEDED_NEW4AP[name]]
        assert sha((ROOT / rec['pdf']).read_bytes()) == rec['pdf_sha256'] and rec['pdf'].removeprefix('paper/') not in text
        if name == 'joint_capacity_baseline':
            assert scope['removed_figures'][name]['pdf_sha256'] == rec['pdf_sha256'] and 'fig:joint:capacity' not in text
        else:
            new = scope['replaced_figures']['Main8']
            assert new['old_pdf_sha256'] == rec['pdf_sha256']
            assert sha((ROOT / new['new_pdf']).read_bytes()) == new['new_pdf_sha256']
            assert f"\\includegraphics[width={width}]{{{new['new_pdf'].removeprefix('paper/')}}}" in text
    elif name in SUPERSEDED_NEW4AL and NEW4AL.exists():
        rec = json.loads(NEW4AL.read_text(encoding='utf-8'))['figures'][SUPERSEDED_NEW4AL[name]]
        assert sha((ROOT / rec['current_pdf']).read_bytes()) == rec['current_pdf_sha256'] == rec['reproduced_sha256']
        assert sha((ROOT / rec['pdf']).read_bytes()) == rec['pdf_sha256']
        assert f"\\includegraphics[width={width}]{{{rec['pdf'].removeprefix('paper/')}}}" in text
    elif name in SUPERSEDED_NEW4W and NEW4W.exists():
        stem, key = SUPERSEDED_NEW4W[name]
        rec = json.loads(NEW4W.read_text(encoding='utf-8'))[key]
        assert sha((ROOT / f'paper/figures/new4w/{stem}.pdf').read_bytes()) == rec['pdf_sha256']
        assert f'\\includegraphics[width={width}]{{figures/new4w/{stem}.pdf}}' in text
    elif name in ADOPTED_NEW4T and adopted.exists():
        # 保留以上NEW-4p历史图件校验，正式引用改核对已批准入稿的新图。
        current_rel = f'paper/figures/new4t/{ADOPTED_NEW4T[name]}.pdf'
        current = json.loads(adopted.read_text(encoding='utf-8'))['outputs'][current_rel]
        assert sha((ROOT / current_rel).read_bytes()) == current['sha256']
        if current.get('author_approved_colorbar_cleanup'):
            assert current['colorbar_cleanup']['previous_pdf_sha256'] == current['approved_preview_sha256']
        else:
            assert current['sha256'] == current['approved_preview_sha256']
        assert f'\\includegraphics[width={width}]{{figures/new4t/{ADOPTED_NEW4T[name]}.pdf}}' in text
    else:
        assert f'\\includegraphics[width={width}]{{figures/new4p/{name}.pdf}}' in text


def test_cost_optimal_trajectory_matches_tables(receipt):
    sp = receipt['checks']['xian_strategy_process']
    assert all(v < 1e-12 for v in sp['Re_formula_max_rel_err'].values())
    qo = sp['quarantine_only_cross_check']
    assert abs(qo['t1_diff']) < 1e-9 and abs(qo['t2_diff']) < 1e-9 and abs(qo['Itcum_end_rel_diff']) < 1e-12
    co = sp['cost_optimal']
    xian = xian_text()
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
    xt = xian_text()
    base_s = f"J\\approx {base['J']:.3f}$ d、$\\Delta t\\approx {base['duration']:.2f}$ d"
    xian_s = f"J\\approx {xian['J']:.2f}$ d、$\\Delta t\\approx {xian['duration']:.1f}$ d"
    # xian_text() 取 NEW-4w 之前的历史稿；NEW-4ap（N44）后基准代表点的结果不再入稿，收据中的值不变
    assert xian_s in xt and (base_s in num) == (not NEW4AP.exists())
    assert base['q_required_quarantine_only'] > base['point']['q_cap'] and xian['q_required_quarantine_only'] > xian['point']['q_cap']
    assert base['u_required_contact_only'] > base['point']['u_max'] and xian['u_required_contact_only'] > xian['point']['u_max']


def test_observed_fit_matches_text(receipt):
    """图 7 的观测病例数与第 7.1 节一致；模型 40 日累计与补充 S8 记录的 TDINN 拟合轨迹在 t=40 d 的值一致。"""
    of = receipt['checks']['xian_observed_fit']
    assert (of['observed_days'], of['observed_community'], of['observed_quarantine'], of['observed_total']) == (40, 583, 1467, 2050)
    s8 = (ROOT / 'paper/supplement_sections/S8_numerics.tex').read_text(encoding='utf-8')
    # NEW-4ao（N43）：补充 S8 中 TDINN 在 t=40 d 与清零时的累计一句经作者同意删去；收据中的值不变，只核对它不再入稿。
    assert f"{of['model_total_40d']:.4f}" == '2098.9747' and '2098.9747' not in s8


def test_phase_panels_reuse_new4d_cache(receipt):
    ph = receipt['checks']
    assert ph['joint_phase_baseline']['gamma_points'] > 0 and ph['xian_joint']['phase']['gamma_points'] > 0
    assert 2 < ph['xian_joint']['phase']['r_cont'] < 4 and 2 < ph['joint_phase_baseline']['r_cont'] < 4
    render = json.loads((SRC.HERE / 'results' / 'new4d_figure7_render.json').read_text(encoding='utf-8'))
    assert ph['joint_phase_baseline']['profile_jumps'] == render['profile_jumps']
    # 红线接到三角 (S*/S_c, r_C)：按最后两个采样点外推到 r_C，应落在 S*/S_c 附近，接上的一段不改变曲线走势
    for tail in (ph['joint_phase_baseline']['endpoint_tail'], ph['xian_joint']['phase']['endpoint_tail']):
        assert tail['last_sample']['r'] < tail['endpoint']['r'] and tail['last_sample']['z'] < tail['endpoint']['z']
        assert abs(tail['z_extrapolated_at_r_C'] - tail['endpoint']['z']) < 0.01
