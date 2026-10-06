"""新版来源与正文保护的正、负例；不编译、不运行科学计算。"""
from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import threshold_revision_text as revision


class ThresholdRevisionTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[2]
        base = cls.root / "reproducibility/manuscript_versions" / revision.BASE_VERSION
        bundle = cls.root / revision.BUNDLE_RELATIVE / "latex"
        cls.old_main = (base / "flatten_curve_analysis_cn.tex").read_text(encoding="utf-8-sig")
        cls.old_si = (base / "flatten_curve_supplement_cn.tex").read_text(encoding="utf-8-sig")
        cls.new_main = (bundle / "flatten_curve_analysis_cn.tex").read_text(encoding="utf-8-sig")
        cls.new_si = (bundle / "flatten_curve_supplement_cn.tex").read_text(encoding="utf-8-sig")
        cls.bib = (base / "references.bib").read_text(encoding="utf-8-sig")

    def check_pair(self, main=None, si=None, old_main=None):
        return revision.assert_protected_unchanged(
            self.old_main if old_main is None else old_main,
            self.new_main if main is None else main,
            self.old_si, self.new_si if si is None else si,
        )

    def test_approved_source_and_pair(self):
        source = revision.validate_source_bundle(self.root)
        self.assertTrue(source["passed"])
        self.assertEqual(len(source["source_hashes"]), 8)
        self.assertEqual(source["source"]["commit"], revision.BASE_COMMIT)
        checks = self.check_pair()
        self.assertEqual(checks["counts"]["figure"], 24)
        self.assertEqual(checks["counts"]["proof"], 27)
        self.assertEqual(checks["main_tables"], 5)
        self.assertEqual(checks["supplement_tables"], 3)
        self.assertTrue(checks["sec9_only_approved_intro_change"])
        self.assertFalse(checks["scientific_calculation_reexecuted"])

    def test_source_hash_manifest_and_every_file_change_rejected(self):
        with tempfile.TemporaryDirectory(prefix="threshold_source_guard_") as temp:
            root = Path(temp)
            copied = root / revision.BUNDLE_RELATIVE
            shutil.copytree(self.root / revision.BUNDLE_RELATIVE, copied)
            for relative in (*revision.APPROVED_HASHES, "review/SHA256.json"):
                target = copied / relative
                original = target.read_bytes()
                target.write_bytes(original + b"\nchanged")
                try:
                    with self.subTest(relative=relative), self.assertRaisesRegex(ValueError, "哈希"):
                        revision.validate_source_bundle(root)
                finally:
                    target.write_bytes(original)

    def test_missing_source_rejected(self):
        with tempfile.TemporaryDirectory(prefix="threshold_source_missing_") as temp:
            with self.assertRaisesRegex(ValueError, "文件缺失"):
                revision.validate_source_bundle(Path(temp))

    def test_theory_formula_proof_figure_and_table_changes_rejected(self):
        for marker in (r"\begin{theorem}", r"\begin{equation}", r"\begin{proof}",
                       r"\begin{figure}", r"\begin{tabularx}"):
            changed = self.new_main.replace(marker, marker + "\n% unapproved", 1)
            self.assertNotEqual(self.new_main, changed)
            with self.subTest(marker=marker), self.assertRaisesRegex(ValueError, "保护内容变化"):
                self.check_pair(main=changed)
        changed = self.new_si.replace(r"\begin{tabular*}", r"\begin{tabular*}" + "\n% unapproved", 1)
        with self.assertRaisesRegex(ValueError, "补充表体"):
            self.check_pair(si=changed)

    def test_section7_joint_block_and_sec9_changes_rejected(self):
        for marker in (r"\label{sec:joint:compare-numerics}", "% BEGIN JOINT_EXTRA:comparison",
                       r"\label{sec:dom:setup}"):
            changed = self.new_main.replace(marker, marker + "\n% unapproved", 1)
            with self.subTest(marker=marker), self.assertRaisesRegex(ValueError, "保护内容变化"):
                self.check_pair(main=changed)
        with self.assertRaisesRegex(ValueError, "须唯一"):
            self.check_pair(main=self.new_main.replace(revision.SEC9_AFTER, "", 1))

    def test_original_main_and_supplement_labels_rejected(self):
        with self.assertRaisesRegex(ValueError, "正文标签"):
            self.check_pair(main=self.new_main + r"\label{unapproved}")
        with self.assertRaisesRegex(ValueError, "两个标签"):
            self.check_pair(si=self.new_si + r"\label{unapproved}")
        with self.assertRaisesRegex(ValueError, "两个标签"):
            self.check_pair(si=self.new_si.replace("sec:sup:medical-link", "sec:sup:wrong-link", 1))

    def test_unauthorized_prose_and_old_generator_restore_rejected(self):
        with self.assertRaisesRegex(ValueError, "完整文案"):
            self.check_pair(main=self.new_main + "\n% unauthorized prose")
        with self.assertRaisesRegex(ValueError, "完整文案"):
            self.check_pair(si=self.new_si.replace("初始时刻之前", "初始仓室", 1))
        with self.assertRaisesRegex(ValueError, "第9节"):
            self.check_pair(main=self.old_main)
        with self.assertRaisesRegex(ValueError, "完整文案"):
            self.check_pair(old_main=self.old_main + "\n% changed baseline")

    def test_citations_checked_per_document_and_library_entry_retained(self):
        checks = revision.assert_citations_resolved(self.new_main, self.new_si, self.bib)
        self.assertTrue(checks["passed"])
        self.assertIn("Baas2021Occupancy", checks["documents"]["supplement"]["citation_keys"])
        self.assertNotIn("Baas2021Occupancy", checks["documents"]["main"]["citation_keys"])
        self.assertIn("Zhang2026Behavior", revision.bibliography_entries(self.bib))
        for name, main, si in (("main", self.new_main + r"\cite{missing-key}", self.new_si),
                              ("supplement", self.new_main, self.new_si + r"\cite{missing-key}")):
            with self.subTest(document=name), self.assertRaisesRegex(ValueError, name + " 引用键"):
                revision.assert_citations_resolved(main, si, self.bib)
        for main, si in ((self.new_main.replace(r"\printbibliography", ""), self.new_si),
                         (self.new_main, self.new_si + r"\printbibliography")):
            with self.assertRaisesRegex(ValueError, "一次参考文献"):
                revision.assert_citations_resolved(main, si, self.bib)

    def test_bom_and_newlines_do_not_change_protection_identity(self):
        checks = self.check_pair(main="\ufeff" + self.new_main.replace("\n", "\r\n"),
                                 si=self.new_si.replace("\n", "\r\n"))
        self.assertTrue(checks["passed"])


if __name__ == "__main__":
    unittest.main()
