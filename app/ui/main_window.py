"""Main window for lifting verification."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
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
        self._connect_auto_calculate()
        self._setup_shortcuts()
        self._configure_input_metadata()
        self._set_tab_order()
        self._validate_fck_relationship()
        # Auto-calculate with default values on startup
        self._on_calculate(show_errors=False)

    def _build_ui(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.setStyleSheet(base_style())

        central = QWidget()
        root_layout = QVBoxLayout(central)
        root_layout.setSpacing(10)
        root_layout.setContentsMargins(12, 12, 12, 12)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_verification_tab(), "Verificação")
        self.tabs.addTab(self._build_memory_tab(), "Memória de Cálculo")

        root_layout.addWidget(self.tabs)
        self.setCentralWidget(central)
        self._build_menu_bar()
        self.statusBar().showMessage("Pronto.")

    def _build_verification_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 10, 0, 0)

        top_content = QWidget()
        top_row = QHBoxLayout(top_content)
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(10)
        top_row.addWidget(self._build_input_group(), 3)
        top_row.addWidget(self._build_result_panel(), 4)

        sketch_group = QGroupBox("Representação Gráfica")
        sketch_layout = QVBoxLayout(sketch_group)
        sketch_layout.setContentsMargins(4, 4, 4, 4)
        self.sketch_widget = LiftingSketchWidget()
        self.sketch_widget.setMinimumHeight(140)
        sketch_layout.addWidget(self.sketch_widget)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(top_content)
        splitter.addWidget(sketch_group)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([560, 160])
        layout.addWidget(splitter, 1)

        return tab

    def _build_input_group(self) -> QGroupBox:
        group = QGroupBox("Dados de Entrada")
        outer = QVBoxLayout(group)
        outer.setSpacing(6)
        outer.setContentsMargins(8, 16, 8, 8)

        # --- Instancia widgets ---
        self.piece_id_input = QLineEdit()
        self.piece_id_input.setPlaceholderText("Ex.: VIGA P1 - LOTE 03")

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
        self.volume_input.setSuffix(" m³")

        self.unit_weight_input = QDoubleSpinBox()
        self.unit_weight_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.unit_weight_input.setRange(0.1, 5.0)
        self.unit_weight_input.setDecimals(3)
        self.unit_weight_input.setValue(2.5)
        self.unit_weight_input.setSuffix(" tf/m³")

        self.strand_input = QComboBox()
        for strand_key in STRAND_SPECS:
            self.strand_input.addItem(strand_key)
        idx = self.strand_input.findText("CP 190-RB 12,7 mm")
        if idx >= 0:
            self.strand_input.setCurrentIndex(idx)

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
        self.bond_input.addItem("Boa aderência", BondCondition.GOOD.value)
        self.bond_input.addItem("Má aderência", BondCondition.POOR.value)

        self.anchorage_type_input = QComboBox()
        for anc_type, label in ANCHORAGE_TYPE_LABELS.items():
            self.anchorage_type_input.addItem(label, anc_type.value)
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

        # --- Formulário único com separadores visuais leves ---
        form = QFormLayout()
        form.setSpacing(7)
        form.setContentsMargins(0, 0, 0, 0)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # Define largura mínima para todos os campos de entrada
        for widget in (
            self.piece_id_input,
            self.fckj_input, self.fck_28_input,
            self.volume_input, self.unit_weight_input,
            self.strand_input, self.inclination_input, self.loops_input,
            self.anchorage_input, self.anchorage_type_input, self.bond_input,
            self.beta_a_input, self.gamma_n_input,
        ):
            widget.setMinimumWidth(120)

        form.addRow("Identificação:", self.piece_id_input)
        form.addRow(self._form_separator())
        form.addRow("Fck,j (içamento):", self.fckj_input)
        form.addRow("Fck,28 (28 dias):", self.fck_28_input)
        form.addRow(self._form_separator())
        form.addRow("Volume da peça:", self.volume_input)
        form.addRow("Peso específico:", self.unit_weight_input)
        form.addRow(self._form_separator())
        form.addRow("Cordoalha:", self.strand_input)
        form.addRow("Inclinação da alça:", self.inclination_input)
        form.addRow("Número de alças:", self.loops_input)
        form.addRow(self._form_separator())
        form.addRow("Comprimento de ancoragem:", self.anchorage_input)
        form.addRow("Tipo de ancoragem:", self.anchorage_type_input)
        form.addRow("Condição de aderência:", self.bond_input)
        form.addRow(self._form_separator())
        form.addRow("βa (ampl. dinâmica):", self.beta_a_input)
        form.addRow("γn (majoração):", self.gamma_n_input)

        outer.addLayout(form)

        calculate_button = QPushButton("Calcular Verificação")
        calculate_button.setCursor(Qt.PointingHandCursor)
        calculate_button.clicked.connect(lambda: self._on_calculate(show_errors=True))

        # Scroll area para o formulário (permite acessar todos os campos em janelas menores)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 4, 0)
        form_layout.setSpacing(0)
        form_layout.addLayout(form)
        form_layout.addStretch(1)
        scroll.setWidget(form_container)

        outer.addWidget(scroll, 1)
        outer.addWidget(calculate_button)
        return group

    def _build_result_panel(self) -> QGroupBox:
        group = QGroupBox("Resultado da Verificação")
        outer_layout = QVBoxLayout(group)
        outer_layout.setSpacing(8)
        outer_layout.setContentsMargins(8, 16, 8, 8)

        # --- Banner de status ---
        self.status_label = QLabel("Preencha os dados e clique em 'Calcular Verificação'.")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(38)
        self.status_label.setStyleSheet(
            "background: #eef0f2; padding: 8px 10px; border: 1px solid #d2d6dc;"
            " border-radius: 4px; font-weight: 700; font-size: 11pt;"
        )
        outer_layout.addWidget(self.status_label)

        # --- Barras de Resumo ---
        bars_group = QGroupBox("Resumo Visual")
        bars_layout = QFormLayout(bars_group)
        bars_layout.setSpacing(6)
        self.utilization_bar = self._indicator_bar()
        self.safety_factor_bar = self._indicator_bar()
        bars_layout.addRow("Utilização:", self.utilization_bar)
        bars_layout.addRow("Fator de segurança:", self.safety_factor_bar)
        outer_layout.addWidget(bars_group)

        # --- Indicadores essenciais (sem scroll, fixo) ---
        self.result_fields: dict[str, QLineEdit] = {}

        indicators_group = QGroupBox("Indicadores")
        ind_form = QFormLayout(indicators_group)
        ind_form.setSpacing(5)
        for key, label in (
            ("utilization", "Taxa de utilização"),
            ("safety_factor", "Fator de segurança (FS)"),
            ("piece_weight_tf", "Massa da peça (tf)"),
            ("majorated_weight_tf", "Massa majorada (tf)"),
            ("tension_per_loop_tf", "Carga por alça (tf)"),
            ("required_anchorage_cm", "Anc. necessária (cm)"),
            ("available_anchorage_cm", "Anc. disponível (cm)"),
        ):
            field = self._result_field()
            self.result_fields[key] = field
            ind_form.addRow(label + ":", field)
        outer_layout.addWidget(indicators_group)

        # --- Campos adicionais ocultos (populados mas não exibidos aqui) ---
        for key in (
            "stress_developed", "stress_mobilization",
            "tension_per_leg_tf", "total_legs",
            "ecj_mpa", "fctm_j_mpa", "fctm_28_mpa",
            "fpyd_mpa", "fbpd_j_mpa", "fbpd_28_mpa",
            "max_load_steel_tf", "max_load_bond_tf", "max_load_tf",
            "governing_criterion", "base_anchorage_cm",
        ):
            field = self._result_field()
            self.result_fields[key] = field
            # Não adiciona ao layout — apenas populado para a memória

        memory_hint = QLabel("<a href='#'>Memória completa na aba 'Memória de Cálculo'.</a>")
        memory_hint.setAlignment(Qt.AlignCenter)
        memory_hint.setStyleSheet("font-size: 9pt; color: #334155;")
        memory_hint.setOpenExternalLinks(False)
        memory_hint.linkActivated.connect(lambda: self.tabs.setCurrentIndex(1))
        outer_layout.addWidget(memory_hint)
        outer_layout.addStretch(1)

        return group

    def _build_memory_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)
        layout.setContentsMargins(6, 6, 6, 6)

        toolbar = QHBoxLayout()
        copy_button = QPushButton("Copiar Memória")
        copy_button.setCursor(Qt.PointingHandCursor)
        copy_button.clicked.connect(self._copy_memory)
        toolbar.addWidget(copy_button)
        toolbar.addStretch(1)

        self.memory_text = QTextEdit()
        self.memory_text.setReadOnly(True)
        self.memory_text.setPlaceholderText("Calcule na aba 'Verificação' para gerar a memória.")

        layout.addLayout(toolbar)
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

    @staticmethod
    def _indicator_bar() -> QProgressBar:
        bar = QProgressBar()
        bar.setRange(0, 250)
        bar.setValue(0)
        bar.setTextVisible(True)
        bar.setFormat("-")
        bar.setMinimumHeight(20)
        bar.setStyleSheet(
            "QProgressBar { border: 1px solid #cbd5e1; border-radius: 6px; text-align: center; background: #f8fafc; }"
            "QProgressBar::chunk { background-color: #2563eb; border-radius: 5px; }"
        )
        return bar

    def _build_menu_bar(self) -> None:
        menu = self.menuBar()

        file_menu = menu.addMenu("&Arquivo")
        export_memory_action = QAction("Exportar Memória (.txt)...", self)
        export_memory_action.setShortcut(QKeySequence("Ctrl+S"))
        export_memory_action.triggered.connect(self._export_memory)
        file_menu.addAction(export_memory_action)

        tools_menu = menu.addMenu("&Ferramentas")
        restore_defaults_action = QAction("Restaurar Padrões", self)
        restore_defaults_action.setShortcut(QKeySequence("Ctrl+R"))
        restore_defaults_action.triggered.connect(self._restore_defaults)
        tools_menu.addAction(restore_defaults_action)

        help_menu = menu.addMenu("A&juda")
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    @staticmethod
    def _form_separator() -> QFrame:
        """Returns a thin horizontal line used as a visual section divider in the form."""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #e2e8f0; margin: 2px 0;")
        return line

    def _configure_input_metadata(self) -> None:
        self.piece_id_input.setToolTip(
            "Identificação opcional da peça para rastreabilidade da memória de cálculo."
        )
        self.fckj_input.setToolTip(
            "Resistência característica do concreto na idade do içamento (MPa). "
            "Valor típico: 15 a 25 MPa."
        )
        self.fck_28_input.setToolTip(
            "Resistência característica aos 28 dias (MPa). Deve ser maior ou igual a Fck,j."
        )
        self.volume_input.setToolTip("Volume da peça de concreto em metros cúbicos.")
        self.unit_weight_input.setToolTip("Peso específico do concreto em tf/m3.")
        self.strand_input.setToolTip("Tipo de cordoalha de protensão utilizado no içamento.")
        self.inclination_input.setToolTip("Inclinação da alça em relação ao plano horizontal.")
        self.anchorage_input.setToolTip("Comprimento de ancoragem disponível em centímetros.")
        self.anchorage_type_input.setToolTip("Tratamento da ponta da alça para redução da ancoragem.")
        self.bond_input.setToolTip("Condição de aderência entre aço e concreto.")
        self.loops_input.setToolTip("Número total de alças de içamento.")
        self.beta_a_input.setToolTip(
            "Coeficiente de amplificação dinâmica. Padrão: 3,00."
        )
        self.gamma_n_input.setToolTip(
            "Coeficiente de majoração adicional. Padrão: 1,30."
        )

        self.piece_id_input.setAccessibleName("Identificação da peça")
        self.fckj_input.setAccessibleName("Fck na idade de içamento em MPa")
        self.fck_28_input.setAccessibleName("Fck aos 28 dias em MPa")
        self.volume_input.setAccessibleName("Volume da peça em metros cúbicos")
        self.unit_weight_input.setAccessibleName("Peso específico do concreto em tf por metro cúbico")
        self.strand_input.setAccessibleName("Tipo de cordoalha")
        self.inclination_input.setAccessibleName("Inclinação da alça em graus")
        self.anchorage_input.setAccessibleName("Comprimento de ancoragem disponível em centímetros")
        self.anchorage_type_input.setAccessibleName("Tipo de ancoragem")
        self.bond_input.setAccessibleName("Condição de aderência")
        self.loops_input.setAccessibleName("Número de alças")
        self.beta_a_input.setAccessibleName("Coeficiente beta a")
        self.gamma_n_input.setAccessibleName("Coeficiente gama n")

    def _connect_auto_calculate(self) -> None:
        for spinbox in (
            self.fckj_input,
            self.fck_28_input,
            self.volume_input,
            self.unit_weight_input,
            self.inclination_input,
            self.anchorage_input,
            self.beta_a_input,
            self.gamma_n_input,
        ):
            spinbox.valueChanged.connect(self._on_auto_calculate)

        self.loops_input.valueChanged.connect(self._on_auto_calculate)
        self.piece_id_input.textChanged.connect(self._on_auto_calculate)
        self.strand_input.currentIndexChanged.connect(self._on_auto_calculate)
        self.bond_input.currentIndexChanged.connect(self._on_auto_calculate)
        self.anchorage_type_input.currentIndexChanged.connect(self._on_auto_calculate)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("F5"), self, lambda: self._on_calculate(show_errors=True))
        QShortcut(QKeySequence("Ctrl+Enter"), self, lambda: self._on_calculate(show_errors=True))
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.tabs.setCurrentIndex(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.tabs.setCurrentIndex(1))

    def _set_tab_order(self) -> None:
        QWidget.setTabOrder(self.piece_id_input, self.fckj_input)
        QWidget.setTabOrder(self.fckj_input, self.fck_28_input)
        QWidget.setTabOrder(self.fck_28_input, self.volume_input)
        QWidget.setTabOrder(self.volume_input, self.unit_weight_input)
        QWidget.setTabOrder(self.unit_weight_input, self.strand_input)
        QWidget.setTabOrder(self.strand_input, self.inclination_input)
        QWidget.setTabOrder(self.inclination_input, self.loops_input)
        QWidget.setTabOrder(self.loops_input, self.anchorage_input)
        QWidget.setTabOrder(self.anchorage_input, self.anchorage_type_input)
        QWidget.setTabOrder(self.anchorage_type_input, self.bond_input)
        QWidget.setTabOrder(self.bond_input, self.beta_a_input)
        QWidget.setTabOrder(self.beta_a_input, self.gamma_n_input)

    def _on_auto_calculate(self, *_: object) -> None:
        self._validate_fck_relationship()
        self._on_calculate(show_errors=False)

    def _on_calculate(self, show_errors: bool = True) -> None:
        self._validate_fck_relationship()
        try:
            data = self._read_input()
            result = self._service.calculate(data)
            memory_text = self._service.build_calculation_memory(data, result)
        except ValidationError as exc:
            self.statusBar().showMessage(f"Erro de validação: {exc}", 6000)
            if show_errors:
                QMessageBox.warning(self, APP_NAME, str(exc))
            return

        is_approved = result.capacity_is_ok and result.anchorage_is_ok
        if is_approved:
            self.status_label.setText("VERIFICAÇÃO APROVADA")
            self.status_label.setStyleSheet(
                "background: #ecfdf3; color: #166534; padding: 8px 10px;"
                " border: 1px solid #bbf7d0; border-radius: 4px;"
                " font-weight: 700; font-size: 11pt;"
            )
            self.statusBar().showMessage(
                f"Aprovada | FS = {result.safety_factor:.2f} | Utilização = {result.utilization_ratio:.1%}"
            )
        else:
            failures = []
            suggestions = []
            
            if not result.capacity_is_ok:
                failures.append("Capacidade estrutural insuficiente")
                suggestions.append("aumente alças ou diâmetro da cordoalha")
            if not result.anchorage_is_ok:
                failures.append(f"Ancoragem insuficiente (disp. {data.available_anchorage_cm:.1f}cm < nec. {result.required_anchorage_cm:.1f}cm)")
                suggestions.append("aumente a altura da peça ou use ganchos")
                
            text = f"VERIFICAÇÃO REPROVADA: {', '.join(failures)}."
            if suggestions:
                text += f"\n💡 Sugestão: {', '.join(set(suggestions))}."
                
            self.status_label.setText(text)
            self.status_label.setStyleSheet(
                "background: #fef2f2; color: #991b1b; padding: 8px 10px;"
                " border: 1px solid #fecaca; border-radius: 4px;"
                " font-weight: 700; font-size: 11pt;"
            )
            self.statusBar().showMessage("Reprovada | " + ", ".join(failures), 9000)

        self._update_result_fields(result, data.available_anchorage_cm)
        self._update_indicator_bars(result)
        self.memory_text.setPlainText(memory_text)
        self.sketch_widget.update_sketch(
            loops_count=data.loops_count,
            anchorage_type=data.anchorage_type,
            inclination_deg=data.inclination_deg,
            anchorage_is_ok=result.anchorage_is_ok,
            capacity_is_ok=result.capacity_is_ok,
            required_anchorage_cm=result.required_anchorage_cm,
            available_anchorage_cm=data.available_anchorage_cm,
        )
        self._validate_anchorage_field(result, data.available_anchorage_cm)

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
            piece_id=self.piece_id_input.text().strip(),
        )

    def _update_result_fields(
        self,
        result: LiftingResult,
        available_anchorage_cm: float,
    ) -> None:
        if result.max_supported_load_by_steel_tf <= result.max_supported_load_by_bond_tf:
            governing = "Aço"
        else:
            governing = "Aderência"

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

    def _update_indicator_bars(self, result: LiftingResult) -> None:
        utilization_percent = int(max(0.0, min(250.0, result.utilization_ratio * 100.0)))
        safety_percent = int(max(0.0, min(250.0, result.safety_factor * 100.0)))

        self.utilization_bar.setValue(utilization_percent)
        self.utilization_bar.setFormat(f"{result.utilization_ratio:.1%}")
        self._set_bar_style(self.utilization_bar, ok=result.utilization_ratio <= 1.0)

        self.safety_factor_bar.setValue(safety_percent)
        self.safety_factor_bar.setFormat(f"{result.safety_factor:.2f}")
        self._set_bar_style(self.safety_factor_bar, ok=result.safety_factor >= 1.0)

    @staticmethod
    def _set_bar_style(bar: QProgressBar, ok: bool) -> None:
        color = "#166534" if ok else "#dc2626"
        bar.setStyleSheet(
            "QProgressBar { border: 1px solid #cbd5e1; border-radius: 6px; text-align: center; background: #f8fafc; }"
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 5px; }}"
        )

    def _validate_anchorage_field(self, result: LiftingResult, available_anchorage_cm: float) -> None:
        is_invalid = available_anchorage_cm < result.required_anchorage_cm
        self.anchorage_input.setProperty("invalid", is_invalid)
        self.anchorage_input.style().unpolish(self.anchorage_input)
        self.anchorage_input.style().polish(self.anchorage_input)

        if is_invalid:
            self.anchorage_input.setToolTip(
                f"Ancoragem insuficiente. Necessário >= {result.required_anchorage_cm:.2f} cm."
            )
        else:
            self.anchorage_input.setToolTip("Comprimento de ancoragem disponível em centímetros.")

    def _restore_defaults(self) -> None:
        self.piece_id_input.clear()
        self.fckj_input.setValue(15.0)
        self.fck_28_input.setValue(40.0)
        self.volume_input.setValue(1.0)
        self.unit_weight_input.setValue(2.5)
        self.inclination_input.setValue(90.0)
        self.anchorage_input.setValue(60.0)
        self.loops_input.setValue(2)
        self.beta_a_input.setValue(3.0)
        self.gamma_n_input.setValue(1.30)

        strand_index = self.strand_input.findText("CP 190-RB 12,7 mm")
        if strand_index >= 0:
            self.strand_input.setCurrentIndex(strand_index)

        bond_index = self.bond_input.findData(BondCondition.GOOD.value)
        if bond_index >= 0:
            self.bond_input.setCurrentIndex(bond_index)

        anchorage_type_index = self.anchorage_type_input.findData(AnchorageType.HOOK_90.value)
        if anchorage_type_index >= 0:
            self.anchorage_type_input.setCurrentIndex(anchorage_type_index)

        self._on_calculate(show_errors=False)
        self.statusBar().showMessage("Parâmetros restaurados para os valores padrão.", 4000)

    def _export_memory(self) -> None:
        text = self.memory_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, APP_NAME, "Não há memória de cálculo para exportar.")
            return

        suggested_name = "memoria_calculo.txt"
        if self.piece_id_input.text().strip():
            safe_piece = "".join(
                char if char.isalnum() or char in ("-", "_") else "_"
                for char in self.piece_id_input.text().strip()
            )
            suggested_name = f"memoria_{safe_piece}.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Memória de Cálculo",
            str(Path.home() / suggested_name),
            "Arquivo de texto (*.txt);;Todos os arquivos (*.*)",
        )
        if not file_path:
            return

        try:
            Path(file_path).write_text(text, encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(self, APP_NAME, f"Falha ao exportar memória: {exc}")
            return

        self.statusBar().showMessage(f"Memória exportada em: {file_path}", 5000)

    def _show_about_dialog(self) -> None:
        QMessageBox.information(
            self,
            "Sobre",
            "Verificador de Içamento - NBR 9062\\n"
            "Ferramenta para verificação de içamento com cordoalhas.",
        )

    def _validate_fck_relationship(self) -> None:
        is_invalid = self.fck_28_input.value() < self.fckj_input.value()
        self.fck_28_input.setProperty("invalid", is_invalid)
        self.fck_28_input.style().unpolish(self.fck_28_input)
        self.fck_28_input.style().polish(self.fck_28_input)
        if is_invalid:
            self.fck_28_input.setToolTip(
                "Fck,28 deve ser maior ou igual a Fck,j."
            )
        else:
            self.fck_28_input.setToolTip(
                "Resistência característica aos 28 dias (MPa). Deve ser maior ou igual a Fck,j."
            )

    def _copy_memory(self) -> None:
        text = self.memory_text.toPlainText()
        if not text.strip():
            self.statusBar().showMessage("Nenhuma memória disponível para copiar.", 4000)
            return
        QApplication.clipboard().setText(text)
        self.statusBar().showMessage("Memória copiada para a área de transferência.", 4000)
