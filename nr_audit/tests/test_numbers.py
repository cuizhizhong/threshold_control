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
    assert by['\\nrICtOneFit']['value'] == q1['state']['t1']
    assert by['\\nrFitObjective']['value'] == fit['at_fit_I0']['objective']
    for m in mapping['macros']:
        assert m['source'].startswith('nr_audit/results/') and (SRC.ROOT / m['source']).exists()


def test_registry_has_no_stop():
    reg = json.loads((RES / 'regression.json').read_text(encoding='utf-8'))
    assert all(r['status'] != 'stop' for r in reg['registry'])
    assert all(c['holds'] for c in reg['claims'])
