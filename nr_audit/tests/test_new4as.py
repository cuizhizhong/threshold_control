"""NEW-4as（N47）：第 8–9 章逐句修订后，第 8.1 节新写出的成本倍数与结果文件一致，讨论与结论的段落结构按作者决定。"""
import json
import re

from conftest import SRC

ROOT = SRC.ROOT
RES = SRC.HERE / 'results'


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def test_cost_ratios_in_section81():
    """成本最优控制比仅隔离控制低的百分比，与仅减少接触相对最小成本的倍数（两组参数）。"""
    base = {r['law']: r['values']['base']['J'] for r in json.loads((RES / 'convergence.json').read_text(encoding='utf-8'))['tolerance_tiers']
            if r['case'] == 'base' and not r['capacity'] and r['law'] in ('q_only', 'c_only', 'opt')}
    xian = {k: v['J'] for k, v in json.loads((RES / 'new4w/xian_theta001.json').read_text(encoding='utf-8'))['laws'].items()}
    gap = [100 * (1 - d['opt'] / d['q_only']) for d in (base, xian)]
    ratio = [d['c_only'] / d['opt'] for d in (base, xian)]
    assert [f'{g:.1f}' for g in gap] == ['4.7', '6.7'] and [f'{x:.1f}' for x in ratio] == ['5.6', '2.9']
    d = text('paper/sections/08_discussion.tex')
    assert r'成本最优控制只比仅隔离控制低约 $4.7\%$ 与 $6.7\%$，仅减少接触的成本则约为最小成本的 $5.6$ 倍与 $2.9$ 倍' in d
    # 两个百分比与第 6.2、7.2 节的写法一致
    assert r'$J$ 降低约 $4.7\%$' in text('paper/sections/06_numerics.tex')
    assert r'$J$ 降低约 $6.7\%$' in text('paper/sections/07_xian.tex')


def paragraphs(block):
    return [p for p in re.split(r'\n\s*\n', block.strip()) if p.strip() and not p.lstrip().startswith('\\')]


def test_discussion_and_conclusion_structure():
    if not (ROOT / 'paper/sections/09_conclusion.tex').exists():
        # NEW-4av（N50）：第 8、9 章合并为“结论与讨论”一章、不分小节，结构由 test_new4av.py 检查
        s7 = text('paper/supplement_sections/S7_return.tex')
        assert '\\begin{itemize}' not in s7 and '（见上）' not in s7
        return
    d = text('paper/sections/08_discussion.tex')
    s83 = d.split('\\label{sec:discussion:return}')[1].split('\\subsection{')[0]
    s84 = d.split('\\label{sec:dom:limits}')[1].split('\\FloatBarrier')[0]
    assert len(paragraphs(s83)) == 2 and len(paragraphs(s84)) == 2
    assert paragraphs(s83)[0].startswith('正文的解析结果依赖隔离易感者在清零前不释放。')
    assert '几个问题尚未解决' not in d and 'Pollinger\\cite{Pollinger2023}已研究' not in d
    assert '与 Zhou 等\\cite{Zhou2024SPCI}和 Pollinger\\cite{Pollinger2023}的联合优化的区别见引言。' in d
    c = text('paper/sections/09_conclusion.tex')
    assert len(paragraphs(c.split('\\label{sec:conclusion}')[1])) == 1
    assert '仅隔离控制最快、感染最少' in c and '含回流时最优组合的解析刻画仍有待研究' in c
    s7 = text('paper/supplement_sections/S7_return.tex')
    assert '\\begin{itemize}' not in s7 and '（见上）' not in s7
