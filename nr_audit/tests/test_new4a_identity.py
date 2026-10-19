"""NEW-4a：真实缓存身份、冻结第二输入与失败路径，不运行分类或ODE。"""
import copy
import hashlib
import json
import sys
import pytest
import import_return_numbers as IR
import audit_return_endpoint as EP
import audit_common as AC
import plot_figure7 as F
from conftest import SRC


@pytest.fixture
def cached_root(tmp_path, monkeypatch):
    root = tmp_path / 'cache'
    data = json.loads(F.DATA.read_text(encoding='utf-8'))
    files = list(data['source_hashes']) + ['nr_audit/results/new_figure7.json',
                                         'nr_audit/results/new_figure7.npz']
    for rel in files:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((SRC.ROOT / rel).read_bytes())
    monkeypatch.setattr(F, 'ROOT', root)
    monkeypatch.setattr(F, 'RESULTS', root / 'nr_audit/results')
    monkeypatch.setattr(F, 'RES', root / 'reproducibility/results/20261005_sec7_v2_refinement/joint_extra')
    monkeypatch.setattr(F, 'DATA', root / 'nr_audit/results/new_figure7.json')
    monkeypatch.setattr(F, 'NPZ', root / 'nr_audit/results/new_figure7.npz')
    return root, data


def test_current_cached_inputs_match(cached_root):
    root, data = cached_root
    F.validate_cached_inputs(data)


@pytest.mark.parametrize('path', [
    'nr_audit/results/weight_brackets.json', 'nr_audit/allocation.py',
    'nr_audit/audit_weights.py', 'nr_audit/params.py',
    'reproducibility/results/20261005_sec7_v2_refinement/joint_extra/phase.json',
    'reproducibility/results/20261005_sec7_v2_refinement/joint_extra/phase_baseline.npz',
    'reproducibility/results/20261005_sec7_v2_refinement/joint_extra/phase_xian.npz'])
def test_changed_figure_input_is_rejected(cached_root, path):
    root, data = cached_root
    p = root / path
    p.write_bytes(p.read_bytes() + b'\0')
    with pytest.raises(ValueError, match='输入已变'):
        F.validate_cached_inputs(data)


def test_changed_local_npz_is_rejected(cached_root):
    root, data = cached_root
    F.NPZ.write_bytes(F.NPZ.read_bytes() + b'\0')
    with pytest.raises(ValueError, match='缓存NPZ'):
        F.validate_cached_inputs(data)


def test_reuse_does_not_classify_or_compute_background(cached_root, monkeypatch):
    root, data = cached_root
    def forbidden(*args, **kwargs):
        raise AssertionError('reuse-data禁止重新分类或计算控制律')
    monkeypatch.setattr(F.AW, 'classify', forbidden)
    monkeypatch.setattr(F.AL, 'make_law_opt', forbidden)
    monkeypatch.setattr(F, 'refine_background', forbidden)
    seen = []
    monkeypatch.setattr(F, 'render', lambda d, a, reuse_data=False: seen.append(
        (d['cases'] == data['cases'], reuse_data, sorted(a))))
    monkeypatch.setattr(sys, 'argv', ['plot_figure7.py', '--reuse-data'])
    before = F.NPZ.read_bytes()
    F.main()
    assert len(seen) == 1 and seen[0][:2] == (True, True)
    assert F.NPZ.read_bytes() == before


def test_convergence_identity_without_history(tmp_path):
    data, identity = IR.read_convergence(repository=tmp_path)
    assert identity['sha256'] == IR.CONVERGENCE_SHA256
    assert identity['blob'] == IR.CONVERGENCE_BLOB
    assert identity['history_check'] == 'not_available'
    assert data['tolerance_summary']['all_pass'] is True
    assert len(data['tolerance']) == 54


