"""第9节边界文案的独立验收；只核查既有结果与产物，不编译、不重算。"""
from __future__ import annotations

import argparse
import ast
import builtins
import copy
import csv
import difflib
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import traceback
from unittest import mock

import pymupdf
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
LATEX = ROOT / 'latex'
RESULTS = ROOT / 'reproducibility/results/20261003_release_final'
MAIN = 'flatten_curve_analysis_cn'
SI = 'flatten_curve_supplement_cn'
START = '% ===== 09_population ====='
END = '% ===== 10_discussion ====='
SCIENCE = {'xian', 'population', 'joint', 'c0', 'scipy', 'mpmath'}


def read(path):
    return Path(path).read_text(encoding='utf-8-sig')


def load(path):
    return json.loads(read(path))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def dump(path, payload):
    path = Path(path).resolve()
    if not path.is_relative_to(REPORT):
        raise ValueError('核查输出越界')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def envs(text, kinds):
    names = '|'.join(re.escape(k) for k in kinds)
    return [m.group(0) for m in re.finditer(rf'\\begin\{{({names})\}}.*?\\end\{{\1\}}', text, re.S)]


def labels(text):
    return re.findall(r'\\label\{([^}]+)\}', text)


def citations(text):
    return sorted({key.strip() for match in re.findall(
        r'\\(?:cite|parencite|textcite|autocite|footcite|nocite)\*?(?:\[[^\]]*\])*\{([^}]+)\}', text)
        for key in match.split(',')})


def split_section(text):
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError('第9节边界定位不唯一')
    start, end = text.index(START), text.index(END)
    return text[:start], text[start:end], text[end:]


def braced(text, offset):
    while offset < len(text) and text[offset].isspace():
        offset += 1
    if text[offset:offset+1] != '{':
        raise ValueError('AUX 花括号组缺失')
    start, depth = offset+1, 1
    offset += 1
    while offset < len(text):
        if text[offset] == '\\':
            offset += 2
            continue
        if text[offset] == '{':
            depth += 1
        elif text[offset] == '}':
            depth -= 1
            if depth == 0:
                return text[start:offset], offset+1
        offset += 1
    raise ValueError('AUX 花括号组未闭合')


def aux(path):
    result, text = {}, read(path)
    for match in re.finditer(r'\\newlabel\s*', text):
        name, end = braced(text, match.end())
        payload, _ = braced(text, end)
        number, end = braced(payload, 0)
        page, _ = braced(payload, end)
        if name in result:
            raise ValueError('重复 AUX 标签 '+name)
        result[name] = {'number':number, 'page':page}
    return result


def forbidden(*args, **kwargs):
    raise AssertionError('纯文案回归禁止IO、整稿生成、积分及拟合')


