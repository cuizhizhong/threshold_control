"""后处理只读前检的实际正/负例；假数据不构成科学数值验收。"""
from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bootstrap import sha
from compare_runs import _json_errors
from postprocess_joint_extra import CALCULATION_FILES, COMMON_RESULTS, TASK_RESULTS, validate_completed_results
from publication import publish_artifacts


class PostprocessGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='joint_postprocess_guard_')
        self.root = Path(self.temp.name)
        self.output = self.root/'reproducibility/runs/fixture'
        self.science = self.output/'joint_extra'
        self.science.mkdir(parents=True)
        self.module = self.root/'reproducibility/joint_extra'
        self.module.mkdir(parents=True)
        self.acceptance = {'test_rule': 1e-8}
        for name in CALCULATION_FILES:
            path = self.module/name
            path.write_text(json.dumps(self.acceptance) if name.endswith('.json') else '# fixture\n', encoding='utf-8')
        self.inputs = {
            'baseline': self.root/'joint_control/threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json',
            'xian_reference': self.root/'reproducibility/results/accepted/xian/reference.json',
        }
        for path in self.inputs.values():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{}', encoding='utf-8')
        for name in set(COMMON_RESULTS).union(*(set(TASK_RESULTS[key]) for key in 'ABC')):
            (self.science/name).write_text('{}', encoding='utf-8')
        self.manifest = {
            'schema': 'joint-extra-v2', 'root': str(self.root), 'created': '2026-10-04T12:00:00',
            'calculation_source_hashes': {name: sha(self.module/name) for name in CALCULATION_FILES},
            'inputs': {key: {'path': str(path), 'sha256': sha(path)} for key, path in self.inputs.items()},
            'acceptance': self.acceptance, 'tasks_requested': list('ABCD'),
            'software': {'python': platform.python_version(), 'numpy': importlib.metadata.version('numpy'),
                         'scipy': importlib.metadata.version('scipy')},
        }
        self.validation = {'passed': False, 'status': 'partial',
            'tasks': {key: {'passed': key != 'D', 'status': 'passed' if key != 'D' else 'failed'} for key in 'ABCD'}}
        self.write('input_manifest.json', self.manifest)
        self.write('validation.json', self.validation)
        self.write('acceptance.json', self.acceptance)
        self.version = {'approved_tasks': list('ABC'), 'inherited_science_reference': 'reproducibility/results/accepted'}

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, value):
        (self.science/name).write_text(json.dumps(value), encoding='utf-8')

    def preflight(self):
        return validate_completed_results(self.output, self.root, self.version)

    def test_partial_D_failure_allowed_without_science_mutation(self):
        before = {p.name: p.read_bytes() for p in self.science.iterdir()}
        report = self.preflight()
        self.assertTrue(report['passed'])
        self.assertFalse(report['validation_overall_passed'])
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.science.iterdir()})
        self.assertEqual(set(self.output.iterdir()), {self.science})

    def test_calculation_code_changed_rejected(self):
        (self.module/'core.py').write_text('# changed\n', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, '计算源码发生变化'):
            self.preflight()

    def test_input_changed_rejected(self):
        self.inputs['xian_reference'].write_text('{"changed":true}', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, '科学输入路径或哈希已改变'):
            self.preflight()

    def test_running_or_failed_approved_task_rejected(self):
        self.validation['status'] = 'running'
        self.write('validation.json', self.validation)
        with self.assertRaisesRegex(RuntimeError, '尚未结束'):
            self.preflight()
        self.validation['status'] = 'partial'
        self.validation['tasks']['B']['passed'] = False
        self.write('validation.json', self.validation)
        with self.assertRaisesRegex(RuntimeError, '实际验收未通过'):
            self.preflight()

    def test_missing_artifact_rejected(self):
        (self.science/'phase_baseline.npz').unlink()
        with self.assertRaisesRegex(FileNotFoundError, '已计算结果缺失'):
            self.preflight()

    def test_existing_postprocess_output_rejected(self):
        target = self.output/'run_report.json'
        target.write_text('previous', encoding='utf-8')
        with self.assertRaises(FileExistsError):
            self.preflight()
        self.assertEqual(target.read_text(encoding='utf-8'), 'previous')

    def test_acceptance_record_changed_rejected(self):
        self.write('acceptance.json', {'test_rule': 1e-4})
        with self.assertRaisesRegex(RuntimeError, '验收规则'):
            self.preflight()

    def test_creation_time_exception_is_schema_and_top_level_only(self):
        a = {'schema': 'joint-extra-v2', 'created': 'first', 'value': 1.0}
        b = {'schema': 'joint-extra-v2', 'created': 'second', 'value': 1.0}
        self.assertEqual(_json_errors(a, b, self.output, self.output), [])
        b['value'] = 2.0
        self.assertEqual(_json_errors(a, b, self.output, self.output), ['/value'])
        self.assertEqual(_json_errors({'created': 'first'}, {'created': 'second'}, self.output, self.output), ['/created'])
        a['nested'] = {'created': 'first'}
        b['value'] = 1.0
        b['nested'] = {'created': 'second'}
        self.assertEqual(_json_errors(a, b, self.output, self.output), ['/nested/created'])

    def test_repeated_publication_cannot_overwrite_success_record(self):
        target=self.root/'reproducibility/release_reports/fixture/publication/publication_manifest.json'
        target.parent.mkdir(parents=True)
        prior='{"passed":true,"approved":"original"}'
        target.write_text(prior,encoding='utf-8')
        with patch.object(publish_artifacts,'ROOT',self.root):
            with self.assertRaisesRegex(RuntimeError,'保持历史记录原样'):
                publish_artifacts.main(self.output,False)
        self.assertEqual(target.read_text(encoding='utf-8'),prior)
        self.assertEqual(list(target.parent.iterdir()),[target])


if __name__ == '__main__':
    unittest.main()
