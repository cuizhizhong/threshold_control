"""NEW-4ao（N43）：第 6 章逐句修订后，移入正文的数字与新写出的论断都能追溯到已登记的结果。"""
import json
import math
import re

import params as PR
from conftest import SRC

ROOT = SRC.ROOT
RES = SRC.HERE / 'results'


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def load(rel):
    return json.loads((RES / rel).read_text(encoding='utf-8'))


def new4ap():
    """NEW-4ap（N44）删去能力约束后的收据；存在时，能力约束的段落已不在稿中。"""
    path = RES / 'new4ap_scope.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None


def test_capacity_front_segment_moved_to_main_text():
    """基准代表点上能力约束起作用的前一段：约 1.94 d，接触率降幅从约 39.1% 开始减小；补充 S8 不再列出。"""
    seg = load('regression.json')['capacity']['base']['front_segment']
    fig = load('new4p_figures.json')['checks']['joint_capacity_baseline']
    assert abs(seg['contact_reduction_at_start'] - fig['u_max_on_path']) < 1e-12
    num, s8 = text('paper/sections/06_numerics.tex'), text('paper/supplement_sections/S8_numerics.tex')
    d, u = f"{seg['duration']:.2f}", f"{100 * seg['contact_reduction_at_start']:.1f}"
    assert (d, u) == ('1.94', '39.1')
    assert d not in s8 and u not in s8 and 'sec:joint:capacity-numerics' not in s8
    if new4ap():
        # NEW-4ap（N44）：6.3 节整节删去，这两个数值只留在结果文件中
        assert 'sec:joint:capacity-numerics' not in num and f"启动后约 ${d}$ d" not in num
        return
    assert f"启动后约 ${d}$ d 内，隔离比例停在上限" in num and f"降幅从启动时的约 ${u}\\%$" in num


def test_chapter6_structure_and_pointers():
    num = text('paper/sections/06_numerics.tex')
    expected = ['参数与方法', '四种控制的比较', '能力约束', '成本权重']
    if new4ap():
        expected.remove('能力约束')                    # NEW-4ap（N44）：6.3 节删去
    if (RES / 'new4at_scope.json').exists():
        expected[1] = '三种控制的比较'                  # NEW-4at（N48）：删去显式族
    assert re.findall(r'\\subsection\{([^}]*)\}', num) == expected
    # 6.4 节第 2 段的补充引用合为段末一句；单控制的可行条件改引第 4 章
    assert num.count(r'\ref{sec:sup:weight-structure}') == 1
    assert r'\ref*{prop:sup:rhat}' not in num and r'\ref*{tab:joint:weight-transitions}' not in num
    assert (r'\ref{cor:joint:single-endpoints}' in num) != bool(new4ap()) and '逐点的数值核对' not in num
    assert r'\ref*{lem:sup:infected-bound}' in num


def test_r317_profile_has_jump_just_below_switch():
    """6.4 节第 3 段：r=3.17 落在 r_cont 与 r̂ 之间，跳变位置 ζ_j 紧挨 ζ_sw（补充命题的闭式）。"""
    B = PR.BASE
    b = (1 - B.beta) * (1 - B.q0)
    r_cont = 16 / (b + math.sqrt(b * b - 8 * b + 8)) ** 2
    z_sw = (3 + math.sqrt(9 - 8 * b)) / 2
    r_hat = (z_sw / (z_sw - 1)) ** 2
    r = 3.17
    z_j = 2 * (b + (1 - b) * math.sqrt(r))
    assert r_cont < r < r_hat and 0 < z_sw - z_j < 0.01
    assert 'r=3.17$ 时也先降后回升，但在 $S_{\\rm sw}$ 稍下方先向下跳变一次' in text('paper/sections/06_numerics.tex')


def test_tdinn_values_kept_elsewhere():
    """补充 S8 删去的 TDINN 一句：清零时的累计与清零时间仍在表 4，结果文件不变。"""
    st = load('new4w/xian_theta001.json')['strategies']['TDINN']
    assert round(st['total']) == 2106 and round(st['t_end'], 2) == 45.29
    xt = text('paper/sections/07_xian.tex')
    assert 'TDINN 控制 & 153 & 2106 & 45.29' in xt
    assert '2105.6330' not in text('paper/supplement_sections/S8_numerics.tex')
