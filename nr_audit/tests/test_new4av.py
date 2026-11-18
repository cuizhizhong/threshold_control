"""NEW-4av（N50）：第 8、9 章合并为“结论与讨论”一章；删去的内容在第 3、7 章与引言中仍有，标签保留。"""
import re

from conftest import SRC

ROOT = SRC.ROOT


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def paragraphs(block):
    out = []
    for p in re.split(r'\n\s*\n', block.strip()):
        p = re.sub(r'^(\s*\\label\{[^}]*\}\s*\n)+', '', p)
        if p.strip() and not p.lstrip().startswith('\\') and not p.lstrip().startswith('%'):
            out.append(p.strip())
    return out


def test_merged_chapter_structure():
    main = text('paper/flatten_curve_analysis_cn.tex')
    assert '\\input{sections/08_discussion}' in main and '09_conclusion' not in main
    assert not (ROOT / 'paper/sections/09_conclusion.tex').exists()
    d = text('paper/sections/08_discussion.tex')
    assert re.findall(r'\\section\{([^}]*)\}', d) == ['结论与讨论'] and '\\subsection' not in d
    for lab in ('sec:discussion', 'sec:conclusion', 'sec:discussion:return', 'sec:dom:limits'):
        assert d.count(f'\\label{{{lab}}}') == 1, lab
    ps = paragraphs(d.split('\\label{sec:conclusion}')[1].split('\\FloatBarrier')[0])
    assert len(ps) == 9
    assert ps[0].startswith('本文在含密切接触者追踪与隔离的 SIR 型模型中')
    # NEW-4bc（N57）：回流前提段改写，两个局限段删去段首提示句
    bc = (ROOT / 'paper/revision_notes/NEW_4bc_ch8.md').exists()
    assert ps[4].startswith('正文的解析结果以隔离易感者在清零前不返回社区为前提' if bc
                            else '正文的解析结果依赖隔离易感者在清零前不释放。')
    p6, p7 = ('$S_c$ 与退出时累计新增感染的下界', '控制若按模型预先计算') if bc else ('其他模型前提', '实施与成本')
    assert ps[6].startswith(p6) and ps[7].startswith(p7) and ps[8].startswith('提前干预与安全余量')
    # 第 5 章引用的局限一段：标签紧接在局限段之前
    assert '\\label{sec:dom:limits}\n' + p6 in d
    # NEW-4az（N54）：第 5.1 节删去与第 8 章展望段重复的半句，第 5 章不再引用该标签
    if not (ROOT / 'paper/revision_notes/NEW_4az_ch5.md').exists():
        assert '第~\\ref{sec:dom:limits}~节' in text('paper/sections/05_quadratic_cost.tex')


def test_removed_text_kept_elsewhere():
    d = text('paper/sections/08_discussion.tex')
    for gone in ('退出要求还限制了累计新增感染', '唯一确定', 'Pollinger', 'Zhou', '0.7565', '下面讨论', '仍有待研究'):
        assert gone not in d, gone
    x = text('paper/sections/07_xian.tex')
    assert '\\Itcum(t_2)\\ge\\beta(S_0-S_c)' in x and '多出的感染换来的是退出后的状态' in x and '下界不限于阈值策略' in x
    intro = text('paper/sections/01_introduction.tex')
    assert '这些研究多以单一传播率表示干预，沿容量运行时，它由维持感染水平的条件唯一确定' in intro
    assert 'Pollinger\\cite{Pollinger2023}' in intro
    assert '第~\\ref{sec:discussion}~节总结全文，并讨论结果的意义、隔离易感者回流的影响与局限。' in intro
    assert 'sec:conclusion' not in intro
    assert 'q_1\\approx0.7565' in text('paper/sections/03_single_control.tex')
