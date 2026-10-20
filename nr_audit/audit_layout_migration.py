"""只读核对 NEW-4g 的跨文件迁移，不运行科学计算。"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'paper' / 'tools'))
import statement_diff as sd

DOCS = ['paper/flatten_curve_analysis_cn.tex', 'paper/flatten_curve_supplement_cn.tex']
ENV = '|'.join(sd.ENVS)


def norm(text):
    return re.sub(r'\s+', '', text)


def environments(text, names):
    return re.findall(r'\\begin\{(' + names + r')\}([\s\S]*?)\\end\{\1\}', text)


def statements(text):
    result = {}
    for kind, body in environments(text, ENV):
        labels = re.findall(r'\\label\{([^}]+)\}', body)
        if labels:
            result[labels[0]] = {'kind': kind, 'text': norm(body)}
    return result


def assets(text):
    return Counter(re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', text))


def aux_labels(path):
    if not path.exists():
        return {}
    result = {}
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        match = re.match(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}', line)
        if match:
            result[match[1]] = {'number': match[2], 'page': match[3]}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='83ddcdb')
    parser.add_argument('--out', default='paper/revision_notes/NEW_4g_migration_audit.json')
    args = parser.parse_args()
    old = '\n'.join(sd.expand_spec(args.base + ':' + p) for p in DOCS)
    new = '\n'.join(sd.expand_spec(str(ROOT / p)) for p in DOCS)
    os_, ns = statements(old), statements(new)
    old_proofs = Counter(norm(body) for _, body in environments(old, 'proof'))
    new_proofs = Counter(norm(body) for _, body in environments(new, 'proof'))
    old_tables = Counter(norm(body) for _, body in environments(old, r'tabular|tabularx|tabular\*'))
    new_tables = Counter(norm(body) for _, body in environments(new, r'tabular|tabularx|tabular\*'))
    ol = Counter(re.findall(r'\\label\{([^}]+)\}', old))
    nl = Counter(re.findall(r'\\label\{([^}]+)\}', new))
    old_assets, new_assets = assets(old), assets(new)
    images = {}
    for name in old_assets:
        candidates = [ROOT / 'paper' / name, ROOT / 'paper/figures' / name]
        if not Path(name).suffix:
            candidates = [p.with_suffix(ext) for p in candidates for ext in ['.pdf', '.png', '.jpg']]
        found = next((p for p in candidates if p.is_file()), None)
        if found:
            rel = found.relative_to(ROOT).as_posix()
            prior = subprocess.check_output(['git', 'show', args.base + ':' + rel], cwd=ROOT)
            current = found.read_bytes()
            images[rel] = {'sha256': hashlib.sha256(current).hexdigest(), 'unchanged': prior == current}
        else:
            images[name] = {'unchanged': False, 'error': 'asset not found'}
    macros = ROOT / 'paper/generated/nr_numbers.tex'
    macro_old = subprocess.check_output(['git', 'show', args.base + ':paper/generated/nr_numbers.tex'], cwd=ROOT)
    baseline = json.loads((ROOT / 'paper/revision_notes/NEW_4g_baseline.json').read_text(encoding='utf-8'))
    macro_raw_sha = hashlib.sha256(macros.read_bytes()).hexdigest()
    aux = {}
    for doc in DOCS:
        aux.update(aux_labels((ROOT / doc).with_suffix('.aux')))
    report = {
        'base': args.base,
        'scope': 'static manuscript migration only; no scientific solve or scan',
        'statements': {'old_count': len(os_), 'new_count': len(ns),
                       'lost': sorted(os_.keys() - ns.keys()), 'added': sorted(ns.keys() - os_.keys()),
                       'changed': [k for k in os_.keys() & ns.keys() if os_[k] != ns[k]]},
        'proofs': {'old_count': sum(old_proofs.values()), 'new_count': sum(new_proofs.values()),
                   'missing_exact_blocks': sum((old_proofs - new_proofs).values()),
                   'added_exact_blocks': sum((new_proofs - old_proofs).values())},
        'tables': {'old_count': sum(old_tables.values()), 'new_count': sum(new_tables.values()),
                   'missing_exact_blocks': sum((old_tables - new_tables).values()),
                   'added_exact_blocks': sum((new_tables - old_tables).values())},
        'labels': {'lost': sorted(ol.keys() - nl.keys()), 'added': sorted(nl.keys() - ol.keys()),
                   'duplicates': sorted(k for k, count in nl.items() if count > 1)},
        'figure_occurrences_unchanged': old_assets == new_assets,
        'figure_assets': images,
        'generated_number_macros_unchanged': (
            macro_old.replace(b'\r\n', b'\n') == macros.read_bytes().replace(b'\r\n', b'\n')
            and baseline['files']['paper/generated/nr_numbers.tex'] == macro_raw_sha),
        'generated_number_macros_raw_sha256': macro_raw_sha,
        'current_label_numbers': {k: aux[k] for k in sorted(nl) if k in aux},
    }
    report['static_pass'] = (
        os_ == ns and old_proofs == new_proofs and old_tables == new_tables
        and not report['labels']['lost'] and not report['labels']['duplicates']
        and old_assets == new_assets and all(a['unchanged'] for a in images.values())
        and report['generated_number_macros_unchanged'])
    dest = ROOT / args.out
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['static_pass', 'statements', 'proofs', 'tables', 'labels',
                                            'figure_occurrences_unchanged', 'generated_number_macros_unchanged']},
                     ensure_ascii=False))
    return 0 if report['static_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
