"""受控版本文献库与编译入口的源码收集测试；不执行科学计算或 TeX。"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bootstrap import prepare_workspace, sha


class BootstrapVersionAssetsTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='bootstrap_version_assets_')
        self.root=Path(self.temporary.name)/'project'
        self.output=Path(self.temporary.name)/'isolated'
        (self.root/'latex/figures').mkdir(parents=True)
        for relative in ('真实数据/Xianguankong.xlsx','refs/SIQR模型示意图_可编辑.pptx',
                         'refs/SIQR模型示意图_Nature配色_可编辑.pptx',
                         'latex/flatten_curve_analysis_cn.tex','latex/flatten_curve_supplement_cn.tex',
                         'latex/elegantpaper.cls','latex/references.bib','latex/build_paper.ps1'):
            self.fixture(relative,b'interface fixture\n')
        adapter=("SKILL = Path('legacy')\n"
                 "sys.path.insert(0, str(SKILL))\n"
                 "from audit_panel_alignment import require_matplotlib_panel_alignment\n")
        for relative in ('latex/revision_layout_v5/layout_python.py',
                         'latex/revision_style_restore/restore_figures.py',
                         'latex/revision_v4/plot_revisions.py'):
            self.fixture(relative,adapter.encode('utf-8'))
        self.fixture('latex/revision_layout_v5/layout_matlab.m',
            ("fullfile(root, 'archive_unused', 'generated_snapshots', ...\n"
             "    'scenario1_threshold_landscape_current_run', 'output_csv', 'landscape_summary.csv')").encode('utf-8'))
        self.version='reproducibility/manuscript_versions/fixture/'
        self.fixture(self.version+'references.bib',b'@article{Reference,year={2021}}\r\n')
        self.fixture(self.version+'build_paper.ps1',b'# controlled script\r\n')
        self.fixture(self.version+'manifest.json',b'{}\n')
        for relative in ('reproducibility/build.py','reproducibility/bootstrap.py',
                         'reproducibility/threshold_revision.py','reproducibility/threshold_revision_text.py'):
            self.fixture(relative,b'# controlled publication interface\n')
        self.fixture(self.version+'__pycache__/cache.py',b'# excluded\n')
        self.fixture(self.version+'historical.npz',b'excluded numerical cache')

    def fixture(self,relative,content):
        target=self.root/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(content)

    def tearDown(self):
        self.temporary.cleanup()

    def test_controlled_bibliography_script_and_revision_interfaces_are_collected(self):
        workspace=prepare_workspace(self.output,self.root)
        manifest=json.loads((self.output/'source_manifest.json').read_text(encoding='utf-8'))['source_files']
        for relative in (self.version+'references.bib',self.version+'build_paper.ps1',
                         'reproducibility/build.py','reproducibility/bootstrap.py',
                         'reproducibility/threshold_revision.py','reproducibility/threshold_revision_text.py'):
            with self.subTest(relative=relative):
                self.assertEqual((workspace/relative).read_bytes(),(self.root/relative).read_bytes())
                self.assertEqual(manifest[relative],sha(self.root/relative))
        self.assertFalse((workspace/(self.version+'__pycache__/cache.py')).exists())
        self.assertFalse((workspace/(self.version+'historical.npz')).exists())


if __name__=='__main__':
    unittest.main()
