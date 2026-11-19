"""NEW-4ba（N55）：第 6 章按外部意见的核对结论逐句改准；不改定理类陈述、表值与图件。"""
from conftest import SRC

ROOT = SRC.ROOT


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def test_ch6_wording():
    ch6 = text('paper/sections/06_numerics.tex')
    for s in (
        '计算采用无回流模型',
        '比较三种控制时，成本权重取默认值',
        '积分时控制作为预先算出的时间函数输入',
        '的相图在 $(r,S)$ 网格上计算',
        '与 $\\Delta S_q$ 的排序与定理~\\ref{thm:joint:comparison}(iii)及推论~\\ref{cor:joint:whole-epidemic}一致',
        '启动时的易感者人数 $S^*$ 大于 $S_{\\rm sw}$',
        '该段 $c=c_0$，$S$ 越大，下降越快',
        '接触率相对 $c_0$ 的最大降幅约为 $19.8\\%$',
        '被追踪的新感染者直接进入 $I_q$',
        '成本最优控制的峰值出现在转入两者并用后不久',
        '各控制共用的 $I+I_q$ 上界',
        '(b)、(c)、(d) 中的红色虚线分别为',
        '成本也接近最小成本',
        '$r_*<r<\\hat r$' if (ROOT / 'paper/revision_notes/NEW_4bi_notation.md').exists() else '$r_{\\rm cont}<r<\\hat r$',   # NEW-4bi（N63）
        '$r>\\hat r$ 且仍有仅隔离段时，切换提前：在切换状态与 $S_{\\rm sw}$ 之间',
        '跳变位置的闭式表达式、各转折权重的数值范围',
        '在 $S_c$ 一端的 $r$ 值因而趋于 $y/(1-y)$',
        # 保留的说明
        '$\\delta_q$ 只出现在 $I_q$ 与 $R$ 的方程中',
        '$\\nrCostRcontBase$', '$\\nrCostRhatBase$', '$\\nrCostGapOneBase\\%$',
    ):
        assert s in ch6, s
    for gone in ('用来演示解析结果', '名义模型', '有限个网格点', '这一排序同时决定', '启动状态 $S^*$ 高于',
                 '接触减少的幅度不大', '分别约为 $1.92$', '对所有控制都成立的上界', '红色虚线依次为',
                 '可以直接判断', '几乎不损失成本', 'r\\le\\hat r$（', '闭式、各转折的括区', '趋于水平线'):
        assert gone not in ch6, gone
    # 表值不变
    for v in ('1.92\\\\', '1.89\\\\', '1.02\\\\', '& 2.12 &', '& 7.75 &'):
        assert v in ch6, v
    # 术语一轮
    for s in ('表~\\ref{tab:joint:compare}中 $\\Delta t$', '维持阈值所需的隔离比例降低',
              '这些感染者不参与社区传播', '两种权重只通过其比值 $r=w_q/w_c$ 影响最优控制',
              '允许区间内部另一个局部最小点上的 $f(S,c)$ 更低', '跳到该点',
              '接触率随时间的变化则依赖权重', '黑色数字标注等高线的 $y$ 值'):
        assert s in ch6, s
    for gone in ('比较三种控制。表中', '隔离强度降低', '不进入社区', '属于这一档', '内部局部最优的成本',
                 '时间形态', '黑色数字为等值'):
        assert gone not in ch6, gone
    # 第 7.2 节同步
    ch7 = text('paper/sections/07_xian.tex')
    assert '仅隔离控制在这组参数下的成本也接近最小成本' in ch7
    assert '几乎不损失成本' not in ch7
