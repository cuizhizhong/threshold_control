"""发布输入风险：字节保护、无历史导入与失败路径，不改参照数值。"""
import hashlib
import subprocess
import pytest
import import_return_numbers as IR
from conftest import SRC


def test_canonical_input_hash_and_no_history(tmp_path):
    out = IR.build_import(SRC.ROOT / IR.SOURCE_PATH, repository=tmp_path)
    assert len(out['runs']) == 18
    assert out['source']['history_check'] == 'not_available'
    assert out['source']['sha256'] == IR.SOURCE_SHA256


def test_missing_input_fails(tmp_path):
    with pytest.raises(FileNotFoundError):
        IR.build_import(tmp_path / 'missing.json', repository=tmp_path)


@pytest.mark.parametrize('edit', ['crlf', 'newline', 'corrupt'])
def test_changed_input_fails(tmp_path, edit):
    raw = (SRC.ROOT / IR.SOURCE_PATH).read_bytes()
    bad = {'crlf': raw.replace(b'\n', b'\r\n'), 'newline': raw + b'\n',
           'corrupt': raw.replace(b'first_below_one', b'wrong_endpoint', 1)}[edit]
    path = tmp_path / 'source.json'
    path.write_bytes(bad)
    with pytest.raises(ValueError, match='SHA-256'):
        IR.build_import(path, repository=tmp_path)


def test_frozen_loader_is_canonical_lf():
    raw = (SRC.ROOT / 'xian_control_comparison/xian_control_comparison.py').read_bytes()
    assert b'\r\n' not in raw
    assert hashlib.sha256(raw).hexdigest() == 'c029a604c8f7147a24d59e6c0d39a927ff360f0dbb1b7338f23bd86573ff15a2'


def test_fixed_paths_ignore_autocrlf(tmp_path):
    """真实attributes全文和真实相对路径，在同一Windows主机模拟两种检出配置。"""
    repo = tmp_path / 'repo'
    repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    def git(*args):
        return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True)
    # 必须复制仓库真正的属性文件，不能用简化规则替代。
    (repo / '.gitattributes').write_bytes((SRC.ROOT / '.gitattributes').read_bytes())
    lf_paths = [
        'nr_audit/allocation.py', 'nr_audit/audit_weights.py', 'nr_audit/params.py',
        'nr_audit/plot_figure7.py', 'nr_audit/audit_common.py',
        'nr_audit/import_return_numbers.py', 'nr_audit/audit_return_endpoint.py',
        'nr_audit/make_numbers.py', 'nr_audit/results/weight_brackets.json',
        'nr_audit/results/new_figure7.json', 'nr_audit/results/new_figure7_render.json',
        'nr_audit/results/new_return_endpoint.json', 'nr_audit/results/nr_numbers_map.json',
        'nr_audit/results/new_figure7_alignment.json', 'nr_audit/results/new_figure7_collisions.json',
        'nr_audit/results/new4a_identity_migration.json', 'nr_audit/results/new4b_identity_migration.json']
    frozen_paths = [
        IR.SOURCE_PATH, IR.CONVERGENCE_PATH, 'xian_control_comparison/xian_control_comparison.py',
        'nr_audit/results/new_figure7.npz',
        'reproducibility/results/20261005_sec7_v2_refinement/joint_extra/phase.json',
        'reproducibility/results/20261005_sec7_v2_refinement/joint_extra/phase_baseline.npz',
        'reproducibility/results/20261005_sec7_v2_refinement/joint_extra/phase_xian.npz']
    expected = {p: (SRC.ROOT / p).read_bytes() for p in lf_paths + frozen_paths}
    assert all(b'\r' not in expected[p] for p in lf_paths)
    for name, content in expected.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    git('add', '.gitattributes', *expected)
    attrs = git('check-attr', 'text', 'eol', '--', *expected).stdout.decode().splitlines()
    for p in lf_paths:
        assert f'{p}: text: set' in attrs
        assert f'{p}: eol: lf' in attrs
    for p in frozen_paths:
        assert f'{p}: text: unset' in attrs
    for setting in ('true', 'false'):
        git('config', 'core.autocrlf', setting)
        for name in expected:
            (repo / name).unlink()
        git('checkout-index', '-f', '--all')
        assert all((repo / p).read_bytes() == content for p, content in expected.items())
