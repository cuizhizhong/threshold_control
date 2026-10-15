"""数字来源测试：参数、初值与能力代表点逐位取自来源字段；来源文件未变；参照数据的列存在；
复用代码的来源 blob 与回流分支提交一致；稿件表 1 的显示值与未取整参数一致。"""
import json
import re
import subprocess

import pytest

from conftest import CASE_FILE, PR, SRC

MANIFEST = SRC.OUT


@pytest.fixture(scope='module')
def manifest():
    return json.loads(MANIFEST.read_text(encoding='utf-8'))


def test_manifest_current(manifest):
    """results/source_manifest.json 与按当前代码重新生成的清单一致（稿件文件的哈希除外）。"""
    fresh = json.loads(json.dumps(SRC.build(), ensure_ascii=False))
    for fid in fresh['files']:
        fresh['files'][fid].pop('sha256') if not fresh['files'][fid]['pinned'] else None
        manifest['files'][fid].pop('sha256') if not manifest['files'][fid]['pinned'] else None
    assert fresh == manifest


def test_pinned_files_unchanged(manifest):
    """只读目录中的来源文件与清单中的 SHA-256 一致。"""
    for fid, f in manifest['files'].items():
        if f['pinned']:
            assert SRC.sha256(SRC.ROOT / f['path']) == f['sha256'], fid


@pytest.mark.parametrize('case', ['base', 'xian'])
def test_params_equal_source_fields(case):
    """params.py 的每个数值与来源字段逐位相等（==，不是近似）。"""
    P = PR.CASES[case]
    for name, (fid, field) in SRC.PARAM_SOURCES[case].items():
        assert getattr(P, name) == SRC.get_field(SRC.load_json(fid), field), (case, name)


def test_derived_rules():
    B, X = PR.BASE, PR.XIAN
    assert B.eta == 0.05 * B.N == 38.15
    assert X.eta == 0.002 * X.N == 26326.0
    assert X.S0 == X.N - X.I0 == SRC.load_json('xian_fit')['S0']
    assert X.I0 == SRC.load_json('xian_fit')['I0'] == 0.00100659188867187
    assert (X.Sq0, X.Iq0, X.R0) == (0.0, 0.0, 0.0) and (B.Sq0, B.Iq0, B.R0) == (0.0, 0.0, 0.0)
    assert (B.wc, B.wq, X.wc, X.wq) == (1.0, 2.0, 1.0, 2.0)
    assert B.S0 + B.I0 == B.N


def test_audit_notes_I0():
    text = (SRC.ROOT / SRC.FILES['audit_notes'][0]).read_text(encoding='utf-8')
    assert 'I0=0.00100659188867187' in text and '计算不使用论文显示的取整数' in text


def test_manuscript_table1_display():
    """稿件表 1 的显示值是未取整参数的舍入（西安 I0 显示为 ≈1.00659×10^-3）。"""
    text = (SRC.ROOT / SRC.FILES['table1'][0]).read_text(encoding='utf-8')
    rows = {m.group(1): m.group(0) for m in re.finditer(r'^\$(N|\\beta|\\gamma|\\delta_q|c_0|q_0|I_0|S_0|\\eta)\$.*$',
                                                         text, flags=re.M)}
    B, X = PR.BASE, PR.XIAN
    assert '763' in rows['N'] and r'\num{13163000}' in rows['N']
    assert '0.155' in rows[r'\beta'] and '0.1498' in rows[r'\beta']
    assert '0.3504' in rows[r'\gamma'] and '0.2953' in rows[r'\gamma']
    assert '0.3504' in rows[r'\delta_q'] and '0.3531' in rows[r'\delta_q']
    assert '& 10 &' in rows['c_0'] and '12.8872' in rows['c_0']
    assert '0.01526' in rows['q_0'] and '0.3230' in rows['q_0']
    assert r'\approx1.00659\times10^{-3}' in rows['I_0'] and f'{X.I0:.5e}' == '1.00659e-03'
    assert '762' in rows['S_0'] and B.S0 == 762.0
    assert '0.05N=38.15' in rows[r'\eta'] and r'\num{26326}' in rows[r'\eta']
    assert (B.beta, B.gamma, B.delta_q, B.c0, B.q0) == (0.155, 0.3504, 0.3504, 10.0, 0.01526)
    assert (X.beta, X.gamma, X.delta_q, X.c0, X.q0) == (0.1498, 0.2953, 0.3531, 12.8872, 0.3230)


def test_default_weights_in_manuscript():
    text = (SRC.ROOT / SRC.FILES['model_section'][0]).read_text(encoding='utf-8')
    assert r'默认取 $w_c=1,w_q=2$' in text


def test_capacity_points():
    """能力代表点与 capacity.json 的 point 字段、图 6 图注一致。"""
    cap = SRC.load_json('capacity')
    for case, key in (('base', 'baseline'), ('xian', 'xian')):
        C, pt = PR.REP_CAPACITY[case], cap[key]['point']
        assert C.c_min == pt['c_min'] and C.q_cap == pt['q_cap']
        assert pt['u_max'] == 0.5 and C.c_min / PR.CASES[case].c0 == 0.5
    text = (SRC.ROOT / SRC.FILES['table1'][0]).read_text(encoding='utf-8')
    assert r'基准 $c_{\min}/c_0=0.5$、$q_{\rm cap}=0.6$，西安 $c_{\min}/c_0=0.5$、$q_{\rm cap}=0.75$' in text


def test_reference_columns():
    """回归用到的参照列存在，且两组参照与本模块的参数一致（读自 input_manifest.json）。"""
    need = {'duration', 'J', 't1', 't2', 't_end', 'total_infections', 'Sq_increment_plateau',
            'plateau_infections_time', 'peak_I_plus_Iq_over_eta', 'duration_state', 'J_state'}
    for case, fid in CASE_FILE.items():
        rows = SRC.read_csv(fid)
        assert {r['strategy'] for r in rows} == {'contact_only', 'alpha_0.5', 'quarantine_only', 'minimum_cost'}
        assert need <= set(rows[0])
    man = SRC.load_json('input_manifest')
    for case, key in (('base', 'baseline'), ('xian', 'xian')):
        P = PR.CASES[case]
        par = man['cases'][key]['parameters']
        for name in ('N', 'S0', 'I0', 'beta', 'gamma', 'delta_q', 'c0', 'q0', 'eta', 'wc', 'wq', 'Sq0', 'Iq0', 'R0'):
            assert par[name] == getattr(P, name), (case, name)


def _git(*args):
    try:
        return subprocess.run(['git', *args], cwd=SRC.ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def test_code_reuse_blobs(manifest):
    """复用代码的来源文件在回流分支提交 bb52b96 中的 blob 与清单一致（需要 git 与该提交）。"""
    if _git('cat-file', '-e', SRC.REUSE_COMMIT) is None:
        pytest.skip('本地没有回流分支的提交 bb52b96')
    for r in manifest['code_reuse']:
        assert _git('rev-parse', f"{r['source_commit']}:{r['source']}") == r['blob'], r['file']
