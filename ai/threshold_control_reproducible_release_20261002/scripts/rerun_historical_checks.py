#!/usr/bin/env python3
"""原样执行恢复的历史理论检查程序；输出到单独目录，不覆盖原始记录。"""
from pathlib import Path
import argparse,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,default=ROOT/'validation/historical_recheck')
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='threshold-historical-') as tmp:
        v=Path(tmp)/'validation';v.mkdir()
        target=v/'check_completed_theory.py'
        shutil.copy2(ROOT/'provenance/original_checks/check_completed_theory.py',target)
        with (out/'stdout.log').open('w',encoding='utf-8') as log:
            subprocess.run([sys.executable,str(target)],check=True,stdout=log,stderr=subprocess.STDOUT,timeout=240)
        shutil.copy2(v/'completed_theory_checks.json',out/'completed_theory_checks.json')
    print(out/'completed_theory_checks.json')
if __name__=='__main__':main()
