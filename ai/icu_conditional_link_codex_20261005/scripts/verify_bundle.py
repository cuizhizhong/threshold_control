#!/usr/bin/env python3
"""Verify package bytes only; does not verify epidemiological or clinical results."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]
manifest=root/'MANIFEST_SHA256.json'
if not manifest.is_file():
    raise SystemExit('缺少MANIFEST_SHA256.json')
entries=json.loads(manifest.read_text(encoding='utf-8'))['files']
fail=[]
for rel,expected in entries.items():
    p=root/rel
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
        fail.append(rel)
if fail:
    print('未通过：\n'+'\n'.join(fail));sys.exit(1)
print(f'已核对{len(entries)}个文件，哈希一致。这只验证文件完整性，不认证临床或数值结论。')
