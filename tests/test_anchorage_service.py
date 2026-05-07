"""Tests for AnchorageVerifierService."""

import pytest

from app.core.anchorage_models import (
    AnchorageInput,
    AnchorageType,
    BondCondition,
    COMMERCIAL_REBAR_DIAMETERS,
    EffortType,
    SteelType,
)
from app.core.anchorage_services import AnchorageVerifierService
from app.core.exceptions import ValidationError


@pytest.fixture
def service() -> AnchorageVerifierService:
    return AnchorageVerifierService()


def test_base_case_tension(service: AnchorageVerifierService) -> None:
    data = AnchorageInput(
        diameter_mm=10.0,
        fck_mpa=30.0,
        steel_type=SteelType.CA50,
        bond_condition=BondCondition.GOOD,
        effort_type=EffortType.TENSION,
        anchorage_type=AnchorageType.STRAIGHT,
        as_calc_cm2=1.0,
        as_ef_cm2=1.0,
        available_anchorage_cm=50.0,
    )
    result = service.calculate(data)
    assert result.fctm_mpa == pytest.approx(2.896, 0.01)
    assert result.fyd_mpa == pytest.approx(434.78, 0.01)
    assert result.lb_cm > 10.0
    assert result.alpha == 1.0


def test_commercial_diameter_catalog() -> None:
    assert [diameter.diameter_mm for diameter in COMMERCIAL_REBAR_DIAMETERS] == [
        5.0,
        6.3,
        8.0,
        10.0,
        12.5,
        16.0,
        20.0,
        25.0,
        32.0,
        40.0,
    ]


@pytest.mark.parametrize("diameter", COMMERCIAL_REBAR_DIAMETERS)
def test_all_commercial_diameters_calculate(
    service: AnchorageVerifierService,
    diameter,
) -> None:
    data = AnchorageInput(
        diameter_mm=diameter.diameter_mm,
        fck_mpa=30.0,
        steel_type=SteelType.CA50,
        bond_condition=BondCondition.GOOD,
        effort_type=EffortType.TENSION,
        anchorage_type=AnchorageType.STRAIGHT,
        as_calc_cm2=1.0,
        as_ef_cm2=1.0,
        available_anchorage_cm=500.0,
    )

    result = service.calculate(data)

    assert result.lb_cm > 0.0


@pytest.mark.parametrize(
    ("steel_type", "expected_fyd", "expected_eta1"),
    (
        (SteelType.CA25, 250.0 / 1.15, 1.0),
        (SteelType.CA50, 500.0 / 1.15, 2.25),
        (SteelType.CA60, 600.0 / 1.15, 1.4),
    ),
)
def test_steel_types(
    service: AnchorageVerifierService,
    steel_type: SteelType,
    expected_fyd: float,
    expected_eta1: float,
) -> None:
    data = AnchorageInput(
        diameter_mm=10.0,
        fck_mpa=30.0,
        steel_type=steel_type,
        bond_condition=BondCondition.GOOD,
        effort_type=EffortType.TENSION,
        anchorage_type=AnchorageType.STRAIGHT,
        as_calc_cm2=1.0,
        as_ef_cm2=1.0,
        available_anchorage_cm=100.0,
    )

    result = service.calculate(data)

    assert result.fyd_mpa == pytest.approx(expected_fyd)
    assert result.eta1 == pytest.approx(expected_eta1)


@pytest.mark.parametrize(
    ("anchorage_type", "expected_alpha"),
    (
        (AnchorageType.STRAIGHT, 1.0),
        (AnchorageType.HOOK, 0.7),
        (AnchorageType.WELDED, 0.7),
        (AnchorageType.HOOK_WELDED, 0.5),
    ),
)
def test_anchorage_types_in_tension(
    service: AnchorageVerifierService,
    anchorage_type: AnchorageType,
    expected_alpha: float,
) -> None:
    data = AnchorageInput(
        diameter_mm=10.0,
        fck_mpa=30.0,
        steel_type=SteelType.CA50,
        bond_condition=BondCondition.GOOD,
        effort_type=EffortType.TENSION,
        anchorage_type=anchorage_type,
        as_calc_cm2=1.0,
        as_ef_cm2=1.0,
        available_anchorage_cm=100.0,
    )

    result = service.calculate(data)

    assert result.alpha == pytest.approx(expected_alpha)


def test_base_case_compression(service: AnchorageVerifierService) -> None:
    data = AnchorageInput(
        diameter_mm=10.0,
        fck_mpa=30.0,
        steel_type=SteelType.CA50,
        bond_condition=BondCondition.GOOD,
        effort_type=EffortType.COMPRESSION,
        anchorage_type=AnchorageType.STRAIGHT,
        as_calc_cm2=1.0,
        as_ef_cm2=1.0,
        available_anchorage_cm=50.0,
    )
    result = service.calculate(data)
    assert result.alpha == 1.0
    # lb,min para compressao eh maior
    assert result.lb_min_cm >= 10.0


def test_good_vs_poor_bond(service: AnchorageVerifierService) -> None:
    data_good = AnchorageInput(
        diameter_mm=10.0,
        fck_mpa=30.0,
        steel_type=SteelType.CA50,
        bond_condition=BondCondition.GOOD,
        effort_type=EffortType.TENSION,
        anchorage_type=AnchorageType.STRAIGHT,
        as_calc_cm2=1.0,
        as_ef_cm2=1.0,
        available_anchorage_cm=50.0,
    )
    data_poor = AnchorageInput(
        diameter_mm=10.0,
        fck_mpa=30.0,
        steel_type=SteelType.CA50,
        bond_condition=BondCondition.POOR,
        effort_type=EffortType.TENSION,
        anchorage_type=AnchorageType.STRAIGHT,
        as_calc_cm2=1.0,
        as_ef_cm2=1.0,
        available_anchorage_cm=50.0,
    )
    result_good = service.calculate(data_good)
    result_poor = service.calculate(data_poor)
    assert result_poor.fbd_mpa < result_good.fbd_mpa
    assert result_poor.lb_cm > result_good.lb_cm


