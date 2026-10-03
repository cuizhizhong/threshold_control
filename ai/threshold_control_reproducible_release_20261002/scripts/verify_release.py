#!/usr/bin/env python3
"""校验最终稿、图件及复现代码的锁定哈希；不验证数学证明。只使用标准库。"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock',type=Path,default=ROOT/'validation/locked_files.json')
    args=parser.parse_args()
    try:
        locked=json.loads(args.lock.read_text(encoding='utf-8'))
        mismatches=[]
        for rel,expected in locked['files'].items():
            p=ROOT/rel
            actual=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
            if actual != expected: mismatches.append({'path':rel,'expected':expected,'actual':actual})
        result={'checked_files':len(locked['files']),'passed':not mismatches,'mismatches':mismatches,
                'scope':'锁定稿件、PDF、20幅图及计算入口；不能认证数学证明或临床有效性。'}
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if mismatches:sys.exit(1)
    except (OSError,ValueError,KeyError) as exc:
        parser.exit(2,str(exc)+'\n')

if __name__=='__main__':main()
