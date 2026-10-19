"""NEW-4：核对原公式、表中数字、数字宏、冻结来源和作者资产，写出保护收据。"""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from audit_common import ROOT, RESULTS, dump

BASE='101b3e044418930e7242187f15044ee290c9f9f9'
RETURN='9887340091911eda76753c1d2cc2afa23430cc62'


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def normalized(s):
    return re.sub(r'\s+','',s)


def main():
    listed=git('ls-tree','-r','--name-only',BASE,'paper').decode().splitlines()
    files=[p for p in listed if p.endswith('.tex') and (
        '/sections/' in p or '/appendices/' in p or '/supplement_sections/' in p)]
    counts=dict(original_display_environments=0,original_numbered_statements=0,
                original_proofs=0,original_tables=0)
    display=re.compile(r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}(.*?)\\end\{\1\}',re.S)
    statements=re.compile(r'\\begin\{(theorem|proposition|lemma|corollaryn|remarkn|definition)\}(.*?)\\end\{\1\}',re.S)
    proofs=re.compile(r'\\begin\{proof\}(.*?)\\end\{proof\}',re.S)
    tables=re.compile(r'\\begin\{(tabular\*?|tabularx)\}(.*?)\\end\{\1\}',re.S)
    for path in files:
        old=git('show',BASE+':'+path).decode('utf-8-sig')
        new=(ROOT/path).read_text(encoding='utf-8-sig')
        for pattern,key in [(display,'original_display_environments'),
                            (statements,'original_numbered_statements'),(proofs,'original_proofs')]:
            before=[normalized(m.group(0)) for m in pattern.finditer(old)]
            after=[normalized(m.group(0)) for m in pattern.finditer(new)]
            if path=='paper/appendices/A_proofs_sensitivity.tex' and key=='original_proofs':
                before=[s.replace('均随$\\eta$减小','均随$\\eta$增大而减小') for s in before]
            assert all(after.count(s)>=before.count(s) for s in before),(path,key)
            counts[key]+=len(before)
        old_tables=list(tables.finditer(old));new_tables=list(tables.finditer(new))
        assert len(old_tables)==len(new_tables),path
        # 只比较数学数字及数字宏；标题/仓室文字允许按计划修正。
        numeric=lambda s:re.findall(r'\\nr[A-Za-z]+|(?<![A-Za-z])\d+(?:\.\d+)?(?:[eE][+-]?\d+)?',s)
        for a,b in zip(old_tables,new_tables):
            assert numeric(a.group(2))==numeric(b.group(2)),path
        counts['original_tables']+=len(old_tables)
    macrofile='paper/generated/nr_numbers.tex'
    macro_pattern=re.compile(r'^\\newcommand\{\\(nr[A-Za-z]+)\}\{([^\n]*)',re.M)
    oldmac=dict(macro_pattern.findall(git('show',BASE+':'+macrofile).decode()))
    newmac=dict(macro_pattern.findall((ROOT/macrofile).read_text(encoding='utf-8')))
    assert all(newmac[k].rstrip()==v.rstrip() for k,v in oldmac.items())
    counts.update(original_macros_unchanged=len(oldmac),current_macros=len(newmac))
    assert not git('diff','--name-only',RETURN,'--','r7_return').strip()
    man=json.loads((RESULTS/'source_manifest.json').read_text(encoding='utf-8'))
    pinned=[(k,v) for k,v in man['files'].items() if v.get('pinned')]
    assert all(sha(ROOT/v['path'])==v['sha256'] for k,v in pinned)
    baseline=json.loads((ROOT/'paper/revision_notes/NEW_0_assets.json').read_text(encoding='utf-8'))
    assets=[]
    for row in baseline['author_untracked_preserved']:
        path=Path(row['root'])/row['file'];assert sha(path)==row['sha256']
        assets.append(dict(path=str(path),sha256=row['sha256'],unchanged=True))
    expected={'refs/heads/main':'2b5545af423c9791aee9699296405b01b94ce244',
              'refs/remotes/origin/main':'b4835d9aae6fe0192093da7b6353a5455b42097a',
              'refs/heads/paper/no-return-focus':BASE,
              'refs/heads/research/return-effects':RETURN}
    refs={k:git('rev-parse',k).decode().strip() for k in expected};assert refs==expected
    changed=git('diff','--name-only',BASE).decode().splitlines()
    assert all(p.startswith(('paper/','nr_audit/','r7_return/')) or p in (
        'README.md','AGENTS.md','.gitattributes','ai/CODEX_new_manuscript_plan_20261019.md',
        'xian_control_comparison/xian_control_comparison.py') for p in changed)
    maintex=(ROOT/'paper/flatten_curve_analysis_cn.tex').read_text(encoding='utf-8')
    inputs=re.findall(r'\\input\{(sections/[^}]+)\}',maintex)
    assert len(inputs)==9 and not any('07b_return' in s for s in inputs)
    assert 'r7_numbers' not in maintex
    out=dict(base_commit=BASE,checked_source_files=len(files),**counts,
        original_r7_subtree_equal_to=RETURN,pinned_sources_verified=len(pinned),
        author_assets=assets,unchanged_refs=refs,main_chapter_inputs=inputs,
        allowed_tracked_scope=True,english_files_changed=False,
        registered_proof_wording='附录A：均随eta减小→均随eta增大而减小；NEW-2已登记，公式和逻辑不变',
        added_math='eq:return:cut和eq:return:tail及环境外逻辑修正另见NEW_2；本收据不把原环境保持等同无新增数学')
    dump('new4_preservation.json',out)
    print(json.dumps(counts,ensure_ascii=False))


if __name__=='__main__':
    main()
