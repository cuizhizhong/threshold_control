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
    from manuscript_version import load_version
    version = load_version(root)
    source=(version['_directory']/version['documents']['main']['file'] if version else
            root/'joint_control/threshold_control_reproducible_release_20261002/latex/flatten_curve_analysis_cn.tex')
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
            'approved_manuscript_version':version['version'] if version else 'frozen_20261002',
            'mathematical_proof_certification':False,
            'scope':'与明确批准版本逐环境核对，新增命题须先经局部审阅纳入受控来源；文本保护不宣称独立证明认证。数值同步不得改写证明。'}
    dump(output/'validation/theory_trace.json',report)
    if not report['passed']:raise RuntimeError('数学命题或证明发生改写，请查看 theory_trace.json')
    return report
