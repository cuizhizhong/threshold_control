"""论文/工程记录分流的独立验收；不编译，不运行任何科学入口。"""
from __future__ import annotations

import argparse
import builtins
import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import traceback
from unittest import mock

import pymupdf
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
LATEX = ROOT / 'latex'
RESULTS = ROOT / 'reproducibility/results/20261003_release_final'
MAIN = 'flatten_curve_analysis_cn'
SI = 'flatten_curve_supplement_cn'
SPECS = {
    'S2_body_resolution': ('main', r'图\ref{fig:xian:observed-fit}与三策略比较'),
    'inflection_backsubstitution': ('main', r'固定 $\beta=0.1498$，在 $\eta\in'),
    'table4_source_navigation': ('main', r'\item 注：前四项为近似值。'),
    'discussion_unified_integration': ('main', '对于边界明确的校园或厂区'),
    'SI_data_location': ('supplement', '本文件列出仅隔离控制的'),
    'S1_source_note': ('supplement', r'\item 注：数值取自本次重新计算的基准实验结果'),
    'S2_diagnosis_resolved': ('supplement', r'\item 注：观测窗口为'),
    'S3_source_note': ('supplement', r'\item 注：数值取自统一积分设置下重新计算的西安阈值敏感性结果'),
}


def read(path):
    return Path(path).read_text(encoding='utf-8-sig')


def load(path):
    return json.loads(read(path))


def dump(path, payload):
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def text_sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def envs(text, kinds):
    names = '|'.join(re.escape(kind) for kind in kinds)
    return [m.group(0) for m in re.finditer(rf'\\begin\{{({names})\}}.*?\\end\{{\1\}}', text, re.S)]


def labels(text):
    return re.findall(r'\\label\{([^}]+)\}', text)


def citations(text):
    return sorted({key.strip() for match in re.findall(
        r'\\(?:cite|parencite|textcite|autocite|footcite|nocite)\*?(?:\[[^\]]*\])*\{([^}]+)\}', text)
        for key in match.split(',')})


def braced(text, offset):
    while offset < len(text) and text[offset].isspace():
        offset += 1
    if text[offset:offset+1] != '{':
        raise ValueError('缺少 AUX 花括号组')
    start, depth = offset + 1, 1
    offset += 1
    while offset < len(text):
        if text[offset] == '\\':
            offset += 2
            continue
        if text[offset] == '{':
            depth += 1
        elif text[offset] == '}':
            depth -= 1
            if depth == 0:
                return text[start:offset], offset + 1
        offset += 1
    raise ValueError('AUX 花括号组未闭合')


def aux(path):
    text, result = read(path), {}
    for match in re.finditer(r'\\newlabel\s*', text):
        name, end = braced(text, match.end())
        payload, _ = braced(text, end)
        number, end = braced(payload, 0)
        page, _ = braced(payload, end)
        if name in result:
            raise ValueError('重复 AUX 标签 ' + name)
        result[name] = {'number': number, 'page': page}
    return result


def forbidden(*args, **kwargs):
    raise AssertionError('出版文案回归禁止 IO、科学入口与整稿生成入口')


