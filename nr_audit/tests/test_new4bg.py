"""NEW-4bg（N61）：补充材料按外部意见改准；上集性引理补 S>S_c，r̂ 命题在 S_sw 处换为直接恒等式；数值与标签不变。"""
import sympy as sp

from conftest import SRC

ROOT = SRC.ROOT
SUP = ROOT / 'paper/supplement_sections'


def text(name):
    return (SUP / name).read_text(encoding='utf-8')


def test_rhat_identity():
    p, z, r = sp.symbols('p zeta r', positive=True)
    b = z * (3 - z) / 2                      # zeta_sw^2 - 3 zeta_sw + 2b = 0
    G = lambda pp, zz: ((1 - pp / zz)**2 + r * (1 - 1 / pp)**2) / (pp - b)
    a = z / (z - 1)
    rhs = (z - p)**2 / (z**2 * p**2 * (p - b)) * ((p - a)**2 + (a**2 - r) * (2 * (z - 1) * p / z - 1))
    assert sp.simplify(G(p, z) - G(z, z) - rhs) == 0


def test_supplement_wording():
    s1, s2, s3 = text('S1_medical.tex'), text('S2_single_control.tex'), text('S5_weight_structure.tex')
    s4, s5, s6 = text('S6_xian.tex'), text('S7_return.tex'), text('S8_numerics.tex')
    main3 = (ROOT / 'paper/sections/03_single_control.tex').read_text(encoding='utf-8')
    checks = [
        (s1, '乘以感染者在该仓室中的平均停留时间 $1/\\delta_q$'), (s1, '所得峰值与上界 $\\kappa_I\\approx4.42$ 相距较大'),
        (s2, '常规峰值趋于 $\\eta$'), (s2, '左侧至少一处为正、右侧至少一处为负'), (s2, '黑色数字标注相应的指标值'),
        (s3, '设 $w_c,w_q>0$ 且 $S>S_c$。'), (s3, '证明中的右端点导数公式'), (s3, 'a=\\zeta/(\\zeta-1)=\\sqrt{\\hat r}'),
        (s3, '临界情形 $r=\\hat r$ 时'), (s3, '未取整的区间宽度均小于 $10^{-3}$'), (s3, '解析值 & 数值区间'),
        (s3, '允许区间内部的最优选择是五次驻点方程的根'), (s3, '直至所得 $r$ 区间的宽度小于 $10^{-3}$'),
        (s4, '分别纳入 $580$ 例和 $651$ 例成人确诊者'), (s4, '按全国的床位密度换算'),
        (s5, '$\\omega>0$ 时，隔离易感者的停留时间'), (s5, '未感染接触者的隔离与回流只在'),
        (s5, '按接触率降幅首次超过仅减少接触时降幅的 $1\\%$ 定位'), (s5, '三种未重新优化的控制'),
        (s6, '无回流模型下的求解器设置'), (s6, '以 $\\ln(I/N)$ 为变量积分'), (s6, '退出按预先计算的控制时长执行'),
        (s6, '在每个网格局部极小点相邻的区间内作有界一维最小化'), (s6, '包括 TDINN 与常规控制在内'),
    ]
    for src, s in checks:
        assert s in src, s
    gone = [
        (s1, '与 Angulo 等的处理相同'), (s1, '末列为 $5.06$'), (s2, '$\\eta$ 趋于常规峰值'), (s2, '黑色数字为等值'),
        (s2, '是正文图~\\ref{fig:scenario1_summary_eta}的完整扫描'), (s3, '括区'), (s3, '上集性'), (s3, 'K(p)='),
        (s3, '最优选择本身是五次方程的根'), (s4, '0.001$ 即 $0.1\\%$'), (s4, '下界一致'),
        (s5, '回放核验'), (s5, '固定控制律'), (s5, '改变的是量级'), (s5, '\\nrRwBaseDiffPct'),
        (s6, '感染分量按其自然对数积分'), (s6, '网格值低于根法值即视为漏根'), (s6, '各片'),
        (main3, '低阈值下的渐近行为'),
    ]
    for src, s in gone:
        assert s not in src, s
    for lab in ('lem:sup:upper-set', 'prop:sup:rhat', 'prop:sup:jump', 'tab:joint:weight-transitions',
                'sec:sup:threshold-scale', 'tab:sup:eta', 'rem:release-at-exit', 'eq:return:U', 'tab:sup:convergence'):
        assert any(('\\label{' + lab + '}') in t for t in (s3, s4, s5, s6)), lab
