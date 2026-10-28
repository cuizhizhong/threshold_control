"""NEW-4h 文本行尾的正反回归；只读原件，变体与损坏均写 pytest 临时目录。"""
import copy
import hashlib
import json
from pathlib import Path

import pytest

import audit_layout_migration as LM
from conftest import SRC
import test_sources as source_tests
import text_identity as TI

RECEIPT = json.loads((SRC.HERE / 'manuscript_path_migration_NEW4g.json').read_text(encoding='utf-8'))
BASELINE = json.loads((SRC.ROOT / 'paper/revision_notes/NEW_4g_baseline.json').read_text(encoding='utf-8'))
MACROS = (SRC.ROOT / LM.MACROS).read_bytes()
# NEW-4w（N33）授权更新数字宏后，以 results/new4w/macros_identity.json 的内容身份为宏的基线；其余文件仍用 NEW-4g 基线。
MACRO_BASELINE = copy.deepcopy(BASELINE)
_NEW4W_MACROS = SRC.HERE / 'results/new4w/macros_identity.json'
if _NEW4W_MACROS.exists():
    _reg = json.loads(_NEW4W_MACROS.read_text(encoding='utf-8'))
    assert _reg['path'] == LM.MACROS and _reg['policy'] == BASELINE['text_identity']['policy']
    MACRO_BASELINE['text_identity']['content_sha256'][LM.MACROS] = _reg['content_sha256']
    MACRO_BASELINE['files'][LM.MACROS] = _reg['raw_sha256']
LOCATIONS = [('manifest', key) for key in RECEIPT['manifest_manuscript_locations']]
LOCATIONS += [('fragment', i, j) for i, group in enumerate(RECEIPT['file_fragments'])
              for j, _ in enumerate(group['current_fragments'])]


def eol(raw, newline):
    return raw.replace(b'\r\n', b'\n').replace(b'\n', newline)


@pytest.fixture
def checkout(tmp_path):
    receipt = copy.deepcopy(RECEIPT)
    for relative, _ in TI.current_text_rows(receipt):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((SRC.ROOT / relative).read_bytes())
    TI.refresh_current_content_hashes(receipt, tmp_path)
    return tmp_path, receipt


@pytest.mark.parametrize('where', LOCATIONS, ids=lambda key: '-'.join(map(str, key)))
@pytest.mark.parametrize('newline', [b'\n', b'\r\n'], ids=['LF', 'CRLF'])
def test_every_current_location_and_fragment_accepts_only_eol(checkout, where, newline):
    root, receipt = checkout
    if where[0] == 'manifest':
        row = receipt['manifest_manuscript_locations'][where[1]]
        relative = row['current_path']
    else:
        row = receipt['file_fragments'][where[1]]['current_fragments'][where[2]]
        relative = row['path']
    path = root / relative
    path.write_bytes(eol(path.read_bytes(), newline))
    TI.validate_current_texts(receipt, root)
    path.write_bytes(path.read_bytes() + b' % real content change\n')
    with pytest.raises(ValueError, match='文本内容 SHA-256 不匹配'):
        TI.validate_current_texts(receipt, root)


@pytest.mark.parametrize('before', [b'\n', b'\r\n'], ids=['base-LF', 'base-CRLF'])
@pytest.mark.parametrize('after', [b'\n', b'\r\n'], ids=['current-LF', 'current-CRLF'])
def test_number_macros_accept_all_eol_pairs(before, after):
    result = LM.generated_macro_identity(eol(MACROS, before), eol(MACROS, after), MACRO_BASELINE)
    assert result['unchanged'] is True
    assert result['baseline_raw_sha256'] == MACRO_BASELINE['files'][LM.MACROS]
    assert result['base_git_content_sha256'] == result['current_content_sha256']


@pytest.mark.parametrize('damage', ['base', 'current', 'both', 'baseline_content_hash'])
def test_number_macros_reject_content_damage_even_if_both_sides_match(damage):
    old, current, baseline = MACROS, MACROS, copy.deepcopy(MACRO_BASELINE)
    if damage in ('base', 'both'):
        old += b' % changed\n'
    if damage in ('current', 'both'):
        current += b' % changed\n'
    if damage == 'baseline_content_hash':
        baseline['text_identity']['content_sha256'][LM.MACROS] = '0' * 64
    assert LM.generated_macro_identity(old, current, baseline)['unchanged'] is False


