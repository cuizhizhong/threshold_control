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

from text_identity import content_sha256, require_policy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'paper' / 'tools'))
import statement_diff as sd

DOCS = ['paper/flatten_curve_analysis_cn.tex', 'paper/flatten_curve_supplement_cn.tex']
ENV = '|'.join(sd.ENVS)
MACROS = 'paper/generated/nr_numbers.tex'


def generated_macro_identity(old, current, baseline):
    """两份文本都须匹配独立基线的内容身份；raw 快照仅保留为原始来源。"""
    require_policy(baseline)
    expected = baseline['text_identity']['content_sha256'][MACROS]
    old_digest, current_digest = content_sha256(old), content_sha256(current)
    return {
        'unchanged': (old.replace(b'\r\n', b'\n') == current.replace(b'\r\n', b'\n')
                      and old_digest == expected and current_digest == expected),
        'baseline_raw_sha256': baseline['files'][MACROS],
        'current_raw_sha256': hashlib.sha256(current).hexdigest(),
        'baseline_content_sha256': expected,
        'base_git_content_sha256': old_digest,
        'current_content_sha256': current_digest,
        'policy': baseline['text_identity']['policy'],
    }


def norm(text):
    return re.sub(r'\s+', '', text)


def table_reference_norm(text):
    """仅登记两个补充命题的引用前缀；其余内容按原去空白判据保持一致。"""
    text = norm(text)
    text = text.replace(r'、补充命题\ref{prop:contact-effects}',
                        r'、\ref{prop:contact-effects}')
    return text.replace(r'补充命题\ref{prop:s1:lambda-sensitivity}',
                        r'命题\ref{prop:s1:lambda-sensitivity}')


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
    old_tables_refs = Counter(table_reference_norm(body) for body in old_tables.elements())
    new_tables_refs = Counter(table_reference_norm(body) for body in new_tables.elements())
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
    macros = ROOT / MACROS
    macro_old = subprocess.check_output(['git', 'show', args.base + ':' + MACROS], cwd=ROOT)
    baseline = json.loads((ROOT / 'paper/revision_notes/NEW_4g_baseline.json').read_text(encoding='utf-8'))
    macro_identity = generated_macro_identity(macro_old, macros.read_bytes(), baseline)
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
                   'added_exact_blocks': sum((new_tables - old_tables).values()),
                   'reference_wording_only': old_tables != new_tables and old_tables_refs == new_tables_refs,
                   'missing_after_registered_reference_prefixes': sum((old_tables_refs - new_tables_refs).values()),
                   'added_after_registered_reference_prefixes': sum((new_tables_refs - old_tables_refs).values()),
                   'registered_reference_labels': ['prop:contact-effects', 'prop:s1:lambda-sensitivity'],
                   'old_exact_block_deltas': list((old_tables - new_tables).elements()),
                   'new_exact_block_deltas': list((new_tables - old_tables).elements())},
        'labels': {'lost': sorted(ol.keys() - nl.keys()), 'added': sorted(nl.keys() - ol.keys()),
                   'duplicates': sorted(k for k, count in nl.items() if count > 1)},
        'figure_occurrences_unchanged': old_assets == new_assets,
        'figure_assets': images,
        'generated_number_macros_unchanged': macro_identity['unchanged'],
        'generated_number_macros_raw_sha256': macro_identity['current_raw_sha256'],
        'generated_number_macros_content_identity': macro_identity,
        'current_label_numbers': {k: aux[k] for k in sorted(nl) if k in aux},
    }
    report['static_pass'] = (
        os_ == ns and old_proofs == new_proofs and old_tables_refs == new_tables_refs
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
