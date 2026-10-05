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
from manuscript_version import inventory,freeze_current_version,load_version,expected_figures
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

    def freeze(self,approved_tasks=None):
        return freeze_current_version(self.root,'approved_test',approved_tasks=approved_tasks or ['A'],textwidth_bp=451.275616438,
                inherited_science='reproducibility/results/accepted',baseline_main=self.baseline,
                original_figure_hashes={'old.pdf':self.old_hash})

    def test_version_and_asset_identity(self):
        self.freeze(approved_tasks=['A','B','C'])
        version=load_version(self.root,required=True)
        self.assertTrue(version['protected_previous_revision']['sec9_byte_preserved'])
        self.assertEqual(expected_figures(self.root)[0]['label'],'fig:old')

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
