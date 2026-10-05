#!/usr/bin/env python3
"""Propose exact textual edits in a NEW directory; never write to the source.

This is an editing utility, not a clinical calibration or epidemic simulation.
UTF-8/BOM and CRLF/LF are supported. Ambiguous or changed anchors are not guessed.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys

BUNDLE = Path(__file__).resolve().parents[1]

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def normalize(text: str) -> str:
    return text.replace('\r\n', '\n').replace('\r', '\n')

def environments(text: str, names: tuple[str, ...]) -> list[tuple[str, str]]:
    pattern = r'\\begin\{(' + '|'.join(re.escape(n) for n in names) + r')\}.*?\\end\{\1\}'
    return [(m.group(1), m.group(0)) for m in re.finditer(pattern, text, re.S)]

def propose(source: Path, out: Path) -> int:
    source = source.expanduser().resolve()
    out = out.expanduser().resolve()
    if not source.is_file():
        raise ValueError(f'不存在源文件: {source}')
    if out.exists():
        raise ValueError('输出目录已存在。请提供一个全新的目录，避免覆盖先前工作。')
    # Source can never be underneath the newly created output directory.
    if out == source or out in source.parents:
        raise ValueError('输出目录不能包含源文件。')
    raw = source.read_bytes()
    text = normalize(raw.decode('utf-8-sig'))
    manifest = json.loads((BUNDLE / 'merge_manifest.json').read_text(encoding='utf-8'))
    report = {
        'operation': 'exact editing proposal only',
        'source': str(source), 'source_sha256': sha(raw),
        'source_git_blob_sha': hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),
        'reference_commit': manifest['reference_commit'],
        'reference_blob': manifest['reference_main_blob_sha'],
        'scientific_computation_run': False, 'source_modified': False,
        'matches': [], 'status': 'anchor_check',
    }
    operations = []
    for item in manifest['operations']:
        old = normalize((BUNDLE/item['before_file']).read_text(encoding='utf-8')).strip()
        new = normalize((BUNDLE/item['after_file']).read_text(encoding='utf-8')).strip()
        count = text.count(old)
        report['matches'].append({'id':item['id'],'section':item['section'],'count':count})
        operations.append((old, new))
    out.mkdir(parents=True, exist_ok=False)
    if any(m['count'] != 1 for m in report['matches']):
        report['status'] = 'stopped: non-unique or missing anchors; no candidate created'
        (out/'matching_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(report['status'])
        return 2
    changed = text
    for old,new in operations:
        if changed.count(old) != 1:
            raise RuntimeError('早先替换影响了后续唯一锚点；停止，不写候选主稿。')
        changed = changed.replace(old,new,1)
    envs = ('equation','align','gather','multline','theorem','lemma','proposition','corollaryn','remarkn','proof','figure','table')
    old_labels=re.findall(r'\\label\{([^}]+)\}',text)
    new_labels=re.findall(r'\\label\{([^}]+)\}',changed)
    preservation={
        'all_protected_environments_identical':environments(text,envs)==environments(changed,envs),
        'label_sequence_identical':old_labels==new_labels,
        'old_label_count':len(old_labels),'new_label_count':len(new_labels),
        'source_bytes_unchanged':source.read_bytes()==raw,
    }
    report['preservation']=preservation
    if not all(preservation[k] for k in ('all_protected_environments_identical','label_sequence_identical','source_bytes_unchanged')):
        report['status']='stopped: preservation check failed; no candidate created'
        (out/'matching_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(report['status'])
        return 3
    newline='\r\n' if b'\r\n' in raw else '\n'
    encoded=changed.replace('\n',newline).encode('utf-8')
    if raw.startswith(b'\xef\xbb\xbf'):
        encoded=b'\xef\xbb\xbf'+encoded
    candidate=out/'flatten_curve_analysis_cn.candidate.tex'
    candidate.write_bytes(encoded)
    diff=''.join(difflib.unified_diff(text.splitlines(True),changed.splitlines(True),fromfile='before/flatten_curve_analysis_cn.tex',tofile='candidate/flatten_curve_analysis_cn.tex'))
    (out/'proposed_changes.diff').write_text(diff,encoding='utf-8')
    report.update({'status':'candidate generated for review only',
        'candidate':candidate.name,'candidate_sha256':sha(encoded),
        'bibliography_merged':False,'active_version_approved':False,
        'full_manuscript_compiled':False})
    (out/'matching_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'已生成独立候选：{candidate}\n源文件未改；未合并bib、未批准活动版本、未编译全文。')
    return 0

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    try:
        return propose(args.source,args.out)
    except (OSError,UnicodeError,ValueError,RuntimeError) as exc:
        print(f'停止：{exc}',file=sys.stderr)
        return 1
if __name__=='__main__':
    sys.exit(main())
