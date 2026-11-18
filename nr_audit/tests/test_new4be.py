"""NEW-4be（N59）：第 7、8 章措辞一轮，11 处搭配与省略写准；不改陈述、宏与数字。"""
from conftest import SRC

ROOT = SRC.ROOT


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def test_ch7_ch8_terms():
    x = text('paper/sections/07_xian.tex')
    d = text('paper/sections/08_discussion.tex')
    for s in ('TDINN 控制取自他们的工作', '按 He 等的处理，两类病例分别对应', '仅隔离控制截至清零时的总累计新增感染',
              '在西安参数下，该权重约为 $\\nrWtXianBToCApx$',
              'TDINN 控制达到清零终点时，社区易感者人数仍接近全市人口',
              '计算这些长时结果时，将观测窗口内拟合的传播参数外推到整个过程'):
        assert s in x, s
    for s in ('成本最优控制的成本只比仅隔离控制低约', '若更看重缩短控制时长或减少累计新增感染，采用仅隔离控制所增加的成本不大',
              '以 $S$ 参数化控制', '仅隔离控制在减少累计新增感染方面的较大优势，主要依赖',
              '以 $I=1$ 作为清零标准。'):
        assert s in d, s
    for gone in ('外部参照', '病例对应方式', '到清零时间的总累计', '西安约为', '把感染者压到清零终点',
                 '这些长时结果把'):
        assert gone not in x, gone
    for gone in ('看重控制时长或感染时', '状态参数化', '在这两组比较中', '操作性终点'):
        assert gone not in d, gone
