"""NEW-4t：批准预览的原字节接收入稿、可移植来源身份与关键科学保真检查。"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import pytest

from conftest import SRC


ROOT = SRC.HERE.parent
RES = SRC.HERE / 'results/new4t_figures.json'
ASSETS = SRC.HERE / 'results/new4t_figures'
WIDTH_MM = 452.9679 / 72 * 25.4
LABELS = {
    'Main6': 'fig:joint:phase', 'Main8': 'fig:xian:joint',
    'S1': 'fig:scenario1_summary_c0', 'S2': 'fig:sup:eta-summary',
    'S3': 'fig:baseline:q-joint', 'S4': 'fig:scenario1_heatmaps_c0_eta',
    'S5': 'fig:s1:lambda-sensitivity', 'S6': 'fig:sup:phase-detail',
    'S8': 'fig:xian_heatmaps',
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def array_digest(values):
    return digest(np.ascontiguousarray(values, dtype='<f8').tobytes())


@pytest.fixture(scope='module')
def adopted():
    if not RES.exists():
        pytest.skip('尚未接收NEW-4t正式图件')
    return json.loads(RES.read_text(encoding='utf-8'))


def figure_receipt(adopted, name):
    path = ROOT / adopted['figure_receipts'][name]
    assert path.is_relative_to(ASSETS)
    return json.loads(path.read_text(encoding='utf-8'))


@pytest.mark.parametrize('name', sorted(LABELS))
def test_approved_bytes_and_current_manuscript_use(adopted, name):
    rel = f'paper/figures/new4t/{name}.pdf'
    out = adopted['outputs'][rel]
    assert out['figure'] == name and out['label'] == LABELS[name]
    actual = digest((ROOT / rel).read_bytes())
    assert actual == out['sha256']
    if out.get('author_approved_colorbar_cleanup'):
        previous = json.loads((ROOT / out['colorbar_cleanup']['previous_receipt']).read_text(encoding='utf-8'))
        assert previous['output_sha256'][name + '.pdf'] == out['colorbar_cleanup']['previous_pdf_sha256']
    elif out.get('author_approved_reference_fix'):
        assert name == 'S8'
        assert out['reference_fix']['previous_pdf_sha256'] == out['approved_preview_sha256']
    else:
        assert actual == out['approved_preview_sha256']
    receipt = figure_receipt(adopted, name)
    assert receipt['approved_preview_sha256'] == out['approved_preview_sha256']
    if out.get('author_approved_reference_fix'):
        assert receipt['author_approved_reference_fix'] is True
        assert receipt['output_sha256']['S8.pdf'] == actual
    assert digest((ROOT / receipt['old_pdf']).read_bytes()) == receipt['old_pdf_sha256']
    assert out['fonts'] and all(re.search(r'cm(r|mi|sy|ex)10', f, re.I) for f in out['fonts'])
    factor = .8 if name in ('S4', 'S5', 'S8') else 1.
    assert abs(out['size_mm'][0] - factor * WIDTH_MM) < .05
    assert out['width'] == (r'0.8\textwidth' if factor == .8 else r'\textwidth')
    text = (ROOT / out['tex']).read_text(encoding='utf-8')
    new4w = SRC.HERE / 'results/new4w/figures.json'
    if name in ('Main8', 'S8') and new4w.exists():
        # NEW-4w（N33）：西安设计阈值改为 0.001N 后重绘，正式引用改为 figures/new4w/；NEW-4t 字节与收据只读保留。
        rec = json.loads(new4w.read_text(encoding='utf-8'))[name]
        assert digest((ROOT / f'paper/figures/new4w/{name}.pdf').read_bytes()) == rec['pdf_sha256']
        assert f'{{figures/new4w/{name}.pdf}}' in text
        return
    blocks = re.findall(r'\\begin\{figure\*?\}([\s\S]*?)\\end\{figure\*?\}', text)
    block = next(b for b in blocks if f"\\label{{{out['label']}}}" in b)
    match = re.search(r'\\includegraphics\[([^]]*)\]\{([^}]+)\}', block)
    assert match and 'width=' + out['width'] in re.sub(r'\s+', '', match[1])
    candidates = [(ROOT / 'paper' / match[2]).resolve(), (ROOT / 'paper/figures' / match[2]).resolve()]
    assert (ROOT / rel).resolve() in candidates


def test_exactly_nine_adopted_figures_and_no_new_solves(adopted):
    assert set(adopted['outputs']) == {f'paper/figures/new4t/{name}.pdf' for name in LABELS}
    assert set(adopted['figure_receipts']) == set(LABELS)
    activity = adopted['scientific_activity']
    assert activity['current_adoption'] == dict(ode_solves=0, optimization_solves=0, fits=0,
                                               classification_solves=0, boundary_root_solves=0)
    assert activity['preview_history']['S4_unique_threshold_points'] == 241
    assert activity['preview_history']['S4_actual_brentq_calls'] == 1205
    import figure_table_sources as mapping
    for label in LABELS.values():
        assert 'adopt_new4t_figures.py' in mapping.FIG[label][1]


@pytest.mark.parametrize('name', ['Main6', 'Main8', 'S4', 'S6', 'S8'])
def test_colorbar_cleanup_preserves_scientific_content(adopted, name):
    out = adopted['outputs'][f'paper/figures/new4t/{name}.pdf']
    if not out.get('author_approved_colorbar_cleanup'):
        pytest.skip('尚未接收色柱整理')
    receipt = figure_receipt(adopted, name)
    previous = json.loads((ROOT / out['colorbar_cleanup']['previous_receipt']).read_text(encoding='utf-8'))
    current_checks = dict(receipt['checks'])
    style = current_checks.pop('colorbar_style' if name.startswith('Main') else 'colorbar_layout')
    assert current_checks == previous['checks']
    assert receipt['output_sha256'][name + '.pdf'] == out['sha256']
    if name.startswith('Main'):
        assert style['auxiliary_lines_before'] == 9 and style['auxiliary_lines_after'] == 0
        assert style['plot_geometry_unchanged'] and style['position_unchanged']
    else:
        assert style['panel_geometry_unchanged'] and style['colorbar_width_height_unchanged']
        assert len(style['pairs']) == (1 if name == 'S6' else 4)
        for row in style['pairs']:
            assert row['after_gap_mm'] < row['before_gap_mm']
            panel_width = row['panel_bounds'][2]
            assert abs((row['after_bounds'][0] - sum(row['panel_bounds'][::2])) / panel_width
                       - style['gap_to_panel_width']) < 1e-12


def test_portable_scientific_inputs_and_archived_blobs(adopted):
    """允许点名文本CRLF/LF等价；冻结CSV、NPZ与固定Git blob仍严格按原字节核对。"""
    assert adopted['inputs']
    for rel, identity in adopted['inputs'].items():
        assert 'paper/tmp/' not in rel and not Path(rel).is_absolute(), rel
        if rel.startswith('git:'):
            _, tag, path = rel.split(':', 2)
            raw = subprocess.check_output(['git', 'show', f'{tag}:{path}'], cwd=ROOT)
            assert 'content_sha256' not in identity
        else:
            raw = (ROOT / rel).read_bytes()
        if 'content_sha256' in identity:
            assert rel.startswith('nr_audit/') and Path(rel).suffix in ('.json', '.py'), rel
            assert digest(raw.replace(b'\r\n', b'\n')) == identity['content_sha256'], rel
        else:
            assert digest(raw) == identity['sha256'], rel
    for name in LABELS:
        receipt = figure_receipt(adopted, name)
        assert receipt['inputs']
        assert all('paper/tmp/' not in rel and not Path(rel).is_absolute() for rel in receipt['inputs'])


def test_s6_original_arrays_boundaries_zero_mask_and_display_only_partitions(adopted):
    receipt = figure_receipt(adopted, 'S6')
    data = json.loads((SRC.HERE / 'results/new_figure7.json').read_text(encoding='utf-8'))
    closed = json.loads((SRC.HERE / 'results/new4d_cost_structure.json').read_text(encoding='utf-8'))
    from plot_figure7 import edge_kind
    with np.load(SRC.HERE / 'results/new_figure7.npz', allow_pickle=False) as cached:
        for case, panel in receipt['checks']['panels'].items():
            z, rr, values = (cached[f'{case}_{field}'] for field in ('z', 'background_r', 'background_y'))
            assert panel['background']['source']['sha256'] == array_digest(values)
            assert panel['background']['source'] == panel['background']['plotted']
            r = cached[f'{case}_r']
            expected = {}
            zero = []
            for kind in ('continuous', 'endpoint', 'internal'):
                xs = []
                for row in data['cases'][case]['samples']:
                    nodes = [b['z'] for b in row['breakpoints'] if edge_kind(b) == kind]
                    xs.append(nodes[0] if nodes else np.nan)
                xs = np.asarray(xs)
                expected[kind] = np.column_stack((xs, r))
                assert panel['boundaries'][kind]['x']['sha256'] == array_digest(xs)
                assert panel['boundaries'][kind]['y']['sha256'] == array_digest(r)
                if kind != 'internal':
                    zero.extend([float(x), float(y)] for x, y in zip(xs, r) if np.isfinite(x))
            point = [closed['cases'][case]['z_sw'], closed['cases'][case]['r_hat']]
            zero.append(point)
            zero = np.asarray(sorted(zero, key=lambda row: row[1]))
            threshold = np.interp(rr, zero[:, 1], zero[:, 0])
            mask = z[None, :] >= threshold[:, None]
            assert np.count_nonzero(mask & (values > 1e-12)) == 0
            assert panel['zero_region_mask']['covered_original_nodes'] == int(mask.sum())
            assert panel['zero_region_mask']['covered_nonzero_nodes'] == 0
            for kind, indexer in (('endpoint', np.argmin), ('continuous', np.argmax)):
                nodes = expected[kind]
                nodes = nodes[np.isfinite(nodes[:, 0])]
                connector = panel['known_endpoint_connectors'][kind]
                assert connector['to'] == point
                assert connector['from_'] == nodes[int(indexer(nodes[:, 1]))].tolist()
            display = panel['branch_display_partitions']
            assert (display['new_classifications'], display['new_grid_nodes'], display['new_solves']) == (0, 0, 0)
            assert all(layer['retained_original_values_exact'] for layer in display['layers'].values())
            assert panel['white_line_outline'] is False


def test_s8_original_levels_paths_and_short_label_gaps(adopted):
    receipt = figure_receipt(adopted, 'S8')
    checks = receipt['checks']
    assert checks['contour_style'] == dict(line_color='red', linestyle='-.', label_color='black',
                                           inline_gap=True, label_path_effects=[])
    assert '40' in checks['removed_annotation']
    metrics = checks['metrics']
    assert set(metrics) == {'control_duration', 'clear_time', 'cum_total_infections', 'J'}
    for metric, record in metrics.items():
        assert record['source']['sha256'] == record['plotted']['sha256']
        assert record['source']['shape'] == [47, 98] and record['source']['nan_count'] == 0
        assert record['normalization'] == ('linear' if metric == 'cum_total_infections' else 'log')
        paths = record['contour_paths_and_inline_gaps']
        assert paths['hidden_after_inline_cut'] == 0
        assert [p['level'] for p in paths['raw_paths']] == record['contour_levels']
        assert [p['level'] for p in paths['final_paths']] == record['contour_levels']
        assert len(paths['gap_metrics']) == len(record['contour_levels'])
        for raw, final, gap in zip(paths['raw_paths'], paths['final_paths'], paths['gap_metrics']):
            assert gap['pass_'] and gap['removed_length_px'] <= gap['label_gap_upper_bound_px']
            assert gap['before_length_px'] >= gap['after_length_px'] - 1e-8
            if gap['label_count'] == 0:
                assert raw == final
    reference = json.loads((ROOT / 'reproducibility/results/20261003_release_final/xian/reference.json').read_text(encoding='utf-8'))
    approved_fix = checks.get('author_approved_reference_fix', receipt.get('author_approved_reference_fix', False))
    if approved_fix:
        assert checks['reference_positions'][0] == reference['I_peak_T']
        assert checks['reference_fix_source']['field'] == 'I_peak_T'
        assert checks['reference_fix_source']['value'] == reference['I_peak_T']
        assert all(row == [reference['I_peak_T'], 26326.]
                   for row in checks['plotted_reference_positions'].values())
        previous = json.loads((ASSETS / 'S8.receipt.json').read_text(encoding='utf-8'))
        assert checks['metrics'] == previous['checks']['metrics']
    else:
        assert checks['reference_positions'][0] == checks['existing_reference_discrepancy']['original_plot_source']
