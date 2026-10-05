"""只测试文案入口的拒绝规则；不运行TeX、传播计算或绘图。"""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import document_revision as revision
from bootstrap import dump, sha


class ReviewGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        for stem in (revision.MAIN, revision.SUPPLEMENT):
            (self.directory / (stem + '.pdf')).write_bytes(b'fixture-not-a-real-pdf')
        self.build = {'documents': {stem: {'pdf_sha256': sha(self.directory / (stem + '.pdf')), 'page_count': count}
                                    for stem, count in ((revision.MAIN, 4), (revision.SUPPLEMENT, 3))},
                      'required_detail_pages': [1, 2, 4]}
        self.review = {'passed': True, 'failures': [], 'scientific_calculation_reexecuted': False,
                       'main_pdf_sha256': self.build['documents'][revision.MAIN]['pdf_sha256'],
                       'supplement_pdf_sha256': self.build['documents'][revision.SUPPLEMENT]['pdf_sha256'],
                       'main_contact_pages_viewed': [1, 2, 3, 4], 'supplement_contact_pages_viewed': [1, 2, 3],
                       'detail_pages_viewed': {'main': [1, 2, 4], 'supplement': [1, 2, 3]}}

    def tearDown(self): self.temp.cleanup()

    def test_review_passes_only_with_current_hash_and_coverage(self):
        revision.validate_review(self.review, self.build, self.directory)

    def test_review_missing_rejected(self):
        with self.assertRaises(RuntimeError): revision.validate_review({}, self.build, self.directory)

    def test_review_incomplete_overview_rejected(self):
        self.review['main_contact_pages_viewed'] = [1, 2]
        with self.assertRaises(RuntimeError): revision.validate_review(self.review, self.build, self.directory)

    def test_review_other_pdf_rejected(self):
        self.review['main_pdf_sha256'] = '0' * 64
        with self.assertRaises(RuntimeError): revision.validate_review(self.review, self.build, self.directory)

    def test_review_invalid_detail_page_rejected(self):
        self.review['detail_pages_viewed']['main'] = [999]
        with self.assertRaises(RuntimeError): revision.validate_review(self.review, self.build, self.directory)

    def test_review_required_page_missing_rejected(self):
        self.review['detail_pages_viewed']['main'] = [1, 2]
        with self.assertRaises(RuntimeError): revision.validate_review(self.review, self.build, self.directory)

    def test_review_claims_science_reexecuted_rejected(self):
        self.review['scientific_calculation_reexecuted'] = True
        with self.assertRaises(RuntimeError): revision.validate_review(self.review, self.build, self.directory)

    def test_path_metadata_serialization(self):
        value = {'version_activation': {'_directory': self.directory, '_receipt_path': self.directory / 'receipt.json',
                                        'record': {'nested': [self.directory]}}}
        self.assertIsInstance(json.loads(json.dumps(revision.json_ready(value)))['version_activation']['_directory'], str)


class InheritanceGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.parent = self.root / 'reproducibility/runs/old'
        self.publication = self.root / 'reproducibility/release_reports/old/publication'
        self.old_version = {'_directory': self.root / 'reproducibility/manuscript_versions' / revision.BASE_VERSION,
                            'documents': {}}
        dump(self.old_version['_directory'] / 'manifest.json', {'fixture': True})
        for name in ('core.py', 'run.py', 'validation.py', 'acceptance.json'):
            target = self.root / 'reproducibility/joint_extra' / name
            target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(name.encode())
        for name in ('baseline', 'xian_reference'):
            target = self.root / 'input' / (name + '.json')
            dump(target, {'fixture': name})
        rows = []
        artifacts = {}
        for name in ('run_1', 'run_2'):
            run = self.parent / name
            dump(run / 'run_report.json', {'passed': True, 'manuscript_version': revision.BASE_VERSION})
            dump(run / 'joint_extra/validation.json', {'passed': True, 'tasks': {task: {'passed': True} for task in 'ABCD'}})
            science = {'validation.json': sha(run / 'joint_extra/validation.json')}
            dump(run / 'postprocessing_manifest.json', {'manuscript_version': revision.BASE_VERSION,
                'manuscript_manifest_sha256': sha(self.old_version['_directory'] / 'manifest.json'),
                'calculation_phase': {'approved_tasks': list('ABCD'), 'scientific_results_sha256': science,
                    'calculation_source_hashes': {source: sha(self.root / 'reproducibility/joint_extra' / source)
                                                  for source in ('core.py', 'run.py', 'validation.py', 'acceptance.json')},
                    'input_sources': {source: {'path': str(self.root / 'input' / (source + '.json')),
                                               'sha256': sha(self.root / 'input' / (source + '.json'))}
                                      for source in ('baseline', 'xian_reference')}}})
            rows.append({'name': name, 'directory': name, 'report_files_sha256': {
                file: sha(run / file) for file in ('run_report.json', 'postprocessing_manifest.json', 'joint_extra/validation.json')}})
            artifacts[name] = [{'file': 'joint_extra/validation.json', 'sha256': science['validation.json']}]
        dump(self.parent / 'accepted_runs.json', {'schema': 'accepted-runs-v1', 'runs': rows})
        dump(self.parent / 'repeatability.json', {'passed': True, 'run_names': ['run_1', 'run_2'], 'run_identity_check': {'passed': True}})
        dump(self.publication / 'publication_manifest.json', {'passed': True, 'formal_files_published': True,
            'accepted_runs_manifest_sha256': sha(self.parent / 'accepted_runs.json'),
            'accepted_run_names': ['run_1', 'run_2'], 'scientific_artifacts': artifacts})
        dump(self.publication / 'collection_manifest.json', {'passed': True,
            'accepted_runs_manifest_sha256': sha(self.parent / 'accepted_runs.json'), 'files': []})
        self.mock_version = patch.object(revision, 'load_version', return_value=self.old_version)
        self.mock_version.start()

    def tearDown(self): self.mock_version.stop(); self.temp.cleanup()

    def test_accepts_old_identity_without_science_rerun(self):
        result = revision.validate_inheritance(self.root, self.parent)
        self.assertFalse(result['scientific_calculation_reexecuted'])

    def test_old_report_changed_rejected(self):
        dump(self.parent / 'run_1/run_report.json', {'passed': False})
        with self.assertRaises(RuntimeError): revision.validate_inheritance(self.root, self.parent)

    def test_incomplete_repeatability_rejected(self):
        dump(self.parent / 'repeatability.json', {'passed': False})
        with self.assertRaises(RuntimeError): revision.validate_inheritance(self.root, self.parent)

    def test_new_scientific_identity_rejected_even_if_rehashed(self):
        report = self.parent / 'run_1/run_report.json'
        dump(report, {'passed': True, 'manuscript_version': revision.VERSION_ID})
        selection = revision.read(self.parent / 'accepted_runs.json')
        selection['runs'][0]['report_files_sha256']['run_report.json'] = sha(report)
        dump(self.parent / 'accepted_runs.json', selection)
        for name in ('publication_manifest.json', 'collection_manifest.json'):
            target = self.publication / name; value = revision.read(target)
            value['accepted_runs_manifest_sha256'] = sha(self.parent / 'accepted_runs.json'); dump(target, value)
        with self.assertRaisesRegex(RuntimeError, '重新包装'): revision.validate_inheritance(self.root, self.parent)

    def test_archive_source_current_registry_may_change(self):
        archived = self.root / 'archive/registry.json'; dump(archived, {'old': True})
        dump(self.root / 'reproducibility/registry.json', {'new': True})
        target = self.publication / 'collection_manifest.json'; value = revision.read(target)
        value['files'] = [{'file': 'archive/registry.json', 'source': 'reproducibility/registry.json', 'sha256': sha(archived)}]
        dump(target, value)
        revision.validate_inheritance(self.root, self.parent)
        dump(archived, {'tampered': True})
        with self.assertRaises(RuntimeError): revision.validate_inheritance(self.root, self.parent)

    def test_source_parameter_changed_rejected(self):
        dump(self.root / 'input/baseline.json', {'tampered': True})
        with self.assertRaises(RuntimeError): revision.validate_inheritance(self.root, self.parent)


if __name__ == '__main__': unittest.main()