def pure_regression():
    source = ROOT / 'reproducibility/paper_sync.py'
    spec = importlib.util.spec_from_file_location('audit_paper_sync', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    reference = load(RESULTS / 'xian/reference.json')
    difference = load(RESULTS / 'xian/S2_difference.json')
    supplemental = load(RESULTS / 'population/supplementary_anchors.json')
    arguments = (reference, difference, supplemental)
    saved = copy.deepcopy(arguments)
    sentinel = copy.deepcopy(difference)
    for key in ('legacy_fit', 'legacy_fit_40_cumulative', 'legacy_event_40_cumulative',
                'unified_at_legacy_I0_40_cumulative', 'early_tolerance', 'explanation'):
        sentinel[key] = 'REMOVED_LEGACY_SENTINEL'
    changed = copy.deepcopy(difference)
    changed['reference_tolerance_differences']['cum_total_infections'] *= 10
    with mock.patch.object(module, 'prepare_manuscript', forbidden), \
         mock.patch.object(module, '_json', forbidden), mock.patch.object(module, '_csv', forbidden), \
         mock.patch.object(Path, 'read_text', forbidden), mock.patch.object(Path, 'read_bytes', forbidden), \
         mock.patch.object(Path, 'write_text', forbidden), mock.patch.object(Path, 'write_bytes', forbidden), \
         mock.patch.object(Path, 'open', forbidden), mock.patch.object(Path, 'mkdir', forbidden), \
         mock.patch.object(builtins, 'open', forbidden), mock.patch.object(subprocess, 'run', forbidden):
        prose = module.publication_prose(*arguments)
        without_history = module.publication_prose(reference, sentinel, supplemental)
        tightened = module.publication_prose(reference, changed, supplemental)
    result = {
        'passed': set(prose) == set(SPECS) and prose == without_history and arguments == saved
                  and [k for k in prose if prose[k] != tightened[k]] == ['S2_diagnosis_resolved'],
        'keys': list(prose), 'eight_keys_exact': set(prose) == set(SPECS),
        'input_objects_unchanged': arguments == saved, 'legacy_numbers_not_consumed': prose == without_history,
        'tightened_evidence_only_changes_S2_note': [k for k in prose if prose[k] != tightened[k]],
        'io_and_whole_manuscript_entry_mocked_to_fail': True,
        'scientific_modules_imported': [k for k in sys.modules if k in ('xian', 'joint', 'population', 'c0')],
        'input_sha256': {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in (
            RESULTS/'xian/reference.json', RESULTS/'xian/S2_difference.json', RESULTS/'population/supplementary_anchors.json')},
        'no_refit_no_integration_no_prepare_manuscript': True,
        'source_sha256': sha(source),
    }
    if result['scientific_modules_imported']:
        result['passed'] = False
    return prose, result


def static_checks(baseline, backup, prose):
    documents = {'main': MAIN, 'supplement': SI}
    old = {role: read(backup/'latex'/f'{stem}.tex') for role, stem in documents.items()}
    new = {role: read(LATEX/f'{stem}.tex') for role, stem in documents.items()}
    expected = copy.deepcopy(old)
    changes = []
    for key, (role, start) in SPECS.items():
        selected = [line for line in old[role].splitlines() if line.startswith(start)]
        if len(selected) != 1:
            raise ValueError(f'{key} 修改前定位不唯一: {len(selected)}')
        old_line = selected[0]
        if key == 'discussion_unified_integration':
            prefix = old_line[:old_line.index('当前联合控制的数值结果')]
            new_line = prefix + prose[key]
        else:
            new_line = prose[key]
        expected[role] = expected[role].replace(old_line, new_line, 1)
        changes.append({'key': key, 'document': role, 'old': old_line, 'new': new_line,
                        'present_exactly_once': new[role].count(new_line) == 1})
    by_document = {}
    for role in documents:
        numbered_old = envs(old[role], ('equation', 'align', 'gather', 'multline', 'eqnarray'))
        numbered_new = envs(new[role], ('equation', 'align', 'gather', 'multline', 'eqnarray'))
        tables_old, tables_new = envs(old[role], ('table',)), envs(new[role], ('table',))
        tabular_old = envs(old[role], ('tabular', 'tabular*', 'tabularx'))
        tabular_new = envs(new[role], ('tabular', 'tabular*', 'tabularx'))
        # 注释之外的表格布局语句和数据行必须逐字保持；只剔除 tablenotes 文案。
        structural_old = [re.sub(r'\\begin\{tablenotes\}.*?\\end\{tablenotes\}', '<NOTES>', block, flags=re.S) for block in tables_old]
        structural_new = [re.sub(r'\\begin\{tablenotes\}.*?\\end\{tablenotes\}', '<NOTES>', block, flags=re.S) for block in tables_new]
        lines_old, lines_new = old[role].splitlines(), new[role].splitlines()
        diff = [{'opcode': kind, 'old_lines': [i+1, j], 'new_lines': [a+1, b]}
                for kind, i, j, a, b in difflib.SequenceMatcher(a=lines_old, b=lines_new, autojunk=False).get_opcodes() if kind != 'equal']
        row = {'only_expected_prose_changes': expected[role] == new[role], 'diff_hunks': diff,
               'label_order_exact': labels(old[role]) == labels(new[role]), 'label_count': len(labels(new[role])),
               'numbered_math_exact': numbered_old == numbered_new, 'numbered_math_count': len(numbered_new),
               'all_proofs_exact': envs(old[role], ('proof',)) == envs(new[role], ('proof',)),
               'all_theorem_statements_exact': envs(old[role], ('theorem', 'lemma', 'proposition', 'corollaryn', 'remarkn')) == envs(new[role], ('theorem', 'lemma', 'proposition', 'corollaryn', 'remarkn')),
               'table_count': len(tables_new), 'tabular_data_and_styles_exact': tabular_old == tabular_new,
               'table_structure_outside_notes_exact': structural_old == structural_new,
               'figure_environments_exact': envs(old[role], ('figure', 'figure*')) == envs(new[role], ('figure', 'figure*')),
               'figure_count': len(envs(new[role], ('figure', 'figure*'))),
               'citation_keys_exact': citations(old[role]) == citations(new[role]),
               'citation_keys': citations(new[role]), 'bibliography_print_count': new[role].count(r'\printbibliography')}
        row['passed'] = all(row[k] for k in ('only_expected_prose_changes', 'label_order_exact', 'numbered_math_exact',
            'all_proofs_exact', 'all_theorem_statements_exact', 'tabular_data_and_styles_exact',
            'table_structure_outside_notes_exact', 'figure_environments_exact', 'citation_keys_exact'))
        by_document[role] = row
    protected_paragraphs = {
        'eta_finite_scale_test': '由首次积分，$i_0$ 通过',
        'six_population_science': r'固定 $\theta=0.002$，取',
        'unfavorable_restore_Re': '在西安重构的这一终点',
        'empty_clearance_region': '在当前数值范围内，成本、时长和累计感染边界',
    }
    scientific = {}
    for name, start in protected_paragraphs.items():
        block = next((line for line in old['main'].splitlines() if start in line), None)
        scientific[name] = {'found_before': block is not None, 'retained_exact': bool(block and block in new['main'])}
    capacity_end = old['main'].index(r'\label{sec:xian}')
    capacity_new_end = new['main'].index(r'\label{sec:xian}')
    capacity_exact = old['main'][:capacity_end] == new['main'][:capacity_new_end]
    count_checks = by_document['main']['table_count'] == 4 and by_document['supplement']['table_count'] == 3 \
        and by_document['main']['figure_count'] == 20 and by_document['main']['bibliography_print_count'] == 1 \
        and by_document['supplement']['bibliography_print_count'] == 0
    result = {'passed': all(row['passed'] for row in by_document.values()) and capacity_exact and count_checks
                        and all(row['retained_exact'] for row in scientific.values()) and all(row['present_exactly_once'] for row in changes),
              'documents': by_document, 'whitelist_count': len(changes), 'whitelist': changes,
              'pre_xian_capacity_additions_and_all_prior_content_exact': capacity_exact,
              'scientific_findings_and_repetition_retained': scientific}
    return result


def protection(baseline):
    allowed, failures, changed = set(baseline['allowed_existing_changes']), [], []
    figures = []
    for item in baseline['protected_files']:
        path = ROOT/item['file']
        current = sha(path) if path.is_file() else None
        if item['file'].startswith('latex/figures/') and path.suffix.lower() == '.pdf':
            figures.append({'file': item['file'], 'passed': current == item['sha256']})
        if current != item['sha256']:
            record = {'file': item['file'], 'before_sha256': item['sha256'], 'after_sha256': current}
            changed.append(record)
            if item['file'] not in allowed:
                failures.append(record)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    return {'passed': not failures and len(figures) == 20 and all(row['passed'] for row in figures) and head == baseline['head'],
            'protected_count': len(baseline['protected_files']), 'allowed_existing_changes': sorted(allowed),
            'changed_files': changed, 'unexpected_changes': failures,
            'formal_figure_count': len(figures), 'formal_figures': figures, 'git_head_unchanged': head == baseline['head']}


def audit_migration(path):
    if not path.is_file():
        return {'passed': False, 'file': str(path), 'error': '新复现说明尚不存在'}
    text = read(path)
    compact = re.sub(r'\s+', '', text)
    difference = load(RESULTS/'xian/S2_difference.json')
    reference = load(RESULTS/'xian/reference.json')
    required = tuple(str(difference[key]) for key in ('legacy_fit_40_cumulative', 'legacy_event_40_cumulative',
        'unified_at_legacy_I0_40_cumulative', 'unified_refit_40_cumulative')) + (
        str(difference['legacy_fit']['I0']), str(reference['fit']['I0']), '1e-7', '1e-5', '1e-8', '1e-4')
    checks = {token: token in compact for token in required}
    checks['float_backsub_2.22e-16'] = bool(re.search(r'2\.22(?:[eE]-16|\\times10\^\{-16\}|[×x]10(?:\^?\(?-16\)?))', compact))
    checks['distinct_fit_and_solver_changes'] = '重新拟合' in text and ('两个' in text or '分别' in text or '两步' in text)
    checks['S2_scope_limited'] = '清零' in text and '固定' in text and ('不' in text or '未' in text)
    return {'passed': all(checks.values()), 'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'checks': checks}


def complete_checks(backup):
    numbering = {}
    for stem in (MAIN, SI):
        before, after = aux(backup/'latex'/f'{stem}.aux'), aux(LATEX/f'{stem}.aux')
        differences = [{'label': key, 'before': value['number'], 'after': after.get(key, {}).get('number')}
                       for key, value in before.items() if value['number'] != after.get(key, {}).get('number')]
        numbering[stem] = {'passed': not differences and set(before) == set(after), 'checked_labels': len(before), 'differences': differences}
    logs = {}
    fatal = r'undefined|Missing character|Overfull|Float too large|multiply defined|^!|(?:LaTeX|Package \S+) Error:'
    for stem in (MAIN, SI):
        text = read(LATEX/f'{stem}.log')
        errors = [line for line in text.splitlines() if re.search(fatal, line, re.I)]
        warnings = [line for line in text.splitlines() if 'Warning' in line or 'Underfull' in line]
        complete = bool(re.search(r'Output written on .*\.pdf \(\d+ pages?', text))
        logs[stem] = {'passed': complete and not errors and not warnings, 'complete_pdf': complete, 'errors': errors, 'warnings': warnings}
    blg = read(LATEX/f'{MAIN}.blg')
    warnings = [line for line in blg.splitlines() if re.search(r'WARN|ERROR', line)]
    logs['biber'] = {'passed': not warnings and 'Writing' in blg and '.bbl' in blg, 'warnings': warnings}
    keys = sorted(set(re.findall(r'\\entry\{([^}]+)\}', read(LATEX/f'{MAIN}.bbl'))))
    expected = citations(read(backup/'latex'/f'{MAIN}.tex'))
    documents = {}
    seeds, bibliography_pages = [], []
    phrases = ('统一归一化方程', '将解析拐点时刻回代', '不表示已证明任意参数下', '尚未开展西安参数下的系统计算')
    for stem in (MAIN, SI):
        outside, placeholders = [], []
        with pymupdf.open(LATEX/f'{stem}.pdf') as document:
            count = len(document)
            for index, page in enumerate(document):
                text = page.get_text()
                compact = re.sub(r'\s+', '', text)
                if stem == MAIN:
                    if any(phrase in compact for phrase in phrases):
                        seeds.append(index+1)
                    if '参考文献' in text:
                        bibliography_pages.append(index+1)
                if '[?]' in text or '??' in text:
                    placeholders.append(index+1)
                for block in page.get_text('dict')['blocks']:
                    for line in block.get('lines', []):
                        for span in line.get('spans', []):
                            if span['text'].strip() and not (page.rect+(-1,-1,1,1)).contains(pymupdf.Rect(span['bbox'])):
                                outside.append({'page': index+1, 'text': span['text'], 'bbox': span['bbox']})
        documents[stem] = {'passed': not outside and not placeholders, 'page_count': count,
                           'sha256': sha(LATEX/f'{stem}.pdf'), 'outside_page_text': outside, 'unresolved_placeholders_pages': placeholders}
    for key in ('tab:xian_initial_fit', 'tab:dom:thresholds'):
        seeds.append(int(aux(LATEX/f'{MAIN}.aux')[key]['page']))
    count = documents[MAIN]['page_count']
    detail_pages = sorted({p for seed in seeds+bibliography_pages for p in (seed-1,seed,seed+1) if 1 <= p <= count})
    bibliography = {'passed': keys == expected and len(keys) == 20 and bool(bibliography_pages),
                    'printed_count': len(keys), 'keys': keys, 'heading_pages': bibliography_pages}
    return {'passed': all(row['passed'] for row in numbering.values()) and all(row['passed'] for row in logs.values())
                      and all(row['passed'] for row in documents.values()) and bibliography['passed'],
            'actual_numbering': numbering, 'build_logs': logs, 'documents': documents,
            'bibliography': bibliography, 'main_detail_pages': detail_pages}


def render(documents, detail_pages):
    poppler = shutil.which('pdftoppm')
    if not poppler:
        raise FileNotFoundError('找不到 Poppler pdftoppm')
    qa = REPORT/'qa'
    qa.mkdir(exist_ok=True)
    montages, images = [], {}
    for stem, prefix in ((MAIN, 'main'), (SI, 'supplement')):
        count = documents[stem]['page_count']
        subprocess.run([poppler, '-r', '120', '-png', str(LATEX/f'{stem}.pdf'), str(qa/prefix)],
                       check=True, timeout=180, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        files = sorted(qa.glob(prefix+'-*.png'))
        if len(files) != count:
            raise ValueError(f'{prefix} 渲染页数 {len(files)} != {count}')
        images[prefix] = [str(path.relative_to(REPORT)).replace('\\', '/') for path in files]
        for start in range(0, count, 8):
            group = files[start:start+8]
            sheet = Image.new('RGB', (1500, 1120), '#dedede')
            draw = ImageDraw.Draw(sheet)
            for i, path in enumerate(group):
                with Image.open(path) as image:
                    image.thumbnail((355, 520))
                    x, y = i%4*375+10, i//4*560+30
                    sheet.paste(image, (x,y))
                    draw.text((x,y-22), f'{prefix}: page {start+i+1}', fill='black')
            target = qa/f'{prefix}_overview_{start+1:02d}_{start+len(group):02d}.png'
            sheet.save(target)
            montages.append(str(target.relative_to(REPORT)).replace('\\', '/'))
    return {'renderer': 'Poppler pdftoppm 120dpi', 'all_document_pages_rendered': images,
            'overview_montages': montages, 'main_detail_pages': detail_pages,
            'supplement_detail_pages': list(range(1,documents[SI]['page_count']+1)),
            'independent_manual_review': 'pending', 'root_manual_review': 'pending'}


def run(args):
    baseline = load(REPORT/'baseline.json')
    backup = ROOT/baseline['backup']
    result = {'passed': False, 'nature_skills_used': False, 'full_numerical_rerun': False,
              'compile_started_by_verifier': False, 'failures': [],
              'scope': '出版文案/表体/历史保护及已有编译、页面核查；不新增拟合积分或收敛实验。'}
    prose, result['prose_regression'] = pure_regression()
    result['static'] = static_checks(baseline, backup, prose)
    result['protection'] = protection(baseline)
    result['audit_migration'] = audit_migration((ROOT/args.audit_notes).resolve())
    fields = ('prose_regression', 'static', 'protection', 'audit_migration')
    if args.phase == 'complete':
        result['compiled'] = complete_checks(backup)
        fields += ('compiled',)
        result['visual_review'] = render(result['compiled']['documents'], result['compiled']['main_detail_pages'])
    result['failures'] = [key for key in fields if not result[key]['passed']]
    result['passed'] = not result['failures']
    result['acceptance_status'] = ('automated_pass_manual_pending' if args.phase == 'complete' else 'static_pass_build_pending') \
        if result['passed'] else 'failed'
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('static','complete'), default='static')
    parser.add_argument('--audit-notes', default='reproducibility/manuscript_audit_notes.md')
    args = parser.parse_args()
    try:
        result = run(args)
    except Exception as exc:
        result = {'passed': False, 'error': str(exc), 'traceback': traceback.format_exc(),
                  'nature_skills_used': False, 'full_numerical_rerun': False,
                  'compile_started_by_verifier': False, 'acceptance_status': 'failed'}
    target = REPORT/('verification.json' if args.phase == 'complete' else 'verification_static.json')
    dump(target, result)
    print(json.dumps({key: result.get(key) for key in ('passed','failures','error','acceptance_status')}, ensure_ascii=False))
    sys.exit(0 if result['passed'] else 1)
