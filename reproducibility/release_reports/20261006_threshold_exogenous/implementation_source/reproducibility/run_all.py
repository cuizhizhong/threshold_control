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

def _joint_extra(output: Path, version: dict, *, inherited: bool) -> dict:
    """新科学量只由活动模块计算；旧科学来源是否继承写入报告。"""
    from joint_extra.run import run as run_extra
    reference=(ROOT/version['inherited_science_reference']/'xian/reference.json' if inherited else
               output/'xian/reference.json')
    result=run_extra(output_dir=output/'joint_extra',
                     baseline_path=ROOT/'joint_control/threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json',
                     xian_reference=reference,tasks=version['approved_tasks'])
    validation=json.loads((output/'joint_extra/validation.json').read_text(encoding='utf-8-sig'))
    if not all(validation.get('tasks',{}).get(task,{}).get('passed') is True for task in version['approved_tasks']):
        raise RuntimeError('新增联合科学阶段未通过；保留逐任务失败记录')
    return {**result,'passed':True,'tasks':validation['tasks'],
            'validation_overall_passed':validation.get('passed') is True,
            'approved_tasks':version['approved_tasks'],
            'scope':'仅批准任务逐项通过；未通过或未执行任务保留原状态。'}


def _integrated_figures(output: Path, version: dict, *, inherited: bool) -> dict:
    from bootstrap import sha
    import shutil
    directory=output/'figures'
    directory.mkdir(exist_ok=True)
    records=[]
    if inherited and 'generated_figure_labels' in version:
        selected=version['generated_figure_labels']
        figures=version['inventory']['main']['figures']
        available={item['label']:item for item in figures}
        known={'fig:joint:compare','fig:joint:capacity','fig:joint:phase','fig:joint:frontier'}
        if not selected or len(set(selected))!=len(selected) or not set(selected)<=known or not set(selected)<=set(available):
            raise ValueError('逐图生成批准标签非法、重复或不在正式清单。')
        retained=[]
        for item in figures:
            if item['label'] in selected:
                continue
            source=ROOT/'latex/figures'/item['image']
            expected=version['inherited_figure_sha256'].get(item['image'])
            if expected is None or not source.is_file() or sha(source)!=expected:
                raise RuntimeError('原图继承身份未锁定或改变：'+item['image'])
            retained.append((item,source,expected))
        # 空目录只生成批准图，随后复制原图；不能先重画后标成继承。
        target=directory/'joint_v2'
        subprocess.run([sys.executable,'-B',str(ROOT/'reproducibility/joint_extra/figures.py'),
                        '--res',str(output/'joint_extra'),'--out',str(target),
                        '--textwidth-bp',str(version['textwidth_bp']),
                        '--labels',*selected],check=True)
        manifest=json.loads((target/'figure_manifest.json').read_text(encoding='utf-8'))
        if {item['label'] for item in manifest['figures']}!=set(selected) or len(manifest['figures'])!=len(selected):
            raise RuntimeError('生成图件清单与批准标签不一致。')
        records.extend(manifest['figures'])
        for item,source,expected in retained:
            destination=directory/item['image']
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,destination)
            if sha(destination)!=expected:
                raise RuntimeError('继承图件复制后哈希改变：'+item['image'])
            records.append({'label':item['label'],'file':str(destination),'file_sha256':expected,
                            'inherited':True,'status':'inherited','original_source':str(source)})
        report={'passed':True,'status':'generated_and_inherited','figures':records,
                'figure_count':len(records),'historical_pickle_replay_used':False,
                'old_figures_regenerated':False,'new_figures_regenerated':True,
                'generated_figure_labels':selected,'inherited_figure_count':len(retained),
                'scope':'只生成批准标签；其余正式图按批准SHA逐件继承，不重画。'}
        dump(output/'validation/figure_generation.json',report)
        return report
    if inherited:
        for item in version['inventory']['main']['figures']:
            if item['label'].startswith('fig:joint:'):
                continue
            source=ROOT/'latex/figures'/item['image']
            expected=version['inherited_figure_sha256'].get(item['image'])
            if expected is None or sha(source)!=expected:
                raise RuntimeError('原图继承身份未锁定或改变：'+item['image'])
            target=directory/item['image']
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
            records.append({'label':item['label'],'file':str(target),'file_sha256':sha(target),
                            'inherited':True,'status':'inherited','original_source':str(source)})
    else:
        records=json.loads((output/'validation/figure_generation.json').read_text(encoding='utf-8'))['figures']
    target=directory/'joint_v2'
    subprocess.run([sys.executable,'-B',str(ROOT/'reproducibility/joint_extra/figures.py'),
                    '--res',str(output/'joint_extra'),'--out',str(target),
                    '--textwidth-bp',str(version['textwidth_bp'])],check=True)
    manifest=json.loads((target/'figure_manifest.json').read_text(encoding='utf-8'))
    records.extend(manifest['figures'])
    report={'passed':True,'status':'generated_and_inherited' if inherited else 'generated',
            'figures':records,'figure_count':len(records),'historical_pickle_replay_used':False,
            'old_figures_regenerated':not inherited,'new_figures_regenerated':True,
            'scope':'旧正式图按批准哈希继承；只有联合新图本轮再生成。' if inherited else '同轮图件再生成。'}
    dump(output/'validation/figure_generation.json',report)
    return report


