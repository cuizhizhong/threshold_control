"""NEW-4s：正文图 4 按图 2 风格重绘后的收据（results/new4s_figures.json）。
核对输入数据的原字节身份未变、入库图件即收据登记的输出、字体与印刷宽度，以及各轨迹画至自身的清零时间、
两感染仓室峰值与正文表 1 一致。"""
import hashlib
import json
import re

import pytest

from conftest import SRC

RES = SRC.HERE / 'results' / 'new4s_figures.json'
ROOT = SRC.HERE.parent
FIG = 'paper/figures/new4s/joint_compare_baseline.pdf'
WIDTH_MM = 0.85 * 452.9679 / 72 * 25.4


@pytest.fixture(scope='module')
def receipt():
    if not RES.exists():
        pytest.skip('尚未运行 plot_new4s_figures.py')
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
    text = (ROOT / 'paper/sections/06_numerics.tex').read_text(encoding='utf-8')
    assert r'\includegraphics[width=0.85\textwidth]{figures/new4s/joint_compare_baseline.pdf}' in text


def test_trajectories_match_table(receipt):
    c = receipt['checks']
    assert all(c['ends_at_clearance'].values()) and all(c['peak_matches_table'].values())
    text = (ROOT / 'paper/sections/06_numerics.tex').read_text(encoding='utf-8')
    for key, name in (('contact_only', '仅减少接触'), ('alpha_0.5', r'显式族 $\alpha=0.5$'),
                      ('quarantine_only', '仅隔离控制'), ('minimum_cost', '成本最优控制')):
        law = c['laws'][key]
        row = next(line for line in text.splitlines() if line.startswith(name + ' &'))
        assert row.split('&')[2].strip() == f"{law['t_end']:.2f}"                  # 表 1 的清零时间
        assert row.rstrip('\\ ').split('&')[-1].strip() == f"{law['peak_ratio_table']:.2f}"
