"""Domain models for lap splice verification of passive rebars."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.anchorage_models import (
    AnchorageType,
    BondCondition,
    EffortType,
    SteelType,
)


@dataclass(frozen=True)
class Alpha0tBracket:
    """Normative alpha0t bracket for tension lap splices."""

    label: str
    max_percent: float | None
    value: float


ALPHA0T_BRACKETS: tuple[Alpha0tBracket, ...] = (
    Alpha0tBracket("<= 20%", 20.0, 1.2),
    Alpha0tBracket("<= 25%", 25.0, 1.4),
    Alpha0tBracket("<= 33%", 33.0, 1.6),
    Alpha0tBracket("<= 50%", 50.0, 1.8),
    Alpha0tBracket("> 50%", None, 2.0),
)


@dataclass(frozen=True)
class LapSpliceInput:
    """Inputs required for lap splice verification."""

    diameter_1_mm: float
    diameter_2_mm: float
    fck_mpa: float
    steel_type: SteelType
    bond_condition: BondCondition
    effort_type: EffortType
    anchorage_type: AnchorageType
    as_calc_cm2: float
    as_ef_cm2: float
    spliced_bars_percent: float
    clear_distance_cm: float
    available_lap_cm: float
    gamma_c: float = 1.4
    gamma_s: float = 1.15


@dataclass(frozen=True)
class LapSpliceResult:
    """Calculated values for lap splice verification."""

    reference_diameter_mm: float
    used_larger_diameter: bool
    fctm_mpa: float
    fctk_inf_mpa: float
    fctd_mpa: float
    fyd_mpa: float
    eta1: float
    eta2: float
    eta3: float
    fbd_mpa: float
    lb_cm: float
    alpha1: float
    lb_min_cm: float
    lb_nec_calculated_cm: float
    lb_nec_cm: float
    alpha0t: float | None
    alpha0t_label: str | None
    lap_calculated_cm: float
    lap_min_cm: float
    lap_min_governing_term: str
    lap_before_addition_cm: float
    clear_distance_limit_cm: float
    clear_distance_addition_cm: float
    required_lap_cm: float
    lap_is_ok: bool
    deficit_cm: float
    requires_transverse_reinforcement: bool
    transverse_reinforcement_reasons: tuple[str, ...]
    spacing_reference_cm: float
    spacing_warning: bool
