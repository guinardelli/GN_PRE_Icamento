"""Business rules for anchorage verification."""

from __future__ import annotations

import math
from datetime import datetime

from app.core.exceptions import ValidationError
from app.core.anchorage_models import (
    AnchorageInput,
    AnchorageResult,
    AnchorageType,
    BondCondition,
    EffortType,
    SteelType,
)

STEEL_PROPERTIES: dict[SteelType, dict[str, float | str]] = {
    SteelType.CA25: {
        "fyk_mpa": 250.0,
        "eta1": 1.0,
        "surface": "Lisa",
    },
    SteelType.CA50: {
        "fyk_mpa": 500.0,
        "eta1": 2.25,
        "surface": "Nervurada",
    },
    SteelType.CA60: {
        "fyk_mpa": 600.0,
        "eta1": 1.4,
        "surface": "Entalhada",
    },
}

BOND_FACTOR_BY_CONDITION: dict[BondCondition, float] = {
    BondCondition.GOOD: 1.0,
    BondCondition.POOR: 0.7,
}

ANCHORAGE_ALPHA: dict[AnchorageType, float] = {
    AnchorageType.STRAIGHT: 1.0,
    AnchorageType.HOOK: 0.7,
    AnchorageType.WELDED: 0.7,
    AnchorageType.HOOK_WELDED: 0.5,
}

ANCHORAGE_ALPHA_NOTE: dict[AnchorageType, str] = {
    AnchorageType.STRAIGHT: "barra sem gancho",
    AnchorageType.HOOK: "barra tracionada com gancho e cobrimento normal ao gancho >= 3 phi",
    AnchorageType.WELDED: "barra transversal soldada conforme NBR 6118 9.4.2.2",
    AnchorageType.HOOK_WELDED: (
        "barra transversal soldada e gancho com cobrimento normal ao gancho >= 3 phi"
    ),
}

HOOK_ANCHORAGE_TYPES = {
    AnchorageType.HOOK,
    AnchorageType.HOOK_WELDED,
}