@pytest.fixture
def manifest_checkout(checkout, monkeypatch):
    root, receipt = checkout
    raw = source_tests.MANIFEST.read_bytes()
    manifest = json.loads(raw)
    manifest_path = root / receipt['historical_manifest']['path']
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(raw)
    receipt_path = root / 'nr_audit/manuscript_path_migration_NEW4g.json'
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False), encoding='utf-8')

    def fresh():
        # 不调用任何计算器；保留原manifest全体字段，只提供当前TeX原字节哈希。
        result = copy.deepcopy(manifest)
        for fid, row in receipt['manifest_manuscript_locations'].items():
            result['files'][fid]['path'] = row['current_path']
            result['files'][fid]['sha256'] = hashlib.sha256((root / row['current_path']).read_bytes()).hexdigest()
        return result

    monkeypatch.setattr(SRC, 'ROOT', root)
    monkeypatch.setattr(SRC, 'HERE', root / 'nr_audit')
    monkeypatch.setattr(SRC, 'build', fresh)
    monkeypatch.setattr(source_tests, 'MANIFEST', manifest_path)
    return manifest, manifest_path, fresh


@pytest.mark.parametrize('newline', [b'\n', b'\r\n'], ids=['LF', 'CRLF'])
def test_historical_manifest_eol_passes_actual_projection(manifest_checkout, newline):
    manifest, path, _ = manifest_checkout
    path.write_bytes(eol(path.read_bytes(), newline))
    source_tests.test_manifest_current(manifest)


def test_historical_manifest_content_damage_fails_actual_projection(manifest_checkout):
    manifest, path, _ = manifest_checkout
    # JSON仍能解析，但额外空格不能被内容哈希忽略。
    path.write_bytes(path.read_bytes() + b' ')
    with pytest.raises(ValueError, match='文本内容 SHA-256 不匹配'):
        source_tests.test_manifest_current(manifest)


def test_full_manifest_pinned_fields_remain_strict(manifest_checkout, monkeypatch):
    manifest, _, fresh = manifest_checkout
    changed = fresh()
    fid = next(key for key, row in changed['files'].items() if row['pinned'])
    changed['files'][fid]['sha256'] = '0' * 64
    monkeypatch.setattr(SRC, 'build', lambda: changed)
    with pytest.raises(AssertionError):
        source_tests.test_manifest_current(manifest)


@pytest.mark.parametrize('name,raw', [
    ('asset.pdf', b'%PDF-1.4\n\x00\xff'),
    ('cache.npz', b'PK\n\x00\xff'),
    ('frozen.json', b'{"scientific_value": 1}\n'),
])
def test_binary_and_frozen_scientific_text_keep_raw_checks(tmp_path, monkeypatch, name, raw):
    path = tmp_path / name
    path.write_bytes(raw)
    monkeypatch.setattr(SRC, 'ROOT', tmp_path)
    manifest = {'files': {'frozen': {'path': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'pinned': True}}}
    source_tests.test_pinned_files_unchanged(manifest)
    path.write_bytes(eol(raw, b'\r\n'))
    with pytest.raises(AssertionError):
        source_tests.test_pinned_files_unchanged(manifest)


@pytest.mark.parametrize('changed', [b'x = 1\n ', b'\xef\xbb\xbfx = 1\n', b'x = 1\r', b'x = 2\n'])
def test_content_identity_preserves_spaces_bom_lone_cr_and_numbers(changed):
    with pytest.raises(ValueError, match='文本内容 SHA-256 不匹配'):
        TI.require_content(changed, TI.content_sha256(b'x = 1\r\n'), name='explicit text')


def test_refresh_updates_only_new_content_fields(checkout):
    root, receipt = checkout
    before = copy.deepcopy(receipt)
    path = root / receipt['manifest_manuscript_locations']['table1']['current_path']
    path.write_bytes(path.read_bytes() + b' % authorized editorial change\n')
    assert TI.refresh_current_content_hashes(receipt, root) == 19
    assert receipt['manifest_manuscript_locations']['table1']['current_content_sha256'] != before['manifest_manuscript_locations']['table1']['current_content_sha256']
    for record in (before, receipt):
        for _, row in TI.current_text_rows(record):
            row.pop('current_content_sha256')
    assert receipt == before


def test_current_content_policy_does_not_expand_to_binary_or_frozen_inputs(checkout):
    root, receipt = checkout
    receipt['manifest_manuscript_locations']['table1']['current_path'] = 'nr_audit/results/new_figure7.npz'
    with pytest.raises(ValueError, match='内容身份仅用于点名'):
        TI.validate_current_texts(receipt, root)
