"""接收作者确认的九幅预览，逐字节入稿；默认仅核验，不重绘或运行计算。

接收：python -X utf8 nr_audit/adopt_new4t_figures.py --adopt
核验：python -X utf8 nr_audit/adopt_new4t_figures.py
重新生成预览仍使用 preview_supplement_style.py；色表及S4边界使用入库材料。
"""
import argparse
import copy
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / 'paper/tmp/supplement_style_preview_20261027'
ASSETS = ROOT / 'paper/figures/new4t'
MATERIALS = ROOT / 'nr_audit/results/new4t_figures'
MANIFEST = ROOT / 'nr_audit/results/new4t_figures.json'
BASE = 'a4472d5b775975705fd7e8d2fc2b9c948e96029b'
ITEMS = (
    ('Main6', 'fig:joint:phase', 'paper/sections/06_numerics.tex', r'\textwidth'),
    ('Main8', 'fig:xian:joint', 'paper/sections/07_xian.tex', r'\textwidth'),
    ('S1', 'fig:scenario1_summary_c0', 'paper/supplement_sections/S2_single_control.tex', r'\textwidth'),
    ('S2', 'fig:sup:eta-summary', 'paper/supplement_sections/S2_single_control.tex', r'\textwidth'),
    ('S3', 'fig:baseline:q-joint', 'paper/supplement_sections/S2_single_control.tex', r'\textwidth'),
    ('S4', 'fig:scenario1_heatmaps_c0_eta', 'paper/supplement_sections/S2_single_control.tex', r'0.8\textwidth'),
    ('S5', 'fig:s1:lambda-sensitivity', 'paper/supplement_sections/S3_inflection.tex', r'0.8\textwidth'),
    ('S6', 'fig:sup:phase-detail', 'paper/supplement_sections/S5_weight_structure.tex', r'\textwidth'),
    ('S8', 'fig:xian_heatmaps', 'paper/supplement_sections/S6_xian.tex', r'0.8\textwidth'),
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def record(raw, text=False):
    result = dict(sha256=digest(raw))
    if text:
        result['content_sha256'] = digest(raw.replace(b'\r\n', b'\n'))
    return result


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def raw_input(relative):
    if relative.startswith('git:'):
        _, ref, path = relative.split(':', 2)
        return subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=ROOT)
    return (ROOT / relative).read_bytes()


def require(relative, rec):
    raw = raw_input(relative)
    key = 'content_sha256' if 'content_sha256' in rec else 'sha256'
    actual = digest(raw.replace(b'\r\n', b'\n') if key == 'content_sha256' else raw)
    if actual != rec[key]:
        raise ValueError(f'NEW-4t输入身份不匹配：{relative}')


def remap_cache_paths(value):
    if isinstance(value, dict):
        return {k: remap_cache_paths(v) for k, v in value.items()}
    if isinstance(value, list):
        return [remap_cache_paths(v) for v in value]
    if isinstance(value, str) and value == 'paper/tmp/supplement_style_preview_20261027/S4_boundary_display.json':
        return 'nr_audit/results/new4t_figures/S4_boundary_display.json'
    return value


