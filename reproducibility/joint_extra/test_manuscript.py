"""出版文案的确定性正负例；只读历史验收数据，不复算、不写入验收目录。"""
from __future__ import annotations

import copy
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

if __package__:
    from . import manuscript as m
else:
    import manuscript as m


class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = Path(__file__).resolve().parents[1] / "results/joint_integration_20261004/joint_extra"
        cls.manifest = m.load_json(cls.res / "input_manifest.json")
        cls.validation = m.load_json(cls.res / "validation.json")
        cls.phase = m.load_json(cls.res / "phase.json")
        cls.capacity = m.load_json(cls.res / "capacity.json")
        cls.compare = {case: m.comparison_rows(cls.res, case) for case in ("baseline", "xian")}
        cls.frontier = m.load_rows(cls.res / "frontier_baseline.csv")
        cls.grid = {case: m.phase_grid(cls.res, case) for case in cls.compare}
        cls.allocation = {
            case: m.allocation_structure(cls.res, case, cls.phase[case], cls.compare[case],
                                         cls.validation["tasks"]["A"])
            for case in cls.compare
        }

    def test_full_readonly_publication_regression(self):
        fragments = m.build_publication_fragments(self.res)
        self.assertEqual(set(fragments), {"comparison", "capacity", "phase", "duration", "xian", "conclusion"})
        self.assertIn("几乎处处", fragments["comparison"])
        self.assertIn("同一易感者状态下", fragments["capacity"])
        self.assertIn("直到网格点", fragments["phase"])
        self.assertIn("充分条件", fragments["duration"])
        self.assertNotIn("增长加快", fragments["duration"])

    def test_default_weights_from_manifest(self):
        original = m.load_json
        bad = copy.deepcopy(self.manifest)
        bad["settings"]["weights"] = [1., 3.]
        with patch.object(m, "load_json", side_effect=lambda path: bad if Path(path).name == "input_manifest.json" else original(path)):
            with self.assertRaisesRegex(ValueError, "默认二次权重"):
                m.build_publication_fragments(self.res)

    def test_parameters_weights_cannot_disagree(self):
        bad = copy.deepcopy(self.manifest)
        bad["cases"]["xian"]["parameters"]["wq"] = 1.
        with patch.object(m, "load_json", return_value=bad):
            with self.assertRaisesRegex(ValueError, "输入参数"):
                m.check_default_weights(self.res)

    def test_real_c0_not_controlled_start_c(self):
        bad = copy.deepcopy(self.manifest)
        bad["cases"]["baseline"]["parameters"]["c0"] *= .609
        with patch.object(m, "load_json", return_value=bad):
            with self.assertRaisesRegex(ValueError, "常规接触率"):
                m.capacity_structure(self.res, "baseline", self.capacity["baseline"], self.phase["baseline"],
                                     self.compare["baseline"], self.validation["tasks"]["A"],
                                     self.validation["tasks"]["B"])

    def test_contact_cap_point_fifteen_rejected(self):
        bad = copy.deepcopy(self.capacity["baseline"])
        bad["point"]["u_max"] = .15
        with self.assertRaisesRegex(ValueError, "接触减少超过能力"):
            m.capacity_structure(self.res, "baseline", bad, self.phase["baseline"], self.compare["baseline"],
                                 self.validation["tasks"]["A"], self.validation["tasks"]["B"])

    def test_missing_time_boundary_rejected(self):
        task = copy.deepcopy(self.validation["tasks"]["A"])
        task["cases"]["baseline"]["strategies"]["minimum_cost"]["time_diagnostics"]["nominal_segment_methods"] = []
        with self.assertRaisesRegex(ValueError, "没有 S="):
            m.allocation_structure(self.res, "baseline", self.phase["baseline"], self.compare["baseline"], task)

    def test_changed_default_independent_switch_rejected(self):
        task = copy.deepcopy(self.validation["tasks"]["A"])
        task["cases"]["baseline"]["strategies"]["minimum_cost"]["candidate_checks"]["switches"][0]["S"] += 1.
        with self.assertRaisesRegex(ValueError, "唯一的连续切换"):
            m.allocation_structure(self.res, "baseline", self.phase["baseline"], self.compare["baseline"], task)

    def test_changed_peak_relation_rejected(self):
        bad = copy.deepcopy(self.allocation)
        bad["xian"]["same_peak"] = False
        with self.assertRaisesRegex(ValueError, "峰值与分配分叉"):
            m.comparison_text(self.compare["baseline"], self.compare["xian"], {}, bad)

    def test_default_ratio_is_not_nearest_grid_row(self):
        self.assertFalse(np.isclose(self.grid["baseline"]["r"], 2., atol=1e-12, rtol=0.).any())
        switch = self.validation["tasks"]["A"]["cases"]["baseline"]["strategies"]["minimum_cost"]
        self.assertAlmostEqual(m.default_switch(switch, self.phase["baseline"]["S_sw"])["S"],
                               self.phase["baseline"]["S_sw"], places=7)

    def test_phase_grid_change_rejected(self):
        bad = copy.deepcopy(self.grid["baseline"])
        bad["r"][10] = 2.
        with patch.object(m, "phase_grid", return_value=bad):
            with self.assertRaisesRegex(ValueError, "有限对数网格"):
                m.phase_structure(self.res, "baseline", self.phase["baseline"])

    def test_phase_switch_backtracking_rejected(self):
        bad = copy.deepcopy(self.phase["baseline"])
        jumps = [i for i, item in enumerate(bad["switches"]) if item["jump"]]
        bad["switches"][jumps[1]]["S"] = .9 * bad["switches"][jumps[0]]["S"]
        with self.assertRaisesRegex(ValueError, "非减地"):
            m.phase_structure(self.res, "baseline", bad)

    def test_phase_jump_pattern_change_rejected(self):
        bad = copy.deepcopy(self.phase["baseline"])
        bad["switches"][0]["jump"] = True
        with self.assertRaisesRegex(ValueError, "先连续"):
            m.phase_structure(self.res, "baseline", bad)

    def test_actual_duration_endpoints_include_equalities(self):
        rows = self.compare["baseline"]
        lower = m.value(rows["quarantine_only"], "duration_state")
        upper = m.value(rows["minimum_cost"], "duration_state")
        self.assertTrue(m.duration_bounds(rows, lower))
        self.assertTrue(m.duration_bounds(rows, upper))
        self.assertFalse(m.duration_bounds(rows, 5.90))
        text = m.duration_text(self.frontier, rows)
        self.assertIn(r"\Delta t[c_0]\le T\le\Delta t[c_c^*]", text)
        self.assertNotIn(r"5.90\le T", text)
        self.assertIn("实际二次成本", text)
        self.assertNotIn("J_q", text)

    def test_failed_row_not_silently_filtered(self):
        bad = copy.deepcopy(self.frontier)
        bad[3]["passed"] = False
        with self.assertRaisesRegex(ValueError, "失败或未验收"):
            m.duration_text(bad, self.compare["baseline"])

    def test_nonfinite_any_numeric_d_field_rejected(self):
        for field in ("duration", "J", "plateau_infections", "kappa"):
            bad = copy.deepcopy(self.frontier)
            bad[5][field] = float("nan")
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "非有限"):
                m.duration_text(bad, self.compare["baseline"])

    def test_failed_d_task_rejected(self):
        original = m.load_json
        bad = copy.deepcopy(self.validation)
        bad["tasks"]["D"].update(passed=False, status="failed")
        with patch.object(m, "load_json", side_effect=lambda path: bad if Path(path).name == "validation.json" else original(path)):
            with self.assertRaisesRegex(RuntimeError, "任务 D 已执行"):
                m.build_publication_fragments(self.res)

    def test_zero_multiplier_regression_rejected(self):
        bad = copy.deepcopy(self.frontier)
        next(row for row in bad if row["kappa"] == 0.)["J"] *= 1.01
        with self.assertRaisesRegex(ValueError, "零乘子回归"):
            m.duration_text(bad, self.compare["baseline"])

    def test_cost_upper_bound_is_actual_not_rounded_ratio(self):
        bad = copy.deepcopy(self.frontier)
        # 仅隔离/最低成本实际比值约1.0497，1.05不能作为替代验收界。
        point = next(row for row in bad if row["kappa"] > 0.)
        point["J"] = 1.05 * m.value(self.compare["baseline"]["minimum_cost"], "J_state")
        with self.assertRaisesRegex(ValueError, "成本高于仅隔离"):
            m.duration_text(bad, self.compare["baseline"])

    def test_dynamic_count_470_is_a_rendering_fixture_not_scientific_claim(self):
        rows = copy.deepcopy(self.frontier)
        for i in range(160):
            row = copy.deepcopy(rows[0])
            row["kappa"] = -200. - i
            rows.append(row)
        text = m.duration_text(rows, self.compare["baseline"])
        self.assertIn("$470$ 个", text)
        self.assertNotIn("$310$ 个", text)

    def test_dynamic_ten_percent_point_and_next_duration(self):
        rows = copy.deepcopy(self.frontier)
        threshold = 1.10 * m.value(self.compare["baseline"]["minimum_cost"], "J_state")
        inside = sorted((row for row in rows if row["kappa"] < 0 and row["J"] <= threshold),
                        key=lambda row: row["duration"])[-1]
        old = inside["duration"]
        inside["duration"] += .02
        text = m.duration_text(rows, self.compare["baseline"])
        self.assertIn(m.fixed(old + .02), text)
        self.assertIn("不是精确的临界时长", text)

    def test_gap_caption_is_actual_connection_data(self):
        old = m.duration_text(self.frontier, self.compare["baseline"])
        self.assertIn("时长间距较大处不连线", old)
        rows = copy.deepcopy(self.frontier)
        for row in rows:
            row.update(connection_group=0., duration_gap_before=False)
        text = m.duration_text(rows, self.compare["baseline"])
        self.assertNotIn("时长间距较大处不连线", text)
        self.assertIn("短虚线", text)
        self.assertIn("不表示中间时长已有匹配乘子", text)

    def test_inconsistent_connection_metadata_rejected(self):
        rows = copy.deepcopy(self.frontier)
        for row in rows:
            row["duration_gap_before"] = False
        with self.assertRaisesRegex(ValueError, "连接分组不一致"):
            m.duration_text(rows, self.compare["baseline"])


if __name__ == "__main__":
    unittest.main()
