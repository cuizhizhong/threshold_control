"""NR-3 的数字宏与结果文件：宏名只用字母且前缀 \\nr；nr_numbers.tex 中每个宏都在映射文件中，显示值与映射一致；
映射记录的全精度值与来源 JSON 一致（抽查可直接读取的字段）；N1 登记中没有“停止”项。"""
import json
import re

import pytest

from conftest import SRC

RES = SRC.HERE / 'results'
TEX = SRC.ROOT / 'paper' / 'generated' / 'nr_numbers.tex'


@pytest.fixture(scope='module')
def mapping():
    if not (RES / 'nr_numbers_map.json').exists():
        pytest.skip('尚未运行 make_numbers.py')
    return json.loads((RES / 'nr_numbers_map.json').read_text(encoding='utf-8'))


def test_tex_matches_map(mapping):
    defs = dict(re.findall(r'\\newcommand\{\\(nr[A-Za-z]+)\}\{([^%\n]*)\}\s*%', TEX.read_text(encoding='utf-8')))
    assert len(defs) == mapping['n_macros'] == len(mapping['macros'])
    for m in mapping['macros']:
        name = m['macro'][1:]
        assert re.fullmatch(r'nr[A-Za-z]+', name)
        assert defs[name] == m['display']


def test_map_values_trace_to_results(mapping):
    ic = json.loads((RES / 'initial_condition.json').read_text(encoding='utf-8'))
    fit = json.loads((RES / 'fit_reconstruction.json').read_text(encoding='utf-8'))
    by = {m['macro']: m for m in mapping['macros']}
    q1 = next(r for r in ic['rows'] if r['law'] == 'q_only' and r['factor'] == 1.0)
    if 'new4w/' in by['\\nrICtOneFit']['source']:          # NEW-4w（N33）：西安 η = 0.001N 的初值诊断
        w = json.loads((RES / 'new4w/xian_theta001.json').read_text(encoding='utf-8'))
        fit1 = next(r for r in w['initial_condition']['rows'] if r['law'] == 'q_only' and r['factor'] == 1.0)
        assert by['\\nrICtOneFit']['value'] == fit1['t1']
    else:
        assert by['\\nrICtOneFit']['value'] == q1['state']['t1']
    assert by['\\nrFitObjective']['value'] == fit['at_fit_I0']['objective']
    for m in mapping['macros']:
        assert m['source'].startswith('nr_audit/results/') and (SRC.ROOT / m['source']).exists()


def test_registry_has_no_stop():
    reg = json.loads((RES / 'regression.json').read_text(encoding='utf-8'))
    assert all(r['status'] != 'stop' for r in reg['registry'])
    assert all(c['holds'] for c in reg['claims'])


def test_population_scale_matches_old_csv():
    """NR-6：人口缩放情景的复核值与原 CSV 一致，正文所写的极差与启动时刻成立。"""
    f = RES / 'population_scale.json'
    if not f.exists():
        pytest.skip('尚未运行 audit_population_scale.py')
    d = json.loads(f.read_text(encoding='utf-8'))
    assert d['old_compare_max'] < 1e-10
    assert abs(d['spread_dt'] - 4.71e-8) < 0.01e-8 and abs(d['spread_J'] - 1.17e-7) < 0.01e-7
    assert round(d['t1_min'], 2) == 11.39 and round(d['t1_max'], 2) == 16.90
    assert all(abs(r['dt'] - 85.07) < 0.005 for r in d['a_fixed_theta'])
    lf = [r['log_factor'] for r in d['c_log_factor']]
    assert round(lf[0], 2) == 2.20 and round(lf[1], 2) == 2.15


def test_noreturn_inf_crosscheck():
    """NR-7：无回流 t→∞ 累计感染与回流分支记录一致，推论前提的判定与记录相同。"""
    f = RES / 'noreturn_inf_crosscheck.json'
    if not f.exists():
        pytest.skip('尚未运行 audit_noreturn_inf.py')
    d = json.loads(f.read_text(encoding='utf-8'))
    assert d['max_rel_vs_return_branch'] < 1e-8
    prem = {(r['case'], r['law']): r['premise_C_lt_L'] for r in d['rows']}
    assert prem[('base', 'c_only')] is False
    assert all(v for k, v in prem.items() if k != ('base', 'c_only'))
