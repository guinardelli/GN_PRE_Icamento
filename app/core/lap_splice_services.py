"""Business rules for lap splice verification according to NBR 6118."""

from __future__ import annotations

import math
from datetime import datetime

from app.core.anchorage_models import AnchorageInput, AnchorageType, EffortType
from app.core.anchorage_services import (
    ANCHORAGE_ALPHA_NOTE,
    HOOK_ANCHORAGE_TYPES,
    STEEL_PROPERTIES,
    AnchorageVerifierService,
)
from app.core.exceptions import ValidationError
from app.core.lap_splice_models import (
    ALPHA0T_BRACKETS,
    LapSpliceInput,
    LapSpliceResult,
)

MAX_LAP_SPLICE_DIAMETER_MM = 32.0
CM_PER_MM = 0.1
MIN_LAP_LENGTH_CM = 20.0


class LapSpliceService:
    """Calculates lap splice lengths for isolated passive rebars."""

    def __init__(self) -> None:
        self._anchorage_service = AnchorageVerifierService()

    def calculate(self, data: LapSpliceInput) -> LapSpliceResult:
        self._validate(data)

        reference_diameter_mm = max(data.diameter_1_mm, data.diameter_2_mm)
        used_larger_diameter = not math.isclose(data.diameter_1_mm, data.diameter_2_mm)

        anchorage_input = AnchorageInput(
            diameter_mm=reference_diameter_mm,
            fck_mpa=data.fck_mpa,
            steel_type=data.steel_type,
            bond_condition=data.bond_condition,
            effort_type=data.effort_type,
            anchorage_type=data.anchorage_type,
            as_calc_cm2=data.as_calc_cm2,
            as_ef_cm2=data.as_ef_cm2,
            available_anchorage_cm=10_000.0,
            gamma_c=data.gamma_c,
            gamma_s=data.gamma_s,
        )
        anchorage_result = self._anchorage_service.calculate(anchorage_input)

        diameter_cm = reference_diameter_mm * CM_PER_MM
        lb_nec_calculated_cm = (
            anchorage_result.alpha
            * anchorage_result.lb_cm
            * (data.as_calc_cm2 / data.as_ef_cm2)
        )

        if data.effort_type == EffortType.TENSION:
            alpha0t, alpha0t_label = self._alpha0t(data.spliced_bars_percent)
            lap_calculated_cm = alpha0t * anchorage_result.lb_nec_cm
            lap_min_terms = {
                f"0.3 * alpha0t * lb = 0.3 * {alpha0t:.2f} * lb": (
                    0.3 * alpha0t * anchorage_result.lb_cm
                ),
                "15 * phi": 15.0 * diameter_cm,
                "20 cm": MIN_LAP_LENGTH_CM,
            }
            lap_min_cm, lap_min_governing_term = self._governing_term(lap_min_terms)
            lap_before_addition_cm = max(lap_calculated_cm, lap_min_cm)
            clear_distance_limit_cm = 4.0 * diameter_cm
            clear_distance_addition_cm = (
                data.clear_distance_cm
                if data.clear_distance_cm > clear_distance_limit_cm
                else 0.0
            )
            required_lap_cm = lap_before_addition_cm + clear_distance_addition_cm
        else:
            alpha0t = None
            alpha0t_label = None
            lap_calculated_cm = anchorage_result.lb_nec_cm
            lap_min_terms = {
                "0.6 * lb": 0.6 * anchorage_result.lb_cm,
                "15 * phi": 15.0 * diameter_cm,
                "20 cm": MIN_LAP_LENGTH_CM,
            }
            lap_min_cm, lap_min_governing_term = self._governing_term(lap_min_terms)
            lap_before_addition_cm = max(lap_calculated_cm, lap_min_cm)
            clear_distance_limit_cm = 4.0 * diameter_cm
            clear_distance_addition_cm = 0.0
            required_lap_cm = lap_before_addition_cm

        lap_is_ok = data.available_lap_cm >= required_lap_cm
        deficit_cm = max(required_lap_cm - data.available_lap_cm, 0.0)
        transverse_reasons = self._transverse_reinforcement_reasons(
            reference_diameter_mm,
            data.spliced_bars_percent,
        )
        spacing_reference_cm = max(2.0 * diameter_cm, 2.0)

        return LapSpliceResult(
            reference_diameter_mm=reference_diameter_mm,
            used_larger_diameter=used_larger_diameter,
            fctm_mpa=anchorage_result.fctm_mpa,
            fctk_inf_mpa=anchorage_result.fctk_inf_mpa,
            fctd_mpa=anchorage_result.fctd_mpa,
            fyd_mpa=anchorage_result.fyd_mpa,
            eta1=anchorage_result.eta1,
            eta2=anchorage_result.eta2,
            eta3=anchorage_result.eta3,
            fbd_mpa=anchorage_result.fbd_mpa,
            lb_cm=anchorage_result.lb_cm,
            alpha1=anchorage_result.alpha,
            lb_min_cm=anchorage_result.lb_min_cm,
            lb_nec_calculated_cm=lb_nec_calculated_cm,
            lb_nec_cm=anchorage_result.lb_nec_cm,
            alpha0t=alpha0t,
            alpha0t_label=alpha0t_label,
            lap_calculated_cm=lap_calculated_cm,
            lap_min_cm=lap_min_cm,
            lap_min_governing_term=lap_min_governing_term,
            lap_before_addition_cm=lap_before_addition_cm,
            clear_distance_limit_cm=clear_distance_limit_cm,
            clear_distance_addition_cm=clear_distance_addition_cm,
            required_lap_cm=required_lap_cm,
            lap_is_ok=lap_is_ok,
            deficit_cm=deficit_cm,
            requires_transverse_reinforcement=bool(transverse_reasons),
            transverse_reinforcement_reasons=tuple(transverse_reasons),
            spacing_reference_cm=spacing_reference_cm,
            spacing_warning=data.clear_distance_cm < spacing_reference_cm,
        )

    def build_calculation_memory(
        self,
        data: LapSpliceInput,
        result: LapSpliceResult,
    ) -> str:
        """Builds a calculation memory text for lap splice verification."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        surface = STEEL_PROPERTIES[data.steel_type]["surface"]
        diameter_note = (
            "Bitolas diferentes: adotada a maior bitola como referencia normativa."
            if result.used_larger_diameter
            else "Bitolas iguais: a bitola informada foi usada como referencia."
        )

        lines = [
            "=" * 68,
            "MEMORIA DE CALCULO - EMENDA POR TRANSPASSE",
            "Referencia: ABNT NBR 6118:2023 Versao Corrigida 2:2024",
            f"GERADO EM: {timestamp}",
            "=" * 68,
            "",
            "ESCOPO E LIMITACOES",
            "-" * 44,
            "Calculo auxiliar para barras passivas isoladas.",
            "Feixes, luvas, solda e dispositivos mecanicos ficam fora desta aba.",
            "A verificacao final deve conferir o texto licenciado da NBR 6118 e o detalhamento da peca.",
            "",
            "DADOS DE ENTRADA",
            "-" * 44,
            f"Barra 1 = {data.diameter_1_mm:.1f} mm",
            f"Barra 2 = {data.diameter_2_mm:.1f} mm",
            f"Phi de referencia = {result.reference_diameter_mm:.1f} mm. {diameter_note}",
            f"Fck = {data.fck_mpa:.2f} MPa",
            f"Aco = {data.steel_type.value}",
            f"Superficie = {surface}",
            f"Condicao de aderencia = {data.bond_condition.value}",
            f"Solicitacao = {data.effort_type.value}",
            f"Ancoragem base = {data.anchorage_type.value}",
            f"As,calc = {data.as_calc_cm2:.2f} cm2",
            f"As,ef = {data.as_ef_cm2:.2f} cm2",
            f"Proporcao de barras emendadas = {data.spliced_bars_percent:.1f} %",
            f"Distancia livre entre barras emendadas = {data.clear_distance_cm:.2f} cm",
            f"Comprimento disponivel (Ldisp) = {data.available_lap_cm:.2f} cm",
            "",
            "1) PROPRIEDADES DO CONCRETO",
            "-" * 44,
            "fctm = 0.3 * fck^(2/3), para fck <= 50 MPa",
            f"fctm = {result.fctm_mpa:.3f} MPa",
            f"fctk,inf = 0.7 * fctm = 0.7 * {result.fctm_mpa:.3f} = {result.fctk_inf_mpa:.3f} MPa",
            f"fctd = fctk,inf / gamma_c = {result.fctk_inf_mpa:.3f} / {data.gamma_c:.2f} = {result.fctd_mpa:.3f} MPa",
            "",
            "2) ADERENCIA E COMPRIMENTO BASICO",
            "-" * 44,
            f"eta1 = {result.eta1:.2f} (superficie do aco: {surface})",
            f"eta2 = {result.eta2:.2f} (condicao de aderencia: {data.bond_condition.value})",
            f"eta3 = {result.eta3:.2f} (funcao do diametro phi)",
            "fbd = eta1 * eta2 * eta3 * fctd",
            f"fbd = {result.eta1:.2f} * {result.eta2:.2f} * {result.eta3:.2f} * {result.fctd_mpa:.3f} = {result.fbd_mpa:.3f} MPa",
            "lb = (phi / 4) * (fyd / fbd)",
            f"fyd = fyk / gamma_s = {result.fyd_mpa:.2f} MPa",
            f"lb = ({result.reference_diameter_mm:.1f} / 4) * ({result.fyd_mpa:.2f} / {result.fbd_mpa:.3f}) / 10 = {result.lb_cm:.2f} cm",
            "",
            "3) ANCORAGEM BASE PARA A EMENDA",
            "-" * 44,
            f"alpha1 = {result.alpha1:.2f} ({ANCHORAGE_ALPHA_NOTE[data.anchorage_type]})",
            "O gancho reduz lb,nec por alpha1; nao ha desconto geometrico adicional no transpasse.",
            "lb,nec,calc = alpha1 * lb * (As,calc / As,ef)",
            f"lb,nec,calc = {result.alpha1:.2f} * {result.lb_cm:.2f} * ({data.as_calc_cm2:.2f} / {data.as_ef_cm2:.2f}) = {result.lb_nec_calculated_cm:.2f} cm",
            f"lb,min = {result.lb_min_cm:.2f} cm",
            f"lb,nec = max(lb,nec,calc; lb,min) = {result.lb_nec_cm:.2f} cm",
            "",
        ]

        if data.effort_type == EffortType.TENSION:
            lines.extend(self._memory_tension_lines(data, result))
        else:
            lines.extend(self._memory_compression_lines(result))

        lines.extend(
            [
                "",
                "5) AVISOS DE DETALHAMENTO",
                "-" * 44,
                self._transverse_memory_line(result),
                self._closed_stirrups_memory_line(result),
                self._spacing_memory_line(data, result),
                "",
                "6) VERIFICACAO",
                "-" * 44,
                f"Ldisp = {data.available_lap_cm:.2f} cm",
                f"l0,final = {result.required_lap_cm:.2f} cm",
                f"Deficit = {result.deficit_cm:.2f} cm",
                "Resultado = ATENDE" if result.lap_is_ok else "Resultado = NAO ATENDE",
                "",
                "-" * 68,
                f"RESULTADO FINAL: {'APROVADO' if result.lap_is_ok else 'REPROVADO'}",
                "-" * 68,
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _memory_tension_lines(
        data: LapSpliceInput,
        result: LapSpliceResult,
    ) -> list[str]:
        assert result.alpha0t is not None
        assert result.alpha0t_label is not None
        return [
            "4) COMPRIMENTO DE TRANSPASSE EM TRACAO",
            "-" * 44,
            f"alpha0t = {result.alpha0t:.2f} para faixa {result.alpha0t_label} de barras emendadas.",
            "l0t = alpha0t * lb,nec",
            f"l0t = {result.alpha0t:.2f} * {result.lb_nec_cm:.2f} = {result.lap_calculated_cm:.2f} cm",
            "l0t,min = max(0.3 * alpha0t * lb; 15 * phi; 20 cm)",
            f"0.3 * alpha0t * lb = 0.3 * {result.alpha0t:.2f} * {result.lb_cm:.2f} = {0.3 * result.alpha0t * result.lb_cm:.2f} cm",
            f"15 * phi = 15 * {result.reference_diameter_mm / 10.0:.2f} = {15.0 * result.reference_diameter_mm / 10.0:.2f} cm",
            "20 cm = 20.00 cm",
            f"l0t,min = {result.lap_min_cm:.2f} cm (governante: {result.lap_min_governing_term})",
            f"max(l0t; l0t,min) = {result.lap_before_addition_cm:.2f} cm",
            f"Limite 4 * phi = {result.clear_distance_limit_cm:.2f} cm",
            f"Distancia livre informada = {data.clear_distance_cm:.2f} cm",
            f"Acrescimo por distancia livre > 4 phi = {result.clear_distance_addition_cm:.2f} cm",
            f"l0t,final = {result.lap_before_addition_cm:.2f} + {result.clear_distance_addition_cm:.2f} = {result.required_lap_cm:.2f} cm",
        ]

    @staticmethod
    def _memory_compression_lines(result: LapSpliceResult) -> list[str]:
        return [
            "4) COMPRIMENTO DE TRANSPASSE EM COMPRESSAO",
            "-" * 44,
            "alpha0t nao se aplica a barras comprimidas.",
            "l0c = lb,nec",
            f"l0c = {result.lap_calculated_cm:.2f} cm",
            "l0c,min = max(0.6 * lb; 15 * phi; 20 cm)",
            f"0.6 * lb = 0.6 * {result.lb_cm:.2f} = {0.6 * result.lb_cm:.2f} cm",
            f"15 * phi = 15 * {result.reference_diameter_mm / 10.0:.2f} = {15.0 * result.reference_diameter_mm / 10.0:.2f} cm",
            "20 cm = 20.00 cm",
            f"l0c,min = {result.lap_min_cm:.2f} cm (governante: {result.lap_min_governing_term})",
            f"l0c,final = max(l0c; l0c,min) = {result.required_lap_cm:.2f} cm",
        ]

    @staticmethod
    def _transverse_memory_line(result: LapSpliceResult) -> str:
        if not result.requires_transverse_reinforcement:
            return (
                "Armadura transversal: verificar detalhamento usual; "
                "criterios automaticos phi >= 16 mm e proporcao >= 25% nao foram acionados."
            )
        reasons = "; ".join(result.transverse_reinforcement_reasons)
        return f"Armadura transversal adicional requerida/alertada: {reasons}."

    @staticmethod
    def _closed_stirrups_memory_line(result: LapSpliceResult) -> str:
        return (
            "Barras fechadas: verificar no detalhamento quando houver emendas proximas "
            f"em distancia menor que 10 phi ({10.0 * result.reference_diameter_mm / 10.0:.2f} cm)."
        )

    @staticmethod
    def _spacing_memory_line(data: LapSpliceInput, result: LapSpliceResult) -> str:
        if not result.spacing_warning:
            return (
                "Distancia livre: atende ao aviso preliminar "
                f">= max(2 phi; 20 mm) = {result.spacing_reference_cm:.2f} cm."
            )
        return (
            "Distancia livre: aviso preliminar para conferir fendilhamento/espacamento; "
            f"{data.clear_distance_cm:.2f} cm < max(2 phi; 20 mm) = {result.spacing_reference_cm:.2f} cm."
        )

    @staticmethod
    def _alpha0t(spliced_bars_percent: float) -> tuple[float, str]:
        for bracket in ALPHA0T_BRACKETS:
            if bracket.max_percent is None or spliced_bars_percent <= bracket.max_percent:
                return bracket.value, bracket.label
        raise ValidationError("Proporcao de barras emendadas invalida.")

    @staticmethod
    def _governing_term(terms: dict[str, float]) -> tuple[float, str]:
        term, value = max(terms.items(), key=lambda item: item[1])
        return value, term

    @staticmethod
    def _transverse_reinforcement_reasons(
        reference_diameter_mm: float,
        spliced_bars_percent: float,
    ) -> list[str]:
        reasons: list[str] = []
        if reference_diameter_mm >= 16.0:
            reasons.append("phi >= 16 mm")
        if spliced_bars_percent >= 25.0:
            reasons.append("proporcao de barras emendadas >= 25%")
        return reasons

    @staticmethod
    def _validate(data: LapSpliceInput) -> None:
        for label, value in (
            ("Bitola da barra 1", data.diameter_1_mm),
            ("Bitola da barra 2", data.diameter_2_mm),
            ("Fck", data.fck_mpa),
            ("As,calc", data.as_calc_cm2),
            ("As,ef", data.as_ef_cm2),
            ("Comprimento disponivel", data.available_lap_cm),
        ):
            if not math.isfinite(value) or value <= 0:
                raise ValidationError(f"{label} deve ser maior que zero.")

        if not math.isfinite(data.clear_distance_cm) or data.clear_distance_cm < 0:
            raise ValidationError("Distancia livre deve ser maior ou igual a zero.")
        if not math.isfinite(data.spliced_bars_percent) or data.spliced_bars_percent <= 0:
            raise ValidationError("Proporcao de barras emendadas deve ser maior que zero.")
        if data.spliced_bars_percent > 100.0:
            raise ValidationError("Proporcao de barras emendadas nao deve exceder 100%.")
        if data.as_calc_cm2 > data.as_ef_cm2:
            raise ValidationError("As,calc nao deve ser maior que As,ef.")

        reference_diameter_mm = max(data.diameter_1_mm, data.diameter_2_mm)
        if reference_diameter_mm > MAX_LAP_SPLICE_DIAMETER_MM:
            raise ValidationError(
                "Emendas por transpasse nao sao permitidas para bitolas > 32 mm. "
                "Utilize luva, solda ou outro dispositivo justificado."
            )

        if data.effort_type == EffortType.COMPRESSION and data.anchorage_type in HOOK_ANCHORAGE_TYPES:
            raise ValidationError("Ganchos nao devem ser considerados para barras comprimidas.")
        if not isinstance(data.anchorage_type, AnchorageType):
            raise ValidationError("Tipo de ancoragem invalido.")
