"""第7节出版同步的成本列与唯一锚点回归；不覆盖正式稿或历史报告。"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paper_sync as sync
from manuscript_version import inventory


class CostPrecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[2]
        cls.source = cls.root / "reproducibility/manuscript_versions/20261004_joint_integration"
        cls.main = (cls.source / "flatten_curve_analysis_cn.tex").read_text(encoding="utf-8-sig")
        cls.si = (cls.source / "flatten_curve_supplement_cn.tex").read_text(encoding="utf-8-sig")
        cls.reference = cls.root / "reproducibility/results/20261003_release_final"

    @staticmethod
    def table(text, label):
        pos = text.index(r"\label{" + label + "}")
        start = text.rfind(r"\begin{table}", 0, pos)
        finish = text.index(r"\end{table}", pos) + len(r"\end{table}")
        return text[start:finish]

    @staticmethod
    def without_cost_cells(text, label):
        """规范化只允许改变的成本单元和列宽声明，其他字节须相同。"""
        target = CostPrecisionTests.table(text, label)
        lines = target.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if " & " not in line or not line.rstrip().endswith(r"\\"):
                continue
            fields = line.split(" & ")
            if len(fields) not in (5, 6):
                continue
            try:
                float(fields[4].removesuffix("\n").removesuffix(r"\\"))
            except ValueError:
                continue
            suffix = r"\\" if fields[4].rstrip().endswith(r"\\") else ""
            newline = "\n" if fields[4].endswith("\n") else ""
            fields[4] = "<cost>" + suffix + newline
            lines[i] = " & ".join(fields)
        normalized = "".join(lines)
        normalized = normalized.replace("S[table-format=2.4]@{}", "S[table-format=2.COST]@{}")
        normalized = normalized.replace("S[table-format=2.2]@{}", "S[table-format=2.COST]@{}")
        normalized = normalized.replace("S[table-format=3.4]S[table-format=7.0]",
                                        "S[table-format=3.COST]S[table-format=7.0]")
        normalized = normalized.replace("S[table-format=3.2]S[table-format=7.0]",
                                        "S[table-format=3.COST]S[table-format=7.0]")
        return text.replace(target, normalized, 1)

    def test_current_unrounded_costs_four_decimal(self):
        main, si, records = sync.synchronize_cost_precision(self.main, self.si, self.reference)
        self.assertEqual(len(records), 14)
        self.assertIn("45.29 & 49.3894", main)
        self.assertIn("258.10 & 40.7686", main)
        self.assertIn("75.57 & 0.0000", main)
        self.assertIn("0.0020 & 0.8454 & 85.07 & 258.10 & 40.7686", si)
        self.assertIn("S[table-format=2.4]@{}", self.table(main, "tab:xian_summary"))
        self.assertIn("S[table-format=3.4]S[table-format=7.0]", self.table(si, "tab:sup:eta"))
        for record in records:
            self.assertRegex(record["new"], r"^\d+\.\d{4}$")

    def test_only_j_cells_and_j_column_declaration_change(self):
        main, si, _ = sync.synchronize_cost_precision(self.main, self.si, self.reference)
        self.assertEqual(self.without_cost_cells(main, "tab:xian_summary"),
                         self.without_cost_cells(self.main, "tab:xian_summary"))
        self.assertEqual(self.without_cost_cells(si, "tab:sup:eta"),
                         self.without_cost_cells(self.si, "tab:sup:eta"))
        self.assertEqual(inventory(main), inventory(self.main))
        self.assertEqual(inventory(si), inventory(self.si))

    def test_sec9_and_s1_s2_bodies_unchanged(self):
        main, si, _ = sync.synchronize_cost_precision(self.main, self.si, self.reference)
        section = main.index(r"\label{sec:dominance}")
        self.assertEqual(main[section:], self.main[self.main.index(r"\label{sec:dominance}"):])
        for label in ("tab:sup:baseline", "tab:sup:initial"):
            self.assertEqual(self.table(si, label), self.table(self.si, label))

    def test_sync_is_idempotent(self):
        main, si, _ = sync.synchronize_cost_precision(self.main, self.si, self.reference)
        again_main, again_si, records = sync.synchronize_cost_precision(main, si, self.reference)
        self.assertEqual((main, si), (again_main, again_si))
        self.assertFalse(any(row["changed"] for row in records))

    def test_wrong_cost_rejected_not_corrected_silently(self):
        bad = self.main.replace("45.29 & 49.39", "45.29 & 48.39", 1)
        with self.assertRaisesRegex(ValueError, "成本值"):
            sync.synchronize_cost_precision(bad, self.si, self.reference)
        bad_si = self.si.replace("258.10 & 40.77", "258.10 & 41.77", 1)
        with self.assertRaisesRegex(ValueError, "成本值"):
            sync.synchronize_cost_precision(self.main, bad_si, self.reference)

    def test_missing_and_duplicate_main_row_rejected(self):
        row = next(line for line in self.main.splitlines() if line.startswith("TDINN 控制 & "))
        for replacement in ("", row + "\n" + row):
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, "成本行必须唯一"):
                sync.synchronize_cost_precision(self.main.replace(row, replacement, 1), self.si, self.reference)

    def test_missing_and_duplicate_si_row_rejected(self):
        row = next(line for line in self.si.splitlines() if line.startswith("0.0020 & "))
        for replacement in ("", row + "\n" + row):
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, "成本行必须唯一"):
                sync.synchronize_cost_precision(self.main, self.si.replace(row, replacement, 1), self.reference)

    def test_duplicate_table_label_rejected(self):
        bad = self.main + "\n" + r"\label{tab:xian_summary}"
        with self.assertRaisesRegex(ValueError, "成本表标签必须唯一"):
            sync.synchronize_cost_precision(bad, self.si, self.reference)

    def test_nonfinite_reference_cost_rejected(self):
        reference = sync._json(self.reference / "xian/reference.json")
        reference["strategies"][0]["J"] = float("nan")
        original = sync._json
        with patch.object(sync, "_json", side_effect=lambda path: reference if Path(path).name == "reference.json" else original(path)):
            with self.assertRaisesRegex(ValueError, "成本列不是有限"):
                sync.synchronize_cost_precision(self.main, self.si, self.reference)

    def test_controlled_version_enables_precision(self):
        version = json.loads((self.source / "manifest.json").read_text(encoding="utf-8"))
        version.update(publication_cost_digits=4, _directory=self.source)
        with tempfile.TemporaryDirectory(prefix="sec7_cost_sync_") as directory:
            output = Path(directory)
            extra = output / "joint_extra"
            extra.mkdir()
            (extra / "validation.json").write_text(json.dumps({
                "passed": True, "tasks": {key: {"passed": True} for key in ("A", "B", "C", "D")}
            }), encoding="utf-8")
            with patch("manuscript_version.load_version", return_value=version), \
                 patch("manuscript_version.version_texts", return_value=(self.main, self.si)), \
                 patch("joint_extra.manuscript.build_publication_fragments", return_value={}):
                main, si, report = sync.prepare_manuscript(self.root, output, scientific_reference=self.reference)
            self.assertIn("49.3894", main)
            self.assertIn("826.4066", si)
            self.assertEqual(len([row for row in report["changes"] if row["anchor"] == "cost_precision"]), 14)


class UniqueAnchorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sec7_anchor_sync_")
        self.root = Path(self.temp.name)
        self.output = self.root / "run"
        self.extra = self.output / "joint_extra"
        self.extra.mkdir(parents=True)
        (self.extra / "validation.json").write_text(json.dumps({
            "passed": True, "tasks": {"A": {"passed": True}}
        }), encoding="utf-8")
        self.reference = self.root / "reproducibility/results/accepted"
        for name in ("xian/reference.json", "xian/fit.json", "population/critical.json",
                     "c0/extrema.json", "joint/results.json"):
            path = self.reference / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{"value":1}', encoding="utf-8")
        self.text = (
            r"\section{原理论}\label{sec:joint}" + "\n"
            "% BEGIN JOINT_EXTRA:comparison\n旧文案\n% END JOINT_EXTRA:comparison\n"
            r"\section{第9节}\label{sec:dominance}" + "\n固定绝对初值。\n"
            r"\section{讨论}\label{sec:discussion}" + "\n块外图注保持原样。\n"
        )
        self.supplement = "补充材料保持原样。\n"
        self.version = {
            "version": "unit_fixture", "approved_tasks": ["A"],
            "inherited_science_reference": "reproducibility/results/accepted",
            "inventory": {"main": inventory(self.text), "supplement": inventory(self.supplement)},
            "documents": {role: {"file": role + ".tex", "sha256": "unit-fixture"}
                          for role in ("main", "supplement")},
            "_directory": self.root,
        }

    def tearDown(self):
        self.temp.cleanup()

    def run_sync(self, text):
        with patch("manuscript_version.load_version", return_value=self.version), \
             patch("manuscript_version.version_texts", return_value=(text, self.supplement)), \
             patch("joint_extra.manuscript.build_publication_fragments", return_value={"comparison": "批准的新文案"}):
            return sync.prepare_manuscript(self.root, self.output, scientific_reference=self.reference)

    def test_unique_anchor_updates_only_block(self):
        text, supplement, report = self.run_sync(self.text)
        self.assertEqual(text, self.text.replace("旧文案", "批准的新文案"))
        self.assertEqual(supplement, self.supplement)
        self.assertTrue(report["passed"])
        self.assertIn("块外图注保持原样", text)

    def test_missing_begin_or_end_rejected(self):
        for marker in ("% BEGIN JOINT_EXTRA:comparison", "% END JOINT_EXTRA:comparison"):
            with self.subTest(marker=marker), self.assertRaisesRegex(ValueError, "锚点须唯一"):
                self.run_sync(self.text.replace(marker, "", 1))
        self.assertFalse((self.output / "manuscript").exists())

    def test_duplicate_begin_or_end_rejected(self):
        for marker in ("% BEGIN JOINT_EXTRA:comparison", "% END JOINT_EXTRA:comparison"):
            with self.subTest(marker=marker), self.assertRaisesRegex(ValueError, "锚点须唯一"):
                self.run_sync(self.text + "\n" + marker)
        self.assertFalse((self.output / "manuscript").exists())

    def test_reversed_boundaries_rejected(self):
        bad = self.text.replace("% BEGIN JOINT_EXTRA:comparison", "% HOLD", 1)
        bad = bad.replace("% END JOINT_EXTRA:comparison", "% BEGIN JOINT_EXTRA:comparison", 1)
        bad = bad.replace("% HOLD", "% END JOINT_EXTRA:comparison", 1)
        with self.assertRaisesRegex(ValueError, "边界次序错误"):
            self.run_sync(bad)
        self.assertFalse((self.output / "manuscript").exists())


if __name__ == "__main__":
    unittest.main()
