"""NEW-4at（N48）：删去显式控制族后，被删的陈述、标签与表行不再入稿，图 4 的新图与收据一致，收敛宏可追溯。"""
import hashlib
import json
import re

import pytest

from conftest import SRC
from text_identity import content_sha256

ROOT = SRC.ROOT
RES = SRC.HERE / 'results'


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


@pytest.fixture(scope='module')
def scope():
    return json.loads((RES / 'new4at_scope.json').read_text(encoding='utf-8'))


def test_removed_content_absent_and_archive_intact(scope):
    files = [f for fs in scope['current_inputs'].values() for f in fs]
    arch = scope['archived_source']
    assert arch['path'] not in files and 'S4_explicit_control' not in text('paper/flatten_curve_supplement_cn.tex')
    assert content_sha256((ROOT / arch['path']).read_bytes()) == arch['content_sha256']
    current = ''.join(text(f) for f in files)
    for lab in scope['removed_labels']:
        assert lab not in current, lab
    for gone in ('显式族', '显式控制族', r'\alpha=0.5', '四种控制的比较', '四种控制采用'):
        assert gone not in current, gone
    assert scope['scientific_activity'] == dict(ode_solves=0, optimization_solves=0, fits=0, redraws=1)


def test_comparison_theorem_items():
    ch4 = text('paper/sections/04_joint_control.tex')
    thm = ch4[ch4.index(r'\label{thm:joint:comparison}'):ch4.index(r'\end{theorem}', ch4.index(r'\label{thm:joint:comparison}'))]
    assert thm.count(r'\item') == 3                       # 原 (ii) 删去，(iii)(iv) 顺延为 (ii)(iii)
    # NEW-4au（N49）把 4.2 节标题改为“时长与感染目标”
    second = '时长与感染目标' if (ROOT / 'paper/revision_notes/NEW_4au_ch4.md').exists() else '不同目标的最优控制'
    assert re.findall(r'\\subsection\{([^}]*)\}', ch4) == ['状态参数化', second]
    num = text('paper/sections/06_numerics.tex')
    assert r'\ref{thm:joint:comparison}(iii)与推论' in num and r'\ref{thm:joint:comparison}(iv)' not in num


def test_removed_rows_trace_to_results(scope):
    w3 = json.loads((RES / 'new4w/xian_theta001.json').read_text(encoding='utf-8'))
    a = w3['laws']['alpha']
    row = scope['removed_table_rows']['tab:xian:joint-compare']['row']
    assert row == (f"显式族 $\\alpha=0.5$ & {a['dt']:.2f} & {a['t_end']:.2f} & {a['total_to_clearance'] / 1e6:.3f} & "
                   f"{a['dSq'] / 1e6:.3f} & {a['J']:.2f} & {a['peak_ratio']:.2f}")
    s = json.loads((RES / 'new4s_figures.json').read_text(encoding='utf-8'))['checks']['laws']['alpha_0.5']
    assert scope['removed_table_rows']['tab:joint:compare']['row'].endswith(f"{s['peak_ratio_table']:.2f}")


def test_figure4_receipt(scope):
    rec = json.loads((RES / 'new4at_fig4.json').read_text(encoding='utf-8'))
    old = json.loads((RES / 'new4s_figures.json').read_text(encoding='utf-8'))
    assert rec['inputs_sha256'] == old['inputs_sha256']
    assert set(rec['checks']['laws']) == {'contact_only', 'quarantine_only', 'minimum_cost'}
    for key, v in rec['checks']['laws'].items():
        assert v == old['checks']['laws'][key]
    for rel, out in rec['outputs'].items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == out['sha256']
        assert rel.removeprefix('paper/') in text('paper/sections/06_numerics.tex')
    sup = rec['superseded']
    assert hashlib.sha256((ROOT / sup['path']).read_bytes()).hexdigest() == sup['sha256']
    assert rec['scientific_activity']['ode_solves'] == 0


def test_convergence_macro(scope):
    by = {m['macro']: m for m in json.loads((RES / 'nr_numbers_map.json').read_text(encoding='utf-8'))['macros']}
    m = by['\\nrConvTolMaxRel']
    assert m['display'] == scope['macro_changes']['\\nrConvTolMaxRel']['new'] == '2\\times10^{-12}'
    cv = json.loads((RES / 'new4w/convergence.json').read_text(encoding='utf-8'))
    rows = [r for r in cv['tolerance_tiers'] if not r['capacity'] and r['law'] not in ('tdinn', 'routine', 'alpha')]
    assert m['value'] == max(max(r['max_rel_change_vs_base'].values()) for r in rows)
    assert '两组参数的三种控制、TDINN 与常规控制' in text('paper/supplement_sections/S8_numerics.tex')