def adopt():
    if MANIFEST.exists():
        current_manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
        if any(row.get('author_approved_reference_fix') for row in current_manifest['outputs'].values()):
            raise ValueError('S8已接收作者确认的参照线纠错，不能用旧九图预览覆盖；请运行默认核验。')
    ASSETS.mkdir(parents=True, exist_ok=True)
    MATERIALS.mkdir(parents=True, exist_ok=True)
    imported = {}
    materials = (
        ('parula256.json', 'parula256.json'),
        ('S4_boundary_display.json', 'S4_boundary_display.json'),
        ('reference/inputs_sha256.json', 'style_reference_sha256.json'),
        ('preview_manifest.json', 'approved_preview_manifest.json'),
        ('S6_S8_refinement_validation.json', 'S6_S8_refinement_validation.json'),
    )
    for src, name in materials:
        raw = (PREVIEW / src).read_bytes()
        target = MATERIALS / name
        target.write_bytes(raw)
        imported[target.relative_to(ROOT).as_posix()] = record(raw)
    outputs, receipts, inputs = {}, {}, {}
    optional_style_inputs = {}
    for name, label, tex, width in ITEMS:
        receipt_path = PREVIEW / f'{name}.receipt.json'
        raw_receipt = receipt_path.read_bytes()
        original = json.loads(raw_receipt)
        pdf_raw = (PREVIEW / f'{name}.pdf').read_bytes()
        pdf_sha = digest(pdf_raw)
        assert pdf_sha == original['output_sha256'][f'{name}.pdf']
        assert digest((ROOT / original['old_pdf']).read_bytes()) == original['old_pdf_sha256']
        approved_receipt = MATERIALS / 'approved_receipts' / f'{name}.receipt.json'
        approved_receipt.parent.mkdir(exist_ok=True)
        approved_receipt.write_bytes(raw_receipt)
        imported[approved_receipt.relative_to(ROOT).as_posix()] = record(raw_receipt)
        formal = copy.deepcopy(original)
        formal['preview_only'] = False
        formal['approved_preview_receipt_sha256'] = digest(raw_receipt)
        formal['approved_preview_sha256'] = pdf_sha
        formal['original_preview_inputs'] = original['inputs']
        formal['inputs'] = {}
        formal['style_reference_inputs'] = {}
        for path, expected in original['inputs'].items():
            if Path(path).is_absolute():
                # 外部EPS仅作为画法来源登记，不构成重绘或科学核验的运行依赖。
                formal['style_reference_inputs'][path] = expected
                optional_style_inputs[path] = expected
                continue
            if path.startswith('paper/tmp/'):
                if path.endswith('parula256.json'):
                    path = 'nr_audit/results/new4t_figures/parula256.json'
                elif path.endswith('reference/inputs_sha256.json'):
                    path = 'nr_audit/results/new4t_figures/style_reference_sha256.json'
                else:
                    raise ValueError(f'未登记的临时输入：{path}')
            raw = raw_input(path)
            assert digest(raw) == expected, (name, path)
            text = not path.startswith('git:') and path.startswith('nr_audit/') and Path(path).suffix in {'.json', '.py'}
            rec = record(raw, text=text)
            formal['inputs'][path] = rec
            if path in inputs:
                assert inputs[path] == rec
            inputs[path] = rec
        formal['checks'] = remap_cache_paths(formal['checks'])
        relative = f'paper/figures/new4t/{name}.pdf'
        (ROOT / relative).write_bytes(pdf_raw)
        formal['formal_pdf'] = relative
        final_receipt = MATERIALS / f'{name}.receipt.json'
        write_json(final_receipt, formal)
        imported[final_receipt.relative_to(ROOT).as_posix()] = record(final_receipt.read_bytes())
        receipts[name] = final_receipt.relative_to(ROOT).as_posix()
        outputs[relative] = dict(figure=name, label=label, tex=tex, width=width,
                                sha256=pdf_sha, approved_preview_sha256=pdf_sha,
                                size_mm=original['size_mm'], fonts=original['fonts'])
    manifest = dict(phase='NEW-4t', date='2026-10-27', base_commit=BASE,
                    authorization='作者在本对话确认九图入稿、同步图注、编译检查和本地提交；不推送',
                    outputs=outputs, inputs=inputs, figure_receipts=receipts,
                    materials=imported, style_reference_inputs=optional_style_inputs,
                    old_figures_preserved=True,
                    scientific_activity=dict(current_adoption=dict(ode_solves=0, optimization_solves=0,
                       fits=0, classification_solves=0, boundary_root_solves=0),
                       preview_history=dict(S4_unique_threshold_points=241, S4_actual_brentq_calls=1205)))
    write_json(MANIFEST, manifest)
    return manifest


