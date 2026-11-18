"""NEW-4bf（N60）：附录 A、B 措辞一轮，11 处写准与 6 处合并重复；陈述、证明逻辑、标签与数字不变。"""
from conftest import SRC

ROOT = SRC.ROOT


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def test_appendix_terms():
    a = text('paper/appendices/A_proofs_sensitivity.tex')
    b = text('paper/appendices/B_control_cost.tex')
    for s in ('$S_q$ 的流入项 $(1-\\beta)cqSI/N$ 与初值均非负', '另外两个偏导数为',
              '上述积分的闭式表达式见附录', '先由速度界建立时间控制与状态反馈函数的对应，再求时间积分公式和退出时的控制极限',
              '阈值控制期内几乎处处有 $q<1$ 和', '与 $S(t)$ 或 $t(S)$ 复合均保持可测性',
              '式\\eqref{eq:joint:Sdot}满足 (i) 中的速度界', '反过来，给定满足式\\eqref{eq:joint:contact-range}的可测函数 $c_c$',
              '$f$ 在允许区域上连续。', '得到相应的允许控制，其成本达到上述下界', '长度为正的区间',
              '两种单控制对应的 $f(S,c)$ 均严格大于该状态上的最小值',
              '$\\zeta_s$ 在两种情形下都是 $(1,\\zeta_{\\rm sw})$ 到自身的严格递增连续双射',
              '因此两者的最优取值均随 $r$ 不增', '$p_1$、$p_2$ 均属于两个状态的允许区间'):
        assert s in a, s
    for gone in ('只有流入，流入', '完整表达', '初等表达', '可测对应', '两个方向的复合', '再证 (i) 的反方向',
                 '连续有限', '产生可行时间控制', '正长度区间', '成本密度', '即得逐状态结论', '在两个状态上都允许'):
        assert gone not in a, gone
    # (ii) 不再第二次列出速度界
    assert a.count('c_0(S^*-\\bar S)') == 0 and a.count('\\frac{\\eta c_0}{N}(S^*-\\bar S)') == 1
    assert '仅隔离控制下 $J_q$ 与 $J$ 的积分表达式见式\\eqref{eq:cost:state}。' in b
    assert '下降速度恒为' not in b and '故 $dt=-N\\,dS/[c_0\\eta(S_c-\\bar S)]$' in b
