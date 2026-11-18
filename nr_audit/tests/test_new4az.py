"""NEW-4az（N54）：第 5 章按外部意见的核对结论逐句改准；陈述只改措辞，标签与数字不变。"""
import re

from conftest import SRC

ROOT = SRC.ROOT


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def test_ch5_wording():
    ch5 = text('paper/sections/05_quadratic_cost.tex')
    for s in (
        '单位时间的成本除以 $S$ 的下降速率',
        '$(q-q_0)/(1-q_0)=1-c_0S_c/(cS)$',
        '允许控制 $c_c$ 使 $J$ 达到最小值',
        '启动时的易感者人数 $S^*$ 是否大于 $S_{\\rm sw}$',
        '由式\\eqref{eq:model:Sc}与\\eqref{eq:joint:ssw}',
        '在 $(S_c,\\infty)$ 上恰有一次跳变',
        '两种归一化强度的渐近比例由权重决定',
        '下降速度趋于同一个正值',
        '分别趋于 $2/3$ 与 $1/3$',
        '可以在共同经过的状态上取相同的',
    ):
        assert s in ch5, s
    for gone in ('累计预算', 'sec:dom:limits', '高阶小量', '兼容', '阈值只通过系数', '启动状态是否高于',
                 '退出附近的组合则由权重直接决定'):
        assert gone not in ch5, gone
    # 第 8 章仍完整说明逐状态分离的限制
    assert '逐状态分离' in text('paper/sections/08_discussion.tex')
    # 命题 5.5 的证明仍给出阈值经 N/eta 与 S^* 进入成本
    assert re.search(r'有 \$N/\\eta_1>N/\\eta_2\$ 与 \$S\^\*\(\\eta_1\)>S\^\*\(\\eta_2\)\$', ch5)
    # 定理类陈述的列表项不再以分号收尾
    for env in re.findall(r'\\begin\{(?:theorem|proposition)\}(.*?)\\end\{(?:theorem|proposition)\}', ch5, re.S):
        items = [i.strip() for i in env.split('\\item')[1:]]
        if not items:
            continue
        last = items[-1].split('\\end{enumerate}')[0].strip()
        assert not last.endswith('；'), last[-30:]