def verify(manifest):
    for path, rec in manifest['inputs'].items():
        require(path, rec)
    for path, rec in manifest['materials'].items():
        require(path, rec)
    for path, rec in manifest['outputs'].items():
        assert digest((ROOT / path).read_bytes()) == rec['sha256'], path
        if rec.get('author_approved_reference_fix'):
            assert rec['figure'] == 'S8'
            assert rec['reference_fix']['previous_pdf_sha256'] == rec['approved_preview_sha256']
            receipt = json.loads((ROOT / manifest['figure_receipts']['S8']).read_text(encoding='utf-8'))
            reference = json.loads((ROOT / receipt['checks']['reference_fix_source']['path']).read_text(encoding='utf-8'))
            assert receipt['checks']['reference_positions'][0] == reference['I_peak_T']
        else:
            assert rec['sha256'] == rec['approved_preview_sha256'], path
        assert f"\\includegraphics[width={rec['width']}]{{{path.removeprefix('paper/')}}}" in (ROOT / rec['tex']).read_text(encoding='utf-8'), path
    return dict(figures=len(manifest['outputs']), portable_inputs=len(manifest['inputs']),
                materials=len(manifest['materials']), new_scientific_solves=0)


def adopt_s8_reference_fix(preview_dir):
    """仅接收作者已批准的S8参照线纠错；原批准收据和其余八图保持。"""
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    verify(manifest)
    relative = 'paper/figures/new4t/S8.pdf'
    current = manifest['outputs'][relative]
    assert not current.get('author_approved_reference_fix'), 'S8参照线纠错已接收'
    original_receipt = manifest['figure_receipts']['S8']
    original = json.loads((ROOT / original_receipt).read_text(encoding='utf-8'))
    receipt = json.loads((preview_dir / 'S8.receipt.json').read_text(encoding='utf-8'))
    checks = receipt['checks']
    assert checks['author_approved_reference_fix'] is True
    for key in ('x', 'y', 'metrics', 'contour_style'):
        assert checks[key] == original['checks'][key], f'S8参照线之外的绘图内容变化：{key}'
    assert receipt['axes'] == original['axes']
    inputs = {}
    for path, expected in receipt['inputs'].items():
        if Path(path).is_absolute():
            assert original['style_reference_inputs'][path] == expected
            continue
        raw = raw_input(path)
        assert digest(raw) == expected, path
        inputs[path] = record(raw, text=path.startswith('nr_audit/') and Path(path).suffix in {'.json', '.py'})
        assert inputs[path] == manifest['inputs'][path]
    raw_pdf = (preview_dir / 'S8.pdf').read_bytes()
    actual = digest(raw_pdf)
    assert actual == receipt['output_sha256']['S8.pdf']
    fix = dict(authorization='作者2026-10-27确认按既有结果修正参照线，图注仍保留152.55',
               base_commit='73fd5aa2aa240198339d94face4b5bcbcc9f4481',
               previous_pdf_sha256=current['sha256'], previous_receipt=original_receipt,
               original_position=original['checks']['reference_positions'][0],
               corrected_position=checks['reference_positions'][0],
               source=checks['reference_fix_source'], new_scientific_solves=0)
    receipt.update(preview_only=False, inputs=inputs,
                   style_reference_inputs=original['style_reference_inputs'],
                   formal_pdf=relative, approved_preview_sha256=current['approved_preview_sha256'],
                   author_approved_reference_fix=True, reference_fix=fix)
    final_receipt = MATERIALS / 'S8_reference_corrected.receipt.json'
    write_json(final_receipt, receipt)
    receipt_rel = final_receipt.relative_to(ROOT).as_posix()
    manifest['materials'][receipt_rel] = record(final_receipt.read_bytes())
    manifest['figure_receipts']['S8'] = receipt_rel
    current.update(sha256=actual, author_approved_reference_fix=True, reference_fix=fix)
    (ROOT / relative).write_bytes(raw_pdf)
    write_json(MANIFEST, manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--adopt', action='store_true', help='逐字节接收当前已确认的九图')
    mode.add_argument('--fix-s8-reference', type=Path, metavar='PREVIEW_DIR',
                      help='仅接收作者批准的S8参照线修正预览')
    args = parser.parse_args()
    if args.fix_s8_reference:
        manifest = adopt_s8_reference_fix(args.fix_s8_reference)
    else:
        manifest = adopt() if args.adopt else json.loads(MANIFEST.read_text(encoding='utf-8'))
    print(json.dumps(verify(manifest), ensure_ascii=False))


if __name__ == '__main__':
    main()