@pytest.mark.parametrize('edit', ['crlf', 'newline', 'value'])
def test_modified_second_input_fails_before_use(tmp_path, edit):
    original = (SRC.ROOT / IR.CONVERGENCE_PATH).read_bytes()
    if edit == 'crlf':
        bad = original.replace(b'\n', b'\r\n')
    elif edit == 'newline':
        bad = original + b'\n'
    else:
        data = json.loads(original)
        data['tolerance_summary']['max_rel_change_tight'] *= 2
        bad = json.dumps(data).encode('utf-8')
    p = tmp_path / 'bad.json'
    p.write_bytes(bad)
    ep = json.loads((SRC.ROOT / 'nr_audit/results/new_return_endpoint.json').read_text(encoding='utf-8'))
    with pytest.raises(ValueError, match='SHA-256'):
        IR.read_convergence(p, repository=tmp_path)
    with pytest.raises(ValueError, match='SHA-256'):
        EP.build_audit(convergence_path=p, repository=tmp_path)
    with pytest.raises(ValueError, match='SHA-256'):
        EP.validate_endpoint_sources(ep, convergence_path=p, repository=tmp_path)


def test_missing_second_input_fails(tmp_path):
    p = tmp_path / 'missing.json'
    with pytest.raises(FileNotFoundError):
        IR.read_convergence(p, repository=tmp_path)
    with pytest.raises(FileNotFoundError):
        EP.build_audit(convergence_path=p, repository=tmp_path)


@pytest.mark.parametrize('edit', ['value', 'identity'])
def test_derived_endpoint_must_match_verified_source(tmp_path, edit):
    ep = json.loads((SRC.ROOT / 'nr_audit/results/new_return_endpoint.json').read_text(encoding='utf-8'))
    if edit == 'value':
        ep['solver_tolerance_max_rel_tight'] *= 2
    else:
        ep['convergence_source']['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='派生终点审计'):
        EP.validate_endpoint_sources(ep, repository=tmp_path)


def test_json_writer_uses_lf(tmp_path, monkeypatch):
    monkeypatch.setattr(AC, 'RESULTS', tmp_path)
    AC.dump('record.json', {'说明': ['第一行', '第二行']})
    raw = (tmp_path / 'record.json').read_bytes()
    assert b'\n' in raw and b'\r' not in raw


def test_migration_keeps_historical_calculation_identity():
    data = json.loads((SRC.ROOT / 'nr_audit/results/new_figure7.json').read_text(encoding='utf-8'))
    migration = json.loads((SRC.ROOT / 'nr_audit/results/new4a_identity_migration.json').read_text(encoding='utf-8'))
    history = migration['historical_figure_record']
    assert data['compute_script_sha256'] == history['compute_script_sha256']
    assert data['background_refinement']['script_sha256'] == history['background_refinement_script_sha256']
    assert data['identity_history'][0] == history
    assert data['cache_npz_sha256'] == migration['local_cache_npz_sha256']
    assert all(p['lf_only_content_change'] for p in migration['eol_only_input_migrations'])



@pytest.mark.parametrize('newline', [b'\n', b'\r\n'], ids=['LF', 'CRLF'])
def test_reuse_accepts_text_checkout_eol(cached_root, monkeypatch, newline):
    """同一文本内容的两种行尾均能复用；二进制/冻结源不改写。"""
    root, data = cached_root
    for rel in data['source_hashes']:
        if rel.startswith('nr_audit/') and (rel.endswith('.py') or rel.endswith('.json')):
            p = root / rel
            p.write_bytes(p.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', newline))
    # 元数据JSON本身也允许两种检出行尾。
    F.DATA.write_bytes(F.DATA.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', newline))
    F.validate_cached_inputs(data)
    def forbidden(*args, **kwargs):
        raise AssertionError('换行验收禁止重算')
    monkeypatch.setattr(F.AW, 'classify', forbidden)
    monkeypatch.setattr(F.AL, 'make_law_opt', forbidden)
    monkeypatch.setattr(F, 'refine_background', forbidden)
    seen = []
    monkeypatch.setattr(F, 'render', lambda d, a, reuse_data=False: seen.append(reuse_data))
    monkeypatch.setattr(sys, 'argv', ['plot_figure7.py', '--reuse-data'])
    F.main()
    assert seen == [True]


def test_frozen_json_still_requires_raw_bytes(cached_root):
    root, data = cached_root
    path = F.RES / 'phase.json'
    before = path.read_bytes()
    assert b'\r\n' in before
    path.write_bytes(before.replace(b'\r\n', b'\n'))
    # 文本规范化身份相同，但历史冻结原字节的单独校验仍应拒绝。
    assert F.inputs() == data['source_hashes']
    with pytest.raises(ValueError, match='冻结图7输入原始字节'):
        F.validate_cached_inputs(data)
