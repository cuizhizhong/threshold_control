"""本轮文案发布入口的拒绝测试；不运行科学计算、绘图或TeX。"""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import threshold_revision as revision
from bootstrap import dump, sha


class ThresholdRevisionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.output = self.root / 'reproducibility/release_reports/review'
        self.output.mkdir(parents=True)

    def tearDown(self):
        self.temp.cleanup()

    def test_wrong_revision_schema_rejected(self):
        dump(self.output / 'revision.json', {'schema': 'document-revision-v1'})
        with self.assertRaisesRegex(RuntimeError, '身份不符'):
            revision.check_revision(self.root, self.output)

    def test_claimed_scientific_rerun_rejected(self):
        dump(self.output / 'revision.json', {'schema': 'threshold-document-revision-v1',
            'version': revision.VERSION_ID, 'base_version': revision.BASE_VERSION,
            'scientific_calculation_reexecuted': True})
        with self.assertRaisesRegex(RuntimeError, '冒充科学运行'):
            revision.check_revision(self.root, self.output)

    def test_output_outside_report_directory_rejected(self):
        with self.assertRaises(ValueError):
            revision.output_path(self.root, self.root / 'latex')

    def test_existing_stage_output_rejected(self):
        with self.assertRaises(FileExistsError):
            revision.stage(self.root, self.output, self.root / 'science')

    def test_generator_restoring_old_text_rejected(self):
        record = {'manifest_sha256': 'locked', 'inheritance': {'joint_extra_directory': str(self.root / 'science')}}
        version = {'inherited_science_reference': 'science'}
        with patch.object(revision, 'check_revision', return_value=(record, version)), \
             patch.object(revision, 'version_texts', return_value=('approved main', 'approved SI')), \
             patch('paper_sync.prepare_manuscript', return_value=('old main', 'old SI', {})), \
             patch('build.run') as compile_job:
            with self.assertRaisesRegex(RuntimeError, '全文生成回归改变'):
                revision.verify(self.root, self.output)
            compile_job.assert_not_called()

    def test_generation_cannot_claim_new_science(self):
        record = {'manifest_sha256': 'locked', 'inheritance': {'joint_extra_directory': str(self.root / 'science')}}
        version = {'inherited_science_reference': 'science'}
        with patch.object(revision, 'check_revision', return_value=(record, version)), \
             patch.object(revision, 'version_texts', return_value=('main', 'SI')), \
             patch('paper_sync.prepare_manuscript', return_value=('main', 'SI', {'scientific_calculation_reexecuted': True})), \
             patch('build.run') as compile_job:
            with self.assertRaisesRegex(RuntimeError, '错误标记为科学重跑'):
                revision.verify(self.root, self.output)
            compile_job.assert_not_called()


class SupplementReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        for stem in (revision.MAIN, revision.SUPPLEMENT):
            (self.directory / (stem + '.pdf')).write_bytes(b'not-a-real-pdf-test-fixture')
        self.build = {'documents': {stem: {'pdf_sha256': sha(self.directory / (stem + '.pdf')), 'page_count': 5}
                                   for stem in (revision.MAIN, revision.SUPPLEMENT)},
                      'required_detail_pages': [1, 5], 'required_supplement_detail_pages': [1, 2, 3, 4, 5]}
        self.review = {'passed': True, 'failures': [], 'scientific_calculation_reexecuted': False,
            'main_pdf_sha256': self.build['documents'][revision.MAIN]['pdf_sha256'],
            'supplement_pdf_sha256': self.build['documents'][revision.SUPPLEMENT]['pdf_sha256'],
            'main_contact_pages_viewed': [1, 2, 3, 4, 5], 'supplement_contact_pages_viewed': [1, 2, 3, 4, 5],
            'detail_pages_viewed': {'main': [1, 5], 'supplement': [1, 2, 3, 4, 5]}}

    def tearDown(self): self.temp.cleanup()

    def test_complete_review_passes(self):
        revision.validate_review(self.review, self.build, self.directory)

    def test_supplement_content_not_reviewed_rejected(self):
        self.review['detail_pages_viewed']['supplement'] = [1, 2, 3]
        with self.assertRaisesRegex(RuntimeError, '补充材料新增推导'):
            revision.validate_review(self.review, self.build, self.directory)

    def test_missing_review_rejected(self):
        with self.assertRaises(RuntimeError):
            revision.validate_review({}, self.build, self.directory)

    def test_mismatched_pdf_rejected(self):
        self.review['supplement_pdf_sha256'] = '0' * 64
        with self.assertRaises(RuntimeError):
            revision.validate_review(self.review, self.build, self.directory)


if __name__ == '__main__': unittest.main()