def import_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pure_regression(backup, function_name):
    source = ROOT/'reproducibility/paper_sync.py'
    module = import_module(source, 'sec9_wording_sync')
    old_module = import_module(backup/'reproducibility/paper_sync.py', 'sec9_wording_sync_before')
    reference = load(RESULTS/'xian/reference.json')
    fit = load(RESULTS/'xian/fit.json')
    critical = load(RESULTS/'population/critical.json')
    diagnostics = load(RESULTS/'population/diagnostics.json')
    difference = load(RESULTS/'xian/S2_difference.json')
    supplemental = load(RESULTS/'population/supplementary_anchors.json')
    with (RESULTS/'population/fixed_absolute_scale.csv').open(encoding='utf-8-sig', newline='') as stream:
        scale = list(csv.DictReader(stream))
    values = {'reference':reference, 'ref':reference, 'fit':fit, 'critical':critical, 'diagnostics':diagnostics,
              'pd':diagnostics, 'scale':scale, 'difference':difference, 'supplemental':supplemental}
    fn = getattr(module, function_name)
    localized = module._Editor(read(backup/'latex'/f'{MAIN}.tex'), read(backup/'latex'/f'{SI}.tex'))
    parameters = list(inspect.signature(fn).parameters)
    unknown = [name for name in parameters if name not in values]
    if unknown:
        raise ValueError('纯函数参数未绑定: '+str(unknown))
    arguments = [values[name] for name in parameters]
    snapshot = copy.deepcopy(arguments)
    original_import = builtins.__import__
    def checked_import(name, *args, **kwargs):
        if name.split('.')[0] in SCIENCE:
            return forbidden()
        return original_import(name, *args, **kwargs)
    with mock.patch.object(module, 'prepare_manuscript', forbidden), \
         mock.patch.object(module, '_json', forbidden), mock.patch.object(module, '_csv', forbidden), \
         mock.patch.object(Path, 'read_text', forbidden), mock.patch.object(Path, 'read_bytes', forbidden), \
         mock.patch.object(Path, 'write_text', forbidden), mock.patch.object(Path, 'write_bytes', forbidden), \
         mock.patch.object(Path, 'open', forbidden), mock.patch.object(Path, 'mkdir', forbidden), \
         mock.patch.object(builtins, 'open', forbidden), mock.patch.object(builtins, '__import__', checked_import), \
         mock.patch.object(subprocess, 'run', forbidden), mock.patch.object(subprocess, 'Popen', forbidden):
        prose = fn(*arguments)
        again = fn(*arguments)
        publication = module.publication_prose(reference, difference, supplemental)
        previous_publication = old_module.publication_prose(reference, difference, supplemental)
        module._sync_population_comparison(localized, reference, fit, critical)
    valid = isinstance(prose,dict) and bool(prose) and all(isinstance(v,str) for v in prose.values())
    science = sorted(k for k in sys.modules if k.split('.')[0] in SCIENCE)
    result = {'passed':valid and prose==again and arguments==snapshot and publication==previous_publication and not science,
              'function':function_name, 'parameter_names':parameters, 'keys':list(prose) if valid else [],
              'deterministic':prose==again, 'input_objects_unchanged':arguments==snapshot,
              'previous_eight_publication_prose_exact':publication==previous_publication,
              'localized_sync_entries':len(localized.changes),
              'localized_sync_raw_inputs_retained':all(item.get('unrounded_value') for item in localized.changes),
              'no_IO_no_prepare_manuscript_no_scientific_import':True, 'scientific_modules_imported':science,
              'source_sha256':sha(source), 'prior_source_sha256':sha(backup/'reproducibility/paper_sync.py'),
              'conditional_existing_results_not_a_fresh_scientific_run':True,
              'input_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in (
                  RESULTS/'xian/reference.json', RESULTS/'xian/fit.json', RESULTS/'population/critical.json', RESULTS/'population/diagnostics.json',
                  RESULTS/'population/fixed_absolute_scale.csv', RESULTS/'xian/S2_difference.json',
                  RESULTS/'population/supplementary_anchors.json')}}
    result['passed'] = result['passed'] and len(localized.changes)==14 and result['localized_sync_raw_inputs_retained']
    return prose, publication, result, localized.documents


