"""清理后的隔离编译、逐页等价及源码收集冒烟检查；不改正式工程。"""
from __future__ import annotations

import hashlib
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
TEMP = ROOT / 'tmp' / 'cleanup_verify_20261003'
STEMS = {'flatten_curve_analysis_cn': 45, 'flatten_curve_supplement_cn': 3}
sys.path.insert(0, str(ROOT / 'reproducibility'))
import bootstrap
import integrity
import pymupdf
from PIL import Image, ImageDraw


def read(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(resume_validation: bool = False) -> dict:
    manifest = read(REPORT / 'manifest.json')
    journal = read(REPORT / 'recycle_journal.json')
    if journal['state'] != 'recycled_pending_validation' or len(journal['files']) != 337:
        raise RuntimeError('尚未完整回收固化清单，禁止开始验收。')
    if TEMP.exists() and not resume_validation:
        raise FileExistsError(f'独立验收目录必须不存在：{TEMP}')
    latex = TEMP / 'latex'
    if len(manifest['formal_figures']) != 20:
        raise AssertionError('正式图件清单不是20幅。')
    stdout = REPORT / 'build_stdout.log'
    if resume_validation:
        previous = read(REPORT / 'verification.json')
        if previous.get('compile_exit_code') != 0 or not latex.is_dir():
            raise RuntimeError('只能重核已经实际完整编译成功的隔离副本。')
        failure_archive = REPORT / 'verification_attempt_1.json'
        if failure_archive.exists():
            raise FileExistsError('首份验收记录已封存，不覆盖。')
        shutil.copy2(REPORT / 'verification.json', failure_archive)
        compile_exit_code = 0
    else:
        TEMP.mkdir(parents=True)
        latex.mkdir()
        for name in ('flatten_curve_analysis_cn.tex', 'flatten_curve_supplement_cn.tex',
                     'elegantpaper.cls', 'references.bib', 'build_paper.ps1'):
            shutil.copy2(ROOT / 'latex' / name, latex / name)
        for relative in manifest['formal_figures']:
            target = latex / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / 'latex' / relative, target)
        shell = shutil.which('pwsh') or shutil.which('powershell')
        if not shell:
            raise FileNotFoundError('PowerShell unavailable')
        env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUTF8': '1'}
        with stdout.open('wb') as stream:
            completed = subprocess.run([shell, '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                        '-File', str(latex / 'build_paper.ps1')],
                                       cwd=latex, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                       timeout=900, check=False)
        compile_exit_code = completed.returncode
    result = {'passed': False, 'compile_exit_code': compile_exit_code,
              'compile_sequence': 'SI XeLaTeX x2; main XeLaTeX -> Biber -> XeLaTeX x2',
              'temporary_directory': str(TEMP), 'formal_files_changed': False,
              'full_numerical_rerun': False, 'nature_skills_used': False,
              'documents': {}, 'logs': {}, 'failures': []}
    if compile_exit_code:
        raise RuntimeError(f'完整编译失败，退出码 {compile_exit_code}；见 {stdout}')
    if resume_validation:
        result['verification_basis_correction'] = {
            'first_attempt_preserved': 'verification_attempt_1.json',
            'reason': 'accepted run的source_manifest收集于paper_sync之前，仅两份正式TEX已在发布阶段同步；以publication_manifest.final_sha256核查这两项，其余源码及输入仍逐项按原manifest核查。',
            'compile_reexecuted': False, 'bootstrap_prepare_reexecuted': False,
            'formal_content_changed_to_pass': False}

    all_pages = []
    forbidden = r'undefined|Missing character|Overfull|Float too large|multiply defined|^!|(?:LaTeX|Package \S+) Error:'
    for stem, expected_count in STEMS.items():
        log_text = (latex / (stem + '.log')).read_text(encoding='utf-8', errors='replace')
        fatal = [line for line in log_text.splitlines() if re.search(forbidden, line, re.I)]
        warnings = [line for line in log_text.splitlines() if 'Warning' in line or 'Underfull' in line]
        result['logs'][stem] = {'failures': fatal, 'warnings': warnings}
        result['failures'].extend(f'{stem}: {line}' for line in fatal + warnings)
        pages, outside = [], []
        with pymupdf.open(ROOT / 'latex' / (stem + '.pdf')) as formal, pymupdf.open(latex / (stem + '.pdf')) as rebuilt:
            if len(formal) != expected_count or len(rebuilt) != expected_count:
                result['failures'].append(f'{stem}: page counts {len(formal)}, {len(rebuilt)}, expected {expected_count}')
            for index in range(min(len(formal), len(rebuilt))):
                a, b = formal[index], rebuilt[index]
                old_text, new_text = a.get_text(), b.get_text()
                old_pixels, new_pixels = a.get_pixmap(dpi=120, alpha=False), b.get_pixmap(dpi=120, alpha=False)
                text_exact = old_text == new_text
                render_exact = (old_pixels.width, old_pixels.height, old_pixels.n, old_pixels.samples) == \
                               (new_pixels.width, new_pixels.height, new_pixels.n, new_pixels.samples)
                row = {'page': index + 1, 'text_exact': text_exact, 'render_exact_120dpi': render_exact,
                       'formal_text_sha256': hashlib.sha256(old_text.encode()).hexdigest(),
                       'rebuilt_text_sha256': hashlib.sha256(new_text.encode()).hexdigest(),
                       'formal_pixel_sha256': hashlib.sha256(old_pixels.samples).hexdigest(),
                       'rebuilt_pixel_sha256': hashlib.sha256(new_pixels.samples).hexdigest()}
                pages.append(row)
                if not text_exact or not render_exact:
                    result['failures'].append(f'{stem}: page {index + 1} differs')
                for block in b.get_text('dict')['blocks']:
                    for line in block.get('lines', []):
                        for span in line.get('spans', []):
                            if span['text'].strip() and not (b.rect + (-1, -1, 1, 1)).contains(pymupdf.Rect(span['bbox'])):
                                outside.append({'page': index + 1, 'text': span['text'], 'bbox': span['bbox']})
                all_pages.append({'stem': stem, 'page': index + 1})
        result['documents'][stem] = {'page_count': len(pages), 'pages': pages,
                                     'outside_page_text': outside,
                                     'formal_pdf_sha256': sha(ROOT / 'latex' / (stem + '.pdf')),
                                     'rebuilt_pdf_sha256': sha(latex / (stem + '.pdf')),
                                     'metadata_ignored': True,
                                     'all_pages_exact': len(pages) == expected_count and all(p['text_exact'] and p['render_exact_120dpi'] for p in pages)}
        if outside:
            result['failures'].append(f'{stem}: page geometry violations {len(outside)}')

    text = (latex / 'flatten_curve_analysis_cn.tex').read_text(encoding='utf-8-sig')
    supplement = (latex / 'flatten_curve_supplement_cn.tex').read_text(encoding='utf-8-sig')
    main = 'flatten_curve_analysis_cn'
    blg = (latex / (main + '.blg')).read_text(encoding='utf-8', errors='replace')
    biber_warnings = [line for line in blg.splitlines() if re.search(r'WARN|ERROR', line)]
    bbl = (latex / (main + '.bbl')).read_text(encoding='utf-8', errors='replace')
    printed_keys = sorted(set(re.findall(r'\\entry\{([^}]+)\}', bbl)))
    previous_build = read(ROOT / 'reproducibility/runs/20261003_release_final/run_1/document/build_report.json')
    expected_keys = sorted(previous_build['printed_bibliography_keys'])
    with pymupdf.open(latex / (main + '.pdf')) as pdf:
        bibliography_pages = [i + 1 for i, page in enumerate(pdf) if '参考文献' in page.get_text()]
    citation_keys = sorted(set(k.strip() for group in re.findall(r'\\(?:cite|parencite|textcite)\*?(?:\[[^\]]*\])*\{([^}]+)\}', text) for k in group.split(',')))
    result['bibliography'] = {'printed_keys': printed_keys, 'expected_keys': expected_keys,
                              'citation_keys': citation_keys, 'printed_count': len(printed_keys),
                              'main_print_count': text.count('\\printbibliography'),
                              'supplement_print_count': supplement.count('\\printbibliography'),
                              'heading_pages': bibliography_pages, 'biber_warnings': biber_warnings,
                              'passed': printed_keys == expected_keys and len(printed_keys) == 20 and
                                        set(citation_keys) <= set(printed_keys) and text.count('\\printbibliography') == 1 and
                                        supplement.count('\\printbibliography') == 0 and bool(bibliography_pages) and not biber_warnings}
    if not result['bibliography']['passed']:
        result['failures'].append('参考文献完整性/唯一打印核查失败')
    result['structure'] = {'main_figures': len(re.findall(r'\\begin\{figure\}', text)),
                           'main_tables': len(re.findall(r'\\begin\{table\}', text)),
                           'supplement_tables': len(re.findall(r'\\begin\{table\}', supplement))}
    if result['structure'] != {'main_figures': 20, 'main_tables': 4, 'supplement_tables': 3}:
        result['failures'].append('图表结构数量变化')

    smoke = TEMP / 'bootstrap_smoke'
    workspace = smoke / 'workspace' if resume_validation else bootstrap.prepare_workspace(smoke, ROOT)
    integrity_report = integrity.run(ROOT, smoke)
    shutil.copy2(smoke / 'source_manifest.json', REPORT / 'bootstrap_source_manifest.json')
    shutil.copy2(smoke / 'validation/source_integrity.json', REPORT / 'bootstrap_source_integrity.json')
    visual_files = sorted(p.relative_to(smoke / 'visual_reference').as_posix() for p in (smoke / 'visual_reference').rglob('*.pdf'))
    expected_visual = sorted(p.removeprefix('figures/') for p in manifest['formal_figures'])
    original_source = read(ROOT / 'reproducibility/runs/20261003_release_final/run_1/source_manifest.json')['source_files']
    fresh_source = read(smoke / 'source_manifest.json')['source_files']
    expected_source = dict(original_source)
    publication = read(ROOT / 'reproducibility/release_reports/publication_manifest.json')
    formal_document_paths = {'latex/flatten_curve_analysis_cn.tex', 'latex/flatten_curve_supplement_cn.tex'}
    publication_document_records = [row for row in publication['files'] if row['file'] in formal_document_paths]
    if len(publication_document_records) != 2:
        raise AssertionError('正式稿发布清单必须有且仅有两份TEX基准。')
    for row in publication_document_records:
        expected_source[row['file']] = row['final_sha256']
    same_source = fresh_source == expected_source
    source_differences = [{'file': path, 'expected_sha256': expected_source.get(path),
                           'fresh_sha256': fresh_source.get(path)}
                          for path in sorted(set(fresh_source) | set(expected_source))
                          if fresh_source.get(path) != expected_source.get(path)]
    result['bootstrap'] = {'passed': integrity_report['passed'] and visual_files == expected_visual and same_source,
                           'workspace': str(workspace), 'visual_reference_count': len(visual_files),
                           'visual_reference_exact': visual_files == expected_visual,
                           'source_manifest_same_as_accepted_presync_run': fresh_source == original_source,
                           'source_manifest_matches_locked_publication': same_source,
                           'source_manifest_differences': source_differences,
                           'formal_document_publication_basis': publication_document_records,
                           'source_manifest_count': len(fresh_source),
                           'frozen_files_checked': len(integrity_report['frozen_release']),
                           'frozen_manifest_sha256': integrity_report['frozen_manifest_sha256'],
                           'historical_numerical_caches_copied': False,
                           'source_input_changes': integrity_report['changed_original_sources']}
    if not result['bootstrap']['passed']:
        result['failures'].append('源码收集/原始输入/视觉参考/冻结包验收失败')

    registry = read(ROOT / 'reproducibility/registry.json')
    required = list(registry['runtime_dependencies'])
    def collect_sources(value):
        if isinstance(value, dict):
            if 'path' in value and isinstance(value['path'], str) and value.get('exists') is True:
                required.append(value['path'])
            for child in value.values():
                collect_sources(child)
        elif isinstance(value, list):
            for child in value:
                collect_sources(child)
    collect_sources(registry)
    missing = sorted(set(path for path in required if not (ROOT / path).is_file()))
    result['registry_dependencies'] = {'passed': not missing, 'unique_paths_checked': len(set(required)), 'missing': missing}
    if missing:
        result['failures'].append('registry依赖缺失: ' + ', '.join(missing))
    collection = read(ROOT / 'reproducibility/release_reports/collection_manifest.json')
    collection_failures = [row['file'] for row in collection['files'] if not (ROOT / row['file']).is_file() or sha(ROOT / row['file']) != row['sha256']]
    result['collected_evidence'] = {'passed': not collection_failures, 'files_checked': len(collection['files']), 'changed': collection_failures}
    if collection_failures:
        result['failures'].append('既有汇集结果/报告发生变化')

    # Poppler 用于本轮全部页面概览；120dpi数值逐像素比较另由PyMuPDF完成。
    poppler = shutil.which('pdftoppm')
    if not poppler:
        raise FileNotFoundError('pdftoppm unavailable for visual review')
    render = TEMP / 'poppler_review'
    if not resume_validation:
        render.mkdir()
        for stem in STEMS:
            subprocess.run([poppler, '-r', '60', '-png', str(latex / (stem + '.pdf')), str(render / stem)],
                           check=True, timeout=240, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    montage_paths = []
    for start in range(0, len(all_pages), 12):
        sheet = Image.new('RGB', (1240, 1780), '#dedede')
        draw = ImageDraw.Draw(sheet)
        for j, row in enumerate(all_pages[start:start + 12]):
            options = sorted(render.glob(f"{row['stem']}-*.png"))
            file = next(p for p in options if int(p.stem.rsplit('-', 1)[1]) == row['page'])
            with Image.open(file) as img:
                img.thumbnail((398, 410))
                x, y = (j % 3) * 413 + 7, (j // 3) * 445 + 26
                sheet.paste(img, (x, y))
                role = 'main' if row['stem'] == main else 'supplement'
                draw.text((x, y - 20), f'{role}: page {row["page"]}', fill='black')
        path = REPORT / f'page_montage_{start + 1:02d}_{min(start + 12, len(all_pages)):02d}.png'
        sheet.save(path)
        montage_paths.append(path.name)
    result['visual_review'] = {'all_48_pages_rendered': len(all_pages) == 48,
                               'montages': montage_paths, 'renderer': 'Poppler pdftoppm 60dpi',
                               'manual_review': 'pending_main_agent_review'}
    result['passed'] = not result['failures']
    result['scope'] = '实际隔离完整编译、48页文本及120dpi像素等价、源码收集和输入版本检查；不重跑全部数值，也不替代数学证明。'
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume-validation', action='store_true')
    args = parser.parse_args()
    try:
        report = run(args.resume_validation)
    except Exception as error:
        report = {'passed': False, 'error': str(error), 'traceback': traceback.format_exc(),
                  'temporary_directory': str(TEMP), 'formal_files_changed': False,
                  'nature_skills_used': False}
    dump(REPORT / 'verification.json', report)
    print(json.dumps({key: report.get(key) for key in ('passed', 'error', 'failures', 'compile_exit_code')}, ensure_ascii=False))
    sys.exit(0 if report['passed'] else 1)