def test_as_calc_reduction(service: AnchorageVerifierService) -> None:
    data_no_red = AnchorageInput(
        diameter_mm=10.0,
        fck_mpa=30.0,
        steel_type=SteelType.CA50,
        bond_condition=BondCondition.GOOD,
        effort_type=EffortType.TENSION,
        anchorage_type=AnchorageType.STRAIGHT,
        as_calc_cm2=1.0,
        as_ef_cm2=1.0,
        available_anchorage_cm=50.0,
    )
    data_red = AnchorageInput(
        diameter_mm=10.0,
        fck_mpa=30.0,
        steel_type=SteelType.CA50,
        bond_condition=BondCondition.GOOD,
        effort_type=EffortType.TENSION,
        anchorage_type=AnchorageType.STRAIGHT,
        as_calc_cm2=1.0,
        as_ef_cm2=2.0,
        available_anchorage_cm=50.0,
    )
    r1 = service.calculate(data_no_red)
    r2 = service.calculate(data_red)
    assert r2.lb_nec_cm < r1.lb_nec_cm
    assert r2.lb_nec_cm >= r2.lb_min_cm


def test_required_as_ef_when_available_length_is_insufficient(
    service: AnchorageVerifierService,
) -> None:
    data = AnchorageInput(
        diameter_mm=10.0,
        fck_mpa=30.0,
        steel_type=SteelType.CA50,
        bond_condition=BondCondition.GOOD,
        effort_type=EffortType.TENSION,
        anchorage_type=AnchorageType.STRAIGHT,
        as_calc_cm2=1.0,
        as_ef_cm2=1.0,
        available_anchorage_cm=20.0,
    )

    result = service.calculate(data)
    memory = service.build_calculation_memory(data, result)

    assert not result.anchorage_is_ok
    assert result.required_as_ef_cm2 == pytest.approx(
        result.alpha * result.lb_cm * data.as_calc_cm2 / data.available_anchorage_cm
    )
    assert result.required_as_ef_cm2 > data.as_ef_cm2
    assert "As,ef necessaria" in memory


def test_required_as_ef_is_not_applicable_below_minimum_length(
    service: AnchorageVerifierService,
) -> None:
    data = AnchorageInput(
        diameter_mm=10.0,
        fck_mpa=30.0,
        steel_type=SteelType.CA50,
        bond_condition=BondCondition.GOOD,
        effort_type=EffortType.TENSION,
        anchorage_type=AnchorageType.STRAIGHT,
        as_calc_cm2=1.0,
        as_ef_cm2=1.0,
        available_anchorage_cm=5.0,
    )

    result = service.calculate(data)
    memory = service.build_calculation_memory(data, result)

    assert not result.anchorage_is_ok
    assert data.available_anchorage_cm < result.lb_min_cm
    assert result.required_as_ef_cm2 is None
    assert "Nao e possivel atender apenas aumentando As,ef" in memory


def test_hook_blocked_in_compression(service: AnchorageVerifierService) -> None:
    for anchorage_type in (AnchorageType.HOOK, AnchorageType.HOOK_WELDED):
        data = AnchorageInput(
            diameter_mm=10.0,
            fck_mpa=30.0,
            steel_type=SteelType.CA50,
            bond_condition=BondCondition.GOOD,
            effort_type=EffortType.COMPRESSION,
            anchorage_type=anchorage_type,
            as_calc_cm2=1.0,
            as_ef_cm2=1.0,
            available_anchorage_cm=50.0,
        )
        with pytest.raises(ValidationError, match="Ganchos nao devem ser considerados para barras comprimidas."):
            service.calculate(data)


def test_welded_allowed_in_compression(service: AnchorageVerifierService) -> None:
    data = AnchorageInput(
        diameter_mm=10.0,
        fck_mpa=30.0,
        steel_type=SteelType.CA50,
        bond_condition=BondCondition.GOOD,
        effort_type=EffortType.COMPRESSION,
        anchorage_type=AnchorageType.WELDED,
        as_calc_cm2=1.0,
        as_ef_cm2=1.0,
        available_anchorage_cm=50.0,
    )

    result = service.calculate(data)

    assert result.alpha == pytest.approx(0.7)


def test_invalid_inputs(service: AnchorageVerifierService) -> None:
    data = AnchorageInput(
        diameter_mm=-10.0,
        fck_mpa=30.0,
        steel_type=SteelType.CA50,
        bond_condition=BondCondition.GOOD,
        effort_type=EffortType.TENSION,
        anchorage_type=AnchorageType.STRAIGHT,
        as_calc_cm2=1.0,
        as_ef_cm2=1.0,
        available_anchorage_cm=50.0,
    )
    with pytest.raises(ValidationError, match="Bitola deve ser maior que zero."):
        service.calculate(data)

    data_as = AnchorageInput(
        diameter_mm=10.0,
        fck_mpa=30.0,
        steel_type=SteelType.CA50,
        bond_condition=BondCondition.GOOD,
        effort_type=EffortType.TENSION,
        anchorage_type=AnchorageType.STRAIGHT,
        as_calc_cm2=2.0,
        as_ef_cm2=1.0,
        available_anchorage_cm=50.0,
    )
    with pytest.raises(ValidationError, match="As,calc nao deve ser maior que As,ef."):
        service.calculate(data_as)
