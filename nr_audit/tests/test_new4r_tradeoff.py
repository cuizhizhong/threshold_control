"""NEW-4r：正文图 3 改为阈值取舍图后的收据（results/new4r_tradeoff.json）。
核对输入数据的原字节身份未变、入库图件即收据登记的输出、字体与印刷宽度、c0 = 10 曲线与单独的阈值扫描一致，
以及第 3.4 节所写的数字与取舍的倍数。"""
import hashlib
import json
import re

import pytest

from conftest import SRC

RES = SRC.HERE / 'results' / 'new4r_tradeoff.json'
ROOT = SRC.HERE.parent
FIG = 'paper/figures/new4r/threshold_tradeoff.pdf'
WIDTH_MM = 0.9 * 452.9679 / 72 * 25.4


@pytest.fixture(scope='module')
def receipt():
    if not RES.exists():
        pytest.skip('尚未运行 plot_new4r_tradeoff.py')
    return json.loads(RES.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_inputs_unchanged(receipt):
    for rel, digest in receipt['inputs_sha256'].items():
        assert sha(ROOT / rel) == digest, rel


def test_output_registered_and_used(receipt):
    out = receipt['outputs'][FIG]
    assert sha(ROOT / FIG) == out['sha256']
    assert abs(out['size_mm'][0] - WIDTH_MM) < 0.05
    assert out['fonts'] and all(re.search(r'Cm(r|mi|sy|ex)10', f) for f in out['fonts'])
    text = (ROOT / 'paper/sections/03_single_control.tex').read_text(encoding='utf-8')
    assert r'\includegraphics[width=0.9\textwidth]{figures/new4r/threshold_tradeoff.pdf}' in text
    sup = (ROOT / 'paper/supplement_sections/S2_single_control.tex').read_text(encoding='utf-8')
    assert r'\label{fig:sup:eta-summary}' in sup
    adopted = SRC.HERE / 'results/new4t_figures.json'
    if adopted.exists():
        current_rel = 'paper/figures/new4t/S2.pdf'
        current = json.loads(adopted.read_text(encoding='utf-8'))['outputs'][current_rel]
        assert sha(ROOT / current_rel) == current['sha256'] == current['approved_preview_sha256']
        assert r'\includegraphics[width=\textwidth]{figures/new4t/S2.pdf}' in sup
    else:
        assert 'eta_sensitivity_selected_c0.pdf' in sup


def test_curves_and_text_numbers(receipt):
    c = receipt['checks']
    assert set(c['points_per_c0'].values()) == {241}
    assert c['c0_10_vs_eta_scan']['matched'] == 241
    assert all(v < 1e-12 for v in c['c0_10_vs_eta_scan']['max_rel_diff'].values())
    t = c['text_numbers']
    text = (ROOT / 'paper/sections/03_single_control.tex').read_text(encoding='utf-8')
    assert f"控制时长由 ${t['dt_2']:.2f}$ d 增至 ${t['dt_02']:.1f}$ d" in text
    assert f"总累计新增感染却只由 ${t['itcum_2']:.1f}$ 人减至 ${t['itcum_02']:.1f}$ 人" in text
    assert 9.5 < t['J_02'] / t['J_2'] < 10.5                   # 正文“成本也增大约十倍”
    assert t['tend_02'] > t['tend_2']                          # 正文“清零时间也随阈值提高而缩短”
