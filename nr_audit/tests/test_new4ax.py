"""NEW-4ax（N52）：外部审阅意见的局部修订与删去人口缩放命题；不新增计算，新读数可追溯到表中已有数值。"""
import json
import re
import subprocess

import pytest

from conftest import SRC
from text_identity import content_sha256

ROOT = SRC.ROOT
RES = SRC.HERE / 'results'


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


@pytest.fixture(scope='module')
def rec():
    return json.loads((RES / 'new4ax_scope.json').read_text(encoding='utf-8'))


def paper_text():
    main = text('paper/flatten_curve_analysis_cn.tex') + text('paper/flatten_curve_supplement_cn.tex')
    for d in ('paper/sections', 'paper/appendices', 'paper/supplement_sections'):
        for p in sorted((ROOT / d).glob('*.tex')):
            main += p.read_text(encoding='utf-8')
    return main


def test_removed_labels_absent_and_source_recorded(rec):
    s6 = text('paper/supplement_sections/S6_xian.tex')
    supp = text('paper/flatten_curve_supplement_cn.tex')
    for lab in rec['removed_labels']:
        assert '{' + lab + '}' not in s6, lab
    for f in ('paper/sections/08_discussion.tex',):
        assert 'prop:scaling' not in text(f)
    assert '人口缩放' not in s6 and '人口缩放' not in supp and 's=S/N' not in supp
    src = rec['removed_source']
    old = subprocess.run(['git', 'show', f"{src['commit']}:{src['path']}"], cwd=ROOT, capture_output=True).stdout
    assert content_sha256(old) == src['content_sha256'] and b'\\label{prop:scaling}' in old
    assert rec['scientific_activity'] == dict(ode_solves=0, optimization_solves=0, fits=0, redraws=0)


def test_new_readings_from_tables():
    xt = text('paper/sections/07_xian.tex')
    s6 = text('paper/supplement_sections/S6_xian.tex')
    summ = xt.split('\\label{tab:xian_summary}')[1].split('\\end{table}')[0]
    assert re.search(r'TDINN 控制 & 153 &', summ) and r'0.001N=\num{13163}' in xt
    # NEW-4ay（N53）：86 倍（感染者人数之比）改为每日追踪隔离人数的上下界
    if not (RES / 'new4ay_scope.json').exists():
        assert round(13163 / 153) == 86 and '约为 TDINN 峰值 $153$ 的 $86$ 倍' in xt
    assert '152.55' not in summ and '2105.63' not in summ
    rows = {r.split('&')[0].strip(): r.split('&')[2].strip() for r in s6.split('\\midrule')[1].split('\\bottomrule')[0].strip().split('\\\\') if r.strip()}
    assert rows['0.0010'] == '170.63' and rows['0.0005'] == '341.75'
    assert '约为 $171$ 至 $342$ d' in s6 and '量级相同' not in s6 and '这里采用全国的床位密度' in s6


def test_text_fixes():
    xt = text('paper/sections/07_xian.tex')
    d = text('paper/sections/08_discussion.tex')
    j = text('paper/sections/04_joint_control.tex')
    assert '两种措施的最大强度都出现在启动时' not in j and '两种措施的强度有共同的上界' in j
    assert '隔离的相对权重不超过 $r_{\\rm cont}$ 且启动时易感者多于 $S_{\\rm sw}$ 时' in d
    for m in ('nrRwBaseDiffPctNoret', 'nrRwBaseDiffPct', 'nrRwXianDiffPctNoret', 'nrRwXianDiffPct'):
        assert '\\' + m + '\\%' in d, m
    # NEW-4bb（N56）：“两种阈值控制”写明为仅隔离控制与成本最优控制
    bb = (ROOT / 'paper/revision_notes/NEW_4bb_ch7.md').exists()
    assert '对阈值策略，$I_0$ 的误差' in xt and ('仅隔离控制与成本最优控制的启动时刻' if bb else '两种阈值控制的启动时刻') in xt
    assert '不计感染到报告的延迟' in xt and '病例数据由 He、Tang 和 Xiao 提供' in xt
    assert '对仅隔离控制，把 $\\eta/N$' in xt and '两类策略的差别不在强度' not in xt
