"""NEW-4ap（N44）：删去能力约束后，被删的陈述、标签与图不再入稿；图 8 的新读数与收敛宏都能追溯到结果文件。"""
import hashlib
import json
import math
import re

import pytest

import params as PR
from conftest import SRC

ROOT = SRC.ROOT
RES = SRC.HERE / 'results'


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


@pytest.fixture(scope='module')
def scope():
    return json.loads((RES / 'new4ap_scope.json').read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def fig8():
    return json.loads((RES / 'new4ap_fig8.json').read_text(encoding='utf-8'))


def macros():
    return {m['macro']: m for m in json.loads((RES / 'nr_numbers_map.json').read_text(encoding='utf-8'))['macros']}


def test_removed_content_absent(scope):
    # NEW-4av（N50）：第 9 章并入第 8 章，09_conclusion.tex 删去
    current = ''.join(text(f) for fs in scope['current_inputs'].values() for f in fs
                      if f != 'paper/sections/09_conclusion.tex' or (ROOT / f).exists())
    for lab in scope['removed_labels']:
        assert '{' + lab + '}' not in current, lab
    for term in scope['removed_terms']:
        assert term not in current, term
    for name, rec in scope['removed_figures'].items():
        assert hashlib.sha256((ROOT / rec['pdf']).read_bytes()).hexdigest() == rec['pdf_sha256']
        assert rec['pdf'].removeprefix('paper/') not in current
    assert scope['scientific_activity']['ode_solves'] == 0 and not scope['scientific_activity']['phase_background_recomputed']


def test_chapter_structure():
    num = text('paper/sections/06_numerics.tex')
    second = '三种控制的比较' if (RES / 'new4at_scope.json').exists() else '四种控制的比较'   # NEW-4at（N48）
    assert re.findall(r'\\subsection\{([^}]*)\}', num) == ['参数与方法', second, '成本权重']
    ch5 = text('paper/sections/05_quadratic_cost.tex')
    assert re.findall(r'\\subsection\{([^}]*)\}', ch5) == ['逐状态约化', '最优组合的结构', '阈值与权重的影响']
    ch4 = text('paper/sections/04_joint_control.tex')
    # 推论 cor:joint:whole-epidemic(ii) 在 A(η) 中陈述两端
    assert '在 $\\mathcal A(\\eta)$ 中，仅隔离控制同时达到最短的控制时长' in ch4
    intro = text('paper/sections/01_introduction.tex')
    assert '第四，' not in intro and '（2）' not in intro


def test_fig8_output_and_inputs(fig8, scope):
    rep = scope['replaced_figures']['Main8']
    assert fig8['output']['pdf'] == rep['new_pdf'] and fig8['output']['pdf_sha256'] == rep['new_pdf_sha256']
    assert hashlib.sha256((ROOT / rep['new_pdf']).read_bytes()).hexdigest() == rep['new_pdf_sha256']
    reg = json.loads((RES / 'new4al_notation.json').read_text(encoding='utf-8'))['inputs']
    for key, got in fig8['inputs'].items():
        assert got['sha256'] == reg[key]['sha256'] or got['content_sha256'] == reg[key]['content_sha256'], key
    npz = fig8['profiles_npz']
    assert hashlib.sha256((ROOT / npz['path']).read_bytes()).hexdigest() == npz['sha256']
    assert '{figures/new4ap/Main8.pdf}' in text('paper/sections/07_xian.tex')


def test_fig8_readings_and_structure(fig8):
    """五个权重对应五种结构；r = 2.63 的跳变与补充命题 prop:sup:jump 的闭式一致；读数与宏一致。"""
    c = fig8['case']
    X = PR.XIAN
    b = (1 - X.beta) * (1 - X.q0)
    assert abs(b - c['b']) < 1e-12
    assert c['r_cont'] < 2.63 < c['r_hat'] < 4 < c['r_C'] < 10
    by = {r['r']: r for r in fig8['readings']}
    zj = 2 * (b + (1 - b) * math.sqrt(2.63))
    j = by[2.63]['jumps'][0]
    assert j['kind'] == 'internal' and abs(j['z'] - zj) < 2 * (c['z_star'] - 1) / 2000 and j['z'] < c['z_sw']
    j4 = by[4.0]['jumps'][0]
    assert j4['kind'] == 'endpoint' and j4['z'] > c['z_sw'] and j4['x_right'] == 1.0
    assert f"{100 * (1 - by[2.0]['min_c_over_c0']):.1f}" == '28.2'          # 与第 7.2 节第 3 段一致
    m = macros()
    assert m['\\nrXianWtFourSwitch']['display'] == f"{j4['z']:.2f}" == '2.99'
    assert m['\\nrXianWtFourCutPct']['display'] == f"{100 * (1 - j4['x_left']):.0f}" == '56'
    assert m['\\nrXianWtTenCutPct']['display'] == f"{100 * (1 - by[10.0]['start_c_over_c0']):.0f}" == '75'
    assert m['\\nrXianWtTenStartQ']['display'] == f"{by[10.0]['start_q']:.2f}" == '0.39'
    q1 = 1 - (1 - X.q0) / c['z_star']                                        # 仅隔离控制的启动值 q_1
    assert abs(by[1.0]['start_q'] - q1) < 1e-12 and by[10.0]['start_q'] < q1
    xt = text('paper/sections/07_xian.tex')
    for name in ('nrXianWtFourSwitch', 'nrXianWtFourCutPct', 'nrXianWtTenCutPct', 'nrXianWtTenStartQ'):
        assert xt.count('\\' + name) == 1, name


def test_convergence_macros_exclude_capacity_points(scope):
    cv = json.loads((RES / 'new4w/convergence.json').read_text(encoding='utf-8'))
    tiers = [r for r in cv['tolerance_tiers'] if not r['capacity'] and r['law'] not in ('tdinn', 'routine')]
    pl = max(t['plateau_abs_dev'] for r in tiers for t in r['residuals'].values())
    ex = max(abs(t['exit_S_error']) for r in tiers for t in r['residuals'].values())
    m = macros()
    assert m['\\nrConvPlateauMax']['value'] == pl and m['\\nrConvExitMax']['value'] == ex
    for name, (old, new) in scope['changed_macros'].items():
        assert m[name]['display'] == new != old
    assert len([r for r in cv['state_grid'] if r['kind'] != 'cap']) == 10
    s8 = text('paper/supplement_sections/S8_numerics.tex')
    assert '共 $10$ 组' in s8 and '同样 $10$ 组' in s8 and '能力' not in s8


def test_tdinn_intensity_moved_to_section_73():
    """TDINN 的强度与阈值策略所需强度的比较由第 7.2 节移到第 7.3 节第 2 段。"""
    xt = text('paper/sections/07_xian.tex')
    s72, s73 = xt.split('\\subsection{控制组合}')[1].split('\\subsection{与实际干预的对照}')
    assert '0.98' not in s72 and '隔离比例趋向约 $0.98$、接触率降低约 $73\\%$' in s73
    assert '两类策略的差别不在强度，而在要维持多久' in s73