class AnchorageVerifierService:
    """Calculates anchorage lengths according to NBR 6118."""

    def calculate(self, data: AnchorageInput) -> AnchorageResult:
        self._validate(data)

        # fctm
        if data.fck_mpa <= 50.0:
            fctm_mpa = 0.3 * (data.fck_mpa ** (2.0 / 3.0))
        else:
            fctm_mpa = 2.12 * math.log1p(0.11 * data.fck_mpa)

        fctk_inf_mpa = 0.7 * fctm_mpa
        fctd_mpa = fctk_inf_mpa / data.gamma_c

        steel_properties = STEEL_PROPERTIES.get(data.steel_type)
        if steel_properties is None:
            raise ValidationError("Tipo de aco desconhecido.")

        eta1 = float(steel_properties["eta1"])
        fyk_mpa = float(steel_properties["fyk_mpa"])
        fyd_mpa = fyk_mpa / data.gamma_s

        eta2 = BOND_FACTOR_BY_CONDITION[data.bond_condition]

        # eta 3
        if data.diameter_mm <= 32.0:
            eta3 = 1.0
        else:
            eta3 = (132.0 - data.diameter_mm) / 100.0

        fbd_mpa = eta1 * eta2 * eta3 * fctd_mpa

        # lb (cm)
        lb_mm = (data.diameter_mm / 4.0) * (fyd_mpa / fbd_mpa)
        lb_cm = lb_mm / 10.0

        diameter_cm = data.diameter_mm / 10.0

        # lb,min (cm)
        if data.effort_type == EffortType.TENSION:
            lb_min_cm = max(0.3 * lb_cm, 10.0 * diameter_cm, 10.0)
        else:
            lb_min_cm = max(0.6 * lb_cm, 10.0 * diameter_cm, 10.0)

        alpha = ANCHORAGE_ALPHA[data.anchorage_type]

        # lb,nec (cm)
        lb_nec_calculated = alpha * lb_cm * (data.as_calc_cm2 / data.as_ef_cm2)
        lb_nec_cm = max(lb_nec_calculated, lb_min_cm)

        anchorage_is_ok = data.available_anchorage_cm >= lb_nec_cm
        required_as_ef_cm2 = None
        if not anchorage_is_ok and data.available_anchorage_cm >= lb_min_cm:
            required_as_ef_cm2 = (
                alpha
                * lb_cm
                * data.as_calc_cm2
                / data.available_anchorage_cm
            )

        return AnchorageResult(
            fctm_mpa=fctm_mpa,
            fctk_inf_mpa=fctk_inf_mpa,
            fctd_mpa=fctd_mpa,
            fyd_mpa=fyd_mpa,
            eta1=eta1,
            eta2=eta2,
            eta3=eta3,
            fbd_mpa=fbd_mpa,
            lb_cm=lb_cm,
            alpha=alpha,
            lb_min_cm=lb_min_cm,
            lb_nec_cm=lb_nec_cm,
            required_as_ef_cm2=required_as_ef_cm2,
            anchorage_is_ok=anchorage_is_ok,
        )

    def build_calculation_memory(self, data: AnchorageInput, result: AnchorageResult) -> str:
        """Builds a calculation memory text for anchorage."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        is_approved = result.anchorage_is_ok

        lines = [
            "=" * 60,
            "MEMORIA DE CALCULO - COMPRIMENTO DE ANCORAGEM",
            "NBR 6118",
            f"GERADO EM: {timestamp}",
            "=" * 60,
            "",
            "DADOS DE ENTRADA",
            "-" * 40,
            f"Bitola = {data.diameter_mm:.1f} mm",
            f"Fck = {data.fck_mpa:.2f} MPa",
            f"Aco = {data.steel_type.value}",
            f"Superficie = {STEEL_PROPERTIES[data.steel_type]['surface']}",
            f"Condicao de aderencia = {data.bond_condition.value}",
            f"Solicitacao = {data.effort_type.value}",
            f"Ancoragem = {data.anchorage_type.value}",
            f"As,calc = {data.as_calc_cm2:.2f} cm2",
            f"As,ef = {data.as_ef_cm2:.2f} cm2",
            f"Comprimento disponivel (Ldisp) = {data.available_anchorage_cm:.2f} cm",
            "",
            "COEFICIENTES DE SEGURANCA",
            "-" * 40,
            f"yc (concreto) = {data.gamma_c:.2f}",
            f"ys (aco) = {data.gamma_s:.2f}",
            "",
            "CALCULOS",
            "-" * 40,
            "",
            "1) Propriedades do Concreto",
            f"   fctm = {result.fctm_mpa:.3f} MPa",
            f"   fctk,inf = 0.7 * fctm = {result.fctk_inf_mpa:.3f} MPa",
            f"   fctd = fctk,inf / yc = {result.fctk_inf_mpa:.3f} / {data.gamma_c:.2f} = {result.fctd_mpa:.3f} MPa",
            "",
            "2) Propriedades do Aco e Aderencia",
            f"   fyd = fyk / ys = {result.fyd_mpa:.2f} MPa",
            f"   eta1 (tipo de aco) = {result.eta1:.2f}",
            f"   eta2 (situacao aderencia) = {result.eta2:.2f}",
            f"   eta3 (diametro da barra) = {result.eta3:.2f}",
            f"   fbd = eta1 * eta2 * eta3 * fctd = {result.fbd_mpa:.3f} MPa",
            "",
            "3) Comprimento Basico de Ancoragem (lb)",
            "   lb = (phi / 4) * (fyd / fbd)",
            f"   lb = ({data.diameter_mm:.1f} / 4) * ({result.fyd_mpa:.2f} / {result.fbd_mpa:.3f}) / 10 = {result.lb_cm:.2f} cm",
            "",
            "4) Comprimento Minimo de Ancoragem (lb,min)",
            f"   lb,min = {result.lb_min_cm:.2f} cm",
            "",
            "5) Comprimento Necessario de Ancoragem (lb,nec)",
            f"   alpha = {result.alpha:.2f}",
            f"   criterio alpha = {ANCHORAGE_ALPHA_NOTE[data.anchorage_type]}",
            "   lb,nec = max(alpha * lb * (As,calc / As,ef), lb,min)",
            f"   lb,nec = max({result.alpha:.2f} * {result.lb_cm:.2f} * ({data.as_calc_cm2:.2f} / {data.as_ef_cm2:.2f}), {result.lb_min_cm:.2f})",
            f"   lb,nec = {result.lb_nec_cm:.2f} cm",
            "",
            "=" * 60,
            "VERIFICACAO",
            "=" * 60,
            f"   Ldisp = {data.available_anchorage_cm:.2f} cm",
            f"   lb,nec = {result.lb_nec_cm:.2f} cm",
            "   OK - Ancoragem atende" if is_approved else "   NAO ATENDE - Ancoragem insuficiente",
            self._build_required_as_ef_line(data, result),
            "",
            "-" * 60,
            f"RESULTADO FINAL: {'APROVADO' if is_approved else 'REPROVADO'}",
            "-" * 60,
        ]
        return "\n".join(lines)

    @staticmethod
    def _build_required_as_ef_line(
        data: AnchorageInput,
        result: AnchorageResult,
    ) -> str:
        if result.anchorage_is_ok:
            return "   As,ef adotada atende ao comprimento disponivel."
        if result.required_as_ef_cm2 is None:
            return (
                "   Nao e possivel atender apenas aumentando As,ef, pois "
                f"Ldisp ({data.available_anchorage_cm:.2f} cm) < "
                f"lb,min ({result.lb_min_cm:.2f} cm)."
            )
        return (
            "   As,ef necessaria para o Ldisp informado = "
            f"{result.required_as_ef_cm2:.2f} cm2"
        )

    @staticmethod
    def _validate(data: AnchorageInput) -> None:
        if not math.isfinite(data.diameter_mm) or data.diameter_mm <= 0:
            raise ValidationError("Bitola deve ser maior que zero.")
        if not math.isfinite(data.fck_mpa) or data.fck_mpa <= 0:
            raise ValidationError("Fck deve ser maior que zero.")
        if not math.isfinite(data.as_calc_cm2) or data.as_calc_cm2 <= 0:
            raise ValidationError("As,calc deve ser maior que zero.")
        if not math.isfinite(data.as_ef_cm2) or data.as_ef_cm2 <= 0:
            raise ValidationError("As,ef deve ser maior que zero.")
        if data.as_calc_cm2 > data.as_ef_cm2:
            raise ValidationError("As,calc nao deve ser maior que As,ef.")
        if not math.isfinite(data.available_anchorage_cm) or data.available_anchorage_cm <= 0:
            raise ValidationError("Ancoragem disponivel deve ser maior que zero.")

        if not isinstance(data.steel_type, SteelType):
            raise ValidationError("Tipo de aco invalido.")
        if not isinstance(data.bond_condition, BondCondition):
            raise ValidationError("Condicao de aderencia invalida.")
        if not isinstance(data.effort_type, EffortType):
            raise ValidationError("Tipo de solicitacao invalido.")
        if not isinstance(data.anchorage_type, AnchorageType):
            raise ValidationError("Tipo de ancoragem invalido.")

        if data.effort_type == EffortType.COMPRESSION and data.anchorage_type in HOOK_ANCHORAGE_TYPES:
            raise ValidationError("Ganchos nao devem ser considerados para barras comprimidas.")
