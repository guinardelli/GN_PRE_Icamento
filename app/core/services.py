"""Business rules for lifting verification with strands."""

from __future__ import annotations

import math
from datetime import datetime

from app.core.exceptions import ValidationError
from app.core.models import (
    ALPHA_ANCHORAGE,
    AnchorageType,
    BondCondition,
    LiftingInput,
    LiftingResult,
    STRAND_SPECS,
)

N_PER_TF = 9_806.65
GAMMA_C = 1.3
GAMMA_S = 1.15
ETA_P1_FOR_7_WIRE_STRAND = 1.2
ECJ_FACTOR = 0.9
BOND_FACTOR_BY_CONDITION = {
    BondCondition.GOOD: 1.0,
    BondCondition.POOR: 0.7,
}

LEGS_PER_LOOP = 2


class LiftingVerifierService:
    """Calculates lifting checks using simplified code-oriented rules.

    Premissas de cálculo (NBR 6118:2023 §9.3.2.2):
    - Cada alça (loop em U) possui 2 pernas.
    - Majoração total: ged = gk × βa × γn (configurável).
    - Aderência: fbpd = ηp1 × ηp2 × fctd.
    - Comprimento de ancoragem: usa fctd aos 28 dias.
    - Capacidade de aderência: usa fctd na idade j (içamento).
    """

    def calculate(self, data: LiftingInput) -> LiftingResult:
        self._validate(data)

        strand = STRAND_SPECS[data.strand_key]
        inclination_rad = math.radians(data.inclination_deg)
        sin_inclination = math.sin(inclination_rad)

        piece_weight_tf = data.volume_m3 * data.concrete_unit_weight_tf_m3
        majorated_weight_tf = piece_weight_tf * data.beta_a * data.gamma_n

        ecj_mpa = ECJ_FACTOR * 5600.0 * math.sqrt(data.fckj_mpa)

        # --- Propriedades na idade j (içamento) ---
        fctm_j_mpa = self._calculate_fctm(data.fckj_mpa)
        fctk_inf_j_mpa = 0.7 * fctm_j_mpa
        fctd_j_mpa = fctk_inf_j_mpa / GAMMA_C
        bond_factor = BOND_FACTOR_BY_CONDITION[data.bond_condition]
        fbpd_j_mpa = ETA_P1_FOR_7_WIRE_STRAND * bond_factor * fctd_j_mpa

        # --- Propriedades aos 28 dias (ancoragem) ---
        fctm_28_mpa = self._calculate_fctm(data.fck_28_mpa)
        fctk_inf_28_mpa = 0.7 * fctm_28_mpa
        fctd_28_mpa = fctk_inf_28_mpa / GAMMA_C
        fbpd_28_mpa = ETA_P1_FOR_7_WIRE_STRAND * bond_factor * fctd_28_mpa

        fpyd_mpa = strand.fpyk_mpa / GAMMA_S

        tension_per_loop_tf = majorated_weight_tf / (data.loops_count * sin_inclination)
        tension_per_leg_tf = tension_per_loop_tf / LEGS_PER_LOOP
        total_legs = data.loops_count * LEGS_PER_LOOP

        # Capacidade por perna — aço (independente da idade)
        steel_capacity_per_leg_tf = (strand.area_mm2 * fpyd_mpa) / N_PER_TF

        # Capacidade por perna — aderência na idade j (real no içamento)
        bond_capacity_per_leg_tf = (
            fbpd_j_mpa * math.pi * strand.diameter_mm * data.available_anchorage_cm * 10.0
        ) / N_PER_TF

        # Capacidade total = por_perna × n_pernas × sen(θ)
        max_supported_load_by_steel_tf = (
            steel_capacity_per_leg_tf * total_legs * sin_inclination
        )
        max_supported_load_by_bond_tf = (
            bond_capacity_per_leg_tf * total_legs * sin_inclination
        )
        max_supported_load_tf = min(
            max_supported_load_by_steel_tf,
            max_supported_load_by_bond_tf,
        )

        # Ancoragem necessária — usa fbpd_28 (28 dias) conforme NBR 6118:2023
        base_anchorage_cm = (
            (tension_per_leg_tf * N_PER_TF)
            / (fbpd_28_mpa * math.pi * strand.diameter_mm)
            / 10.0
        )
        alpha_anchorage = ALPHA_ANCHORAGE[data.anchorage_type]
        required_anchorage_cm = alpha_anchorage * base_anchorage_cm
        anchorage_is_ok = data.available_anchorage_cm >= required_anchorage_cm
        capacity_is_ok = max_supported_load_tf >= majorated_weight_tf

        # Tensao desenvolvida no aco limitada pela ancoragem (usa fbpd_j)
        stress_developed_mpa = min(
            (fbpd_j_mpa * math.pi * strand.diameter_mm * data.available_anchorage_cm * 10.0)
            / strand.area_mm2,
            fpyd_mpa,
        )
        stress_mobilization_ratio = stress_developed_mpa / fpyd_mpa if fpyd_mpa > 0 else 0.0

        utilization_ratio = (
            majorated_weight_tf / max_supported_load_tf
            if max_supported_load_tf > 0
            else float("inf")
        )
        safety_factor = (
            max_supported_load_tf / majorated_weight_tf
            if majorated_weight_tf > 0
            else float("inf")
        )

        return LiftingResult(
            piece_weight_tf=piece_weight_tf,
            majorated_weight_tf=majorated_weight_tf,
            beta_a=data.beta_a,
            gamma_n=data.gamma_n,
            ecj_mpa=ecj_mpa,
            fctm_j_mpa=fctm_j_mpa,
            fctm_28_mpa=fctm_28_mpa,
            fptk_mpa=strand.fptk_mpa,
            fpyk_mpa=strand.fpyk_mpa,
            fpyd_mpa=fpyd_mpa,
            fbpd_j_mpa=fbpd_j_mpa,
            fbpd_28_mpa=fbpd_28_mpa,
            strand_area_cm2=strand.area_mm2 / 100.0,
            strand_unit_mass_kg_m=strand.unit_mass_kg_per_m,
            base_anchorage_cm=base_anchorage_cm,
            required_anchorage_cm=required_anchorage_cm,
            alpha_anchorage=alpha_anchorage,
            max_supported_load_tf=max_supported_load_tf,
            max_supported_load_by_steel_tf=max_supported_load_by_steel_tf,
            max_supported_load_by_bond_tf=max_supported_load_by_bond_tf,
            anchorage_is_ok=anchorage_is_ok,
            capacity_is_ok=capacity_is_ok,
            utilization_ratio=utilization_ratio,
            safety_factor=safety_factor,
            tension_per_loop_tf=tension_per_loop_tf,
            tension_per_leg_tf=tension_per_leg_tf,
            total_legs=total_legs,
            stress_developed_mpa=stress_developed_mpa,
            stress_mobilization_ratio=stress_mobilization_ratio,
        )

    def build_calculation_memory(self, data: LiftingInput, result: LiftingResult) -> str:
        """Builds a calculation memory text with formulas and substituted values."""
        strand = STRAND_SPECS[data.strand_key]
        sin_inclination = math.sin(math.radians(data.inclination_deg))
        bond_factor = BOND_FACTOR_BY_CONDITION[data.bond_condition]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Valores intermediários para exibição
        fctk_inf_j = 0.7 * result.fctm_j_mpa
        fctd_j = fctk_inf_j / GAMMA_C
        fctk_inf_28 = 0.7 * result.fctm_28_mpa
        fctd_28 = fctk_inf_28 / GAMMA_C

        is_approved = result.capacity_is_ok and result.anchorage_is_ok

        lines = [
            "=" * 60,
            "MEMORIA DE CALCULO - VERIFICACAO DE ICAMENTO",
            "NBR 9062 / NBR 6118:2023",
            f"GERADO EM: {timestamp}",
            f"IDENTIFICACAO DA PECA: {data.piece_id.strip() or '-'}",
            "=" * 60,
            "",
            "DADOS DE ENTRADA",
            "-" * 40,
            f"Fck,j = {data.fckj_mpa:.2f} MPa  (idade do icamento)",
            f"Fck,28 = {data.fck_28_mpa:.2f} MPa  (28 dias)",
            f"Volume = {data.volume_m3:.3f} m3",
            f"Peso especifico = {data.concrete_unit_weight_tf_m3:.3f} tf/m3",
            f"Cordoalha = {strand.label}",
            f"Inclinacao = {data.inclination_deg:.1f} graus",
            f"Ancoragem disponivel = {data.available_anchorage_cm:.2f} cm",
            (
                f"Tipo de ancoragem = {data.anchorage_type.value}  "
                f"(alpha = {result.alpha_anchorage:.2f})"
            ),
            f"Condicao de aderencia = {data.bond_condition.value}",
            f"Quantidade de alcas = {data.loops_count}",
            f"Quantidade de pernas = {result.total_legs} ({LEGS_PER_LOOP} por alca)",
            "",
            "COEFICIENTES ADOTADOS",
            "-" * 40,
            f"Ba (amplificacao dinamica) = {data.beta_a:.2f}",
            f"yn (majoracao) = {data.gamma_n:.2f}",
            f"Ba x yn = {data.beta_a * data.gamma_n:.2f}",
            f"yc (concreto) = {GAMMA_C:.2f}",
            f"ys (aco) = {GAMMA_S:.2f}",
            f"eta_p1 (cordoalha 7 fios) = {ETA_P1_FOR_7_WIRE_STRAND:.2f}",
            f"eta_p2 (aderencia) = {bond_factor:.2f}",
            f"alpha (tipo de ancoragem) = {result.alpha_anchorage:.2f}",
            "",
            "CALCULOS",
            "-" * 40,
            "",
            "1) Peso da peca",
            (
                f"   gk = Volume x gamma_conc = {data.volume_m3:.3f} x "
                f"{data.concrete_unit_weight_tf_m3:.3f} = {result.piece_weight_tf:.3f} tf"
            ),
            "",
            "2) Peso majorado (NBR 9062)",
            (
                f"   ged = gk x Ba x yn = {result.piece_weight_tf:.3f} x "
                f"{data.beta_a:.2f} x {data.gamma_n:.2f} = {result.majorated_weight_tf:.3f} tf"
            ),
            "",
            "3) Modulo do concreto (idade j)",
            (
                f"   Ec,j = 0,9 x 5600 x sqrt(fck,j) = 0,9 x 5600 x sqrt({data.fckj_mpa:.2f})"
                f" = {result.ecj_mpa:.2f} MPa"
            ),
            "",
            "4) Resistencia a tracao do concreto",
            "",
            "   4a) Na idade j (capacidade de aderencia no icamento):",
            (
                f"   fctm,j = 0,30 x fck,j^(2/3) = 0,30 x {data.fckj_mpa:.2f}^(2/3)"
                f" = {result.fctm_j_mpa:.3f} MPa"
            ),
            (
                f"   fctk,inf,j = 0,70 x fctm,j = 0,70 x {result.fctm_j_mpa:.3f}"
                f" = {fctk_inf_j:.3f} MPa"
            ),
            (
                f"   fctd,j = fctk,inf,j / yc = {fctk_inf_j:.3f} / {GAMMA_C:.2f}"
                f" = {fctd_j:.3f} MPa"
            ),
            "",
            "   4b) Aos 28 dias (comprimento de ancoragem - NBR 6118 §9.3.2.2):",
            (
                f"   fctm,28 = 0,30 x fck,28^(2/3) = 0,30 x {data.fck_28_mpa:.2f}^(2/3)"
                f" = {result.fctm_28_mpa:.3f} MPa"
            ),
            (
                f"   fctk,inf,28 = 0,70 x fctm,28 = 0,70 x {result.fctm_28_mpa:.3f}"
                f" = {fctk_inf_28:.3f} MPa"
            ),
            (
                f"   fctd,28 = fctk,inf,28 / yc = {fctk_inf_28:.3f} / {GAMMA_C:.2f}"
                f" = {fctd_28:.3f} MPa"
            ),
            "",
            "5) Aco da cordoalha",
            f"   fptk = {result.fptk_mpa:.1f} MPa",
            f"   fpyk = {result.fpyk_mpa:.1f} MPa",
            (
                f"   fpyd = fpyk / ys = {result.fpyk_mpa:.1f} / {GAMMA_S:.2f}"
                f" = {result.fpyd_mpa:.1f} MPa"
            ),
            "",
            "6) Tensao de aderencia de projeto",
            "",
            "   6a) Na idade j (capacidade):",
            (
                f"   fbpd,j = eta_p1 x eta_p2 x fctd,j = {ETA_P1_FOR_7_WIRE_STRAND:.2f} x "
                f"{bond_factor:.2f} x {fctd_j:.3f} = {result.fbpd_j_mpa:.3f} MPa"
            ),
            "",
            "   6b) Aos 28 dias (ancoragem):",
            (
                f"   fbpd,28 = eta_p1 x eta_p2 x fctd,28 = {ETA_P1_FOR_7_WIRE_STRAND:.2f} x "
                f"{bond_factor:.2f} x {fctd_28:.3f} = {result.fbpd_28_mpa:.3f} MPa"
            ),
            "",
            "7) Carga por alca e por perna",
            (
                f"   T_alca = ged / (n_alcas x sen(i)) = {result.majorated_weight_tf:.3f} / "
                f"({data.loops_count} x {sin_inclination:.4f})"
                f" = {result.tension_per_loop_tf:.3f} tf"
            ),
            (
                f"   T_perna = T_alca / 2 = {result.tension_per_loop_tf:.3f} / 2"
                f" = {result.tension_per_leg_tf:.3f} tf"
            ),
            "",
            "8) Area e peso da cordoalha",
            f"   As = {strand.area_mm2:.1f} mm2 = {result.strand_area_cm2:.4f} cm2",
            f"   Peso = {result.strand_unit_mass_kg_m:.3f} kg/m",
            "",
            "9) Ancoragem necessaria (por perna, usando fbpd,28)",
            (
                f"   Lnec,base = (T_perna x 9806,65) / (fbpd,28 x pi x diam x 10)"
            ),
            (
                f"   Lnec,base = ({result.tension_per_leg_tf:.3f} x {N_PER_TF:.2f})"
                f" / ({result.fbpd_28_mpa:.3f} x {math.pi:.4f} x {strand.diameter_mm:.1f} x 10)"
            ),
            f"   Lnec,base = {result.base_anchorage_cm:.2f} cm",
            (
                f"   Lnec = alpha x Lnec,base = {result.alpha_anchorage:.2f}"
                f" x {result.base_anchorage_cm:.2f}"
                f" = {result.required_anchorage_cm:.2f} cm  [{data.anchorage_type.value}]"
            ),
            "",
            "10) Carga maxima suportada (usando fbpd,j na idade do icamento)",
            f"   Por aco    = {result.max_supported_load_by_steel_tf:.3f} tf",
            f"   Por aderencia = {result.max_supported_load_by_bond_tf:.3f} tf",
            f"   Governante = min(aco, aderencia) = {result.max_supported_load_tf:.3f} tf",
            "",
            "=" * 60,
            "VERIFICACOES",
            "=" * 60,
            "",
            "a) Capacidade de carga:",
            f"   ged = {result.majorated_weight_tf:.3f} tf",
            f"   Carga maxima = {result.max_supported_load_tf:.3f} tf",
            (
                f"   Taxa de utilizacao = {result.utilization_ratio:.1%}"
            ),
            "   OK - Capacidade atende"
            if result.capacity_is_ok
            else "   NAO ATENDE - Capacidade insuficiente",
            "",
            "b) Ancoragem:",
            f"   Tipo: {data.anchorage_type.value}  (alpha = {result.alpha_anchorage:.2f})",
            (
                f"   Lnec,base (reta) = {result.base_anchorage_cm:.2f} cm"
                f"  (fbpd,28 = {result.fbpd_28_mpa:.3f} MPa)"
            ),
            f"   Lnec (com reducao) = {result.required_anchorage_cm:.2f} cm",
            f"   Ldisp = {data.available_anchorage_cm:.2f} cm",
            "   OK - Ancoragem atende"
            if result.anchorage_is_ok
            else "   NAO ATENDE - Ancoragem insuficiente",
            "",
            "c) Fator de seguranca global:",
            f"   FS = {result.safety_factor:.2f}",
            "",
            "d) Tensao desenvolvida no aco (limitada pela ancoragem, usando fbpd,j):",
            "   sigma_s,eff = min( fbpd,j x pi x phi x Ldisp / Ap , fpyd )",
            (
                f"   sigma_s,eff = min("
                f" {result.fbpd_j_mpa:.3f} x {math.pi:.4f} x {strand.diameter_mm:.1f} x "
                f"{data.available_anchorage_cm:.2f} x 10 / {strand.area_mm2:.1f}"
                f" , {result.fpyd_mpa:.1f} )"
            ),
            f"   sigma_s,eff = {result.stress_developed_mpa:.1f} MPa",
            f"   Mobilizacao do aco = sigma_s,eff / fpyd = {result.stress_mobilization_ratio:.1%}",
            (
                "   Interpretacao: a ancoragem disponivel mobiliza "
                f"{result.stress_mobilization_ratio:.1%} da resistencia de calculo do aco."
            ),
            (
                "   (100% = ancoragem suficiente para escoamento pleno; "
                "<100% = aco limitado pela ancoragem)"
            ),
            "",
            "-" * 60,
            f"RESULTADO FINAL: {'APROVADO' if is_approved else 'REPROVADO'}",
            "-" * 60,
        ]
        return "\n".join(lines)

    @staticmethod
    def _calculate_fctm(fck_mpa: float) -> float:
        if fck_mpa <= 50.0:
            return 0.3 * (fck_mpa ** (2.0 / 3.0))
        return 2.12 * math.log1p(0.11 * fck_mpa)

    @staticmethod
    def _validate(data: LiftingInput) -> None:
        LiftingVerifierService._validate_positive_finite(
            data.fckj_mpa,
            "Fck,j deve ser maior que zero.",
        )
        LiftingVerifierService._validate_positive_finite(
            data.fck_28_mpa,
            "Fck (28 dias) deve ser maior que zero.",
        )
        LiftingVerifierService._validate_positive_finite(
            data.volume_m3,
            "Volume deve ser maior que zero.",
        )
        LiftingVerifierService._validate_positive_finite(
            data.concrete_unit_weight_tf_m3,
            "Peso especifico do concreto deve ser maior que zero.",
        )
        LiftingVerifierService._validate_positive_finite(
            data.inclination_deg,
            "Inclinacao deve ser maior que zero.",
        )
        LiftingVerifierService._validate_positive_finite(
            data.available_anchorage_cm,
            "Ancoragem disponivel deve ser maior que zero.",
        )
        LiftingVerifierService._validate_positive_finite(
            data.beta_a,
            "Beta a deve ser maior que zero.",
        )
        LiftingVerifierService._validate_positive_finite(
            data.gamma_n,
            "Gamma n deve ser maior que zero.",
        )

        if not isinstance(data.bond_condition, BondCondition):
            raise ValidationError("Condicao de aderencia invalida.")
        if not isinstance(data.anchorage_type, AnchorageType):
            raise ValidationError("Tipo de ancoragem invalido.")
        if data.fck_28_mpa < data.fckj_mpa:
            raise ValidationError("Fck (28 dias) deve ser >= Fck,j.")
        if data.strand_key not in STRAND_SPECS:
            raise ValidationError("Tipo de cordoalha invalido.")
        if not (0.1 <= data.inclination_deg <= 90.0):
            raise ValidationError("Inclinacao deve estar entre 0,1 e 90 graus.")
        if data.loops_count <= 0:
            raise ValidationError("Quantidade de alcas deve ser maior que zero.")

    @staticmethod
    def _validate_positive_finite(value: float, message: str) -> None:
        if not math.isfinite(value) or value <= 0:
            raise ValidationError(message)