def static_checks(backup, prose, publication, localized):
    old = read(backup/'latex'/f'{MAIN}.tex')
    new = read(LATEX/f'{MAIN}.tex')
    old_si, new_si = read(backup/'latex'/f'{SI}.tex'), read(LATEX/f'{SI}.tex')
    before, section_old, tail = split_section(old)
    after, section_new, tail_new = split_section(new)
    old_intro = [line for line in tail.splitlines() if line.startswith('本附录给出第')]
    new_intro = [line for line in tail_new.splitlines() if line.startswith('本附录给出第')]
    appendix = {'located_once':len(old_intro)==len(new_intro)==1, 'old':old_intro, 'new':new_intro}
    appendix['generated_by_pure_helper'] = bool(appendix['located_once'] and new_intro[0] in prose.values())
    normalized_tail = tail_new.replace(new_intro[0],old_intro[0],1) if appendix['generated_by_pure_helper'] else tail_new
    old_intersection='它与成本线的交点为'
    new_intersection='它与实际成本条件的数值交点约为'
    appendix['numeric_intersection_note']={'old_occurrences':tail.count(old_intersection),
                                         'new_occurrences':tail_new.count(new_intersection)}
    if tail.count(old_intersection)==tail_new.count(new_intersection)==1:
        normalized_tail=normalized_tail.replace(new_intersection,old_intersection,1)
    changes = [{'kind':kind,'old_lines':[i+1,j],'new_lines':[a+1,b],
                'old':'\n'.join(old.splitlines()[i:j]),'new':'\n'.join(new.splitlines()[a:b])}
               for kind,i,j,a,b in difflib.SequenceMatcher(a=old.splitlines(),b=new.splitlines(),autojunk=False).get_opcodes() if kind!='equal']
    numbered_old = envs(old, ('equation','align','gather','multline','eqnarray'))
    numbered_new = envs(new, ('equation','align','gather','multline','eqnarray'))
    math_changes = []
    math_valid = len(numbered_old)==len(numbered_new)
    for index,(a,b) in enumerate(zip(numbered_old,numbered_new)):
        if a==b:
            continue
        align = a.startswith(r'\begin{align}') and '峰值线' in a and '触发线' in a
        allowed = False
        if align:
            row_a, row_b = a.split(r'\\'), b.split(r'\\')
            allowed = len(row_a)==len(row_b)==4 and row_a[0]==row_b[0] \
                and a.count(r'\begin{align}')==b.count(r'\begin{align}')==1 \
                and a.count(r'\end{align}')==b.count(r'\end{align}')==1 and labels(a)==labels(b)
        if r'\label{eq:dom:main-interval}' in a:
            # 用户补充要求：候选跨度不再写成已认证的全区间成员条件。
            allowed = b==a.replace('  =\\bigl[', '  \\approx\\bigl[').replace(r'N_{\rm eff}\in', '')
        math_changes.append({'index':index,'labels':labels(a),'allowed':allowed,'old':a,'new':b})
        math_valid = math_valid and allowed and a in section_old and b in section_new
    publication_preserved = {key: value in new if key in ('S2_body_resolution','inflection_backsubstitution',
        'discussion_unified_integration','table4_source_navigation') else value in new_si for key,value in publication.items()}
    # 新文案必须确实进入正式第9节，避免仅生成器改了、正文仍是旧版。
    prose_present = {key:(value in section_new or (appendix['generated_by_pure_helper'] and value==new_intro[0])
                         or (key=='population_cumulative_arc_bridge' and value==new_intersection and tail_new.count(value)==1))
                     for key,value in prose.items()}
    tables_old = envs(old, ('table',))+envs(old_si, ('table',))
    tables_new = envs(new, ('table',))+envs(new_si, ('table',))
    figures_old,figures_new = envs(old,('figure','figure*')),envs(new,('figure','figure*'))
    # 图13只允许说明文字改动，不允许路径、宽度、标签及其余19幅图改变。
    figure_issues=[]
    for a,b in zip(figures_old,figures_new):
        if a==b:
            continue
        if r'\label{fig:dom}' not in a or not re.sub(r'\\caption\{.*\}(?=\s*\\label)', '<CAPTION>', a, flags=re.S)==re.sub(r'\\caption\{.*\}(?=\s*\\label)', '<CAPTION>', b, flags=re.S):
            figure_issues.append(labels(a))
    protected_starts = ('固定 $\\theta=0.002$，取', '在当前数值范围内，成本、时长和累计感染边界',
                        '由首次积分，$i_0$ 通过')
    findings={}
    for start in protected_starts:
        line=next((line for line in old.splitlines() if line.startswith(start)),None)
        findings[start]={'found_before':line is not None, 'retained_exact':bool(line and line in new)}
    old_tree,new_tree=ast.parse(read(backup/'reproducibility/paper_sync.py')),ast.parse(read(ROOT/'reproducibility/paper_sync.py'))
    protected_functions={node.name:ast.dump(node,include_attributes=False) for node in old_tree.body
                         if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name!='prepare_manuscript'}
    new_functions={node.name:ast.dump(node,include_attributes=False) for node in new_tree.body
                   if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
    function_unchanged={name:new_functions.get(name)==body for name,body in protected_functions.items()}
    old_classes={node.name:ast.dump(node,include_attributes=False) for node in old_tree.body if isinstance(node,ast.ClassDef)}
    new_classes={node.name:ast.dump(node,include_attributes=False) for node in new_tree.body if isinstance(node,ast.ClassDef)}
    def scientific_calls(tree):
        fn=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='prepare_manuscript')
        names={'structural','Params','quad','brentq','solve_ivp','integrate','fit_initial'}
        return [ast.dump(node,include_attributes=False) for node in ast.walk(fn)
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in names]
    checks={'outside_section9_and_approved_appendix_intro_exact':before==after and tail==normalized_tail,
            'appendix_intro_generated_or_unchanged':appendix['generated_by_pure_helper'] or tail==tail_new,
            'supplement_source_exact':old_si==new_si,
            'label_order_exact':labels(old)==labels(new) and labels(old_si)==labels(new_si),
            'numbered_math_count_preserved':len(numbered_old)==len(numbered_new), 'numbered_math_allowed_changes_only':math_valid,
            'all_proofs_exact':envs(old,('proof',))==envs(new,('proof',)),
            'all_numbered_theorem_statements_exact':envs(old,('theorem','lemma','proposition','corollaryn','remarkn'))==envs(new,('theorem','lemma','proposition','corollaryn','remarkn')),
            'seven_tables_entire_source_exact':len(tables_new)==7 and tables_old==tables_new,
            'twenty_figure_environments_only_caption13_changed':len(figures_new)==len(figures_old)==20 and not figure_issues,
            'citation_keys_exact':citations(old)==citations(new) and citations(old_si)==citations(new_si),
            'one_main_bibliography_only':new.count(r'\printbibliography')==1 and new_si.count(r'\printbibliography')==0,
            'capacity_additions_and_prior_sections_exact':before==after,
            'eight_audit_separation_texts_exact':all(publication_preserved.values()),
            'existing_pure_helpers_exact':all(function_unchanged.values()),
            'existing_editor_classes_exact':old_classes==new_classes,
            'whole_generator_scientific_calls_exact':scientific_calls(old_tree)==scientific_calls(new_tree),
            'localized_sync_exactly_reproduces_formal_text':localized=={'main':new,'supplement':new_si},
            'new_prose_matches_manuscript':all(prose_present.values()),
            'finite_tests_and_unfavorable_clearance_findings_exact':all(item['retained_exact'] for item in findings.values())}
    current_interval=next(block for block in numbered_new if r'\label{eq:dom:main-interval}' in block)
    checks.update({
        'candidate_interval_no_exact_membership_assertion':r'N_{\rm eff}\in' not in current_interval,
        'finite_duration_minimum_upper_bound_conditional_on_interval_structure':
            '仅当两项允许人口集合分别为' in section_new and '连续区间时' in section_new,
        'continuous_allowed_population_interval_explicitly_pending':
            '尚未确认整个人口允许集合的区间结构' in section_new and '连续允许区间尚待核查' in section_new,
        'numerical_root_not_promoted_to_global_upper_bound':
            '它是否构成整个人口允许集合的上界仍须核查' in section_new
            and '在此范围内，存在阈值使感染峰值不超过' not in section_new,
        'S0_and_Sc_change_with_N_explicit':
            r'S_c=\gamma N/[\beta c_0(1-q_0)]' in section_new and '均随 $N$ 改变' in section_new,
    })
    return {'passed':all(checks.values()),'checks':checks,'diff_hunks':changes,
            'numbered_math_count':len(numbered_new), 'numbered_math_changes':math_changes,
            'label_count':len(labels(new)), 'prose_present':prose_present,
            'audit_separation_preserved':publication_preserved,'existing_functions_unchanged':function_unchanged,
            'scientific_findings_protection':findings,'figure_issues':figure_issues,'approved_appendix_intro':appendix}


