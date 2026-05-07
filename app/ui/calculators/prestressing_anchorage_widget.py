"""Widget for bonded prestressing anchorage verification."""

from __future__ import annotations


from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.exceptions import ValidationError
from app.core.prestressing_anchorage_models import (
    PRESTRESSING_STEEL_SPECS,
    PrestressingAnchorageInput,
    PrestressingAnchorageResult,
    PrestressingBondCondition,
)
from app.core.prestressing_anchorage_services import PrestressingAnchorageService


class PrestressingAnchorageWidget(QWidget):
    """Calculator for bonded prestressing anchorage with detailed memory."""

    status_message_requested = Signal(str, int)

    def __init__(self) -> None:
        super().__init__()
        self._service = PrestressingAnchorageService()
        self._build_ui()
        self._connect_auto_calculate()
        self._recalculate()

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setSpacing(8)
        root_layout.setContentsMargins(6, 6, 6, 6)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_verification_tab(), "Verificação")
        self.tabs.addTab(self._build_memory_tab(), "Memória de cálculo")
        root_layout.addWidget(self.tabs)

    def _build_verification_tab(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.addWidget(self._build_input_group(), 0)
        layout.addWidget(self._build_result_panel(), 1)
        return tab

    def _build_input_group(self) -> QWidget:
        panel = QWidget()
        outer = QVBoxLayout(panel)
        outer.setSpacing(6)
        outer.setContentsMargins(0, 0, 0, 0)

        self.steel_input = QComboBox()
        for key, spec in PRESTRESSING_STEEL_SPECS.items():
            self.steel_input.addItem(spec.label, key)
        default_index = self.steel_input.findData("STRAND_CP190_RB_12_7")
        if default_index >= 0:
            self.steel_input.setCurrentIndex(default_index)

        self.fck_input = QDoubleSpinBox()
        self.fck_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.fck_input.setRange(5.0, 120.0)
        self.fck_input.setDecimals(2)
        self.fck_input.setValue(30.0)
        self.fck_input.setSuffix(" MPa")

        self.stress_input = QDoubleSpinBox()
        self.stress_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.stress_input.setRange(1.0, 2500.0)
        self.stress_input.setDecimals(2)
        self.stress_input.setValue(1000.0)
        self.stress_input.setSuffix(" MPa")

        self.available_anchorage_input = QDoubleSpinBox()
        self.available_anchorage_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.available_anchorage_input.setRange(1.0, 1000.0)
        self.available_anchorage_input.setDecimals(2)
        self.available_anchorage_input.setValue(80.0)
        self.available_anchorage_input.setSuffix(" cm")

        self.bond_input = QComboBox()
        self.bond_input.addItem(PrestressingBondCondition.GOOD.value, PrestressingBondCondition.GOOD)
        self.bond_input.addItem(PrestressingBondCondition.POOR.value, PrestressingBondCondition.POOR)

        for widget in (
            self.steel_input,
            self.fck_input,
            self.stress_input,
            self.available_anchorage_input,
            self.bond_input,
        ):
            widget.setFixedWidth(170)

        data_group, data_form = self._new_form_group("Dados")
        data_form.addRow("Produto", self.steel_input)
        data_form.addRow("Fck", self.fck_input)
        data_form.addRow("Tensão no aço", self.stress_input)
        data_form.addRow("Ldisp", self.available_anchorage_input)
        data_form.addRow("Aderência", self.bond_input)

        note = QLabel(
            "Memória detalhada na aba ao lado. A tensão informada deve ser definida pelo engenheiro "
            "para a etapa de verificação desejada."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #444444; font-size: 8pt;")

        outer.addWidget(data_group)
        outer.addWidget(note)
        outer.addStretch(1)
        return panel

    def _build_result_panel(self) -> QGroupBox:
        group = QGroupBox("Resultados")
        outer = QVBoxLayout(group)
        outer.setSpacing(6)
        outer.setContentsMargins(8, 14, 8, 8)

        self.status_label = QLabel("Aguardando cálculo")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(28)
        self.status_label.setStyleSheet(
            "background: #efefef; color: #222222; padding: 5px 8px;"
            "border: 1px solid #d6d6d6; font-weight: 700;"
        )
        outer.addWidget(self.status_label)

        self.result_fields: dict[str, QLineEdit] = {}
        form = QFormLayout()
        form.setSpacing(5)
        form.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        for key, label in (
            ("fbpd_mpa", "fbpd (MPa)"),
            ("steel_force_kn", "Fp,d (kN)"),
            ("required_anchorage_cm", "Lnec (cm)"),
            ("available_anchorage_cm", "Ldisp (cm)"),
            ("deficit_cm", "Déficit (cm)"),
        ):
            field = self._result_field()
            self.result_fields[key] = field
            form.addRow(label + ":", field)
        outer.addLayout(form)

        memory_hint = QLabel("<a href='#'>Memória detalhada</a>")
        memory_hint.setAlignment(Qt.AlignCenter)
        memory_hint.setOpenExternalLinks(False)
        memory_hint.linkActivated.connect(lambda: self.tabs.setCurrentIndex(1))
        outer.addWidget(memory_hint)
        outer.addStretch(1)
        return group

    def _build_memory_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)
        layout.setContentsMargins(6, 6, 6, 6)

        toolbar = QHBoxLayout()
        copy_button = QPushButton("Copiar Memória")
        copy_button.clicked.connect(self._copy_memory)
        toolbar.addWidget(copy_button)
        toolbar.addStretch(1)

        self.memory_text = QTextEdit()
        self.memory_text.setReadOnly(True)
        self.memory_text.setPlaceholderText("A memória será atualizada automaticamente.")

        layout.addLayout(toolbar)
        layout.addWidget(self.memory_text)
        return tab

    @staticmethod
    def _new_form_group(title: str) -> tuple[QGroupBox, QFormLayout]:
        group = QGroupBox(title)
        form = QFormLayout(group)
        form.setSpacing(5)
        form.setContentsMargins(8, 14, 8, 8)
        form.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        return group, form

    @staticmethod
    def _result_field() -> QLineEdit:
        field = QLineEdit()
        field.setReadOnly(True)
        field.setFocusPolicy(Qt.NoFocus)
        field.setAlignment(Qt.AlignRight)
        field.setFixedWidth(120)
        field.setStyleSheet(
            "QLineEdit { background-color: #efefef; border: 1px solid #d6d6d6;"
            " color: #111111; font-weight: 600; }"
        )
        return field

    def _connect_auto_calculate(self) -> None:
        self.steel_input.currentIndexChanged.connect(self._on_auto_calculate)
        self.bond_input.currentIndexChanged.connect(self._on_auto_calculate)
        for spinbox in (
            self.fck_input,
            self.stress_input,
            self.available_anchorage_input,
        ):
            spinbox.valueChanged.connect(self._on_auto_calculate)

    def _on_auto_calculate(self, *_: object) -> None:
        self._recalculate()

    def _recalculate(self) -> None:
        try:
            data = self._read_input()
            result = self._service.calculate(data)
            memory = self._service.build_calculation_memory(data, result)
        except ValidationError as exc:
            self._show_validation_error(exc)
            return

        if result.anchorage_is_ok:
            self.status_label.setText("VERIFICAÇÃO APROVADA")
            self.status_label.setStyleSheet(
                "background: #e8f5e9; color: #0b6b2b; padding: 5px 8px;"
                "border: 1px solid #b7dfc0; font-weight: 700;"
            )
            self._show_status("Protensão aderente aprovada.")
        else:
            self.status_label.setText("VERIFICAÇÃO REPROVADA")
            self.status_label.setStyleSheet(
                "background: #fdecec; color: #9b1c1c; padding: 5px 8px;"
                "border: 1px solid #f0b8b8; font-weight: 700;"
            )
            self._show_status(f"Protensão reprovada | Déficit = {result.deficit_cm:.2f} cm", 9000)

        self._update_result_fields(result)
        self.memory_text.setPlainText(memory)

    def _read_input(self) -> PrestressingAnchorageInput:
        return PrestressingAnchorageInput(
            steel_key=str(self.steel_input.currentData()),
            fck_mpa=self.fck_input.value(),
            steel_stress_mpa=self.stress_input.value(),
            available_anchorage_cm=self.available_anchorage_input.value(),
            bond_condition=PrestressingBondCondition(self.bond_input.currentData()),
        )

    def _update_result_fields(self, result: PrestressingAnchorageResult) -> None:
        values = {
            "fbpd_mpa": f"{result.fbpd_mpa:.3f}",
            "steel_force_kn": f"{result.steel_force_kn:.3f}",
            "required_anchorage_cm": f"{result.required_anchorage_cm:.2f}",
            "available_anchorage_cm": f"{result.available_anchorage_cm:.2f}",
            "deficit_cm": f"{result.deficit_cm:.2f}",
        }
        for key, value in values.items():
            self.result_fields[key].setText(value)

        color = "#0b6b2b" if result.anchorage_is_ok else "#c62828"
        self.result_fields["required_anchorage_cm"].setStyleSheet(
            "QLineEdit { background-color: #efefef; border: 1px solid #d6d6d6;"
            f" color: {color}; font-weight: 700; }}"
        )
        self.result_fields["deficit_cm"].setStyleSheet(
            "QLineEdit { background-color: #efefef; border: 1px solid #d6d6d6;"
            f" color: {color}; font-weight: 700; }}"
        )

    def _show_validation_error(self, error: ValidationError) -> None:
        self.status_label.setText("ENTRADA INVÁLIDA")
        self.status_label.setStyleSheet(
            "background: #fff7ed; color: #9a3412; padding: 5px 8px;"
            "border: 1px solid #fed7aa; font-weight: 700;"
        )
        self._show_status(f"Ajuste os dados de protensão: {error}", 9000)
        self.memory_text.setPlainText(
            "ENTRADA INVÁLIDA\n\n"
            f"{error}\n\n"
            "A memória será atualizada automaticamente após a correção."
        )
        for field in self.result_fields.values():
            field.clear()

    def _show_status(self, message: str, timeout_ms: int = 0) -> None:
        self.status_message_requested.emit(message, timeout_ms)

    def _copy_memory(self) -> None:
        text = self.memory_text.toPlainText()
        if not text.strip():
            self._show_status("Nenhuma memória de protensão disponível para copiar.", 4000)
            return
        QApplication.clipboard().setText(text)
        self._show_status("Memória de protensão copiada.", 4000)

