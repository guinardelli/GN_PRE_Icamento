"""Tests for PrestressingAnchorageService."""

import pytest

from app.core.exceptions import ValidationError
from app.core.prestressing_anchorage_models import (
    PrestressingAnchorageInput,
    PrestressingBondCondition,
)
from app.core.prestressing_anchorage_services import PrestressingAnchorageService


@pytest.fixture
def service() -> PrestressingAnchorageService:
    return PrestressingAnchorageService()


def test_strand_case_generates_detailed_memory(
    service: PrestressingAnchorageService,
) -> None:
    data = PrestressingAnchorageInput(
        steel_key="STRAND_CP190_RB_12_7",
        fck_mpa=30.0,
        steel_stress_mpa=1000.0,
        available_anchorage_cm=160.0,
        bond_condition=PrestressingBondCondition.GOOD,
    )

    result = service.calculate(data)
    memory = service.build_calculation_memory(data, result)

    assert result.anchorage_is_ok
    for section in (
        "1) PREMISSAS ADOTADAS E LIMITACOES",
        "2) DADOS DE ENTRADA",
        "3) PROPRIEDADES DO CONCRETO",
        "4) PROPRIEDADES DO ACO DE PROTENSAO",
        "5) COEFICIENTES DE ADERENCIA",
        "6) TENSAO DE ADERENCIA DE PROJETO",
        "7) FORCA/TENSAO CONSIDERADA NA ARMADURA",
        "8) COMPRIMENTO DE ANCORAGEM NECESSARIO",
        "9) VERIFICACAO CONTRA O COMPRIMENTO DISPONIVEL",
        "10) OBSERVACOES DE ENGENHARIA",
    ):
        assert section in memory
    assert "fbpd = eta_p1 * eta_p2 * fctd" in memory
    assert "Lnec = Fp,d / (fbpd * pi * phi_p)" in memory
    assert "Resultado: ATENDE" in memory


def test_wire_case_generates_memory_with_wire_data(
    service: PrestressingAnchorageService,
) -> None:
    data = PrestressingAnchorageInput(
        steel_key="WIRE_CP175_RN_5_0",
        fck_mpa=30.0,
        steel_stress_mpa=900.0,
        available_anchorage_cm=80.0,
        bond_condition=PrestressingBondCondition.GOOD,
    )

    result = service.calculate(data)
    memory = service.build_calculation_memory(data, result)

    assert result.required_anchorage_cm > 0.0
    assert "Elemento = Fio" in memory
    assert "Fio CP 175-RN 5,0 mm" in memory
    assert "fpyk = N/A" in memory


def test_failed_case_reports_deficit(service: PrestressingAnchorageService) -> None:
    data = PrestressingAnchorageInput(
        steel_key="STRAND_CP190_RB_15_2",
        fck_mpa=25.0,
        steel_stress_mpa=1200.0,
        available_anchorage_cm=10.0,
        bond_condition=PrestressingBondCondition.POOR,
    )

    result = service.calculate(data)
    memory = service.build_calculation_memory(data, result)

    assert not result.anchorage_is_ok
    assert result.deficit_cm > 0.0
    assert "Resultado: NAO ATENDE" in memory
    assert "Deficit = Lnec - Ldisp" in memory


def test_invalid_product_raises_validation_error(
    service: PrestressingAnchorageService,
) -> None:
    data = PrestressingAnchorageInput(
        steel_key="INVALID",
        fck_mpa=30.0,
        steel_stress_mpa=900.0,
        available_anchorage_cm=80.0,
        bond_condition=PrestressingBondCondition.GOOD,
    )

    with pytest.raises(ValidationError, match="Produto de protensao invalido."):
        service.calculate(data)
