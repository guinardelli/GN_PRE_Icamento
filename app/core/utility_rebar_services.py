"""Business rules for utility conversion of rebar diameter/spacing."""

from __future__ import annotations

import math

from app.core.exceptions import ValidationError
from app.core.utility_rebar_models import (
    RebarConversionInput,
    RebarConversionOption,
    RebarConversionResult,
)

_FYK_CA50_MPA = 500.0
_FYK_CA60_MPA = 600.0

REBAR_CONVERSION_OPTIONS: tuple[RebarConversionOption, ...] = (
    RebarConversionOption("CA-60 - 4.2 mm", 4.2, _FYK_CA60_MPA),
    RebarConversionOption("CA-60 - 5.0 mm", 5.0, _FYK_CA60_MPA),
    RebarConversionOption("CA-60 - 6.0 mm", 6.0, _FYK_CA60_MPA),
    RebarConversionOption("CA-50 - 6.3 mm", 6.3, _FYK_CA50_MPA),
    RebarConversionOption("CA-60 - 7.0 mm", 7.0, _FYK_CA60_MPA),
    RebarConversionOption("CA-50 - 8.0 mm", 8.0, _FYK_CA50_MPA),
    RebarConversionOption("CA-60 - 8.0 mm", 8.0, _FYK_CA60_MPA),
    RebarConversionOption("CA-60 - 9.5 mm", 9.5, _FYK_CA60_MPA),
    RebarConversionOption("CA-50 - 10.0 mm", 10.0, _FYK_CA50_MPA),
    RebarConversionOption("CA-50 - 12.5 mm", 12.5, _FYK_CA50_MPA),
    RebarConversionOption("CA-50 - 16.0 mm", 16.0, _FYK_CA50_MPA),
    RebarConversionOption("CA-50 - 20.0 mm", 20.0, _FYK_CA50_MPA),
    RebarConversionOption("CA-50 - 25.0 mm", 25.0, _FYK_CA50_MPA),
    RebarConversionOption("CA-50 - 32.0 mm", 32.0, _FYK_CA50_MPA),
    RebarConversionOption("CA-50 - 40.0 mm", 40.0, _FYK_CA50_MPA),
)


class RebarConversionService:
    """Converts spacing between original and equivalent reinforcement bars."""

    def convert(self, data: RebarConversionInput) -> RebarConversionResult:
        self._validate(data)

        area_original_mm2 = math.pi * (data.original_diameter_mm**2) / 4.0
        area_equivalent_mm2 = math.pi * (data.equivalent_diameter_mm**2) / 4.0

        equivalent_spacing_cm = (
            data.original_spacing_cm
            * (area_equivalent_mm2 * data.equivalent_fyk_mpa)
            / (area_original_mm2 * data.original_fyk_mpa)
        )

        return RebarConversionResult(equivalent_spacing_cm=equivalent_spacing_cm)

    @staticmethod
    def _validate(data: RebarConversionInput) -> None:
        if data.original_diameter_mm <= 0:
            raise ValidationError("Bitola original deve ser maior que zero.")
        if data.equivalent_diameter_mm <= 0:
            raise ValidationError("Bitola equivalente deve ser maior que zero.")
        if data.original_spacing_cm <= 0:
            raise ValidationError("Espacamento original deve ser maior que zero.")
        if data.original_fyk_mpa <= 0:
            raise ValidationError("Resistencia da armadura original deve ser maior que zero.")
        if data.equivalent_fyk_mpa <= 0:
            raise ValidationError("Resistencia da armadura equivalente deve ser maior que zero.")
