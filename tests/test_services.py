"""Unit tests for lifting service."""

from __future__ import annotations

import math
import unittest

from app.core.exceptions import ValidationError
from app.core.models import AnchorageType, BondCondition, LiftingInput
from app.core.services import (
    GAMMA_C,
    GAMMA_S,
    LEGS_PER_LOOP,
    LiftingVerifierService,
    N_PER_TF,
)


class LiftingVerifierServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = LiftingVerifierService()

    def _default_input(self, **overrides) -> LiftingInput:
        kwargs = dict(
            fckj_mpa=25.0,
            fck_28_mpa=40.0,
            volume_m3=2.0,
            concrete_unit_weight_tf_m3=2.5,
            strand_key="CP 190-RB 12,7 mm",
            inclination_deg=60.0,
            available_anchorage_cm=60.0,
            bond_condition=BondCondition.GOOD,
            anchorage_type=AnchorageType.STRAIGHT,
            loops_count=2,
        )
        kwargs.update(overrides)
        return LiftingInput(**kwargs)

    def test_calculate_returns_positive_values(self) -> None:
        result = self.service.calculate(self._default_input())

        self.assertGreater(result.piece_weight_tf, 0.0)
        self.assertGreater(result.majorated_weight_tf, result.piece_weight_tf)
        self.assertGreater(result.required_anchorage_cm, 0.0)
        self.assertGreater(result.max_supported_load_tf, 0.0)
        self.assertGreater(result.tension_per_loop_tf, 0.0)

    def test_piece_weight_formula(self) -> None:
        data = self._default_input(volume_m3=3.0, concrete_unit_weight_tf_m3=2.5)
        result = self.service.calculate(data)
        self.assertAlmostEqual(result.piece_weight_tf, 7.5, places=4)

    def test_majorated_weight_formula(self) -> None:
        data = self._default_input(volume_m3=2.0, concrete_unit_weight_tf_m3=2.5)
        result = self.service.calculate(data)
        expected = 2.0 * 2.5 * data.beta_a * data.gamma_n
        self.assertAlmostEqual(result.majorated_weight_tf, expected, places=4)

    def test_tension_per_loop_and_leg(self) -> None:
        data = self._default_input(loops_count=4, inclination_deg=90.0)
        result = self.service.calculate(data)
        expected_loop = result.majorated_weight_tf / (4 * math.sin(math.radians(90.0)))
        self.assertAlmostEqual(result.tension_per_loop_tf, expected_loop, places=4)
        self.assertAlmostEqual(result.tension_per_leg_tf, expected_loop / LEGS_PER_LOOP, places=4)
        self.assertEqual(result.total_legs, 4 * LEGS_PER_LOOP)

    def test_fctm_j_formula_below_50(self) -> None:
        data = self._default_input(fckj_mpa=30.0)
        result = self.service.calculate(data)
        expected_fctm = 0.3 * (30.0 ** (2.0 / 3.0))
        self.assertAlmostEqual(result.fctm_j_mpa, expected_fctm, places=4)

    def test_fctm_28_uses_fck_28(self) -> None:
        data = self._default_input(fck_28_mpa=45.0)
        result = self.service.calculate(data)
        expected_fctm_28 = 0.3 * (45.0 ** (2.0 / 3.0))
        self.assertAlmostEqual(result.fctm_28_mpa, expected_fctm_28, places=4)

    def test_fpyd_formula(self) -> None:
        result = self.service.calculate(self._default_input())
        self.assertAlmostEqual(result.fpyd_mpa, 1710.0 / GAMMA_S, places=2)

    def test_dual_age_fbpd(self) -> None:
        """fbpd_j uses fckj, fbpd_28 uses fck_28. fck_28 > fckj => fbpd_28 > fbpd_j."""
        data = self._default_input(fckj_mpa=20.0, fck_28_mpa=40.0)
        result = self.service.calculate(data)
        self.assertGreater(result.fbpd_28_mpa, result.fbpd_j_mpa)

    def test_anchorage_uses_fbpd_28(self) -> None:
        """Anchorage length should use fbpd_28 (28 days), resulting in
        shorter required length than if fbpd_j were used."""
        data = self._default_input(fckj_mpa=20.0, fck_28_mpa=40.0)
        result = self.service.calculate(data)
        # Recalculate what base_anchorage would be with fbpd_j
        base_anc_with_j = (
            (result.tension_per_leg_tf * N_PER_TF)
            / (result.fbpd_j_mpa * math.pi * 12.7)
            / 10.0
        )
        # Actual base anchorage uses fbpd_28 => shorter
        self.assertLess(result.base_anchorage_cm, base_anc_with_j)

    def test_bond_capacity_uses_fbpd_j(self) -> None:
        """Bond capacity at lifting should use fbpd_j (age j), not fbpd_28."""
        data = self._default_input(fckj_mpa=20.0, fck_28_mpa=40.0)
        result = self.service.calculate(data)
        # Manually compute bond capacity with fbpd_j
        expected_bond_per_leg = (
            result.fbpd_j_mpa * math.pi * 12.7 * data.available_anchorage_cm * 10.0
        ) / N_PER_TF
        sin_i = math.sin(math.radians(data.inclination_deg))
        expected_total = expected_bond_per_leg * result.total_legs * sin_i
        self.assertAlmostEqual(result.max_supported_load_by_bond_tf, expected_total, places=4)

    def test_bad_bond_requires_more_anchorage(self) -> None:
        good = self.service.calculate(
            self._default_input(bond_condition=BondCondition.GOOD)
        )
        poor = self.service.calculate(
            self._default_input(bond_condition=BondCondition.POOR)
        )

        self.assertGreater(poor.required_anchorage_cm, good.required_anchorage_cm)
        self.assertLess(poor.max_supported_load_by_bond_tf, good.max_supported_load_by_bond_tf)

    def test_inclination_90_is_valid(self) -> None:
        data = self._default_input(inclination_deg=90.0)
        result = self.service.calculate(data)
        self.assertGreater(result.max_supported_load_tf, 0.0)

    def test_utilization_ratio_and_safety_factor(self) -> None:
        result = self.service.calculate(self._default_input())
        expected_util = result.majorated_weight_tf / result.max_supported_load_tf
        expected_fs = result.max_supported_load_tf / result.majorated_weight_tf
        self.assertAlmostEqual(result.utilization_ratio, expected_util, places=4)
        self.assertAlmostEqual(result.safety_factor, expected_fs, places=4)

    def test_capacity_is_ok_when_load_within_capacity(self) -> None:
        data = self._default_input(
            volume_m3=0.1,
            loops_count=4,
            available_anchorage_cm=300.0,
        )
        result = self.service.calculate(data)
        self.assertTrue(result.capacity_is_ok)
        self.assertLessEqual(result.utilization_ratio, 1.0)

    def test_capacity_not_ok_when_overloaded(self) -> None:
        data = self._default_input(
            volume_m3=100.0,
            loops_count=1,
            available_anchorage_cm=10.0,
        )
        result = self.service.calculate(data)
        self.assertFalse(result.capacity_is_ok)
        self.assertGreater(result.utilization_ratio, 1.0)

    def test_invalid_volume_raises(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.calculate(self._default_input(volume_m3=0.0))

    def test_invalid_inclination_raises(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.calculate(self._default_input(inclination_deg=0.0))
        with self.assertRaises(ValidationError):
            self.service.calculate(self._default_input(inclination_deg=91.0))

    def test_fck_28_less_than_fckj_raises(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.calculate(self._default_input(fckj_mpa=40.0, fck_28_mpa=30.0))

    def test_calculation_memory_contains_formulas(self) -> None:
        data = self._default_input(fckj_mpa=30.0, volume_m3=1.5)
        result = self.service.calculate(data)
        memory = self.service.build_calculation_memory(data, result)

        self.assertIn("MEMORIA DE CALCULO", memory)
        self.assertIn("ged = gk x Ba x yn", memory)
        self.assertIn("Lnec", memory)
        self.assertIn("VERIFICACOES", memory)
        self.assertIn("RESULTADO FINAL", memory)

    def test_calculation_memory_shows_dual_age(self) -> None:
        data = self._default_input(fckj_mpa=30.0, fck_28_mpa=45.0)
        result = self.service.calculate(data)
        memory = self.service.build_calculation_memory(data, result)
        self.assertIn("Fck,j = 30.00 MPa", memory)
        self.assertIn("Fck,28 = 45.00 MPa", memory)
        self.assertIn("fbpd,j", memory)
        self.assertIn("fbpd,28", memory)

    def test_calculation_memory_includes_piece_identification(self) -> None:
        data = self._default_input(piece_id="VIGA-A1")
        result = self.service.calculate(data)
        memory = self.service.build_calculation_memory(data, result)
        self.assertIn("IDENTIFICACAO DA PECA: VIGA-A1", memory)

    def test_calculation_memory_shows_approved_or_rejected(self) -> None:
        data = self._default_input(volume_m3=0.05, available_anchorage_cm=300.0, loops_count=4)
        result = self.service.calculate(data)
        memory = self.service.build_calculation_memory(data, result)
        self.assertIn("APROVADO", memory)

        data_fail = self._default_input(volume_m3=100.0, available_anchorage_cm=5.0, loops_count=1)
        result_fail = self.service.calculate(data_fail)
        memory_fail = self.service.build_calculation_memory(data_fail, result_fail)
        self.assertIn("REPROVADO", memory_fail)

    def test_custom_beta_a_gamma_n(self) -> None:
        data = self._default_input(beta_a=4.0, gamma_n=1.0)
        result = self.service.calculate(data)
        expected = data.volume_m3 * data.concrete_unit_weight_tf_m3 * 4.0 * 1.0
        self.assertAlmostEqual(result.majorated_weight_tf, expected, places=4)
        self.assertAlmostEqual(result.beta_a, 4.0)
        self.assertAlmostEqual(result.gamma_n, 1.0)

    def test_anchorage_type_straight_has_alpha_1(self) -> None:
        result = self.service.calculate(
            self._default_input(anchorage_type=AnchorageType.STRAIGHT)
        )
        self.assertAlmostEqual(result.alpha_anchorage, 1.00, places=4)
        self.assertAlmostEqual(result.required_anchorage_cm, result.base_anchorage_cm, places=4)

    def test_anchorage_hook_90_reduces_required_length(self) -> None:
        straight = self.service.calculate(
            self._default_input(anchorage_type=AnchorageType.STRAIGHT)
        )
        hook90 = self.service.calculate(
            self._default_input(anchorage_type=AnchorageType.HOOK_90)
        )
        self.assertAlmostEqual(hook90.alpha_anchorage, 0.70, places=4)
        self.assertAlmostEqual(
            hook90.required_anchorage_cm, 0.70 * straight.base_anchorage_cm, places=4
        )
        self.assertLess(hook90.required_anchorage_cm, hook90.base_anchorage_cm)

    def test_anchorage_hook_180_reduces_required_length_most(self) -> None:
        hook90 = self.service.calculate(
            self._default_input(anchorage_type=AnchorageType.HOOK_90)
        )
        hook180 = self.service.calculate(
            self._default_input(anchorage_type=AnchorageType.HOOK_180)
        )
        self.assertAlmostEqual(hook180.alpha_anchorage, 0.50, places=4)
        self.assertLess(hook180.required_anchorage_cm, hook90.required_anchorage_cm)

    def test_hook_may_convert_fail_to_pass(self) -> None:
        """A case that fails with straight anchorage may pass with a hook."""
        data_straight = self._default_input(
            fckj_mpa=25.0, volume_m3=2.0, loops_count=2,
            available_anchorage_cm=60.0, anchorage_type=AnchorageType.STRAIGHT,
        )
        data_hook = self._default_input(
            fckj_mpa=25.0, volume_m3=2.0, loops_count=2,
            available_anchorage_cm=60.0, anchorage_type=AnchorageType.HOOK_90,
        )
        result_straight = self.service.calculate(data_straight)
        result_hook = self.service.calculate(data_hook)
        # Both share the same base anchorage
        self.assertAlmostEqual(
            result_straight.base_anchorage_cm, result_hook.base_anchorage_cm, places=4
        )
        # Hook result has a shorter required length
        self.assertLess(result_hook.required_anchorage_cm, result_straight.required_anchorage_cm)


if __name__ == "__main__":
    unittest.main()
