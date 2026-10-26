"""NEW-4o：图 8 与图 S11 按图 2 风格重绘后的收据（results/new4o_xian_figures.json）。
核对输入数据的原字节身份未变、入库图件即收据登记的输出、图内字体为 Computer Modern、印刷尺寸与稿件中的宽度一致。"""
import hashlib
import json

import pytest

from conftest import SRC

RES = SRC.HERE / 'results' / 'new4o_xian_figures.json'
ROOT = SRC.HERE.parent


@pytest.fixture(scope='module')
def receipt():
    if not RES.exists():
        pytest.skip('尚未运行 plot_xian_fig2_style.py')
    return json.loads(RES.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_inputs_unchanged(receipt):
    for rel, digest in receipt['inputs_sha256'].items():
        assert sha(ROOT / rel) == digest, rel


@pytest.mark.parametrize('name, width_mm', [('xian_strategy_process', 135.0), ('xian_eta_sensitivity', 111.86)])
def test_outputs_registered(receipt, name, width_mm):
    rel = f'paper/figures/new4o/{name}.pdf'
    out = receipt['outputs'][rel]
    assert sha(ROOT / rel) == out['sha256']
    assert abs(out['size_mm'][0] - width_mm) < 0.05
    assert out['fonts'] and all(('Cmr10' in f) or ('Cmmi10' in f) or ('Cmsy10' in f) for f in out['fonts'])


def test_manuscript_uses_new_figures():
    main = (ROOT / 'paper' / 'sections' / '07_xian.tex').read_text(encoding='utf-8')
    sup = (ROOT / 'paper' / 'supplement_sections' / 'S6_xian.tex').read_text(encoding='utf-8')
    assert r'\includegraphics[width=135mm]{figures/new4o/xian_strategy_process.pdf}' in main
    assert r'\includegraphics[width=0.7\textwidth]{new4o/xian_eta_sensitivity.pdf}' in sup


def test_data_checks(receipt):
    sp = receipt['checks']['xian_strategy_process']
    assert abs(sp['t1'] - 16.896725724327304) < 1e-9 and abs(sp['t2'] - 101.96780289071071) < 1e-9
    assert sp['eta'] == 26326.0 and sp['observed_points'] == 40
    assert all(sp['peak_matches_summary'].values())
    es = receipt['checks']['xian_eta_sensitivity']
    assert es['scan_points'] == 11 and abs(es['tdinn']['J'] - 49.389404357321155) < 1e-9