def protection(baseline):
    allowed=set(baseline['allowed_existing_changes'])
    changes,unexpected,figures=[],[],[]
    for item in baseline['protected_files']:
        path=ROOT/item['file']
        current=sha(path) if path.is_file() else None
        if item['file'].startswith('latex/figures/') and path.suffix.lower()=='.pdf':
            figures.append({'file':item['file'],'passed':current==item['sha256']})
        if current!=item['sha256']:
            record={'file':item['file'],'before_sha256':item['sha256'],'after_sha256':current}
            changes.append(record)
            if item['file'] not in allowed:
                unexpected.append(record)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    return {'passed':not unexpected and len(figures)==20 and all(item['passed'] for item in figures) and head==baseline['head'],
            'protected_count':len(baseline['protected_files']),'unexpected_changes':unexpected,'allowed_changes':changes,
            'formal_figure_count':len(figures),'formal_figures':figures,'git_head_unchanged':head==baseline['head']}


def complete_checks(backup):
    numbering,logs,documents={},{},{}
    for stem in (MAIN,SI):
        before,after=aux(backup/'latex'/f'{stem}.aux'),aux(LATEX/f'{stem}.aux')
        differences=[{'label':key,'before':value['number'],'after':after.get(key,{}).get('number')}
                     for key,value in before.items() if value['number']!=after.get(key,{}).get('number')]
        numbering[stem]={'passed':not differences and set(before)==set(after),'checked_labels':len(before),'differences':differences}
        text=read(LATEX/f'{stem}.log')
        errors=[line for line in text.splitlines() if re.search(r'undefined|Missing character|Overfull|Float too large|multiply defined|^!|(?:LaTeX|Package \S+) Error:',line,re.I)]
        warnings=[line for line in text.splitlines() if 'Warning' in line]
        underfull=[line for line in text.splitlines() if 'Underfull' in line]
        complete=bool(re.search(r'Output written on .*\.pdf \(\d+ pages?',text))
        logs[stem]={'passed':complete and not errors and not warnings,'errors':errors,'warnings':warnings,
                    'underfull_boxes_for_manual_review':underfull,'underfull_not_silently_treated_as_overflow':True,
                    'complete_pdf':complete}
    blg=read(LATEX/f'{MAIN}.blg')
    warnings=[line for line in blg.splitlines() if re.search(r'WARN|ERROR',line)]
    logs['biber']={'passed':not warnings and 'Writing' in blg and '.bbl' in blg,'warnings':warnings}
    keys=sorted(set(re.findall(r'\\entry\{([^}]+)\}',read(LATEX/f'{MAIN}.bbl'))))
    expected=citations(read(backup/'latex'/f'{MAIN}.tex'))
    seeds,bibliography_pages=[],[]
    for stem in (MAIN,SI):
        outside,placeholders=[],[]
        with pymupdf.open(LATEX/f'{stem}.pdf') as doc:
            count=len(doc)
            for index,page in enumerate(doc):
                text=page.get_text()
                if '[?]' in text or '??' in text:
                    placeholders.append(index+1)
                if stem==MAIN and '参考文献' in text:
                    bibliography_pages.append(index+1)
                for block in page.get_text('dict')['blocks']:
                    for line in block.get('lines',[]):
                        for span in line.get('spans',[]):
                            if span['text'].strip() and not (page.rect+(-1,-1,1,1)).contains(pymupdf.Rect(span['bbox'])):
                                outside.append({'page':index+1,'text':span['text'],'bbox':span['bbox']})
        documents[stem]={'passed':not outside and not placeholders,'page_count':count,'sha256':sha(LATEX/f'{stem}.pdf'),
                         'outside_page_text':outside,'unresolved_placeholders_pages':placeholders}
    current_aux=aux(LATEX/f'{MAIN}.aux')
    for key in ('sec:dominance','sec:dom:setup','sec:dom:theory','sec:dom:xian','fig:dom','eq:dom:main-interval','sec:dom:limits',
                'app:dom:numerics','app:reference-comparison'):
        seeds.append(int(current_aux[key]['page']))
    page_count=documents[MAIN]['page_count']
    section_start=int(current_aux['sec:dominance']['page'])
    section_end=int(current_aux['sec:discussion']['page'])
    details=sorted(set(range(max(1,section_start-1),min(page_count,section_end+1)+1)) \
                   | {p for seed in seeds+bibliography_pages for p in (seed-1,seed,seed+1) if 1<=p<=page_count})
    bibliography={'passed':keys==expected and len(keys)==20 and bool(bibliography_pages),'printed_count':len(keys),
                  'keys':keys,'heading_pages':bibliography_pages}
    backup_counts={}
    for stem in (MAIN,SI):
        with pymupdf.open(backup/'latex'/f'{stem}.pdf') as backup_doc:
            backup_counts[stem]=len(backup_doc)
    return {'passed':all(row['passed'] for row in numbering.values()) and all(row['passed'] for row in logs.values())
                     and all(row['passed'] for row in documents.values()) and bibliography['passed'],
            'actual_numbering':numbering,'build_logs':logs,'documents':documents,'bibliography':bibliography,
            'main_detail_pages':details,'page_counts_from_backup':backup_counts}


