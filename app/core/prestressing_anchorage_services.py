"""Business rules for bonded prestressing anchorage verification."""

from __future__ import annotations

import math
from datetime import datetime

from app.core.exceptions import ValidationError
from app.core.prestressing_anchorage_models import (
    PRESTRESSING_STEEL_SPECS,
    PrestressingAnchorageInput,
    PrestressingAnchorageResult,
    PrestressingBondCondition,
)

BOND_FACTOR_BY_CONDITION: dict[PrestressingBondCondition, float] = {
    PrestressingBondCondition.GOOD: 1.0,
    PrestressingBondCondition.POOR: 0.7,
}


class PrestressingAnchorageService:
    """Calculates bonded prestressing anchorage and builds detailed memory."""

    def calculate(
        self,
        data: PrestressingAnchorageInput,
    ) -> PrestressingAnchorageResult:
        self._validate(data)
        steel = PRESTRESSING_STEEL_SPECS[data.steel_key]

        fctm_mpa = self._calculate_fctm(data.fck_mpa)
        fctk_inf_mpa = 0.7 * fctm_mpa
        fctd_mpa = fctk_inf_mpa / data.gamma_c
        eta_p2 = BOND_FACTOR_BY_CONDITION[data.bond_condition]
        fbpd_mpa = steel.eta_p1 * eta_p2 * fctd_mpa

        steel_force_n = steel.area_mm2 * data.steel_stress_mpa
        steel_force_kn = steel_force_n / 1000.0
        base_anchorage_mm = steel_force_n / (
            fbpd_mpa * math.pi * steel.diameter_mm
        )
        base_anchorage_cm = base_anchorage_mm / 10.0
        required_anchorage_cm = base_anchorage_cm
        anchorage_is_ok = data.available_anchorage_cm >= required_anchorage_cm
        deficit_cm = max(0.0, required_anchorage_cm - data.available_anchorage_cm)

        return PrestressingAnchorageResult(
            fctm_mpa=fctm_mpa,
            fctk_inf_mpa=fctk_inf_mpa,
            fctd_mpa=fctd_mpa,
            eta_p1=steel.eta_p1,
            eta_p2=eta_p2,
            fbpd_mpa=fbpd_mpa,
            steel_force_kn=steel_force_kn,
            base_anchorage_cm=base_anchorage_cm,
            required_anchorage_cm=required_anchorage_cm,
            available_anchorage_cm=data.available_anchorage_cm,
            deficit_cm=deficit_cm,
            anchorage_is_ok=anchorage_is_ok,
        )

    def build_calculation_memory(
        self,
        data: PrestressingAnchorageInput,
        result: PrestressingAnchorageResult,
    ) -> str:
        """Build a didactic calculation memory for bonded prestressing."""
        steel = PRESTRESSING_STEEL_SPECS[data.steel_key]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fpyk_text = f"{steel.fpyk_mpa:.1f} MPa" if steel.fpyk_mpa else "N/A"

        lines = [
            "=" * 72,
            "MEMORIA DE CALCULO - ANCORAGEM DE PROTENSAO ADERENTE",
            "Referencias: ABNT NBR 6118:2023, ABNT NBR 7482 e ABNT NBR 7483",
            f"GERADO EM: {timestamp}",
            "=" * 72,
            "",
            "1) PREMISSAS ADOTADAS E LIMITACOES",
            "-" * 72,
            "Tipo de verificacao: protensao aderente.",
            "Uso: estimativa auxiliar do comprimento necessario para desenvolver a tensao informada.",
            "Aco: fios conforme NBR 7482 e cordoalhas conforme NBR 7483, com propriedades nominais.",
            "A memoria detalha coeficientes para facilitar revisao por engenheiro responsavel.",
            "Nao substitui verificacoes de transferencia, perdas, fissuracao, detalhamento,",
            "comprimentos de regularizacao, zonas de introducao de esforcos ou verificacao global da peca.",
            "Os valores finais devem ser conferidos no texto licenciado das normas e nos certificados do lote.",
            "",
            "2) DADOS DE ENTRADA",
            "-" * 72,
            f"Elemento = {steel.element_type.value}",
            f"Designacao = {steel.label}",
            f"Referencia do catalogo = {steel.reference}",
            f"fck = {data.fck_mpa:.2f} MPa",
            f"Condicao de aderencia = {data.bond_condition.value}",
            f"Tensao considerada no aco (sigma_p,d) = {data.steel_stress_mpa:.2f} MPa",
            f"Comprimento disponivel (Ldisp) = {data.available_anchorage_cm:.2f} cm",
            f"gamma_c = {data.gamma_c:.2f}",
            "",
            "3) PROPRIEDADES DO CONCRETO",
            "-" * 72,
            "Objetivo: obter a resistencia de calculo a tracao usada na aderencia.",
            "Formula simbolica:",
            "   fctm = 0,30 * fck^(2/3), para fck <= 50 MPa",
            "   fctk,inf = 0,70 * fctm",
            "   fctd = fctk,inf / gamma_c",
            "Substituicao numerica:",
            (
                f"   fctm = 0,30 * {data.fck_mpa:.2f}^(2/3)"
                f" = {result.fctm_mpa:.3f} MPa"
                if data.fck_mpa <= 50.0
                else f"   fctm = 2,12 * ln(1 + 0,11 * {data.fck_mpa:.2f})"
                f" = {result.fctm_mpa:.3f} MPa"
            ),
            f"   fctk,inf = 0,70 * {result.fctm_mpa:.3f} = {result.fctk_inf_mpa:.3f} MPa",
            (
                f"   fctd = {result.fctk_inf_mpa:.3f} / {data.gamma_c:.2f}"
                f" = {result.fctd_mpa:.3f} MPa"
            ),
            "",
            "4) PROPRIEDADES DO ACO DE PROTENSAO",
            "-" * 72,
            "Objetivo: identificar o perimetro aderente e a forca que precisa ser ancorada.",
            f"Tipo = {steel.element_type.value}",
            f"Designacao = {steel.label}",
            f"Diametro nominal (phi_p) = {steel.diameter_mm:.2f} mm",
            f"Area nominal (Ap) = {steel.area_mm2:.2f} mm2",
            f"fptk = {steel.fptk_mpa:.1f} MPa",
            f"fpyk = {fpyk_text}",
            f"Tensao adotada no calculo (sigma_p,d) = {data.steel_stress_mpa:.2f} MPa",
            "",
            "5) COEFICIENTES DE ADERENCIA",
            "-" * 72,
            "Objetivo: transformar fctd em tensao de aderencia de projeto.",
            "Coeficientes adotados:",
            (
                f"   eta_p1 = {result.eta_p1:.2f}: depende do elemento de protensao. "
                "Nesta ferramenta, fios usam 1,00 e cordoalhas de 7 fios usam 1,20."
            ),
            (
                f"   eta_p2 = {result.eta_p2:.2f}: depende da condicao de aderencia. "
                "Boa aderencia = 1,00; ma aderencia = 0,70."
            ),
            "Impacto: quanto menores os coeficientes, menor fbpd e maior o comprimento necessario.",
            "",
            "6) TENSAO DE ADERENCIA DE PROJETO",
            "-" * 72,
            "Formula simbolica:",
            "   fbpd = eta_p1 * eta_p2 * fctd",
            "Substituicao numerica:",
            (
                f"   fbpd = {result.eta_p1:.2f} * {result.eta_p2:.2f}"
                f" * {result.fctd_mpa:.3f} = {result.fbpd_mpa:.3f} MPa"
            ),
            "",
            "7) FORCA/TENSAO CONSIDERADA NA ARMADURA",
            "-" * 72,
            "Formula simbolica:",
            "   Fp,d = Ap * sigma_p,d",
            "Substituicao numerica:",
            (
                f"   Fp,d = {steel.area_mm2:.2f} * {data.steel_stress_mpa:.2f}"
                f" = {result.steel_force_kn:.3f} kN"
            ),
            "Unidades: MPa = N/mm2, portanto Ap(mm2) * sigma(MPa) resulta em N.",
            "",
            "8) COMPRIMENTO DE ANCORAGEM NECESSARIO",
            "-" * 72,
            "Hipotese: aderencia uniforme ao longo do perimetro nominal do elemento.",
            "Formula simbolica:",
            "   Lnec = Fp,d / (fbpd * pi * phi_p)",
            "Substituicao numerica:",
            (
                f"   Lnec = ({result.steel_force_kn:.3f} * 1000)"
                f" / ({result.fbpd_mpa:.3f} * pi * {steel.diameter_mm:.2f})"
                f" / 10 = {result.required_anchorage_cm:.2f} cm"
            ),
            f"Comprimento basico calculado = {result.base_anchorage_cm:.2f} cm",
            f"Comprimento necessario adotado = {result.required_anchorage_cm:.2f} cm",
            "",
            "9) VERIFICACAO CONTRA O COMPRIMENTO DISPONIVEL",
            "-" * 72,
            f"Ldisp = {result.available_anchorage_cm:.2f} cm",
            f"Lnec = {result.required_anchorage_cm:.2f} cm",
            (
                "Resultado: ATENDE, pois Ldisp >= Lnec."
                if result.anchorage_is_ok
                else "Resultado: NAO ATENDE, pois Ldisp < Lnec."
            ),
            (
                "Deficit = 0,00 cm"
                if result.anchorage_is_ok
                else f"Deficit = Lnec - Ldisp = {result.deficit_cm:.2f} cm"
            ),
            "",
            "10) OBSERVACOES DE ENGENHARIA",
            "-" * 72,
            "A tensao informada deve ser compativel com a etapa de verificacao desejada.",
            "Verificar se o produto selecionado, diametro, area e resistencia correspondem ao certificado do lote.",
            "Verificar condicoes reais de aderencia, cobrimento, espacamento, confinamento e detalhamento.",
            "Para pre-tracao, conferir tambem transferencia, comprimento de regularizacao e perdas.",
            "",
            "-" * 72,
            f"RESULTADO FINAL: {'APROVADO' if result.anchorage_is_ok else 'REPROVADO'}",
            "-" * 72,
        ]
        return "\n".join(lines)

    @staticmethod
    def _calculate_fctm(fck_mpa: float) -> float:
        if fck_mpa <= 50.0:
            return 0.3 * (fck_mpa ** (2.0 / 3.0))
        return 2.12 * math.log1p(0.11 * fck_mpa)

    @staticmethod
    def _validate(data: PrestressingAnchorageInput) -> None:
        if data.steel_key not in PRESTRESSING_STEEL_SPECS:
            raise ValidationError("Produto de protensao invalido.")
        if not math.isfinite(data.fck_mpa) or data.fck_mpa <= 0:
            raise ValidationError("Fck deve ser maior que zero.")
        if not math.isfinite(data.steel_stress_mpa) or data.steel_stress_mpa <= 0:
            raise ValidationError("Tensao no aco deve ser maior que zero.")
        if not math.isfinite(data.available_anchorage_cm) or data.available_anchorage_cm <= 0:
            raise ValidationError("Comprimento disponivel deve ser maior que zero.")
        if not isinstance(data.bond_condition, PrestressingBondCondition):
            raise ValidationError("Condicao de aderencia invalida.")
        if not math.isfinite(data.gamma_c) or data.gamma_c <= 0:
            raise ValidationError("Gamma c deve ser maior que zero.")