def single(output: Path, matlab: str, *, scope: str='all') -> dict:
    stages={}
    existing_nonempty=output.exists() and any(output.iterdir())
    try:
        name='preflight'
        prepare_workspace(output,ROOT)
        environment(output)
        from integrity import run as run_integrity
        stages['source_integrity']=run_integrity(ROOT,output)
        dump(output/'validation/source_integrity_initial.json',stages['source_integrity'])
        from manuscript_version import load_version, version_bibliography, version_build_script
        version=load_version(ROOT,required=scope=='joint-extra')
        if version is None and '% BEGIN JOINT_EXTRA:' in (ROOT/'latex/flatten_curve_analysis_cn.tex').read_text(encoding='utf-8-sig'):
            raise RuntimeError('当前主稿已开始联合整合，须先批准受控稿源；不运行旧冻结底稿链条。')
        from figures import run_science, run_figures
        from xian import run_xian
        from population import run_population
        from c0 import run_c0
        from joint import run as run_joint
        from registry import build_registry
        from checks import run as run_checks
        jobs=[] if scope=='joint-extra' else [('baseline',lambda:run_science(output,ROOT,matlab)),
                        ('xian',lambda:run_xian(output,ROOT)),
                        ('population',lambda:run_population(output,ROOT)),
                        ('c0',lambda:run_c0(output,ROOT)),
                        ('joint',lambda:run_joint(output,ROOT)),
                        ('independent_checks',lambda:run_checks(output,ROOT)),
                        ('figures',lambda:run_figures(output,ROOT))]
        if version:
            jobs.extend([('joint_extra',lambda:_joint_extra(output,version,inherited=scope=='joint-extra')),
                         ('integrated_figures',lambda:_integrated_figures(output,version,inherited=scope=='joint-extra'))])
        for name,fn in jobs:
            print('START',name,flush=True); result=fn(); stages[name]=result
            if not result.get('passed',result.get('status')=='pass'):
                raise RuntimeError(f'{name} 未通过')
            dump(output/'stage_results.json',stages)
            print('FINISHED',name,flush=True)
        from paper_sync import prepare_manuscript
        name='manuscript_sync'
        main,si,changes=prepare_manuscript(ROOT,output,
                scientific_reference=ROOT/version['inherited_science_reference'] if scope=='joint-extra' else None)
        dump(output/'manuscript_changes.json',changes)
        if not changes.get('passed'):raise RuntimeError('正文/表格数字同步未通过')
        from theory_trace import run as trace_theory
        stages['theory_trace']=trace_theory(ROOT,output,main)
        from build import run as build
        name='document'
        stages['document']=build(output,ROOT,figure_dir=output/'figures',main_text=main,supplement_text=si,
                bibliography_path=version_bibliography(version) if version else None,
                build_script_path=version_build_script(version) if version else None)
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
                'formal_files_published':False,'stages':stages,'scientific_scope':scope,
                'inherited_old_science':scope=='joint-extra',
                'manuscript_version':version['version'] if version else 'frozen_20261002'}
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
    ap.add_argument('--matlab',default='')
    ap.add_argument('--scope',choices=['all','joint-extra'],default='all')
    ap.add_argument('--repeats',type=int,default=2)
    ap.add_argument('--single',action='store_true')
    args=ap.parse_args()
    if args.scope=='all' and not args.matlab:ap.error('完整科学复现须显式给出 --matlab；新增联合复现不调用MATLAB。')
    if args.single:
        single(args.output.resolve(),args.matlab,scope=args.scope); return
    if args.repeats<2:ap.error('正式验收至少两个独立空输出目录。')
    parent=args.output.resolve()
    if parent.exists():ap.error('总输出目录必须不存在，避免重用或覆盖旧结果。')
    parent.mkdir(parents=True)
    env=os.environ.copy(); env['PYTHONUTF8']='1'; env['MPLBACKEND']='Agg'
    completed=[]
    for i in range(args.repeats):
        path=parent/f'run_{i+1}'
        subprocess.run([sys.executable,'-B',__file__,'--single','--output',str(path),
                        '--scope',args.scope,*(['--matlab',args.matlab] if args.matlab else [])],check=True,env=env)
        completed.append(path.name)
    from run_selection import select_runs, selected_directories
    select_runs(parent,completed[:2])
    first,second=selected_directories(parent)
    from compare_runs import compare
    result=compare(first,second,parent/'repeatability.json')
    if not result['passed']:raise RuntimeError('两个独立运行结果不一致')
    print(json.dumps({'passed':True,'output':str(parent),'visual_review':'pending',
                     'formal_files_published':False},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
