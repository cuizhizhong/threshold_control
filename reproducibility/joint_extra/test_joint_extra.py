"""活动模块的确定性小样本测试；不写入科学输出目录。"""
from __future__ import annotations

from dataclasses import replace
import unittest
import numpy as np

if __package__:
    from . import core, validation, run
else:
    import core
    import validation
    import run


class CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, _, _ = core.load_inputs()
        cls.p = cls.cases["baseline"]
        cls.e = core.basics(cls.p)

    def test_inputs_and_defaults(self):
        self.assertEqual(self.p.N, 763.)
        self.assertEqual(self.cases["xian"].delta_q, .3531)
        self.assertEqual(self.cases["xian"].I0, .00100659188867187)
        self.assertAlmostEqual(self.e["Sstar"], 708.3469575874325, places=7)

    def test_bad_inputs(self):
        for field, value in (("I0", 0.), ("eta", 1.), ("q0", 1.), ("S0", 763.)):
            with self.assertRaises(ValueError):
                core.validate_inputs(replace(self.p, **{field: value}))

    def test_beta_one_is_probability_endpoint(self):
        core.validate_inputs(replace(self.p, beta=1.))

    def test_explicit_endpoint_and_alpha(self):
        for name, expected in (("contact_only", self.p.Sc/self.e["Sstar"]), ("quarantine_only", 1.),
                               ("alpha_0.5", .5+.5*self.p.Sc/self.e["Sstar"])):
            pol = core.build_profile(self.p, self.e, name, ns=101)
            self.assertAlmostEqual(pol.x(self.e["Sstar"]), expected, places=14)
            self.assertEqual(pol.x(self.p.Sc), 1.)

    def test_kappa_changes_stationary_equation(self):
        S = 1.5*self.p.Sc
        normal = core.candidates(S, self.p)["x"]
        positive = core.candidates(S, self.p, kappa=1.)["x"]
        negative = core.candidates(S, self.p, kappa=-1.)["x"]
        self.assertGreater(positive, normal)
        self.assertLess(negative, normal)
        for k in (-1., 0., 1.):
            self.assertTrue(core.grid_check(S, self.p, kappa=k)["passed"])

    def test_coordinate_cross_check(self):
        for r in (.1, 2., 5., 20.):
            for S in np.linspace(self.p.Sc*1.001, self.e["Sstar"], 11):
                a = core.candidates(S, self.p, wq=r, force_coordinate="x")
                b = core.candidates(S, self.p, wq=r, force_coordinate="y")
                self.assertLess(abs(a["x"]-b["x"]), 1e-7)

    def test_near_exit_independent_share(self):
        for r in (.1, .5, 1., 2., 5., 20.):
            for z in (1e-7, 1e-9, 1e-11, 1e-13):
                c = core.candidates(self.p.Sc/(1-z), self.p, wq=r)
                self.assertLess(abs(c["y"]-r/(1+r)), 1e-5)
        self.assertIsNone(core.candidates(self.p.Sc, self.p)["y"])

    def test_capacity_edges(self):
        self.assertTrue(run.capacity_edge_checks(self.p, self.e)["passed"])
        with self.assertRaises(ValueError):
            core.candidates(self.e["Sstar"], self.p, cmin=self.p.c0, qcap=self.p.q0)
        degenerate = core.candidates(self.e["Sstar"], self.p, qcap=self.p.q0)
        self.assertEqual(degenerate["branch"], "degenerate")

    def test_default_j_and_time_small_grid(self):
        pol = core.build_profile(self.p, self.e, ns=1001)
        state = core.evaluate_policy(pol)
        self.assertAlmostEqual(state["J_state"], 2.118274558487, places=7)
        self.assertAlmostEqual(state["duration_state"], 7.75359790983, places=5)
        self.assertTrue(validation.candidate_checks(pol)["passed"])

    def test_openloop_and_peak_baseline(self):
        pol = core.build_profile(self.p, self.e, ns=1001)
        state = core.evaluate_policy(pol)
        time, trace = core.full_run(pol, trace_points=101)
        self.assertTrue(validation.policy_checks(pol, state, time)["passed"])
        self.assertTrue(trace)
        self.assertLess(time["I_threshold_excess"], 1e-5)
        self.assertGreater(time["peak_I_plus_Iq"], self.p.eta)
        self.assertGreater(time["t_peak_I_plus_Iq"], 0.)

    def test_kappa_jump_is_time_segmented(self):
        pol = core.build_profile(self.p, self.e, kappa=-.3, ns=1001)
        self.assertTrue(pol.switches)
        state = core.evaluate_policy(pol)
        time, _ = core.full_run(pol, trace_points=101)
        self.assertTrue(validation.policy_checks(pol, state, time)["passed"])
        self.assertEqual(len(time["nominal_segment_times"]), len(pol.pieces))

    def test_previous_D_fraction_failure_at_exact_switch(self):
        kappa = -.006700187503509591
        pol = core.build_profile(self.p, self.e, kappa=kappa, ns=4001)
        refined = core.build_profile(self.p, self.e, kappa=kappa, ns=8001)
        self.assertTrue(validation.convergence(core.evaluate_policy(pol), core.evaluate_policy(refined))["passed"])
        self.assertTrue(validation.candidate_checks(refined, states=5)["passed"])
        for part in pol.pieces:
            for S in (part["lo"], part["hi"]):
                lo, hi = core.bounds(S, self.p)
                x = pol.local_x(S, part)
                self.assertGreaterEqual(x, lo-1e-12)
                self.assertLessEqual(x, hi+1e-12)

    def test_gauss_orders_default_and_kappa_jump(self):
        for kappa in (0., -.3):
            pol = core.build_profile(self.p, self.e, kappa=kappa, ns=1001)
            state = core.evaluate_policy(pol)
            self.assertEqual(list(state["quadrature_order_values"]), ["4", "8", "16"])
            self.assertTrue(validation.quadrature_checks(state)["passed"])

    def test_xian_contact_analytic_clock_regression(self):
        p = self.cases["xian"]
        pol = core.build_profile(p, name="contact_only", ns=101)
        state = core.evaluate_policy(pol)
        time, _ = core.full_run(pol, trace_points=101)
        tight, _ = core.full_run(pol, tight=True, trace_points=101)
        self.assertTrue(validation.policy_checks(pol, state, time)["passed"])
        self.assertTrue(validation.policy_checks(pol, state, tight)["passed"])
        self.assertTrue(validation.convergence(time, tight, time=True)["passed"])

    def test_xian_capacity_minimum_quadrature_and_openloop(self):
        p = self.cases["xian"]
        pol = core.build_profile(p, cmin=.5*p.c0, qcap=.75, ns=8001)
        state = core.evaluate_policy(pol)
        self.assertAlmostEqual(state["duration_state"], 116.75128552327438, places=8)
        self.assertTrue(validation.quadrature_checks(state)["passed"])
        time, _ = core.full_run(pol, trace_points=101)
        tight, _ = core.full_run(pol, tight=True, trace_points=101)
        self.assertTrue(validation.policy_checks(pol, state, time)["passed"])
        self.assertTrue(validation.policy_checks(pol, state, tight)["passed"])
        self.assertTrue(validation.convergence(time, tight, time=True)["passed"])

    def test_phase_switch_refinement_sample(self):
        for r in (.1, 2., 5., 20.):
            states = np.linspace(self.p.Sc, self.e["Sstar"], 1201)
            rows = [core.candidates(float(S), self.p, 1., r) for S in states]
            self.assertTrue(all(validation.phase_cell_check(row, S, self.p, r)["passed"]
                                for S, row in zip(states[1:], rows[1:])))
            upper = [j for j, row in enumerate(rows) if row["branch"] == "upper"]
            if upper and upper[0] > 1:
                j = upper[0]
                switch = core._locate_switch(self.p, states[j-1], states[j], rows[j-1], rows[j], 1., r, 0., 0., None)
                self.assertTrue(validation.phase_switch_check(switch, self.p, r, (states[j-1], states[j]))["passed"])

    def test_capacity_equality_two_cases_openloop(self):
        for p in self.cases.values():
            e = core.basics(p)
            B = (1-p.q0)*p.Sc/e["Sstar"]
            pol = core.build_profile(p, e, cmin=.5*p.c0, qcap=1-B/.5, ns=8001)
            lo, hi = core.bounds(e["Sstar"], p, pol.cmin, pol.qcap)
            self.assertLess(abs(hi-lo), 1e-14)
            state = core.evaluate_policy(pol)
            time, _ = core.full_run(pol, trace_points=101)
            tight, _ = core.full_run(pol, tight=True, trace_points=101)
            self.assertTrue(validation.policy_checks(pol, state, time)["passed"])
            self.assertTrue(validation.policy_checks(pol, state, tight)["passed"])
            self.assertTrue(validation.convergence(time, tight, time=True)["passed"])

    def test_xian_capacity_full_state_grid_convergence(self):
        p = self.cases["xian"]
        coarse = core.build_profile(p, cmin=.5*p.c0, qcap=.75, ns=8001)
        refined = core.build_profile(p, cmin=.5*p.c0, qcap=.75, ns=16001)
        self.assertTrue(validation.convergence(core.evaluate_policy(coarse), core.evaluate_policy(refined))["passed"])
        geometric = p.c0*p.Sc/coarse.cmin
        self.assertTrue(any(part["lo"] == geometric or part["hi"] == geometric for part in coarse.pieces))

    def test_missing_stationary_branch_not_fake_zero_switch(self):
        kappa = -.24620924014946255
        coarse = core.build_profile(self.p, self.e, kappa=kappa, ns=4001)
        refined = core.build_profile(self.p, self.e, kappa=kappa, ns=8001)
        self.assertTrue(validation.convergence(core.evaluate_policy(coarse), core.evaluate_policy(refined))["passed"])
        for policy in (coarse, refined):
            jumps = [record for record in policy.switches if record["jump"]]
            self.assertEqual(len(jumps), 1)
            self.assertAlmostEqual(jumps[0]["S"], 497.065139816, places=7)
            self.assertTrue(validation.candidate_checks(policy, states=5)["passed"])

    def test_json_missing_is_null(self):
        self.assertIsNone(run.clean(float("nan")))
        self.assertIsNone(run.clean(np.float64("inf")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
