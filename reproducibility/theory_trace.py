"""核对新稿编号数学环境/证明与冻结来源，不把一致性当作证明认证。"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path
from bootstrap import dump


def environments(text):
    pattern=r'\\begin\{(theorem|lemma|proposition|corollaryn|corollary|remarkn|proof)\}(.*?)\\end\{\1\}'
    rows=[]
    for m in re.finditer(pattern,text,re.S):
        body=m.group(0)
        rows.append({'kind':m.group(1),'labels':re.findall(r'\\label\{([^}]+)\}',body),
                     'line':text[:m.start()].count('\n')+1,'body':body,
                     'sha256':hashlib.sha256(body.encode()).hexdigest()})
    return rows


def run(root: Path, output: Path, current: str) -> dict:
    source=root/'ai/threshold_control_reproducible_release_20261002/latex/flatten_curve_analysis_cn.tex'
    original=environments(source.read_text(encoding='utf-8-sig'))
    new=environments(current)
    comparisons=[]
    if len(original)!=len(new):raise RuntimeError('编号理论环境/证明数量改变，需人工核查')
    for before,after in zip(original,new):
        comparisons.append({'kind':before['kind'],'labels':before['labels'],
                'source':str(source.relative_to(root)).replace('\\','/'),
                'source_line':before['line'],'staged_line':after['line'],
                'source_sha256':before['sha256'],'staged_sha256':after['sha256'],
                'text_identical':before['body']==after['body']})
    report={'passed':all(r['text_identical'] for r in comparisons),'environments':comparisons,
            'mathematical_proof_certification':False,
            'scope':'编号环境及证明的来源/文本保护；不宣称已独立证明所有命题。数值同步仅在计算叙述、图表与非证明段落中。'}
    dump(output/'validation/theory_trace.json',report)
    if not report['passed']:raise RuntimeError('数学命题或证明发生改写，请查看 theory_trace.json')
    return report
