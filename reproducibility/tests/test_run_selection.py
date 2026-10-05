"""显式选择新运行的实际守卫测试；假报告不代表科学计算通过。"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from manuscript_version import freeze_current_version
from run_selection import load_selection, select_runs, selected_directories


class RunSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='accepted_run_guard_')
        self.root=Path(self.temp.name)
        self.parent=self.root/'reproducibility/runs/new_version'
        self.parent.mkdir(parents=True)
        (self.root/'latex').mkdir()
        (self.root/'latex/flatten_curve_analysis_cn.tex').write_text(r'\section{模型}\label{sec:test}',encoding='utf-8')
        (self.root/'latex/flatten_curve_supplement_cn.tex').write_text('',encoding='utf-8')
        (self.root/'reproducibility/results/accepted').mkdir(parents=True)
        self.version=freeze_current_version(self.root,'fixture_approved',approved_tasks=list('ABC'),
            textwidth_bp=451.275616438,inherited_science='reproducibility/results/accepted')
        for name in ('run_5','run_6'):
            self.make_run(name)
        self.make_run('run_1',passed=False)
        self.make_run('run_2',passed=False)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, run, name, value):
        path=run/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value),encoding='utf-8')

    def make_run(self,name,passed=True):
        run=self.parent/name
        self.write(run,'run_report.json',{'passed':passed,'numerical_and_build_complete':passed,
            'manuscript_version':'fixture_approved','scientific_scope':'joint-extra',
            'inherited_old_science':True,'approved_tasks':list('ABC')})
        self.write(run,'document/build_report.json',{'passed':passed})
        self.write(run,'registry.json',{'structure_passed':passed})
        integrity={'passed':True,'runner_source_hashes':{'core.py':'test-code-hash'},
            'static_art_assets':{},'raw_inputs':{'raw.xlsx':'test-input-hash'},
            'source_input_hashes':{},'frozen_manifest_sha256':'test-frozen-hash'}
        for path in ('validation/source_integrity_initial.json','validation/source_integrity.json'):
            self.write(run,path,integrity)
        self.write(run,'manuscript_changes.json',{'passed':passed,
            'source_sha256':{role:item['sha256'] for role,item in self.version['documents'].items()}})
        self.write(run,'joint_extra/input_manifest.json',{'schema':'joint-extra-v2','inputs':{'ref':'same-input'},
            'cases':{'baseline':{'parameters':{'N':763,'I0':1}}},'calculation_source_hashes':{'core.py':'same-code'},
            'acceptance':{'error':1e-5},'settings':{'wc':1,'wq':2},'software':{'python':'test'},'tasks_requested':list('ABCD')})
        self.write(run,'joint_extra/validation.json',{'passed':False,
            'tasks':{key:{'passed':key!='D'} for key in 'ABCD'}})
        return run

    def select(self,names=None):
        return select_runs(self.parent,names or ['run_5','run_6'],self.root)

    def test_true_run_names_selected_and_failed_old_runs_unchanged(self):
        old={name:(self.parent/name/'run_report.json').read_bytes() for name in ('run_1','run_2')}
        before={p.name for p in self.parent.iterdir()}
        result=self.select()
        self.assertEqual([item['name'] for item in result['runs']],['run_5','run_6'])
        self.assertEqual(selected_directories(self.parent,self.root),(self.parent/'run_5',self.parent/'run_6'))
        self.assertEqual(before|{'accepted_runs.json'},{p.name for p in self.parent.iterdir()})
        self.assertEqual(old,{name:(self.parent/name/'run_report.json').read_bytes() for name in ('run_1','run_2')})

    def test_missing_selection_has_no_implicit_old_run_fallback(self):
        with self.assertRaisesRegex(FileNotFoundError,'不默认读取旧'):
            load_selection(self.parent,self.root)

    def test_failed_old_run_cannot_be_selected(self):
        with self.assertRaisesRegex(RuntimeError,'未完成机器验收'):
            self.select(['run_1','run_6'])
        self.assertFalse((self.parent/'accepted_runs.json').exists())

    def test_duplicate_or_out_of_scope_run_rejected(self):
        with self.assertRaises(ValueError):self.select(['run_5','run_5'])
        with self.assertRaises(ValueError):self.select(['../run_5','run_6'])

    def test_different_source_identity_rejected(self):
        for path in ('validation/source_integrity_initial.json','validation/source_integrity.json'):
            target=self.parent/'run_6'/path
            value=json.loads(target.read_text(encoding='utf-8'))
            value['runner_source_hashes']['core.py']='different-code'
            self.write(self.parent/'run_6',path,value)
        with self.assertRaisesRegex(RuntimeError,'身份不一致'):
            self.select()

    def test_different_parameters_rejected(self):
        path=self.parent/'run_6/joint_extra/input_manifest.json'
        value=json.loads(path.read_text(encoding='utf-8'))
        value['cases']['baseline']['parameters']['I0']=2
        self.write(self.parent/'run_6','joint_extra/input_manifest.json',value)
        with self.assertRaisesRegex(RuntimeError,'身份不一致'):
            self.select()

    def test_report_changed_after_selection_rejected(self):
        self.select()
        path=self.parent/'run_6/run_report.json'
        value=json.loads(path.read_text(encoding='utf-8'));value['passed']=False
        self.write(self.parent/'run_6','run_report.json',value)
        with self.assertRaisesRegex(RuntimeError,'验收报告或输入发生变化'):
            load_selection(self.parent,self.root)

    def test_selection_is_one_shot_and_does_not_copy_results(self):
        self.select()
        path=self.parent/'accepted_runs.json';before=path.read_bytes()
        with self.assertRaises(FileExistsError):self.select(['run_6','run_5'])
        self.assertEqual(before,path.read_bytes())
        self.assertFalse((self.parent/'run_5_copy').exists())


if __name__=='__main__':unittest.main()
