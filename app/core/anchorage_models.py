"""Domain models for anchorage length verification (barras passivas)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class RebarDiameter:
    """Commercial rebar diameter used by the anchorage calculator."""

    label: str
    diameter_mm: float


class SteelType(str, Enum):
    """Tipos de aco comuns."""

    CA25 = "CA-25 (Lisa)"
    CA50 = "CA-50 (Nervurada)"
    CA60 = "CA-60 (Entalhada)"


class BondCondition(str, Enum):
    """Condicao de aderencia."""

    GOOD = "Boa"
    POOR = "Ma"


class EffortType(str, Enum):
    """Tipo de solicitacao na barra."""

    TENSION = "Tracao"
    COMPRESSION = "Compressao"


class AnchorageType(str, Enum):
    """Tipo de ancoragem."""

    STRAIGHT = "Reta"
    HOOK = "Com Gancho"
    WELDED = "Soldada"
    HOOK_WELDED = "Com Gancho e Soldada"


COMMERCIAL_REBAR_DIAMETERS: tuple[RebarDiameter, ...] = (
    RebarDiameter("Ø5,0 mm", 5.0),
    RebarDiameter("Ø6,3 mm", 6.3),
    RebarDiameter("Ø8,0 mm", 8.0),
    RebarDiameter("Ø10,0 mm", 10.0),
    RebarDiameter("Ø12,5 mm", 12.5),
    RebarDiameter("Ø16,0 mm", 16.0),
    RebarDiameter("Ø20,0 mm", 20.0),
    RebarDiameter("Ø25,0 mm", 25.0),
    RebarDiameter("Ø32,0 mm", 32.0),
    RebarDiameter("Ø40,0 mm", 40.0),
)


@dataclass(frozen=True)
class AnchorageInput:
    """Inputs required for anchorage verification."""

    diameter_mm: float
    fck_mpa: float
    steel_type: SteelType
    bond_condition: BondCondition
    effort_type: EffortType
    anchorage_type: AnchorageType
    as_calc_cm2: float
    as_ef_cm2: float
    available_anchorage_cm: float
    gamma_c: float = 1.4
    gamma_s: float = 1.15


@dataclass(frozen=True)
class AnchorageResult:
    """Result values shown to the user."""

    fctm_mpa: float
    fctk_inf_mpa: float
    fctd_mpa: float
    fyd_mpa: float
    eta1: float
    eta2: float
    eta3: float
    fbd_mpa: float
    lb_cm: float
    alpha: float
    lb_min_cm: float
    lb_nec_cm: float
    required_as_ef_cm2: float | None
    anchorage_is_ok: bool
