"""Domain models used by lifting verification."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BondCondition(str, Enum):
    """Bond condition between strand and concrete."""

    GOOD = "boa"
    POOR = "ma"


class AnchorageType(str, Enum):
    """Type of anchorage at the embedded end of the strand loop.

    Alpha coefficients per NBR 6118:2014, item 9.4.2.4:
    - STRAIGHT : alpha = 1.00  (ancoragem reta, sem dobra)
    - HOOK_90  : alpha = 0.70  (dobra a 90°)
    - HOOK_180 : alpha = 0.50  (gancho a 180°)
    """

    STRAIGHT = "reta"
    HOOK_90 = "dobra_90"
    HOOK_180 = "gancho_180"


ALPHA_ANCHORAGE: dict[str, float] = {
    AnchorageType.STRAIGHT: 1.00,
    AnchorageType.HOOK_90: 0.70,
    AnchorageType.HOOK_180: 0.50,
}

ANCHORAGE_TYPE_LABELS: dict[str, str] = {
    AnchorageType.STRAIGHT: "Reta (sem dobra)   — α = 1,00",
    AnchorageType.HOOK_90: "Dobra 90°           — α = 0,70",
    AnchorageType.HOOK_180: "Gancho 180°        — α = 0,50",
}


@dataclass(frozen=True)
class StrandSpec:
    """Strand catalog data (NBR 7483)."""

    label: str
    diameter_mm: float
    area_mm2: float
    unit_mass_kg_per_m: float
    fptk_mpa: float
    fpyk_mpa: float


STRAND_SPECS: dict[str, StrandSpec] = {
    "CP 190-RB 9,5 mm": StrandSpec(
        label="CP 190-RB 9,5 mm",
        diameter_mm=9.5,
        area_mm2=54.9,
        unit_mass_kg_per_m=0.432,
        fptk_mpa=1900.0,
        fpyk_mpa=1710.0,
    ),
    "CP 190-RB 12,7 mm": StrandSpec(
        label="CP 190-RB 12,7 mm",
        diameter_mm=12.7,
        area_mm2=98.6,
        unit_mass_kg_per_m=0.775,
        fptk_mpa=1900.0,
        fpyk_mpa=1710.0,
    ),
    "CP 190-RB 15,2 mm": StrandSpec(
        label="CP 190-RB 15,2 mm",
        diameter_mm=15.2,
        area_mm2=139.9,
        unit_mass_kg_per_m=1.102,
        fptk_mpa=1900.0,
        fpyk_mpa=1710.0,
    ),
}


@dataclass(frozen=True)
class LiftingInput:
    """Inputs required for lifting verification."""

    fckj_mpa: float
    fck_28_mpa: float             # fck aos 28 dias (para ancoragem)
    volume_m3: float
    concrete_unit_weight_tf_m3: float
    strand_key: str
    inclination_deg: float
    available_anchorage_cm: float
    bond_condition: BondCondition
    anchorage_type: AnchorageType
    loops_count: int
    beta_a: float = 3.0
    gamma_n: float = 1.3


@dataclass(frozen=True)
class LiftingResult:
    """Result values shown to the user."""

    piece_weight_tf: float
    majorated_weight_tf: float
    beta_a: float
    gamma_n: float
    ecj_mpa: float
    fctm_j_mpa: float             # fctm na idade j (içamento)
    fctm_28_mpa: float            # fctm aos 28 dias
    fptk_mpa: float
    fpyk_mpa: float
    fpyd_mpa: float
    fbpd_j_mpa: float             # fbpd na idade j (capacidade)
    fbpd_28_mpa: float            # fbpd aos 28 dias (ancoragem)
    strand_area_cm2: float
    strand_unit_mass_kg_m: float
    base_anchorage_cm: float      # Lnec,base usando fbpd_28
    required_anchorage_cm: float
    alpha_anchorage: float
    max_supported_load_tf: float
    max_supported_load_by_steel_tf: float
    max_supported_load_by_bond_tf: float
    anchorage_is_ok: bool
    capacity_is_ok: bool
    utilization_ratio: float
    safety_factor: float
    tension_per_loop_tf: float
    tension_per_leg_tf: float
    total_legs: int
    stress_developed_mpa: float
    stress_mobilization_ratio: float
