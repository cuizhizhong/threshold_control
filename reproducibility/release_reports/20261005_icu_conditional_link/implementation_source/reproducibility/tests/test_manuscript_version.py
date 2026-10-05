"""受控稿源的实际小样本正/负例；不运行科学计算或正式发布。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from manuscript_version import inventory,freeze_current_version,load_version,expected_figures,activate_version,sha,version_bibliography,version_texts
from paper_sync import prepare_manuscript


MAIN=r'''\section{联合控制}\label{sec:joint}
\begin{figure}\includegraphics{figures/old.pdf}\caption{旧图}\label{fig:old}\end{figure}
\begin{table}\caption{旧表}\label{tab:old}\end{table}
\section{比较}\label{sec:dominance}
固定绝对初值，按实际指标判断。
\section{结论}\label{sec:discussion}
'''


class VersionGuardTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='joint_version_guard_')
        self.root=Path(self.temporary.name)
        (self.root/'latex/figures').mkdir(parents=True)
        (self.root/'latex/flatten_curve_analysis_cn.tex').write_text(MAIN,encoding='utf-8')
        (self.root/'latex/flatten_curve_supplement_cn.tex').write_text(r'\begin{table}\label{tab:sup:test}\end{table}',encoding='utf-8')
        (self.root/'latex/figures/old.pdf').write_bytes(b'test asset, not a real PDF')
        self.old_hash=hashlib.sha256((self.root/'latex/figures/old.pdf').read_bytes()).hexdigest()
        self.baseline=self.root/'before.tex'
        self.baseline.write_text(MAIN,encoding='utf-8')
        (self.root/'reproducibility/results/accepted').mkdir(parents=True)
        (self.root/'reproducibility/results/accepted/reference.json').write_text('{"I0":0.001}',encoding='utf-8')

    def tearDown(self):
        self.temporary.cleanup()

    def freeze(self,approved_tasks=None,version_id='approved_test',**kwargs):
        return freeze_current_version(self.root,version_id,approved_tasks=approved_tasks or ['A'],textwidth_bp=451.275616438,
                inherited_science='reproducibility/results/accepted',baseline_main=self.baseline,
                original_figure_hashes={'old.pdf':self.old_hash},**kwargs)

    def staged_sources(self):
        stage=self.root/'reproducibility/stage/latex'
        stage.mkdir(parents=True)
        sources={role:stage/name for role,name in [('main','flatten_curve_analysis_cn.tex'),
                                                 ('supplement','flatten_curve_supplement_cn.tex')]}
        sources['main'].write_text(MAIN.replace('联合控制','联合控制新文案'),encoding='utf-8')
        sources['supplement'].write_text(r'\begin{table}\label{tab:sup:test}\end{table}',encoding='utf-8')
        return sources

    def new_pending_version(self):
        sources=self.staged_sources()
        self.freeze(version_id='pending',activate=False,source_paths=sources,
                    generated_figure_labels=['fig:old'],publication_cost_digits=4)
        return sources,self.root/'reproducibility/manuscript_versions/pending/manifest.json'

    def activate(self,manifest,expected_current=None):
        return activate_version(self.root,'pending',expected_current_sha256=expected_current,
                                expected_manifest_sha256=sha(manifest),approval_reason='测试显式批准')

    def test_version_and_asset_identity(self):
        self.freeze(approved_tasks=['A','B','C'])
        version=load_version(self.root,required=True)
        self.assertTrue(version['protected_previous_revision']['sec9_byte_preserved'])
        self.assertEqual(expected_figures(self.root)[0]['label'],'fig:old')

    def test_default_still_rejects_existing_pointer(self):
        self.freeze()
        with self.assertRaisesRegex(FileExistsError,'活动指针已存在'):
            self.freeze(version_id='another')
        self.assertFalse((self.root/'reproducibility/manuscript_versions/another').exists())

    def test_pending_stage_snapshot_preserves_current_and_formal_sources(self):
        self.freeze()
        pointer=self.root/'reproducibility/manuscript_versions/current.json'
        before=pointer.read_bytes()
        formal=(self.root/'latex/flatten_curve_analysis_cn.tex').read_bytes()
        sources,manifest=self.new_pending_version()
        self.assertEqual(before,pointer.read_bytes())
        self.assertEqual(formal,(self.root/'latex/flatten_curve_analysis_cn.tex').read_bytes())
        data=json.loads(manifest.read_text(encoding='utf-8'))
        self.assertEqual(data['documents']['main']['origin'],sources['main'].relative_to(self.root).as_posix())
        self.assertEqual(data['generated_figure_labels'],['fig:old'])
        self.assertEqual(data['publication_cost_digits'],4)
        self.assertTrue(data['protected_previous_revision']['sec9_byte_preserved'])
        with self.assertRaisesRegex(FileExistsError,'目录已存在'):
            self.freeze(version_id='pending',activate=False)

    def test_explicit_pending_read_does_not_change_pointer_or_old_return_shape(self):
        self.freeze()
        pointer=self.root/'reproducibility/manuscript_versions/current.json'
        before=pointer.read_bytes()
        _,manifest=self.new_pending_version()
        version=load_version(self.root,version_id='pending',expected_manifest_sha256=sha(manifest))
        self.assertEqual(version['version'],'pending')
        self.assertEqual(len(version_texts(version)),2)
        self.assertEqual(pointer.read_bytes(),before)
        self.assertEqual(load_version(self.root)['version'],'approved_test')
        self.assertIsNone(version_bibliography(version))

    def test_explicit_pending_read_requires_version_and_hash_pair(self):
        _,manifest=self.new_pending_version()
        for kwargs in ({'version_id':'pending'},
                       {'version_id':'pending','expected_manifest_sha256':'invalid'},
                       {'expected_manifest_sha256':sha(manifest)}):
            with self.assertRaises(ValueError):
                load_version(self.root,**kwargs)
        with self.assertRaisesRegex(RuntimeError,'清单改变'):
            load_version(self.root,version_id='pending',expected_manifest_sha256='0'*64)
        with self.assertRaisesRegex(ValueError,'非法版本标识'):
            load_version(self.root,version_id='../pending',expected_manifest_sha256=sha(manifest))

    def test_pending_bibliography_snapshot_is_bound_and_default_remains_compatible(self):
        self.freeze()
        self.assertIsNone(version_bibliography(load_version(self.root)))
        sources=self.staged_sources()
        bibliography=sources['main'].parent/'new_references.bib'
        original=b'@article{Existing2021, title={Original reference}, year={2021}}\n'
        bibliography.write_bytes(original)
        self.freeze(version_id='pending',activate=False,source_paths=sources,bibliography_path=bibliography)
        manifest=self.root/'reproducibility/manuscript_versions/pending/manifest.json'
        version=load_version(self.root,version_id='pending',expected_manifest_sha256=sha(manifest))
        self.assertEqual(version['bibliography']['origin'],bibliography.relative_to(self.root).as_posix())
        self.assertEqual(version_bibliography(version).read_bytes(),original)
        self.assertEqual(version['bibliography']['sha256'],sha(bibliography))

    def test_bibliography_missing_changed_and_origin_changed_are_rejected(self):
        self.freeze()
        pointer=self.root/'reproducibility/manuscript_versions/current.json'
        old=pointer.read_bytes()
        sources=self.staged_sources()
        bibliography=sources['main'].parent/'references.bib'
        bibliography.write_text('@article{Existing2021,year={2021}}',encoding='utf-8')
        self.freeze(version_id='pending',activate=False,source_paths=sources,bibliography_path=bibliography)
        manifest=self.root/'reproducibility/manuscript_versions/pending/manifest.json'
        version=load_version(self.root,version_id='pending',expected_manifest_sha256=sha(manifest))
        snapshot=version_bibliography(version)
        saved=snapshot.read_bytes()
        snapshot.write_bytes(saved+b'% changed')
        with self.assertRaisesRegex(RuntimeError,'受控文献库缺失或改变'):
            load_version(self.root,version_id='pending',expected_manifest_sha256=sha(manifest))
        with self.assertRaisesRegex(RuntimeError,'受控文献库缺失或改变'):
            version_bibliography(version)
        snapshot.unlink()
        with self.assertRaisesRegex(RuntimeError,'受控文献库缺失或改变'):
            load_version(self.root,version_id='pending',expected_manifest_sha256=sha(manifest))
        snapshot.write_bytes(saved)
        bibliography.write_bytes(saved+b'% origin changed')
        with self.assertRaisesRegex(RuntimeError,'文献库的本地来源改变'):
            self.activate(manifest,expected_current=sha(pointer))
        self.assertEqual(pointer.read_bytes(),old)

    def test_bibliography_missing_or_unapproved_source_rejected_before_snapshot_creation(self):
        missing=self.root/'reproducibility/missing.bib'
        with self.assertRaisesRegex(FileNotFoundError,'本地文献库缺失'):
            self.freeze(activate=False,bibliography_path=missing)
        ai=self.root/'ai/references.bib'
        ai.parent.mkdir()
        ai.write_text('@article{candidate,year={2021}}',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'不得取AI来源'):
            self.freeze(activate=False,bibliography_path=ai)
        with tempfile.TemporaryDirectory() as outside:
            external=Path(outside)/'references.bib'
            external.write_text('@article{candidate,year={2021}}',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'项目内本地工作副本'):
                self.freeze(activate=False,bibliography_path=external)
        self.assertFalse((self.root/'reproducibility/manuscript_versions/approved_test').exists())

    def test_explicit_activation_keeps_old_pointer_backup_and_receipt(self):
        self.freeze()
        pointer=self.root/'reproducibility/manuscript_versions/current.json'
        old=pointer.read_bytes()
        _,manifest=self.new_pending_version()
        receipt=self.activate(manifest,expected_current=sha(pointer))
        self.assertEqual(load_version(self.root)['version'],'pending')
        self.assertEqual(receipt['status'],'activated')
        self.assertEqual((self.root/receipt['previous_pointer_backup']).read_bytes(),old)
        self.assertTrue(receipt['_receipt_path'].is_file())
        self.assertFalse(pointer.with_suffix('.activation.lock').exists())

    def test_wrong_pointer_hash_and_concurrent_lock_reject_activation(self):
        self.freeze()
        pointer=self.root/'reproducibility/manuscript_versions/current.json'
        old=pointer.read_bytes()
        _,manifest=self.new_pending_version()
        with self.assertRaisesRegex(RuntimeError,'活动指针哈希'):
            self.activate(manifest,expected_current='0'*64)
        self.assertEqual(pointer.read_bytes(),old)
        lock=pointer.with_suffix('.activation.lock')
        lock.write_text('other caller',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'另一次版本批准'):
            self.activate(manifest,expected_current=sha(pointer))
        self.assertEqual(pointer.read_bytes(),old)
        self.assertTrue(lock.exists())

    def test_origin_changed_after_snapshot_rejects_activation(self):
        self.freeze()
        pointer=self.root/'reproducibility/manuscript_versions/current.json'
        before=pointer.read_bytes()
        sources,manifest=self.new_pending_version()
        sources['main'].write_text(MAIN,encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'本地来源改变'):
            self.activate(manifest,expected_current=sha(pointer))
        self.assertEqual(pointer.read_bytes(),before)

    def test_snapshot_and_reference_changed_reject_activation(self):
        self.freeze()
        pointer=self.root/'reproducibility/manuscript_versions/current.json'
        _,manifest=self.new_pending_version()
        snapshot=manifest.parent/'flatten_curve_analysis_cn.tex'
        original=snapshot.read_bytes()
        snapshot.write_bytes(original+b'% changed')
        with self.assertRaisesRegex(RuntimeError,'受控稿源缺失或改变'):
            self.activate(manifest,expected_current=sha(pointer))
        snapshot.write_bytes(original)
        (self.root/'reproducibility/results/accepted/reference.json').write_text('{"I0":2}',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'继承的已验收科学输出改变'):
            self.activate(manifest,expected_current=sha(pointer))

    def test_source_paths_outside_project_and_ai_rejected(self):
        sources=self.staged_sources()
        ai=self.root/'ai/candidate.tex'
        ai.parent.mkdir()
        ai.write_text(MAIN,encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'不得取AI整稿'):
            self.freeze(activate=False,source_paths={**sources,'main':ai})
        with self.assertRaisesRegex(ValueError,'同时给出'):
            self.freeze(activate=False,source_paths={'main':sources['main']})
        with tempfile.TemporaryDirectory() as outside:
            external=Path(outside)/'draft.tex'
            external.write_text(MAIN,encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'项目内本地工作副本'):
                self.freeze(activate=False,source_paths={**sources,'main':external})

    def test_stage_sec9_changes_rejected_even_when_formal_unchanged(self):
        sources=self.staged_sources()
        sources['main'].write_text(MAIN.replace('固定绝对','固定归一化'),encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'第9节保护段改变'):
            self.freeze(activate=False,source_paths=sources)

    def test_generation_metadata_rejects_unknown_labels_and_cost_digits(self):
        with self.assertRaisesRegex(ValueError,'正式图子集'):
            self.freeze(activate=False,generated_figure_labels=['fig:missing'])
        with self.assertRaisesRegex(ValueError,'四位小数'):
            self.freeze(activate=False,publication_cost_digits=2)

    def test_source_tamper_rejected(self):
        self.freeze()
        source=self.root/'reproducibility/manuscript_versions/approved_test/flatten_curve_analysis_cn.tex'
        source.write_text(MAIN+'changed',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'受控稿源缺失或改变'):
            load_version(self.root)

    def test_reference_tamper_rejected(self):
        self.freeze()
        (self.root/'reproducibility/results/accepted/reference.json').write_text('{"I0":1}',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'继承的已验收科学输出改变'):
            load_version(self.root)

    def test_old_asset_and_sec9_changes_rejected(self):
        (self.root/'latex/figures/old.pdf').write_bytes(b'changed')
        with self.assertRaisesRegex(RuntimeError,'原正式图件改变'):
            self.freeze()
        (self.root/'latex/figures/old.pdf').write_bytes(b'test asset, not a real PDF')
        (self.root/'latex/flatten_curve_analysis_cn.tex').write_text(MAIN.replace('固定绝对','固定归一化'),encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'第9节保护段改变'):
            self.freeze()

    def test_duplicate_labels_rejected(self):
        with self.assertRaisesRegex(ValueError,'重复标签'):
            inventory(MAIN+r'\label{fig:old}')

    def test_no_version_fallback_is_explicit(self):
        self.assertIsNone(load_version(self.root))
        with self.assertRaises(FileNotFoundError):
            load_version(self.root,required=True)

    def test_new_local_manuscript_cannot_fallback_without_version(self):
        path=self.root/'latex/flatten_curve_analysis_cn.tex'
        path.write_text(MAIN+'\n% BEGIN JOINT_EXTRA:comparison\n% END JOINT_EXTRA:comparison\n',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'缺少受控版本'):
            prepare_manuscript(self.root,self.root/'run')
        self.assertFalse((self.root/'run').exists())

    def sync_fixture(self):
        text=MAIN.replace('\\section{联合控制}', '% BEGIN JOINT_EXTRA:comparison\n旧文案\n% END JOINT_EXTRA:comparison\n\\section{联合控制}')
        (self.root/'latex/flatten_curve_analysis_cn.tex').write_text(text,encoding='utf-8')
        reference=self.root/'reproducibility/results/accepted'
        for name in ['xian/reference.json','xian/fit.json','population/critical.json','c0/extrema.json','joint/results.json']:
            path=reference/name;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text('{"value":1}',encoding='utf-8')
        self.freeze(approved_tasks=['A','B','C'])
        output=self.root/'run'
        extra=output/'joint_extra';extra.mkdir(parents=True)
        (extra/'validation.json').write_text(json.dumps({'passed':False,'tasks':{'A':{'passed':True},'B':{'passed':True},'C':{'passed':True},'D':{'passed':False}}}),encoding='utf-8')
        return output,reference

    def test_partial_publication_preserves_failed_D_record(self):
        output,reference=self.sync_fixture()
        with patch('joint_extra.manuscript.build_publication_fragments',return_value={'comparison':'本轮文案'}):
            text,_,report=prepare_manuscript(self.root,output,scientific_reference=reference)
        self.assertIn('本轮文案',text)
        self.assertTrue(report['passed'])
        self.assertFalse(report['validation_overall_passed'])
        self.assertTrue(report['inherited_science']['used'])

    def test_missing_same_run_reference_has_no_fallback(self):
        output,_=self.sync_fixture()
        with self.assertRaisesRegex(FileNotFoundError,'依据缺失'):
            prepare_manuscript(self.root,output)


if __name__=='__main__':
    unittest.main()
