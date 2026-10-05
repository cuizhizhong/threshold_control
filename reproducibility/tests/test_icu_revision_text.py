"""ICU 文案严格合并与保护回归；只使用版本快照和临时目录。"""
from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import icu_revision_text as revision


class ConditionalIcuTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[2]
        version = cls.root / "reproducibility/manuscript_versions/20261005_sec7_v2_refinement"
        cls.main = (version / "flatten_curve_analysis_cn.tex").read_text(encoding="utf-8-sig")
        cls.supplement = (version / "flatten_curve_supplement_cn.tex").read_text(encoding="utf-8-sig")
        cls.bib = (cls.root / "latex/references.bib").read_text(encoding="utf-8-sig")
        # 正式文献库在根任务发布后也可能含 Baas，测试基准仍取本轮以前的原条目。
        entries = revision.bibliography_entries(cls.bib)
        if revision.BAAS_KEY in entries:
            cls.bib = cls.bib.replace(entries[revision.BAAS_KEY], "", 1)
        cls.bundle = cls.root / revision.BUNDLE_RELATIVE
        import json
        cls.manifest = json.loads((cls.bundle / "merge_manifest.json").read_text(encoding="utf-8"))
        cls.anchors = [revision.normalize((cls.bundle / row["before_file"]).read_text(encoding="utf-8-sig")).strip()
                       for row in cls.manifest["operations"]]

    def test_candidate_protects_existing_scientific_content(self):
        main, bib, report = revision.candidate_texts(self.root, self.main, self.bib)
        preservation = revision.assert_protected_unchanged(self.main, main, self.supplement, self.supplement)
        self.assertTrue(report["passed"])
        self.assertFalse(report["scientific_calculation_reexecuted"])
        self.assertFalse(report["clinical_calibration_performed"])
        self.assertEqual(len(report["operations"]), 12)
        self.assertEqual(preservation["counts"]["proof"], 27)
        self.assertEqual(preservation["counts"]["figure"], 24)
        self.assertEqual(preservation["counts"]["table"], 5)
        self.assertEqual(preservation["supplement_tables"], 3)
        self.assertEqual(revision.bibliography_entries(bib).keys() - revision.bibliography_entries(self.bib).keys(),
                         {revision.BAAS_KEY})
        self.assertIn("全过程固定的本病可用容量", main)
        self.assertIn("即使已从传播模型移出", main)
        self.assertIn(revision.SCALING_AFTER, main)
        self.assertIn(revision.INTRO_AFTER, main)
        self.assertEqual(main.count(r"\begin{remark}"), self.main.count(r"\begin{remark}") + 1)

    def test_all_missing_and_duplicate_anchors_rejected(self):
        for anchor, row in zip(self.anchors, self.manifest["operations"]):
            for replacement in ("", anchor + "\n" + anchor):
                with self.subTest(id=row["id"], replacement=bool(replacement)), self.assertRaisesRegex(ValueError, "锚点须唯一"):
                    revision.candidate_texts(self.root, self.main.replace(anchor, replacement, 1), self.bib)

    def test_mixed_and_already_merged_blocks_rejected(self):
        row = self.manifest["operations"][0]
        new = (self.bundle / row["after_file"]).read_text(encoding="utf-8-sig").strip()
        with self.assertRaisesRegex(ValueError, "混入已合并块"):
            revision.candidate_texts(self.root, self.main + "\n" + new, self.bib)
        merged, _, _ = revision.candidate_texts(self.root, self.main, self.bib)
        with self.assertRaisesRegex(ValueError, "锚点须唯一"):
            revision.candidate_texts(self.root, merged, self.bib)

    def test_extra_local_anchors_missing_and_duplicate_rejected(self):
        for anchor in (revision.SCALING_BEFORE, revision.INTRO_BEFORE):
            for replacement in ("", anchor + "\n" + anchor):
                with self.subTest(anchor=anchor[:12], replacement=bool(replacement)), self.assertRaisesRegex(ValueError, "锚点须唯一"):
                    revision.candidate_texts(self.root, self.main.replace(anchor, replacement, 1), self.bib)

    def test_tampered_bundle_file_rejected(self):
        with tempfile.TemporaryDirectory(prefix="icu_prose_integrity_") as temp:
            root = Path(temp)
            copied = root / revision.BUNDLE_RELATIVE
            shutil.copytree(self.bundle, copied)
            target = copied / "tex/02_section22_medical_link.tex"
            target.write_text(target.read_text(encoding="utf-8") + "\n% changed\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "文件哈希不符"):
                revision.candidate_texts(root, self.main, self.bib)

    def test_tampered_hash_manifest_rejected(self):
        with tempfile.TemporaryDirectory(prefix="icu_prose_manifest_") as temp:
            root = Path(temp)
            copied = root / revision.BUNDLE_RELATIVE
            shutil.copytree(self.bundle, copied)
            (copied / "MANIFEST_SHA256.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "清单不是已批准"):
                revision.candidate_texts(root, self.main, self.bib)

    def test_doi_duplicate_and_wrong_key_rejected(self):
        addition = (self.bundle / "bibliography/Baas2021Occupancy.bib").read_text(encoding="utf-8")
        duplicate = self.bib + addition + addition.replace(revision.BAAS_KEY, "DuplicateOccupancy")
        with self.assertRaisesRegex(ValueError, "重复 DOI"):
            revision.candidate_texts(self.root, self.main, duplicate)
        wrong = self.bib + addition.replace(revision.BAAS_DOI, "10.0000/wrong")
        with self.assertRaisesRegex(ValueError, "引用键已用于不同"):
            revision.candidate_texts(self.root, self.main, wrong)

    def test_existing_doi_reuses_existing_key_without_bib_mutation(self):
        addition = (self.bundle / "bibliography/Baas2021Occupancy.bib").read_text(encoding="utf-8")
        old = self.bib + addition.replace(revision.BAAS_KEY, "ExistingOccupancy")
        main, bib, report = revision.candidate_texts(self.root, self.main, old)
        self.assertEqual(bib, old)
        self.assertIn(r"\cite{ExistingOccupancy}", main)
        self.assertNotIn(r"\cite{Baas2021Occupancy}", main)
        self.assertEqual(report["bibliography"]["added_keys"], [])

    def test_bibliography_omission_change_and_duplicate_key_rejected(self):
        _, bib, _ = revision.candidate_texts(self.root, self.main, self.bib)
        entries = revision.bibliography_entries(self.bib)
        original = entries["He2023TDINN"]
        for bad in (bib.replace(original, "", 1), bib.replace("identify the intensity", "change the intensity", 1)):
            with self.assertRaisesRegex(ValueError, "原参考文献条目变化或遗漏"):
                revision.assert_bibliography_preserved(self.bib, bad)
        with self.assertRaisesRegex(ValueError, "重复参考文献键"):
            revision.bibliography_entries(bib + "\n" + original)

    def test_lost_old_citation_rejected(self):
        merged, _, _ = revision.candidate_texts(self.root, self.main, self.bib)
        lost = merged.replace(r"\cite{Corless1996}", "", 1)
        self.assertNotEqual(merged, lost)
        with self.assertRaisesRegex(ValueError, "遗漏旧引用键"):
            revision.assert_protected_unchanged(self.main, lost)

    def test_proof_equation_table_figure_and_sec9_changes_rejected(self):
        merged, _, _ = revision.candidate_texts(self.root, self.main, self.bib)
        for text in (r"\begin{proof}", r"\begin{equation}", r"\begin{table}", r"\begin{figure}"):
            bad = merged.replace(text, text + "\n% unapproved scientific change", 1)
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "保护内容变化"):
                revision.assert_protected_unchanged(self.main, bad)
        marker = r"\label{sec:dominance}"
        with self.assertRaisesRegex(ValueError, "保护内容变化"):
            revision.assert_protected_unchanged(self.main, merged.replace(marker, marker + "\n% changed sec9", 1))

    def test_label_joint_block_and_supplement_changes_rejected(self):
        merged, _, _ = revision.candidate_texts(self.root, self.main, self.bib)
        for bad in (merged + r"\label{new:label}", merged.replace("% BEGIN JOINT_EXTRA:capacity", "% BEGIN JOINT_EXTRA:capacity\n% changed", 1)):
            with self.assertRaisesRegex(ValueError, "保护内容变化"):
                revision.assert_protected_unchanged(self.main, bad)
        with self.assertRaisesRegex(ValueError, "保护内容变化"):
            revision.assert_protected_unchanged(self.main, merged, self.supplement, self.supplement + "changed")

    def test_newline_bom_preserved_and_repeatable(self):
        source = "\ufeff" + self.main.replace("\n", "\r\n")
        first = revision.candidate_texts(self.root, source, self.bib)
        second = revision.candidate_texts(self.root, source, self.bib)
        self.assertEqual(first, second)
        self.assertTrue(first[0].startswith("\ufeff"))
        self.assertIn("\r\n", first[0])
        self.assertNotIn("\n", first[0].replace("\r\n", ""))


if __name__ == "__main__":
    unittest.main()
