"""点名可转换行尾的稿件文本身份；只把 CRLF 字节替换为 LF。

不解码、不去空格、不移除 BOM 或孤立 CR。科学输入与二进制仍由原始字节哈希核验。
最终稿件文本修改后只刷新新增内容字段：python nr_audit/text_identity.py --refresh-current
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = 'sha256(bytes.replace(CRLF, LF)); preserve all other bytes'


def content_sha256(raw: bytes) -> str:
    return hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest()


def require_policy(record):
    if record['text_identity']['policy'] != POLICY:
        raise ValueError('未识别的文本内容身份规则')


def require_content(raw, expected, *, name):
    actual = content_sha256(raw)
    if actual != expected:
        raise ValueError(f'文本内容 SHA-256 不匹配: {name}')
    return actual


def current_text_rows(receipt):
    """仅枚举迁移收据点名的现稿 TeX，不对 protected_original_sha256 分派文本规则。"""
    require_policy(receipt)
    for row in receipt['manifest_manuscript_locations'].values():
        yield row['current_path'], row
    for group in receipt['file_fragments']:
        for row in group['current_fragments']:
            yield row['path'], row


def manuscript_path(root, relative):
    path = Path(relative)
    if path.is_absolute() or path.suffix != '.tex' or not path.parts or path.parts[0] != 'paper':
        raise ValueError(f'内容身份仅用于点名的 paper/*.tex: {relative}')
    root = Path(root).resolve()
    target = (root / path).resolve()
    if not target.is_relative_to(root):
        raise ValueError(f'稿件路径超出仓库: {relative}')
    return target


def validate_current_texts(receipt, root=ROOT):
    digests = {}
    for relative, row in current_text_rows(receipt):
        digests[relative] = require_content(
            manuscript_path(root, relative).read_bytes(), row['current_content_sha256'], name=relative)
    return digests


def refresh_current_content_hashes(receipt, root=ROOT):
    """只更新本轮内容字段；NEW-4g raw hash、历史manifest和冻结输入字段均不改。"""
    count = 0
    for relative, row in current_text_rows(receipt):
        row['current_content_sha256'] = content_sha256(manuscript_path(root, relative).read_bytes())
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-current', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'nr_audit/manuscript_path_migration_NEW4g.json'
    receipt = json.loads(path.read_text(encoding='utf-8'))
    if args.refresh_current:
        count = refresh_current_content_hashes(receipt)
        path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n',
                        encoding='utf-8', newline='\n')
        print(f'仅刷新 {count} 项 current_content_sha256；历史 raw SHA 保持。')
    else:
        print(f'现稿内容身份通过：{len(validate_current_texts(receipt))} 个文件。')


if __name__ == '__main__':
    main()
