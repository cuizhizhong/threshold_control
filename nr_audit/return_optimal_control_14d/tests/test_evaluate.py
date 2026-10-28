"""完整 ODE 评价器的接口与终点回归；只运行本研究新增的必要轨迹。"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("return14_independent_evaluator_test", ROOT / "evaluate.py")
EV = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EV)


@pytest.fixture(scope="module")
def isolation_reference():
    path = ROOT / "results" / "references" / "base_q_only.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else EV.reference("base", "q_only")


def test_linear_isolation_matches_event_reference(isolation_reference):
    result = EV.evaluate("base", isolation_reference["duration"], [1.0, 1.0],
                         save_path=ROOT / "results" / "evaluator_tests" / "linear_isolation.json")
    assert result["feasible"]
    assert abs(result["J"] - isolation_reference["J"]) < 1e-8
    assert abs(result["C_infinity_interval"][0] - isolation_reference["C_infinity_interval"][0]) < 1e-6
    assert result["tail_bound_persons"] <= 1.00001e-4
    assert result["I_not_fixed"] and result["no_compartment_clipping"]
    assert result["tail_state_persons"]["I"] < 1.0


def test_constant_segments_match_same_physical_control(isolation_reference):
    result = EV.evaluate("base", isolation_reference["duration"], [1.0, 1.0, 1.0], interpolation="constant",
                         save_path=ROOT / "results" / "evaluator_tests" / "constant_isolation.json")
    assert result["feasible"]
    assert abs(result["J"] - isolation_reference["J"]) < 1e-8
    assert abs(result["exit_residual_normalized"]) < 1e-9
    assert result["mass_residual_normalized"] < 1e-10
    assert result["cumulative_identity_residual_normalized"] < 1e-10


def test_duration_mismatch_is_reported_not_event_corrected(isolation_reference):
    duration = isolation_reference["duration"] * 0.9
    result = EV.evaluate("base", duration, [1.0], interpolation="constant",
                         save_path=ROOT / "results" / "evaluator_tests" / "wrong_duration.json")
    assert result["duration"] == duration
    assert not result["checks"]["exit_match"]
    assert not result["feasible"]
    assert result["exit_residual_normalized"] > 0.0


def test_invalid_control_is_rejected_without_clipping():
    with pytest.raises(ValueError, match="不作截断"):
        EV.evaluate("base", 10.0, [-0.2, 1.2])


def test_params_and_initial_full_state_are_consistent():
    p = EV.load_params("xian")
    start = EV.prepare_start("xian")
    assert p["omega"] == 1 / 14
    assert p["wc"] == 1 and p["wq"] == 2
    assert abs(sum(start["state_persons"].values()) / p["N"] - 1) < 1e-10
    assert abs(start["state_persons"]["I"] / p["eta"] - 1) < 1e-10
    assert np.asarray(start["y"]).shape == (8,)


def test_small_positive_threshold_excess_is_not_accepted_as_slack():
    assert EV._classify_threshold(1.0) == "satisfied"
    assert EV._classify_threshold(1.0 + 1e-14) == "boundary_roundoff"
    assert EV._classify_threshold(1.0 + 5e-9) == "undetermined"
    assert EV._classify_threshold(1.0 + 2e-7) == "violated"
    stable = EV.paired_threshold_status(1.0 + 5e-9, 1.0 + 5.0001e-9)
    assert stable["status"] == "violated"


def test_terminal_within_state_tolerance_is_explicit_not_null_success():
    assessment = EV._first_exit_assessment(30.0, 20.0, 5e-10,
                                           {"roots": [], "contacts": [], "stationary_points": []})
    assert assessment["time"] == 30.0
    assert assessment["status"] == "terminal_within_tolerance"
    assert assessment["terminal_within_tolerance"]
    assert assessment["early"] is False
    bad = EV._first_exit_assessment(30.0, 20.0, 5e-8, {"roots": []})
    assert bad["status"] == "not_matched" and bad["time"] is None


def test_stationary_contact_is_found_without_state_sign_change():
    touching = 0.43123
    class Dense:
        t = np.array([0.0, 1.0])
        def sol(self, times):
            t = np.asarray(times)
            out = np.zeros((8,) + t.shape)
            out[EV.IS] = 0.2 + (t - touching) ** 2
            return out
    details = EV._find_roots([(0.0, 1.0, Dense())], {"sc_N": 0.2},
                             derivative=lambda t, y: 2.0 * (t - touching), return_details=True)
    assert any(abs(t - touching) < 1e-10 for t in details["roots"])
    assert any(x["kind"] == "stationary_contact_roundoff" for x in details["contacts"])
