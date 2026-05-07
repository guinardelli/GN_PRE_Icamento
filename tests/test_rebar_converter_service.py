"""Tests for RebarConversionService."""

import pytest

from app.core.exceptions import ValidationError
from app.core.utility_rebar_models import RebarConversionInput
from app.core.utility_rebar_services import (
    REBAR_CONVERSION_OPTIONS,
    RebarConversionService,
)


@pytest.fixture
def service() -> RebarConversionService:
    return RebarConversionService()


def _option(label: str):
    for item in REBAR_CONVERSION_OPTIONS:
        if item.label == label:
            return item
    raise AssertionError(f"Opcao nao encontrada: {label}")


def test_same_steel_conversion(service: RebarConversionService) -> None:
    original = _option("CA-50 - 8.0 mm")
    equivalent = _option("CA-50 - 16.0 mm")
    data = RebarConversionInput(
        original_diameter_mm=original.diameter_mm,
        original_spacing_cm=10.0,
        original_fyk_mpa=original.fyk_mpa,
        equivalent_diameter_mm=equivalent.diameter_mm,
        equivalent_fyk_mpa=equivalent.fyk_mpa,
    )

    result = service.convert(data)
    assert result.equivalent_spacing_cm == pytest.approx(40.0, 0.001)


def test_ca60_equivalent_option_increases_spacing(service: RebarConversionService) -> None:
    original = _option("CA-50 - 8.0 mm")
    equivalent = _option("CA-60 - 8.0 mm")
    data = RebarConversionInput(
        original_diameter_mm=original.diameter_mm,
        original_spacing_cm=10.0,
        original_fyk_mpa=original.fyk_mpa,
        equivalent_diameter_mm=equivalent.diameter_mm,
        equivalent_fyk_mpa=equivalent.fyk_mpa,
    )

    result = service.convert(data)
    assert result.equivalent_spacing_cm == pytest.approx(12.0, 0.001)


def test_ca60_original_option_reduces_spacing(service: RebarConversionService) -> None:
    original = _option("CA-60 - 8.0 mm")
    equivalent = _option("CA-50 - 8.0 mm")
    data = RebarConversionInput(
        original_diameter_mm=original.diameter_mm,
        original_spacing_cm=10.0,
        original_fyk_mpa=original.fyk_mpa,
        equivalent_diameter_mm=equivalent.diameter_mm,
        equivalent_fyk_mpa=equivalent.fyk_mpa,
    )

    result = service.convert(data)
    assert result.equivalent_spacing_cm == pytest.approx(8.333, 0.001)


def test_catalog_defines_steel_grade_in_each_option() -> None:
    labels = [option.label for option in REBAR_CONVERSION_OPTIONS]

    assert "CA-50 - 8.0 mm" in labels
    assert "CA-60 - 8.0 mm" in labels
    assert all(label.startswith(("CA-50", "CA-60")) for label in labels)


@pytest.mark.parametrize(
    ("original_diameter_mm", "original_spacing_cm", "original_fyk_mpa", "equivalent_diameter_mm", "equivalent_fyk_mpa"),
    (
        (0.0, 10.0, 500.0, 16.0, 500.0),
        (8.0, 0.0, 500.0, 16.0, 500.0),
        (8.0, 10.0, 0.0, 16.0, 500.0),
        (8.0, 10.0, 500.0, 0.0, 500.0),
        (8.0, 10.0, 500.0, 16.0, 0.0),
    ),
)
def test_invalid_inputs_raise_validation_error(
    service: RebarConversionService,
    original_diameter_mm: float,
    original_spacing_cm: float,
    original_fyk_mpa: float,
    equivalent_diameter_mm: float,
    equivalent_fyk_mpa: float,
) -> None:
    data = RebarConversionInput(
        original_diameter_mm=original_diameter_mm,
        original_spacing_cm=original_spacing_cm,
        original_fyk_mpa=original_fyk_mpa,
        equivalent_diameter_mm=equivalent_diameter_mm,
        equivalent_fyk_mpa=equivalent_fyk_mpa,
    )

    with pytest.raises(ValidationError):
        service.convert(data)
