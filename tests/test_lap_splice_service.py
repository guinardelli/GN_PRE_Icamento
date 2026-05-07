"""Tests for LapSpliceService."""

import pytest

from app.core.anchorage_models import AnchorageType, BondCondition, EffortType, SteelType
from app.core.exceptions import ValidationError
from app.core.lap_splice_models import LapSpliceInput
from app.core.lap_splice_services import LapSpliceService


@pytest.fixture
def service() -> LapSpliceService:
    return LapSpliceService()


def _base_input(**overrides: object) -> LapSpliceInput:
    values = {
        "diameter_1_mm": 10.0,
        "diameter_2_mm": 10.0,
        "fck_mpa": 30.0,
        "steel_type": SteelType.CA50,
        "bond_condition": BondCondition.GOOD,
        "effort_type": EffortType.TENSION,
        "anchorage_type": AnchorageType.STRAIGHT,
        "as_calc_cm2": 1.0,
        "as_ef_cm2": 1.0,
        "spliced_bars_percent": 20.0,
        "clear_distance_cm": 0.0,
        "available_lap_cm": 100.0,
    }
    values.update(overrides)
    return LapSpliceInput(**values)


@pytest.mark.parametrize(
    ("percent", "expected_alpha0t"),
    (
        (20.0, 1.2),
        (25.0, 1.4),
        (33.0, 1.6),
        (50.0, 1.8),
        (75.0, 2.0),
    ),
)
def test_tension_alpha0t_brackets(
    service: LapSpliceService,
    percent: float,
    expected_alpha0t: float,
) -> None:
    result = service.calculate(_base_input(spliced_bars_percent=percent))

    assert result.alpha0t == pytest.approx(expected_alpha0t)
    assert result.lap_calculated_cm == pytest.approx(expected_alpha0t * result.lb_nec_cm)


def test_compression_uses_l0c_minimum_without_alpha0t(service: LapSpliceService) -> None:
    data = _base_input(
        diameter_1_mm=20.0,
        diameter_2_mm=20.0,
        effort_type=EffortType.COMPRESSION,
        anchorage_type=AnchorageType.STRAIGHT,
    )

    result = service.calculate(data)

    assert result.alpha0t is None
    assert result.lap_calculated_cm == pytest.approx(result.lb_nec_cm)
    assert result.lap_min_cm == pytest.approx(
        max(0.6 * result.lb_cm, 15.0 * result.reference_diameter_mm / 10.0, 20.0)
    )


def test_diameter_32_allowed_and_40_blocked(service: LapSpliceService) -> None:
    result = service.calculate(_base_input(diameter_1_mm=32.0, diameter_2_mm=32.0))
    assert result.reference_diameter_mm == 32.0

    with pytest.raises(ValidationError, match="bitolas > 32 mm"):
        service.calculate(_base_input(diameter_1_mm=40.0, diameter_2_mm=40.0))


def test_different_diameters_use_larger_reference(service: LapSpliceService) -> None:
    result = service.calculate(_base_input(diameter_1_mm=12.5, diameter_2_mm=20.0))
    memory = service.build_calculation_memory(
        _base_input(diameter_1_mm=12.5, diameter_2_mm=20.0),
        result,
    )

    assert result.reference_diameter_mm == 20.0
    assert result.used_larger_diameter
    assert "adotada a maior bitola" in memory


def test_clear_distance_greater_than_4_phi_adds_length(service: LapSpliceService) -> None:
    data = _base_input(diameter_1_mm=10.0, diameter_2_mm=10.0, clear_distance_cm=5.0)

    result = service.calculate(data)

    assert result.clear_distance_limit_cm == pytest.approx(4.0)
    assert result.clear_distance_addition_cm == pytest.approx(5.0)
    assert result.required_lap_cm == pytest.approx(
        result.lap_before_addition_cm + data.clear_distance_cm
    )


def test_transverse_reinforcement_warning_for_diameter(service: LapSpliceService) -> None:
    result = service.calculate(_base_input(diameter_1_mm=16.0, diameter_2_mm=16.0))

    assert result.requires_transverse_reinforcement
    assert "phi >= 16 mm" in result.transverse_reinforcement_reasons


def test_transverse_reinforcement_warning_for_percent(service: LapSpliceService) -> None:
    result = service.calculate(_base_input(spliced_bars_percent=25.0))

    assert result.requires_transverse_reinforcement
    assert "proporcao de barras emendadas >= 25%" in result.transverse_reinforcement_reasons


def test_memory_contains_formulas_units_and_governing_criteria(
    service: LapSpliceService,
) -> None:
    data = _base_input(available_lap_cm=10.0, clear_distance_cm=5.0)
    result = service.calculate(data)
    memory = service.build_calculation_memory(data, result)

    assert "fctm" in memory
    assert "fbd = eta1 * eta2 * eta3 * fctd" in memory
    assert "lb,nec,calc = alpha1 * lb * (As,calc / As,ef)" in memory
    assert "l0t,min = max" in memory
    assert "governante" in memory
    assert "Acrescimo por distancia livre > 4 phi" in memory
    assert "Resultado = NAO ATENDE" in memory
    assert "cm" in memory
    assert "MPa" in memory
