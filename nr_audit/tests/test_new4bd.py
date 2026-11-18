"""NEW-4bd（N58）：附录 A、B 按外部意见补证明步骤与改准措辞；A.9 采用两个更短的局部证明；陈述、标签与数字不变。"""
import sympy as sp

from conftest import SRC

ROOT = SRC.ROOT


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def test_appendix_wording():
    a = text('paper/appendices/A_proofs_sensitivity.tex')
    b = text('paper/appendices/B_control_cost.tex')
    for s in (
        '沿局部解分别积分 $S$ 与 $I$ 的线性方程',
        '$S(v)-S(u)=\\int_u^v\\dot S(t)\\,dt<0$',
        '又 $S(t_{\\rm end})<S_c$，故 $\\dot I(t_{\\rm end})<0$',
        '固定 $S$ 对各参数求偏导，再在 $S=S^*$ 处取值',
        '对式\\eqref{eq:cost:state}应用 Leibniz 公式',
        '方括号严格为负',
        '\\partial S_\\infty/\\partial\\eta=-[\\rho_1(1/S_\\infty-1/S_c)]^{-1}<0',
        '先由速度界建立时间与状态之间的可测对应',
        '因此在阈值控制期上几乎处处有 $q<1$',
        '再证 (i) 的反方向',
        '(iii) 取处处满足式\\eqref{eq:joint:contact-range}的代表',
        '每个状态上的最小点集均为非空紧集',
        '$f(S,c_c(S))-m(S)\\ge0$',
        '$g_S$ 的分母一致远离零',
        '由 $g_{S_n}(x_n)\\le g_{S_n}(x^*)$ 及一致收敛',
        '$(S_c,\\min\\{S_c+\\delta,S^*\\})$',
        '在 $\\zeta=\\zeta_{\\rm sw}$ 时为零',
        '$p^4-16(2p-3)=(p-2)^2(p^2+4p+12)\\ge0$',
        'E_\\zeta(1,1)=-2(1-b)<0',
        '$\\zeta_s(p_2)-\\zeta_s(p_1)=\\int_{p_1}^{p_2}\\zeta_s\'(p)\\,dp>0$',
        '\\emph{第三步：最小点及其连续性。}',
        '故在整个内部区间上 $G_p<0$',
        '任取 $\\zeta_i$ 下的最小点 $p_i$',
        '隔离项归一化强度平方的时间积分',
        '补充命题~\\ref{prop:contact-effects}(i)(ii)；命题~\\ref{prop:threshold-tradeoff}(i)',
        '内部拐点条件\\eqref{eq:s1:inflection-condition}成立',
    ):
        assert s in a, s
    for gone in ('本小节证明', '\\kappa=2(1-b)^2', '若 $F$ 无实根', '单峰性', '控制与逐状态最小值之差',
                 '以 $\\theta=\\eta/N$ 替换 $\\eta$ 不改变符号', '因此 (i) 成立，且 (ii) 对一切',
                 '$c_c$ 的可测性在 (ii) 之后证明'):
        assert gone not in a, gone
    for lab in ('tab:sensitivity', 'tab:s1:lambda-sensitivity', 'tab:s1:inflection-roles',
                'eq:s1:Sstar-eta-sign', 'eq:cost:state', 'eq:cumulative-eta', 'eq:joint:balance',
                'eq:proof:cost-E', 'lem:proof:fold-free', 'eq:s1:post-orbit'):
        assert a.count('\\label{' + lab + '}') == 1, lab
    assert '本附录取 $w_c=1$、$w_q=2$' in b and '$dt=-N\\,dS/[c_0\\eta(S_c-\\bar S)]$' in b
    assert '\\begin{proof}' not in b                     # 附录 B 是计算，不套证明环境


def test_shorter_proofs_algebra():
    """A.9 两个新证明用到的恒等式与端点导数。"""
    p, s, b, z = sp.symbols('p sigma b zeta', positive=True)
    assert sp.expand(p**4 - 16 * (2 * p - 3) - (p - 2)**2 * (p**2 + 4 * p + 12)) == 0
    w = sp.sqrt(2 * p - 3)
    X = p**3 - 6 * p**2 + 6 * p + 2 * b * (3 * p - 4)
    F = s**2 * X - 2 * s * b * p * w + p**3
    assert sp.simplify(sp.diff(F / s**2, s) - 2 * p * (b * w * s - p**2) / s**3) == 0
    Ez = -2 * ((p - b)**2 + b * (z - b)) / z**3
    assert sp.simplify(Ez.subs({p: 1, z: 1}) + 2 * (1 - b)) == 0
    assert sp.simplify(Ez.subs(p, z) + 2 * (z - b) / z**2) == 0
