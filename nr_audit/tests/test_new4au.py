"""NEW-4au（N49）：第 4 章再审后，术语统一为“状态反馈函数”，允许区间在第 4.1 节定义，推论 cor:joint:whole-epidemic 前有引导句。"""
import json
import re

from conftest import SRC

ROOT = SRC.ROOT
RES = SRC.HERE / 'results'


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def current_text():
    scope = json.loads((RES / 'new4at_scope.json').read_text(encoding='utf-8'))
    return ''.join(text(f) for fs in scope['current_inputs'].values() for f in fs)


def test_state_feedback_term_unified():
    cur = current_text()
    assert '状态函数' not in cur
    assert re.findall(r'状态反馈(?!函数)', cur) == []
    ch4 = text('paper/sections/04_joint_control.tex')
    assert '称 $c_c$、$q_c$ 为接触率与隔离比例的状态反馈函数' in ch4


def test_admissible_interval_defined_once_in_ch4():
    ch4 = text('paper/sections/04_joint_control.tex')
    ch5 = text('paper/sections/05_quadratic_cost.tex')
    defn = '称 $[c_0S_c/S,c_0]$ 为状态 $S$ 上的允许区间'
    assert defn in ch4 and defn not in ch5
    # 定义出现在定理 thm:joint:representation 之后、第一次使用之前
    assert ch4.index(r'\end{theorem}') < ch4.index(defn)
    assert '允许区间（第~\\ref{sec:joint:state}~节）' in ch5


def test_ch4_statements_and_corollary_lead():
    ch4 = text('paper/sections/04_joint_control.tex')
    thm = ch4[ch4.index(r'\label{thm:joint:comparison}'):]
    assert thm.startswith(r'\label{thm:joint:comparison}' + '\n设条件\\eqref{eq:model:trigger}成立')
    cor = ch4[ch4.index(r'\label{cor:joint:whole-epidemic}'):]
    assert '$\\mathcal A(\\eta)$ 中两个控制的各量分别记上标 (1)、(2)' in cor
    assert '两个允许控制' not in ch4
    lead = '下面的推论说明这两段对各控制相同，整个疫情的差别就是阈值控制期的差别。'
    assert ch4.index(lead) < ch4.index(r'\label{cor:joint:whole-epidemic}')
    # 章末凸组合一句写出表达式与依据
    assert '$c_c=\\alpha c_0+(1-\\alpha)c_0S_c/S$' in ch4 and '凸组合' not in ch4