def render(documents,detail_pages):
    poppler=shutil.which('pdftoppm')
    if not poppler:
        raise FileNotFoundError('找不到 Poppler pdftoppm')
    qa=REPORT/'qa'
    qa.mkdir(exist_ok=True)
    montages,images=[],{}
    for stem,prefix in ((MAIN,'main'),(SI,'supplement')):
        count=documents[stem]['page_count']
        subprocess.run([poppler,'-r','120','-png',str(LATEX/f'{stem}.pdf'),str(qa/prefix)],
                       check=True,timeout=180,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        files=sorted(qa.glob(prefix+'-*.png'))
        if len(files)!=count:
            raise ValueError(f'{prefix} 渲染页数不符')
        images[prefix]=[path.relative_to(REPORT).as_posix() for path in files]
        for start in range(0,count,8):
            group=files[start:start+8]
            sheet=Image.new('RGB',(1500,1120),'#dedede')
            draw=ImageDraw.Draw(sheet)
            for index,path in enumerate(group):
                with Image.open(path) as page:
                    page.thumbnail((355,520))
                    x,y=index%4*375+10,index//4*560+30
                    sheet.paste(page,(x,y))
                    draw.text((x,y-22),f'{prefix}: page {start+index+1}',fill='black')
            target=qa/f'{prefix}_overview_{start+1:02d}_{start+len(group):02d}.png'
            sheet.save(target)
            montages.append(target.relative_to(REPORT).as_posix())
    return {'renderer':'Poppler pdftoppm 120dpi','all_document_pages_rendered':images,'overview_montages':montages,
            'main_detail_pages':detail_pages,'supplement_detail_pages':list(range(1,documents[SI]['page_count']+1)),
            'independent_manual_review':'pending','root_manual_review':'pending'}


def run(args):
    baseline=load(REPORT/'baseline.json')
    backup=ROOT/baseline['backup']
    prose,publication,regression,localized=pure_regression(backup,args.prose_function)
    result={'passed':False,'nature_skills_used':False,'full_numerical_rerun':False,'compile_started_by_verifier':False,
            'scope':'第9节局部文案及已有输出的纯函数回归、保护和编译产物核查，不认证边界渐近证明。',
            'continuous_allowed_population_interval_certification':'not_performed_pending',
            'candidate_roots_are_not_full_interval_certification':True,
            'prose_regression':regression,'static':static_checks(backup,prose,publication,localized),'protection':protection(baseline)}
    fields=['prose_regression','static','protection']
    if args.phase=='complete':
        result['compiled']=complete_checks(backup)
        result['visual_review']=render(result['compiled']['documents'],result['compiled']['main_detail_pages'])
        fields.append('compiled')
    result['failures']=[key for key in fields if not result[key]['passed']]
    result['passed']=not result['failures']
    result['acceptance_status']=('automated_pass_manual_pending' if args.phase=='complete' else 'static_pass_build_pending') if result['passed'] else 'failed'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=('static','complete'),default='static')
    parser.add_argument('--prose-function',default='population_comparison_prose')
    args=parser.parse_args()
    try:
        result=run(args)
    except Exception as exc:
        result={'passed':False,'error':str(exc),'traceback':traceback.format_exc(),'nature_skills_used':False,
                'full_numerical_rerun':False,'compile_started_by_verifier':False,'acceptance_status':'failed'}
    target=REPORT/('verification.json' if args.phase=='complete' else 'verification_static.json')
    dump(target,result)
    print(json.dumps({key:result.get(key) for key in ('passed','failures','error','acceptance_status')},ensure_ascii=False))
    sys.exit(0 if result['passed'] else 1)
