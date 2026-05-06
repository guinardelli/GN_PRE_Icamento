"""Main window for lifting verification."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.config.settings import APP_NAME, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH
from app.core.exceptions import ValidationError
from app.core.models import AnchorageType, ANCHORAGE_TYPE_LABELS, BondCondition, LiftingInput, LiftingResult, STRAND_SPECS
from app.core.services import LiftingVerifierService
from app.ui.sketch_widget import LiftingSketchWidget
from app.ui.styles import base_style



class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self._service = LiftingVerifierService()
        self._build_ui()
        # Auto-calculate with default values on startup
        self._on_calculate()

    def _build_ui(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.setStyleSheet(base_style())

        central = QWidget()
        root_layout = QVBoxLayout(central)
        root_layout.setSpacing(10)
        root_layout.setContentsMargins(12, 12, 12, 12)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_verification_tab(), "Verificacao")
        self.tabs.addTab(self._build_memory_tab(), "Memoria de calculo")

        root_layout.addWidget(self.tabs)
        self.setCentralWidget(central)

    def _build_verification_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        # Top row: inputs (left) + results (right)
        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        top_row.addWidget(self._build_input_group(), 3)
        top_row.addWidget(self._build_result_panel(), 4)
        layout.addLayout(top_row, 5)

        # Bottom: dynamic sketch
        sketch_group = QGroupBox("Representacao grafica")
        sketch_layout = QVBoxLayout(sketch_group)
        sketch_layout.setContentsMargins(4, 4, 4, 4)
        self.sketch_widget = LiftingSketchWidget()
        self.sketch_widget.setMinimumHeight(200)
        sketch_layout.addWidget(self.sketch_widget)
        layout.addWidget(sketch_group, 3)

        return tab

    def _build_input_group(self) -> QGroupBox:
        group = QGroupBox("Dados de entrada")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        form = QFormLayout()
        form.setSpacing(8)

        self.fckj_input = QDoubleSpinBox()
        self.fckj_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.fckj_input.setRange(5.0, 120.0)
        self.fckj_input.setDecimals(2)
        self.fckj_input.setValue(15.0)
        self.fckj_input.setSuffix(" MPa")

        self.fck_28_input = QDoubleSpinBox()
        self.fck_28_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.fck_28_input.setRange(5.0, 120.0)
        self.fck_28_input.setDecimals(2)
        self.fck_28_input.setValue(40.0)
        self.fck_28_input.setSuffix(" MPa")

        self.volume_input = QDoubleSpinBox()
        self.volume_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.volume_input.setRange(0.01, 1000.0)
        self.volume_input.setDecimals(3)
        self.volume_input.setValue(1.0)
        self.volume_input.setSuffix(" m3")

        self.unit_weight_input = QDoubleSpinBox()
        self.unit_weight_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.unit_weight_input.setRange(0.1, 5.0)
        self.unit_weight_input.setDecimals(3)
        self.unit_weight_input.setValue(2.5)
        self.unit_weight_input.setSuffix(" tf/m3")

        self.strand_input = QComboBox()
        for strand_key in STRAND_SPECS:
            self.strand_input.addItem(strand_key)
        # Default to 12,7 mm
        strand_12_7_index = self.strand_input.findText("CP 190-RB 12,7 mm")
        if strand_12_7_index >= 0:
            self.strand_input.setCurrentIndex(strand_12_7_index)

        self.inclination_input = QDoubleSpinBox()
        self.inclination_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.inclination_input.setRange(1.0, 90.0)
        self.inclination_input.setDecimals(1)
        self.inclination_input.setValue(90.0)
        self.inclination_input.setSuffix(" graus")

        self.anchorage_input = QDoubleSpinBox()
        self.anchorage_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.anchorage_input.setRange(1.0, 500.0)
        self.anchorage_input.setDecimals(2)
        self.anchorage_input.setValue(60.0)
        self.anchorage_input.setSuffix(" cm")

        self.bond_input = QComboBox()
        self.bond_input.addItem("Boa aderencia", BondCondition.GOOD.value)
        self.bond_input.addItem("Ma aderencia", BondCondition.POOR.value)

        self.anchorage_type_input = QComboBox()
        for anc_type, label in ANCHORAGE_TYPE_LABELS.items():
            self.anchorage_type_input.addItem(label, anc_type.value)
        # Default to Dobra 90°
        hook90_index = self.anchorage_type_input.findData(AnchorageType.HOOK_90.value)
        if hook90_index >= 0:
            self.anchorage_type_input.setCurrentIndex(hook90_index)

        self.loops_input = QSpinBox()
        self.loops_input.setRange(1, 20)
        self.loops_input.setValue(2)

        self.beta_a_input = QDoubleSpinBox()
        self.beta_a_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.beta_a_input.setRange(1.0, 10.0)
        self.beta_a_input.setDecimals(2)
        self.beta_a_input.setValue(3.0)

        self.gamma_n_input = QDoubleSpinBox()
        self.gamma_n_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.gamma_n_input.setRange(1.0, 5.0)
        self.gamma_n_input.setDecimals(2)
        self.gamma_n_input.setValue(1.30)

        form.addRow("Fck,j (icamento):", self.fckj_input)
        form.addRow("Fck (28 dias):", self.fck_28_input)
        form.addRow("Volume da peca:", self.volume_input)
        form.addRow("Peso especifico:", self.unit_weight_input)
        form.addRow("Cordoalha:", self.strand_input)
        form.addRow("Inclinacao:", self.inclination_input)
        form.addRow("Ancoragem disponivel:", self.anchorage_input)
        form.addRow("Tipo de ancoragem:", self.anchorage_type_input)
        form.addRow("Aderencia:", self.bond_input)
        form.addRow("Quantidade de alcas:", self.loops_input)
        form.addRow("\u03b2a (ampl. dinamica):", self.beta_a_input)
        form.addRow("\u03b3n (majoracao):", self.gamma_n_input)

        calculate_button = QPushButton("Calcular verificacao")
        calculate_button.setCursor(Qt.PointingHandCursor)
        calculate_button.clicked.connect(self._on_calculate)

        layout.addLayout(form)
        layout.addWidget(calculate_button)
        layout.addStretch(1)
        return group

    def _build_result_panel(self) -> QGroupBox:
        group = QGroupBox("Resultado")
        outer_layout = QVBoxLayout(group)
        outer_layout.setSpacing(6)

        # Status banner
        self.status_label = QLabel("Preencha os dados e clique em 'Calcular verificacao'.")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(36)
        self.status_label.setStyleSheet(
            "background: #eef0f2; padding: 8px 10px; border: 1px solid #d2d6dc;"
            " border-radius: 4px; font-weight: 600; font-size: 10pt;"
        )
        outer_layout.addWidget(self.status_label)

        # Scrollable results area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll_content = QWidget()
        result_layout = QVBoxLayout(scroll_content)
        result_layout.setSpacing(10)
        result_layout.setContentsMargins(0, 4, 0, 4)

        self.result_fields: dict[str, QLineEdit] = {}

        # Section 1: Cargas
        result_layout.addWidget(self._section_label("Cargas"))
        load_form = QFormLayout()
        load_form.setSpacing(5)
        for key, label in (
            ("piece_weight_tf", "Massa da peca (tf)"),
            ("majorated_weight_tf", "Massa majorada (tf)"),
            ("tension_per_loop_tf", "Carga por alca (tf)"),
            ("tension_per_leg_tf", "Carga por perna (tf)"),
            ("total_legs", "Total de pernas"),
        ):
            field = self._result_field()
            self.result_fields[key] = field
            load_form.addRow(label + ":", field)
        result_layout.addLayout(load_form)

        # Section 2: Propriedades dos materiais
        result_layout.addWidget(self._section_label("Propriedades dos materiais"))
        mat_form = QFormLayout()
        mat_form.setSpacing(5)
        for key, label in (
            ("ecj_mpa", "Ec,j (MPa)"),
            ("fctm_j_mpa", "fctm,j (MPa)"),
            ("fctm_28_mpa", "fctm,28 (MPa)"),
            ("fpyd_mpa", "fpyd (MPa)"),
            ("fbpd_j_mpa", "fbpd,j (MPa)"),
            ("fbpd_28_mpa", "fbpd,28 (MPa)"),
        ):
            field = self._result_field()
            self.result_fields[key] = field
            mat_form.addRow(label + ":", field)
        result_layout.addLayout(mat_form)

        # Section 3: Verificacoes
        result_layout.addWidget(self._section_label("Verificacoes"))
        check_form = QFormLayout()
        check_form.setSpacing(5)
        for key, label in (
            ("max_load_steel_tf", "Carga max. aco (tf)"),
            ("max_load_bond_tf", "Carga max. aderencia (tf)"),
            ("max_load_tf", "Carga max. governante (tf)"),
            ("governing_criterion", "Criterio governante"),
            ("base_anchorage_cm", "Anc. necessaria reta (cm)"),
            ("required_anchorage_cm", "Anc. necessaria c/reducao (cm)"),
            ("available_anchorage_cm", "Ancoragem disponivel (cm)"),
        ):
            field = self._result_field()
            self.result_fields[key] = field
            check_form.addRow(label + ":", field)
        result_layout.addLayout(check_form)

        # Section 4: Indicadores
        result_layout.addWidget(self._section_label("Indicadores"))
        ind_form = QFormLayout()
        ind_form.setSpacing(5)
        for key, label in (
            ("utilization", "Taxa de utilizacao"),
            ("safety_factor", "Fator de seguranca (FS)"),
            ("stress_developed", "Tensao desenvolvida (MPa)"),
            ("stress_mobilization", "Mobilizacao do aco (% fpyd)"),
        ):
            field = self._result_field()
            self.result_fields[key] = field
            ind_form.addRow(label + ":", field)
        result_layout.addLayout(ind_form)

        result_layout.addStretch(1)
        scroll.setWidget(scroll_content)
        outer_layout.addWidget(scroll, 1)

        memory_hint = QLabel("<a href='#'>Memoria completa na aba 'Memoria de calculo'.</a>")
        memory_hint.setAlignment(Qt.AlignCenter)
        memory_hint.setStyleSheet("font-size: 9pt; color: #4b5563; text-decoration: none;")
        memory_hint.setOpenExternalLinks(False)
        memory_hint.linkActivated.connect(lambda: self.tabs.setCurrentIndex(1))
        outer_layout.addWidget(memory_hint)

        return group

    def _build_memory_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)
        layout.setContentsMargins(6, 6, 6, 6)

        self.memory_text = QTextEdit()
        self.memory_text.setReadOnly(True)
        self.memory_text.setPlaceholderText("Calcule na aba 'Verificacao' para gerar a memoria.")

        layout.addWidget(self.memory_text)
        return tab

    @staticmethod
    def _section_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            "font-weight: 700; font-size: 10pt; color: #0f172a;"
            " border-bottom: 1px solid #cbd5e1; padding-bottom: 4px;"
            " margin-top: 8px; background: transparent;"
        )
        return label

    @staticmethod
    def _result_field() -> QLineEdit:
        field = QLineEdit()
        field.setReadOnly(True)
        field.setFocusPolicy(Qt.NoFocus)
        field.setAlignment(Qt.AlignRight)
        field.setPlaceholderText("-")
        field.setStyleSheet("QLineEdit { background-color: transparent; border: none; color: #0f172a; font-weight: 600; }")
        return field

    def _on_calculate(self) -> None:
        try:
            data = self._read_input()
            result = self._service.calculate(data)
            memory_text = self._service.build_calculation_memory(data, result)
        except ValidationError as exc:
            QMessageBox.warning(self, APP_NAME, str(exc))
            return

        is_approved = result.capacity_is_ok and result.anchorage_is_ok
        if is_approved:
            self.status_label.setText("VERIFICACAO APROVADA")
            self.status_label.setStyleSheet(
                "background: #ecfdf3; color: #166534; padding: 8px 10px;"
                " border: 1px solid #bbf7d0; border-radius: 4px;"
                " font-weight: 700; font-size: 11pt;"
            )
        else:
            failures = []
            if not result.capacity_is_ok:
                failures.append("capacidade insuficiente")
            if not result.anchorage_is_ok:
                failures.append("ancoragem insuficiente")
            self.status_label.setText(
                f"VERIFICACAO REPROVADA: {', '.join(failures)}"
            )
            self.status_label.setStyleSheet(
                "background: #fef2f2; color: #991b1b; padding: 8px 10px;"
                " border: 1px solid #fecaca; border-radius: 4px;"
                " font-weight: 700; font-size: 11pt;"
            )

        self._update_result_fields(result, data.available_anchorage_cm)
        self.memory_text.setPlainText(memory_text)
        self.sketch_widget.update_sketch(
            loops_count=data.loops_count,
            anchorage_type=data.anchorage_type,
            inclination_deg=data.inclination_deg,
        )

    def _read_input(self) -> LiftingInput:
        bond = BondCondition(self.bond_input.currentData())
        anchorage_type = AnchorageType(self.anchorage_type_input.currentData())
        return LiftingInput(
            fckj_mpa=self.fckj_input.value(),
            fck_28_mpa=self.fck_28_input.value(),
            volume_m3=self.volume_input.value(),
            concrete_unit_weight_tf_m3=self.unit_weight_input.value(),
            strand_key=self.strand_input.currentText(),
            inclination_deg=self.inclination_input.value(),
            available_anchorage_cm=self.anchorage_input.value(),
            bond_condition=bond,
            anchorage_type=anchorage_type,
            loops_count=self.loops_input.value(),
            beta_a=self.beta_a_input.value(),
            gamma_n=self.gamma_n_input.value(),
        )

    def _update_result_fields(
        self,
        result: LiftingResult,
        available_anchorage_cm: float,
    ) -> None:
        if result.max_supported_load_by_steel_tf <= result.max_supported_load_by_bond_tf:
            governing = "Aco"
        else:
            governing = "Aderencia"

        values = {
            "piece_weight_tf": f"{result.piece_weight_tf:.3f}",
            "majorated_weight_tf": f"{result.majorated_weight_tf:.3f}",
            "tension_per_loop_tf": f"{result.tension_per_loop_tf:.3f}",
            "tension_per_leg_tf": f"{result.tension_per_leg_tf:.3f}",
            "total_legs": f"{result.total_legs}",
            "ecj_mpa": f"{result.ecj_mpa:.2f}",
            "fctm_j_mpa": f"{result.fctm_j_mpa:.3f}",
            "fctm_28_mpa": f"{result.fctm_28_mpa:.3f}",
            "fpyd_mpa": f"{result.fpyd_mpa:.1f}",
            "fbpd_j_mpa": f"{result.fbpd_j_mpa:.3f}",
            "fbpd_28_mpa": f"{result.fbpd_28_mpa:.3f}",
            "max_load_steel_tf": f"{result.max_supported_load_by_steel_tf:.3f}",
            "max_load_bond_tf": f"{result.max_supported_load_by_bond_tf:.3f}",
            "max_load_tf": f"{result.max_supported_load_tf:.3f}",
            "governing_criterion": governing,
            "base_anchorage_cm": f"{result.base_anchorage_cm:.2f}",
            "required_anchorage_cm": f"{result.required_anchorage_cm:.2f}",
            "available_anchorage_cm": f"{available_anchorage_cm:.2f}",
            "utilization": f"{result.utilization_ratio:.1%}",
            "safety_factor": f"{result.safety_factor:.2f}",
            "stress_developed": f"{result.stress_developed_mpa:.1f}  (fpyd = {result.fpyd_mpa:.1f} MPa)",
            "stress_mobilization": f"{result.stress_mobilization_ratio:.1%}",
        }
        for key, value in values.items():
            self.result_fields[key].setText(value)

        # Color-code critical fields
        self._color_field("utilization", is_ok=result.utilization_ratio <= 1.0)
        self._color_field("safety_factor", is_ok=result.safety_factor >= 1.0)
        self._color_field("base_anchorage_cm", is_ok=result.anchorage_is_ok)
        self._color_field("required_anchorage_cm", is_ok=result.anchorage_is_ok)
        self._color_field("stress_mobilization", is_ok=result.stress_mobilization_ratio >= 1.0)

    def _color_field(self, key: str, is_ok: bool) -> None:
        field = self.result_fields.get(key)
        if field is None:
            return
        if is_ok:
            field.setStyleSheet(
                "QLineEdit { background-color: transparent; border: none; color: #166534; font-weight: 700; }"
            )
        else:
            field.setStyleSheet(
                "QLineEdit { background-color: transparent; border: none; color: #dc2626; font-weight: 700; }"
            )
