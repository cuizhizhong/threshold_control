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
    """Git检出配置模拟，不冒称Linux操作系统实测。"""
    repo = tmp_path / 'repo'
    repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    def git(*args):
        return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True)
    (repo / '.gitattributes').write_text('/source.json -text\n/loader.py -text\n', encoding='utf-8')
    expected = {'source.json': (SRC.ROOT / IR.SOURCE_PATH).read_bytes(),
                'loader.py': (SRC.ROOT / 'xian_control_comparison/xian_control_comparison.py').read_bytes()}
    for name, raw in expected.items():
        (repo / name).write_bytes(raw)
    git('add', '.gitattributes', 'source.json', 'loader.py')
    for setting in ('true', 'false'):
        git('config', 'core.autocrlf', setting)
        for name in expected:
            (repo / name).unlink()
        git('checkout-index', '-f', '--all')
        assert all((repo / name).read_bytes() == raw for name, raw in expected.items())
