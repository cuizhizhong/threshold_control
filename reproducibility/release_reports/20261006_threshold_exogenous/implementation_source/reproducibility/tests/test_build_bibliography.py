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

    def test_explicit_build_script_copied_and_forwarded(self):
        candidate=self.root/'candidate_build.ps1'
        candidate.write_bytes(b'# controlled build script\r\n')
        self.stop_before_tex(build_script_path=candidate)
        self.assertEqual((self.output/'document/latex/build_paper.ps1').read_bytes(),candidate.read_bytes())
        with patch('build._run',return_value={'passed':True}) as inner:
            build.run(self.output,self.root,build_script_path=candidate)
        self.assertEqual(inner.call_args.kwargs['build_script_path'],candidate)

    def test_missing_explicit_build_script_rejected_without_default_fallback(self):
        (self.root/'latex/build_paper.ps1').write_text('# local default',encoding='utf-8')
        with patch('build.subprocess.run') as process:
            with self.assertRaisesRegex(FileNotFoundError,'受控编译脚本缺失'):
                build.run(self.output,self.root,build_script_path=self.root/'missing.ps1')
            process.assert_not_called()

    def test_bibliography_supplement_uses_full_chain_before_main(self):
        texts={build.STEMS[0]:r'\cite{New2021}\printbibliography',
               build.STEMS[1]:r'\cite{Old2021}\printbibliography'}
        jobs=build._document_jobs(texts)
        self.assertEqual([job[0] for job in jobs],['xelatex','biber','xelatex','xelatex']*2)
        self.assertEqual(jobs[1],['biber',build.STEMS[0]])
        self.assertEqual(jobs[5],['biber',build.STEMS[1]])

    def test_legacy_supplement_retains_two_xelatex_jobs(self):
        texts={build.STEMS[0]:'% \\cite{New2021} \\printbibliography\nplain supplement',
               build.STEMS[1]:r'\printbibliography'}
        jobs=build._document_jobs(texts)
        self.assertEqual([job[0] for job in jobs],['xelatex','xelatex','xelatex','biber','xelatex','xelatex'])
        self.assertFalse(any(job == ['biber',build.STEMS[0]] for job in jobs))

    def _bibliography_fixture(self,stem=None):
        stem=stem or build.STEMS[0]
        latex=self.root/'latex'
        (latex/(stem+'.blg')).write_text('INFO - Biber completed\n',encoding='utf-8')
        (latex/(stem+'.bbl')).write_text(r'\entry{New2021}{article}{}',encoding='utf-8')
        return latex,stem

    def test_supplement_references_checked_independently(self):
        latex,stem=self._bibliography_fixture()
        report,failures=build._bibliography_report(latex,stem,r'\cite{New2021}\printbibliography',{'New2021'},[5])
        self.assertEqual(failures,[])
        self.assertTrue(report['enabled'])
        self.assertEqual(report['citation_keys'],['New2021'])
        self.assertEqual(report['bibliography_heading_pages'],[5])

    def test_supplement_missing_key_rejected(self):
        latex,stem=self._bibliography_fixture()
        report,failures=build._bibliography_report(latex,stem,r'\cite{Absent2021}\printbibliography',{'New2021'},[5])
        self.assertEqual(report['missing_citations'],['Absent2021'])
        self.assertEqual(report['missing_printed_references'],['Absent2021'])
        self.assertTrue(failures)

    def test_supplement_missing_printed_entry_rejected(self):
        latex,stem=self._bibliography_fixture()
        (latex/(stem+'.bbl')).write_text('',encoding='utf-8')
        report,failures=build._bibliography_report(latex,stem,r'\cite{New2021}\printbibliography',{'New2021'},[5])
        self.assertEqual(report['missing_citations'],[])
        self.assertEqual(report['missing_printed_references'],['New2021'])
        self.assertTrue(failures)

    def test_supplement_biber_warning_heading_and_print_count_rejected(self):
        latex,stem=self._bibliography_fixture()
        (latex/(stem+'.blg')).write_text('WARN - missing entry\n',encoding='utf-8')
        report,failures=build._bibliography_report(latex,stem,r'\cite{New2021}\printbibliography\printbibliography',{'New2021'},[])
        self.assertEqual(report['bibliography_print_count'],2)
        self.assertEqual(len(failures),3)

    def test_citation_without_print_bibliography_is_rejected(self):
        latex,stem=self._bibliography_fixture()
        report,failures=build._bibliography_report(latex,stem,r'\cite{New2021}',{'New2021'},[5])
        self.assertTrue(report['enabled'])
        self.assertEqual(report['bibliography_print_count'],0)
        self.assertTrue(failures)

    def test_missing_biber_outputs_rejected(self):
        report,failures=build._bibliography_report(self.root/'latex',build.STEMS[0],r'\cite{New2021}\printbibliography',{'New2021'},[5])
        self.assertTrue(any('Biber log missing' in item for item in failures))
        self.assertTrue(any('Biber output missing' in item for item in failures))

    def test_legacy_supplement_needs_no_biber_outputs_or_bibliography_heading(self):
        report,failures=build._bibliography_report(self.root/'latex',build.STEMS[0],'plain supplement',{'New2021'},[])
        self.assertFalse(report['enabled'])
        self.assertEqual(report['bibliography_print_count'],0)
        self.assertEqual(failures,[])

    def test_full_report_preserves_main_flat_fields_and_has_supplement_report(self):
        # 模拟 TeX 和 PDF 接口，只检查报告结构，不冒充实际编译或页面验收。
        text=r'\cite{New2021}\printbibliography'
        class Pixmap:
            def save(self,path):
                build.Image.new('RGB',(20,20),'white').save(path)
        class Page:
            def get_pixmap(self,**kwargs):
                return Pixmap()
            def get_text(self,kind=None):
                return {'blocks':[]} if kind == 'dict' else '参考文献'
            def get_images(self):
                return []
        class Document:
            def __enter__(self):
                return [Page()]
            def __exit__(self,*args):
                return False
        def simulated_tool(job,**kwargs):
            latex=kwargs['cwd']
            stem=Path(job[-1]).stem
            if job[0] == 'xelatex':
                (latex/(stem+'.log')).write_text('',encoding='utf-8')
                (latex/(stem+'.pdf')).write_bytes(b'simulated PDF interface fixture')
            else:
                (latex/(stem+'.blg')).write_text('INFO - completed',encoding='utf-8')
                (latex/(stem+'.bbl')).write_text(r'\entry{New2021}{article}{}',encoding='utf-8')
        with patch('build.shutil.which',return_value='test-tool'), \
             patch('build.subprocess.run',side_effect=simulated_tool), \
             patch('build.pymupdf.open',side_effect=lambda path:Document()):
            report=build.run(self.output,self.root,main_text=text,supplement_text=text,bibliography_path=self.candidate)
        self.assertTrue(report['passed'])
        self.assertEqual(report['citation_keys'],['New2021'])
        self.assertEqual(report['printed_bibliography_keys'],['New2021'])
        self.assertEqual(report['main_bibliography_print_count'],1)
        self.assertEqual(report['bibliography_heading_pages'],[1])
        self.assertEqual(report['bibliographies'][build.STEMS[0]]['citation_keys'],['New2021'])
        self.assertEqual(len(report['executed_jobs']),8)


if __name__=='__main__':
    unittest.main()
