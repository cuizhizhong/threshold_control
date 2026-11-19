"""NEW-4bh（N62）：补充材料与附录 A、B 的最后一轮措辞；只改叙述，跳变命题 (iii) 的 ζ_0 定义只改措辞。"""
from conftest import SRC

ROOT = SRC.ROOT


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def test_terms_round():
    s2 = text('paper/supplement_sections/S2_single_control.tex')
    s3 = text('paper/supplement_sections/S5_weight_structure.tex')
    s5 = text('paper/supplement_sections/S7_return.tex')
    s6 = text('paper/supplement_sections/S8_numerics.tex')
    a = text('paper/appendices/A_proofs_sensitivity.tex')
    b = text('paper/appendices/B_control_cost.tex')
    present = [
        (s2, '积分前的系数 $1/\\beta_1^0$'), (s2, '其中系数 $N/(c_0\\eta)$ 不含 $\\beta,q_0$'),
        (s3, '此时 $p=\\zeta_{\\rm sw}$ 与 $p=a$ 是两个全局最小点，分别对应 $c=c_0$ 与'),
        (s3, '记 $\\zeta_0$ 为使仅隔离控制成为全局最小点的最小 $\\zeta$，则'),
        (s3, '黑线表示由仅隔离控制连续转为两者并用的边界'), (s3, '紫线表示两者并用时两个取值之间的跳变'),
        (s3, '比较前两处结构变化的解析界限与数值区间。'),
        (s5, '在时间区间上采用 Radau 配点法'), (s5, '从十组初始猜测出发求解'),
        (s5, '退出后的积分网格上施加约束 $I\\le\\eta$'), (s5, '分段常值控制的打靶法'),
        (s5, '两组参数下，在所比较的控制中，仅隔离控制'), (s5, '恢复 $(c_0,q_0)$ 并一直保持'),
        (s6, '再与求根法得到的最小值比较'), (s6, '网格搜索所得最小值低于求根法结果的最大相对差约为 $\\nrConvNxMaxGap$'),
        (s6, '阈值策略各指标'), (s6, '新增隔离易感者人数、'), (s6, '$N_x$ 只核对求根法'),
        (s6, '的向上穿越事件确定。退出按'),
        (a, '先由归一化后的被积函数的一致收敛确定'), (a, '此时，在该区间上几乎处处有 $c(1-q)'),
        (b, '闭式表达式中有相近的量相减'),
    ]
    for src, s in present:
        assert s in src, s
    gone = [
        (s2, '前置系数'), (s2, '相应的隔离比例轨迹与二维扫描见'), (s3, '并列，$p=a$ 对应'),
        (s3, '取全局最小的最小状态'), (s3, '内部分支'), (s3, '都落在'),
        (s5, '时间域'), (s5, '十个起点'), (s5, '尾段'), (s5, '分段常控制'), (s5, '不重新启动'), (s5, '相似的结构'),
        (s6, '与根法'), (s6, '网格值低于'), (s6, '核心量'), (s6, '各仓室变量均由'),
        (a, '归一化成本'), (a, '故几乎处处有 $c>0$'), (b, '闭式中'),
    ]
    for src, s in gone:
        assert s not in src, s
    # 标签保留
    for lab in ('prop:sup:rhat', 'prop:sup:jump', 'fig:sup:phase-detail', 'tab:sup:convergence',
                'fig:baseline:q-joint', 'fig:scenario1_heatmaps_c0_eta'):
        assert any(('\\label{' + lab + '}') in t for t in (s2, s3, s6)), lab
