"""两个空输出目录从头复现；任何失败不发布正式稿、不伪造完成标识。"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
from bootstrap import ROOT, dump, environment, prepare_workspace

def single(output: Path, matlab: str) -> dict:
    stages={}
    existing_nonempty=output.exists() and any(output.iterdir())
    try:
        name='preflight'
        prepare_workspace(output,ROOT)
        environment(output)
        from integrity import run as run_integrity
        stages['source_integrity']=run_integrity(ROOT,output)
        dump(output/'validation/source_integrity_initial.json',stages['source_integrity'])
        from figures import run_science, run_figures
        from xian import run_xian
        from population import run_population
        from c0 import run_c0
        from joint import run as run_joint
        from registry import build_registry
        from checks import run as run_checks
        for name,fn in [('baseline',lambda:run_science(output,ROOT,matlab)),
                        ('xian',lambda:run_xian(output,ROOT)),
                        ('population',lambda:run_population(output,ROOT)),
                        ('c0',lambda:run_c0(output,ROOT)),
                        ('joint',lambda:run_joint(output,ROOT)),
                        ('independent_checks',lambda:run_checks(output,ROOT)),
                        ('figures',lambda:run_figures(output,ROOT))]:
            print('START',name,flush=True); result=fn(); stages[name]=result
            if not result.get('passed',result.get('status')=='pass'):
                raise RuntimeError(f'{name} 未通过')
            dump(output/'stage_results.json',stages)
            print('FINISHED',name,flush=True)
        from paper_sync import prepare_manuscript
        name='manuscript_sync'
        main,si,changes=prepare_manuscript(ROOT,output)
        dump(output/'manuscript_changes.json',changes)
        if not changes.get('passed'):raise RuntimeError('正文/表格数字同步未通过')
        from theory_trace import run as trace_theory
        stages['theory_trace']=trace_theory(ROOT,output,main)
        from build import run as build
        name='document'
        stages['document']=build(output,ROOT,figure_dir=output/'figures',main_text=main,supplement_text=si)
        name='registry'
        stages['registry']=build_registry(ROOT,output)
        if not stages['registry'].get('passed'):raise RuntimeError('逐项对应清单不完整')
        dump(output/'stage_results.json',stages)
        stages['source_integrity_final']=run_integrity(ROOT,output)
        for key in ('runner_source_hashes','static_art_assets','raw_inputs',
                    'source_input_hashes','frozen_manifest_sha256'):
            if stages['source_integrity'][key]!=stages['source_integrity_final'][key]:
                raise RuntimeError('运行期间输入或复现源码变化：'+key)
        report={'passed':True,'numerical_and_build_complete':True,'visual_review':'pending',
                'formal_files_published':False,'stages':stages}
        dump(output/'run_report.json',report)
        return report
    except Exception as exc:
        if not existing_nonempty:
            dump(output/'run_report.json',{'passed':False,'formal_files_published':False,
                 'failed_stage':name if 'name' in locals() else 'preflight',
                 'error':str(exc),'traceback':traceback.format_exc(),'stages':stages})
        else:
            print('拒绝覆盖旧运行目录；原有记录保持不变：'+str(exc),file=sys.stderr,flush=True)
        raise

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--matlab',required=True)
    ap.add_argument('--repeats',type=int,default=2)
    ap.add_argument('--single',action='store_true')
    args=ap.parse_args()
    if args.single:
        single(args.output.resolve(),args.matlab); return
    if args.repeats<2:ap.error('正式验收至少两个独立空输出目录。')
    parent=args.output.resolve()
    if parent.exists():ap.error('总输出目录必须不存在，避免重用或覆盖旧结果。')
    parent.mkdir(parents=True)
    env=os.environ.copy(); env['PYTHONUTF8']='1'; env['MPLBACKEND']='Agg'
    for i in range(args.repeats):
        path=parent/f'run_{i+1}'
        subprocess.run([sys.executable,'-B',__file__,'--single','--output',str(path),
                        '--matlab',args.matlab],check=True,env=env)
    from compare_runs import compare
    result=compare(parent/'run_1',parent/'run_2',parent/'repeatability.json')
    if not result['passed']:raise RuntimeError('两个独立运行结果不一致')
    print(json.dumps({'passed':True,'output':str(parent),'visual_review':'pending',
                     'formal_files_published':False},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
