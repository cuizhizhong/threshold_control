"""隔离编译文献来源的接口测试；不执行TeX、不生成科学数据。"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import build


class BuildBibliographyTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='build_bibliography_')
        self.root=Path(self.temporary.name)
        latex=self.root/'latex'
        (latex/'figures').mkdir(parents=True)
        for name in ('flatten_curve_analysis_cn.tex','flatten_curve_supplement_cn.tex','elegantpaper.cls'):
            (latex/name).write_text('% isolated interface fixture',encoding='utf-8')
        self.default=latex/'references.bib'
        self.default.write_bytes(b'@article{Old2021,year={2021}}\n')
        self.candidate=self.root/'candidate.bib'
        self.candidate.write_bytes(b'@article{New2021,year={2021}}\n')
        self.output=self.root/'isolated_output'

    def tearDown(self):
        self.temporary.cleanup()

    def stop_before_tex(self,**kwargs):
        with patch('build.shutil.which',return_value=None), patch('build.subprocess.run') as process:
            with self.assertRaisesRegex(FileNotFoundError,'未找到 xelatex'):
                build.run(self.output,self.root,**kwargs)
            process.assert_not_called()

    def test_default_keeps_current_project_bibliography(self):
        self.stop_before_tex()
        self.assertEqual((self.output/'document/latex/references.bib').read_bytes(),self.default.read_bytes())

    def test_explicit_bibliography_copied_without_formal_overwrite(self):
        before=self.default.read_bytes()
        self.stop_before_tex(bibliography_path=self.candidate)
        self.assertEqual((self.output/'document/latex/references.bib').read_bytes(),self.candidate.read_bytes())
        self.assertEqual(self.default.read_bytes(),before)

    def test_explicit_source_does_not_require_default_bibliography(self):
        self.default.unlink()
        self.stop_before_tex(bibliography_path=self.candidate)
        self.assertEqual((self.output/'document/latex/references.bib').read_bytes(),self.candidate.read_bytes())

    def test_relative_explicit_source_is_resolved_against_project_root(self):
        self.stop_before_tex(bibliography_path=Path('candidate.bib'))
        self.assertEqual((self.output/'document/latex/references.bib').read_bytes(),self.candidate.read_bytes())

    def test_missing_explicit_source_rejected_without_default_fallback_or_tex(self):
        with patch('build.subprocess.run') as process:
            with self.assertRaisesRegex(FileNotFoundError,'编译文献库缺失'):
                build.run(self.output,self.root,bibliography_path=self.root/'missing.bib')
            process.assert_not_called()
        self.assertFalse((self.output/'document/latex/references.bib').exists())
        failure=json.loads((self.output/'document/build_report.json').read_text(encoding='utf-8'))
        self.assertFalse(failure['passed'])

    def test_missing_default_rejected_without_tex(self):
        self.default.unlink()
        with patch('build.subprocess.run') as process:
            with self.assertRaisesRegex(FileNotFoundError,'编译文献库缺失'):
                build.run(self.output,self.root)
            process.assert_not_called()

    def test_public_wrapper_forwards_explicit_source(self):
        with patch('build._run',return_value={'passed':True}) as inner:
            result=build.run(self.output,self.root,bibliography_path=self.candidate)
        self.assertTrue(result['passed'])
        self.assertEqual(inner.call_args.kwargs['bibliography_path'],self.candidate)


if __name__=='__main__':
    unittest.main()
