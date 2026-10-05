"""乘子加密的输入规则测试，不替代 A-D 科学复算。"""
import unittest
import numpy as np

from reproducibility.joint_extra.run import (KAPPA, ORIGINAL_KAPPA,
    KAPPA_REFINEMENT, KAPPA_DUPLICATE_TOLERANCE, refined_kappa_grid)


class KappaRefinementTests(unittest.TestCase):
    def test_counts_and_interval(self):
        self.assertEqual((len(ORIGINAL_KAPPA), len(KAPPA_REFINEMENT), len(KAPPA)), (310, 201, 470))
        self.assertEqual((KAPPA_REFINEMENT[0], KAPPA_REFINEMENT[-1]), (-.6, -.2))
        np.testing.assert_allclose(np.diff(KAPPA_REFINEMENT), .002, rtol=0, atol=np.finfo(float).eps)

    def test_original_float_values_preferred(self):
        for original in ORIGINAL_KAPPA:
            self.assertTrue(np.any(KAPPA == original))
        # 原网格自身有两对近重复浮点数；优先保留原值，不回溯删除它们。
        for new in KAPPA:
            if not np.any(ORIGINAL_KAPPA == new):
                others = KAPPA[KAPPA != new]
                self.assertTrue(np.all(np.abs(others-new) > KAPPA_DUPLICATE_TOLERANCE))

    def test_deterministic_and_zero_retained(self):
        np.testing.assert_array_equal(KAPPA, refined_kappa_grid())
        self.assertEqual(np.count_nonzero(KAPPA == 0), 1)


if __name__ == '__main__':
    unittest.main()
