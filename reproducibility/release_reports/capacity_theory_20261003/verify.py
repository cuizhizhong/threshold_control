"""能力限制局部补充的静态、编译及 PDF 核查；不修改正式工程。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import traceback

import pymupdf
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
BACKUP = ROOT / 'reproducibility/backups/before_capacity_theory_20261003'
LATEX = ROOT / 'latex'
PREVIOUS = ROOT / 'reproducibility/runs/20261003_release_final/run_1/document/latex'
MAIN = 'flatten_curve_analysis_cn'
SI = 'flatten_curve_supplement_cn'


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8-sig', errors='strict')


def json_read(path: Path):
    return json.loads(read(path))


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value) -> str:
    def encode(item):
        if isinstance(item, bytes):
            return {'bytes_sha256': hashlib.sha256(item).hexdigest()}
        return str(item)
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, default=encode)
    return hashlib.sha256(raw.encode()).hexdigest()


def brace(text: str, offset: int):
    """完整解析一层 TeX 花括号；转义花括号不参与深度计数。"""
    while offset < len(text) and text[offset].isspace():
        offset += 1
    if offset == len(text) or text[offset] != '{':
        raise ValueError(f'未找到花括号组，offset={offset}')
    start, depth = offset + 1, 1
    offset += 1
    while offset < len(text):
        char = text[offset]
        if char == '\\':
            offset += 2
            continue
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return text[start:offset], offset + 1
        offset += 1
    raise ValueError('未闭合的花括号组')


def aux_labels(path: Path):
    text = read(path)
    result = {}
    for match in re.finditer(r'\\newlabel\s*', text):
        label, stop = brace(text, match.end())
        payload, _ = brace(text, stop)
        value, stop = brace(payload, 0)
        page, _ = brace(payload, stop)
        if label in result:
            raise ValueError(f'重复的 newlabel: {label}')
        result[label] = {'value': value, 'page': page}
    return result


def env_blocks(text: str, names):
    joined = '|'.join(re.escape(name) for name in names)
    return [(match.group(1), match.group(0)) for match in re.finditer(
        rf'\\begin\{{({joined})\}}.*?\\end\{{\1\}}', text, flags=re.S)]


def cite_keys(text: str):
    return sorted({key.strip() for group in re.findall(
        r'\\(?:cite|parencite|textcite|autocite|footcite|nocite)\*?(?:\[[^\]]*\])*\{([^}]+)\}', text)
        for key in group.split(',')})


def static_checks(old: str, new: str):
    labels_old = re.findall(r'\\label\{([^}]+)\}', old)
    labels_new = re.findall(r'\\label\{([^}]+)\}', new)
    old_math = env_blocks(old, ['equation', 'align', 'gather', 'multline', 'eqnarray'])
    new_math = env_blocks(new, ['equation', 'align', 'gather', 'multline', 'eqnarray'])
    old_floats = env_blocks(old, ['figure', 'figure*', 'table', 'table*'])
    new_floats = env_blocks(new, ['figure', 'figure*', 'table', 'table*'])
    old_prop = next(block for name, block in env_blocks(old, ['proposition'])
                    if r'\label{prop:joint:terminal-allocation}' in block)
    new_prop = next(block for name, block in env_blocks(new, ['proposition'])
                    if r'\label{prop:joint:terminal-allocation}' in block)
    proof_anchor = old.index(old_prop) + len(old_prop)
    old_proof = env_blocks(old[proof_anchor:], ['proof'])[0][1]
    proof_anchor = new.index(new_prop) + len(new_prop)
    new_proof = env_blocks(new[proof_anchor:], ['proof'])[0][1]
    checks = {
        'labels_order_and_set_exact': labels_old == labels_new,
        'labels_count': len(labels_new),
        'numbered_math_environment_count': len(new_math),
        'numbered_math_environments_exact': old_math == new_math,
        'float_environments_count': len(new_floats),
        'float_environments_exact': old_floats == new_floats,
        'float_environment_sha256': [digest(block) for block in new_floats],
        'citation_keys_exact': cite_keys(old) == cite_keys(new),
        'citation_keys': cite_keys(new),
        'terminal_allocation_proposition_exact': old_prop == new_prop,
        'terminal_allocation_proof_exact': old_proof == new_proof,
        'main_bibliography_print_count': new.count(r'\printbibliography'),
        'supplement_bibliography_print_count': read(LATEX / f'{SI}.tex').count(r'\printbibliography'),
        'new_numbered_formula_added': old_math != new_math,
    }
    checks['passed'] = all(checks[key] for key in (
        'labels_order_and_set_exact', 'numbered_math_environments_exact',
        'float_environments_exact', 'citation_keys_exact',
        'terminal_allocation_proposition_exact', 'terminal_allocation_proof_exact')) \
        and checks['main_bibliography_print_count'] == 1 \
        and checks['supplement_bibliography_print_count'] == 0
    return checks


def font_signatures(document, page):
    result = []
    for entry in page.get_fonts(full=True):
        xref, extension, font_type, basename, resource_name, encoding, *_ = entry
        extracted = document.extract_font(xref)
        result.append({'extension': extension, 'type': font_type, 'basename': basename,
                       'resource': resource_name, 'encoding': encoding,
                       'font_bytes_sha256': hashlib.sha256(extracted[3]).hexdigest()})
    return sorted(result, key=lambda row: json.dumps(row, sort_keys=True))


def compare_si():
    pages = []
    with pymupdf.open(BACKUP / f'{SI}.pdf') as old, pymupdf.open(LATEX / f'{SI}.pdf') as new:
        same_count = len(old) == len(new) == 3
        for index in range(min(len(old), len(new))):
            a, b = old[index], new[index]
            pa, pb = a.get_pixmap(dpi=120, alpha=False), b.get_pixmap(dpi=120, alpha=False)
            pages.append({'page': index + 1, 'text_exact': a.get_text() == b.get_text(),
                          'text_positions_and_images_exact': digest(a.get_text('dict')) == digest(b.get_text('dict')),
                          'drawings_exact': digest(a.get_drawings()) == digest(b.get_drawings()),
                          'fonts_exact': font_signatures(old, a) == font_signatures(new, b),
                          'render_exact_120dpi': (pa.width, pa.height, pa.n, pa.samples) ==
                          (pb.width, pb.height, pb.n, pb.samples),
                          'before_pixel_sha256': hashlib.sha256(pa.samples).hexdigest(),
                          'after_pixel_sha256': hashlib.sha256(pb.samples).hexdigest()})
    fields = ('text_exact', 'text_positions_and_images_exact', 'drawings_exact', 'fonts_exact', 'render_exact_120dpi')
    identical = same_count and all(all(row[field] for field in fields) for row in pages)
    byte_identical = sha(BACKUP / f'{SI}.pdf') == sha(LATEX / f'{SI}.pdf')
    return {'page_count': len(pages), 'pages': pages, 'content_exact': identical,
            'byte_identical': byte_identical, 'metadata_only_difference': identical and not byte_identical,
            'backup_sha256': sha(BACKUP / f'{SI}.pdf'), 'current_sha256': sha(LATEX / f'{SI}.pdf'),
            'restore_action': 'none: main agent may restore unchanged original only after content equivalence'}


def render_review(pdf_path: Path, target_pages, page_count):
    qa = REPORT / 'qa'
    qa.mkdir(exist_ok=True)
    poppler = shutil.which('pdftoppm')
    if not poppler:
        raise FileNotFoundError('Poppler pdftoppm 未找到，不能完成页面渲染。')
    for page in target_pages:
        prefix = qa / f'main_page_{page:02d}'
        subprocess.run([poppler, '-f', str(page), '-l', str(page), '-r', '120', '-singlefile',
                        '-png', str(pdf_path), str(prefix)], check=True, timeout=60,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    montages = []
    for start in range(0, len(target_pages), 8):
        group = target_pages[start:start + 8]
        sheet = Image.new('RGB', (1500, 1120), '#dedede')
        draw = ImageDraw.Draw(sheet)
        for position, page in enumerate(group):
            with Image.open(qa / f'main_page_{page:02d}.png') as image:
                image.thumbnail((355, 520))
                x, y = position % 4 * 375 + 10, position // 4 * 560 + 30
                sheet.paste(image, (x, y))
                draw.text((x, y - 22), f'Main page {page}', fill='black')
        path = qa / f'montage_{start + 1:02d}_{start + len(group):02d}.png'
        sheet.save(path)
        montages.append(path.relative_to(REPORT).as_posix())
    return {'renderer': 'Poppler pdftoppm 120dpi', 'document_page_count': page_count,
            'rendered_pages': target_pages,
            'single_page_pngs': [f'qa/main_page_{page:02d}.png' for page in target_pages],
            'montages': montages, 'manual_review': 'pending_main_agent_review',
            'independent_agent_review': 'pending'}


def run():
    baseline = json_read(REPORT / 'baseline.json')
    result = {'passed': False, 'nature_skills_used': False, 'full_numerical_rerun': False,
              'compile_started_by_verifier': False,
              'scope': '静态内容保护、已有完整编译结果与 PDF 核查；不代替数学证明或全文数值复跑。',
              'failures': []}
    old, new = read(BACKUP / f'{MAIN}.tex'), read(LATEX / f'{MAIN}.tex')
    result['static'] = static_checks(old, new)
    if not result['static']['passed']:
        result['failures'].append('静态编号数学/标签/图表/引用/成本边界保护检查失败')

    labels_new = aux_labels(LATEX / f'{MAIN}.aux')
    labels_old = aux_labels(PREVIOUS / f'{MAIN}.aux')
    changes = [{'label': label, 'old_value': row['value'], 'new_value': labels_new.get(label, {}).get('value')}
               for label, row in labels_old.items() if labels_new.get(label, {}).get('value') != row['value']]
    si_new, si_old = aux_labels(LATEX / f'{SI}.aux'), aux_labels(PREVIOUS / f'{SI}.aux')
    si_changes = [{'label': label, 'old_value': row['value'], 'new_value': si_new.get(label, {}).get('value')}
                  for label, row in si_old.items() if si_new.get(label, {}).get('value') != row['value']]
    result['numbering'] = {'passed': not changes and not si_changes,
                           'main_labels_checked': len(labels_old), 'supplement_labels_checked': len(si_old),
                           'parser': 'balanced braces; compare first newlabel payload group, ignore page group',
                           'main_changed': changes, 'supplement_changed': si_changes}
    if not result['numbering']['passed']:
        result['failures'].append('编译后实际标签编号发生变化')

    result['supplement_pdf'] = compare_si()
    if not result['supplement_pdf']['content_exact']:
        result['failures'].append('补充材料 PDF 内容/绘制/字体/120dpi 像素发生变化')

    allowed = {f'latex/{MAIN}.tex', f'latex/{MAIN}.pdf'}
    protected_changes = []
    for item in baseline['protected_files']:
        path = ROOT / item['file']
        current = sha(path) if path.is_file() else None
        if current != item['sha256'] and item['file'] not in allowed:
            if item['file'] == f'latex/{SI}.pdf' and result['supplement_pdf']['content_exact']:
                continue
            protected_changes.append({'file': item['file'], 'before_sha256': item['sha256'], 'after_sha256': current})
    result['protection'] = {'passed': not protected_changes, 'protected_files_checked': len(baseline['protected_files']),
                             'allowed_edits': sorted(allowed), 'unexpected_changes': protected_changes,
                             'supplement_pdf_metadata_ignored_only_after_exact_content_check': True}
    if not result['protection']['passed']:
        result['failures'].append('保护文件发生非预期变化')

    fatal = r'undefined|Missing character|Overfull|Float too large|multiply defined|^!|(?:LaTeX|Package \S+) Error:'
    log_checks = {}
    for stem in (MAIN, SI):
        text = read(LATEX / f'{stem}.log')
        errors = [line for line in text.splitlines() if re.search(fatal, line, re.I)]
        warnings = [line for line in text.splitlines() if 'Warning' in line or 'Underfull' in line]
        completed = bool(re.search(r'Output written on .*\.pdf \(\d+ pages?', text))
        log_checks[stem] = {'completed_pdf': completed, 'errors': errors, 'warnings': warnings,
                            'passed': completed and not errors and not warnings}
    biber = read(LATEX / f'{MAIN}.blg')
    biber_warnings = [line for line in biber.splitlines() if re.search(r'WARN|ERROR', line)]
    log_checks['biber'] = {'warnings_or_errors': biber_warnings,
                           'completed_bbl': 'Writing' in biber and '.bbl' in biber,
                           'passed': not biber_warnings and 'Writing' in biber and '.bbl' in biber}
    result['actual_build_logs'] = log_checks
    if not all(row['passed'] for row in log_checks.values()):
        result['failures'].append('实际编译最终日志存在异常或未完成')

    bbl_keys = sorted(set(re.findall(r'\\entry\{([^}]+)\}', read(LATEX / f'{MAIN}.bbl'))))
    expected = sorted(json_read(PREVIOUS.parent / 'build_report.json')['printed_bibliography_keys'])
    qa_seeds = []
    outside = []
    bibliography_pages = []
    with pymupdf.open(LATEX / f'{MAIN}.pdf') as document:
        page_count = len(document)
        for index, page in enumerate(document):
            text = page.get_text()
            if '参考文献' in text:
                bibliography_pages.append(index + 1)
            compact = re.sub(r'\s+', '', text)
            if any(phrase in compact for phrase in (
                '能力限制不改变', '启动最大隔离', '仅隔离策略可实施', '提高阈值保持',
                '能力上限的实施判据', '接触削减', '仅隔离与联合控制', '单靠隔离')):
                qa_seeds.append(index + 1)
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        if span['text'].strip() and not (page.rect + (-1, -1, 1, 1)).contains(pymupdf.Rect(span['bbox'])):
                            outside.append({'page': index + 1, 'text': span['text'], 'bbox': span['bbox']})
        for label in ('sec:model:strategy', 'cor:s1:qc-structure', 'sec:joint', 'eq:joint:feasibility'):
            page = int(labels_new[label]['page'])
            qa_seeds.extend([page, min(page + 1, page_count)])
    result['main_pdf'] = {'before_page_count': 45, 'actual_page_count': page_count,
                           'outside_page_text': outside, 'current_sha256': sha(LATEX / f'{MAIN}.pdf'),
                           'pagination_change_allowed': True}
    if outside:
        result['failures'].append('主稿存在文本越出 PDF 页面')
    result['bibliography'] = {'passed': bbl_keys == expected and len(bbl_keys) == 20 and bool(bibliography_pages)
                              and set(cite_keys(new)) <= set(bbl_keys),
                              'printed_count': len(bbl_keys), 'printed_keys': bbl_keys,
                              'expected_keys': expected, 'heading_pages': bibliography_pages}
    if not result['bibliography']['passed']:
        result['failures'].append('参考文献条目集合/显示完整性检查失败')
    qa_seeds.extend(bibliography_pages)
    pages = sorted({candidate for page in qa_seeds for candidate in (page - 1, page, page + 1)
                    if 1 <= candidate <= page_count})
    result['visual_review'] = render_review(LATEX / f'{MAIN}.pdf', pages, page_count)
    result['passed'] = not result['failures']
    result['acceptance_status'] = 'automated_pass_manual_pending' if result['passed'] else 'failed'
    return result


if __name__ == '__main__':
    try:
        result = run()
    except Exception as error:
        result = {'passed': False, 'error': str(error), 'traceback': traceback.format_exc(),
                  'nature_skills_used': False, 'full_numerical_rerun': False,
                  'acceptance_status': 'failed'}
    dump(REPORT / 'verification.json', result)
    print(json.dumps({key: result.get(key) for key in ('passed', 'error', 'failures', 'acceptance_status')}, ensure_ascii=False))
    sys.exit(0 if result['passed'] else 1)
