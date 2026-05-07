"""Domain models for bonded prestressing anchorage verification."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PrestressingElementType(str, Enum):
    """Type of prestressing steel element."""

    WIRE = "Fio"
    STRAND = "Cordoalha"


class PrestressingBondCondition(str, Enum):
    """Bond condition between prestressing steel and concrete."""

    GOOD = "Boa"
    POOR = "Ma"


@dataclass(frozen=True)
class PrestressingSteelSpec:
    """Catalog data for bonded prestressing steel."""

    key: str
    label: str
    element_type: PrestressingElementType
    diameter_mm: float
    area_mm2: float
    fptk_mpa: float
    fpyk_mpa: float | None
    eta_p1: float
    reference: str


PRESTRESSING_STEEL_SPECS: dict[str, PrestressingSteelSpec] = {
    "WIRE_CP175_RN_5_0": PrestressingSteelSpec(
        key="WIRE_CP175_RN_5_0",
        label="Fio CP 175-RN 5,0 mm",
        element_type=PrestressingElementType.WIRE,
        diameter_mm=5.0,
        area_mm2=19.6,
        fptk_mpa=1750.0,
        fpyk_mpa=None,
        eta_p1=1.0,
        reference="ABNT NBR 7482 (conferir propriedades do fabricante/lote)",
    ),
    "WIRE_CP175_RN_7_0": PrestressingSteelSpec(
        key="WIRE_CP175_RN_7_0",
        label="Fio CP 175-RN 7,0 mm",
        element_type=PrestressingElementType.WIRE,
        diameter_mm=7.0,
        area_mm2=38.5,
        fptk_mpa=1750.0,
        fpyk_mpa=None,
        eta_p1=1.0,
        reference="ABNT NBR 7482 (conferir propriedades do fabricante/lote)",
    ),
    "STRAND_CP190_RB_9_5": PrestressingSteelSpec(
        key="STRAND_CP190_RB_9_5",
        label="Cordoalha CP 190-RB 9,5 mm",
        element_type=PrestressingElementType.STRAND,
        diameter_mm=9.5,
        area_mm2=56.2,
        fptk_mpa=1900.0,
        fpyk_mpa=1710.0,
        eta_p1=1.2,
        reference="ABNT NBR 7483:2021 / catalogo nominal",
    ),
    "STRAND_CP190_RB_12_7": PrestressingSteelSpec(
        key="STRAND_CP190_RB_12_7",
        label="Cordoalha CP 190-RB 12,7 mm",
        element_type=PrestressingElementType.STRAND,
        diameter_mm=12.7,
        area_mm2=100.9,
        fptk_mpa=1900.0,
        fpyk_mpa=1710.0,
        eta_p1=1.2,
        reference="ABNT NBR 7483:2021 / catalogo nominal",
    ),
    "STRAND_CP190_RB_15_2": PrestressingSteelSpec(
        key="STRAND_CP190_RB_15_2",
        label="Cordoalha CP 190-RB 15,2 mm",
        element_type=PrestressingElementType.STRAND,
        diameter_mm=15.2,
        area_mm2=143.4,
        fptk_mpa=1900.0,
        fpyk_mpa=1710.0,
        eta_p1=1.2,
        reference="ABNT NBR 7483:2021 / catalogo nominal",
    ),
}


@dataclass(frozen=True)
class PrestressingAnchorageInput:
    """Inputs required for bonded prestressing anchorage verification."""

    steel_key: str
    fck_mpa: float
    steel_stress_mpa: float
    available_anchorage_cm: float
    bond_condition: PrestressingBondCondition
    gamma_c: float = 1.4


@dataclass(frozen=True)
class PrestressingAnchorageResult:
    """Result values for bonded prestressing anchorage."""

    fctm_mpa: float
    fctk_inf_mpa: float
    fctd_mpa: float
    eta_p1: float
    eta_p2: float
    fbpd_mpa: float
    steel_force_kn: float
    base_anchorage_cm: float
    required_anchorage_cm: float
    available_anchorage_cm: float
    deficit_cm: float
    anchorage_is_ok: bool
