"""Domain models for utility conversion of rebar diameter/spacing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RebarConversionOption:
    """Available rebar option with normative steel grade."""

    label: str
    diameter_mm: float
    fyk_mpa: float


@dataclass(frozen=True)
class RebarConversionInput:
    """Input values for equivalent spacing conversion."""

    original_diameter_mm: float
    original_spacing_cm: float
    original_fyk_mpa: float
    equivalent_diameter_mm: float
    equivalent_fyk_mpa: float


@dataclass(frozen=True)
class RebarConversionResult:
    """Calculated equivalent spacing."""

    equivalent_spacing_cm: float
