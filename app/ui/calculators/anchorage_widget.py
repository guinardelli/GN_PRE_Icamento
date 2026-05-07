"""Anchorage calculator widget."""

from __future__ import annotations


from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
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
from app.core.anchorage_models import (
    AnchorageInput,
    AnchorageResult,
    AnchorageType,
    BondCondition,
    COMMERCIAL_REBAR_DIAMETERS,
    EffortType,
    SteelType,
)
from app.core.anchorage_services import AnchorageVerifierService
from app.ui.anchorage_sketch_widget import AnchorageSketchWidget
from app.ui.calculators.lap_splice_widget import LapSpliceWidget
from app.ui.calculators.prestressing_anchorage_widget import (
    PrestressingAnchorageWidget,
)


class AnchorageCalculatorWidget(QWidget):
    """Calculator for anchorage length of passive rebars."""

    status_message_requested = Signal(str, int)

    def __init__(self) -> None:
        super().__init__()
        self._service = AnchorageVerifierService()
        self._shortcuts: list[QShortcut] = []
        self._build_ui()
        self._connect_auto_calculate()
        self._setup_shortcuts()
        self._recalculate()

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setSpacing(10)
        root_layout.setContentsMargins(12, 12, 12, 12)

        self.family_tabs = QTabWidget()
        self.passive_tabs = QTabWidget()
        self.passive_tabs.addTab(self._build_verification_tab(), "Verificação")
        self.passive_tabs.addTab(self._build_memory_tab(), "Memória de cálculo")
        self.family_tabs.addTab(self.passive_tabs, "Armadura passiva")

        self.lap_splice_widget = LapSpliceWidget()
        self.lap_splice_widget.status_message_requested.connect(self._show_status)
        self.family_tabs.addTab(self.lap_splice_widget, "Emenda por transpasse")

        self.prestressing_widget = PrestressingAnchorageWidget()
        self.prestressing_widget.status_message_requested.connect(self._show_status)
        self.family_tabs.addTab(self.prestressing_widget, "Cordoalhas/Fios")

        root_layout.addWidget(self.family_tabs)
        self._show_status("Pronto.")

    def _show_status(self, message: str, timeout_ms: int = 0) -> None:
        self.status_message_requested.emit(message, timeout_ms)

    def _build_verification_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 8, 0, 0)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)
        top_row.addWidget(self._build_input_group(), 0)

        right_column = QVBoxLayout()
        right_column.setSpacing(8)
        right_column.addWidget(self._build_result_panel(), 0)

        sketch_group = QGroupBox("Representação Gráfica")
        sketch_layout = QVBoxLayout(sketch_group)
        sketch_layout.setContentsMargins(6, 12, 6, 6)
        self.sketch_widget = AnchorageSketchWidget()
        self.sketch_widget.setMinimumHeight(210)
        sketch_layout.addWidget(self.sketch_widget)
        right_column.addWidget(sketch_group, 1)

        top_row.addLayout(right_column, 1)
        layout.addLayout(top_row, 1)

        return tab

    def _build_input_group(self) -> QWidget:
        panel = QWidget()
        outer = QVBoxLayout(panel)
        outer.setSpacing(6)
        outer.setContentsMargins(0, 0, 0, 0)

        self.diameter_input = QComboBox()
        for diameter in COMMERCIAL_REBAR_DIAMETERS:
            self.diameter_input.addItem(diameter.label, diameter.diameter_mm)
        default_diameter_index = self.diameter_input.findData(10.0)
        if default_diameter_index >= 0:
            self.diameter_input.setCurrentIndex(default_diameter_index)

        self.fck_input = QDoubleSpinBox()
        self.fck_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.fck_input.setRange(5.0, 120.0)
        self.fck_input.setDecimals(2)
        self.fck_input.setValue(30.0)
        self.fck_input.setSuffix(" MPa")

        self.steel_type_input = QComboBox()
        self.steel_type_input.addItem(SteelType.CA25.value, SteelType.CA25)
        self.steel_type_input.addItem(SteelType.CA50.value, SteelType.CA50)
        self.steel_type_input.addItem(SteelType.CA60.value, SteelType.CA60)
        default_steel_index = self.steel_type_input.findData(SteelType.CA50.value)
        if default_steel_index >= 0:
            self.steel_type_input.setCurrentIndex(default_steel_index)

        self.bond_input = QComboBox()
        self.bond_input.addItem(BondCondition.GOOD.value, BondCondition.GOOD)
        self.bond_input.addItem(BondCondition.POOR.value, BondCondition.POOR)

        self.effort_type_input = QComboBox()
        self.effort_type_input.addItem(EffortType.TENSION.value, EffortType.TENSION)
        self.effort_type_input.addItem(EffortType.COMPRESSION.value, EffortType.COMPRESSION)

        self.anchorage_type_input = QComboBox()
        self._populate_anchorage_types(EffortType.TENSION)

        self.as_calc_input = QDoubleSpinBox()
        self.as_calc_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.as_calc_input.setRange(0.01, 100.0)
        self.as_calc_input.setDecimals(2)
        self.as_calc_input.setValue(1.0)
        self.as_calc_input.setSuffix(" cm²")

        self.as_ef_input = QDoubleSpinBox()
        self.as_ef_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.as_ef_input.setRange(0.01, 100.0)
        self.as_ef_input.setDecimals(2)
        self.as_ef_input.setValue(1.0)
        self.as_ef_input.setSuffix(" cm²")

        self.available_anchorage_input = QDoubleSpinBox()
        self.available_anchorage_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.available_anchorage_input.setRange(1.0, 500.0)
        self.available_anchorage_input.setDecimals(2)
        self.available_anchorage_input.setValue(50.0)
        self.available_anchorage_input.setSuffix(" cm")

        for widget in (
            self.diameter_input,
            self.fck_input,
            self.steel_type_input,
            self.bond_input,
            self.effort_type_input,
            self.anchorage_type_input,
            self.as_calc_input,
            self.as_ef_input,
            self.available_anchorage_input,
        ):
            widget.setFixedWidth(142)

        prop_group, prop_form = self._new_form_group("Propriedades")
        prop_form.addRow("Bitola", self.diameter_input)
        prop_form.addRow("Fck", self.fck_input)
        prop_form.addRow("Aço", self.steel_type_input)

        cond_group, cond_form = self._new_form_group("Condições")
        cond_form.addRow("Aderência", self.bond_input)
        cond_form.addRow("Solicitação", self.effort_type_input)
        cond_form.addRow("Ancoragem", self.anchorage_type_input)
        self.anchorage_rule_hint = QLabel(
            "Ganchos não são considerados para barras comprimidas."
        )
        self.anchorage_rule_hint.setWordWrap(True)
        self.anchorage_rule_hint.setStyleSheet("color: #9a3412; font-size: 8pt;")
        self.anchorage_rule_hint.setVisible(False)
        cond_form.addRow("", self.anchorage_rule_hint)

        arm_group, arm_form = self._new_form_group("Armadura e Espaço")
        arm_form.addRow("As,calc", self.as_calc_input)
        arm_form.addRow("As,ef", self.as_ef_input)
        arm_form.addRow("Comp. Disp.", self.available_anchorage_input)

        outer.addWidget(prop_group)
        outer.addWidget(cond_group)
        outer.addWidget(arm_group)
        outer.addStretch(1)
        return panel

    def _build_result_panel(self) -> QGroupBox:
        group = QGroupBox("Resultados")
        outer_layout = QVBoxLayout(group)
        outer_layout.setSpacing(6)
        outer_layout.setContentsMargins(8, 14, 8, 8)

        self.status_label = QLabel("Aguardando cálculo")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(28)
        self.status_label.setStyleSheet(
            "background: #efefef; color: #222222; padding: 5px 8px;"
            "border: 1px solid #d6d6d6; font-weight: 700;"
        )
        outer_layout.addWidget(self.status_label)

        self.result_fields: dict[str, QLineEdit] = {}
        ind_form = QFormLayout()
        ind_form.setSpacing(5)
        ind_form.setContentsMargins(0, 0, 0, 0)
        ind_form.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        for key, label in (
            ("fbd_mpa", "Tensão aderência fbd (MPa)"),
            ("lb_cm", "C. básico lb (cm)"),
            ("lb_min_cm", "C. mínimo lb,min (cm)"),
            ("lb_nec_cm", "C. necessário lb,nec (cm)"),
            ("required_as_ef_cm2", "As,ef necessária (cm²)"),
        ):
            field = self._result_field()
            self.result_fields[key] = field
            ind_form.addRow(label + ":", field)
        outer_layout.addLayout(ind_form)

        memory_hint = QLabel("<a href='#'>Memória completa</a>")
        memory_hint.setAlignment(Qt.AlignCenter)
        memory_hint.setStyleSheet("font-size: 9pt;")
        memory_hint.setOpenExternalLinks(False)
        memory_hint.linkActivated.connect(lambda: self.passive_tabs.setCurrentIndex(1))
        outer_layout.addWidget(memory_hint)

        return group

    @staticmethod
    def _new_form_group(title: str) -> tuple[QGroupBox, QFormLayout]:
        group = QGroupBox(title)
        form = QFormLayout(group)
        form.setSpacing(5)
        form.setContentsMargins(8, 14, 8, 8)
        form.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        return group, form

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
        self.memory_text.setPlaceholderText(
            "A memória é atualizada automaticamente com os dados de entrada."
        )

        layout.addLayout(toolbar)
        layout.addWidget(self.memory_text)
        return tab

    @staticmethod
    def _result_field() -> QLineEdit:
        field = QLineEdit()
        field.setReadOnly(True)
        field.setFocusPolicy(Qt.NoFocus)
        field.setAlignment(Qt.AlignRight)
        field.setPlaceholderText("-")
        field.setFixedWidth(112)
        field.setStyleSheet(
            "QLineEdit { background-color: #efefef; border: 1px solid #d6d6d6;"
            " color: #111111; font-weight: 600; }"
        )
        return field

    def _connect_auto_calculate(self) -> None:
        for spinbox in (
            self.fck_input,
            self.as_calc_input,
            self.as_ef_input,
            self.available_anchorage_input,
        ):
            spinbox.valueChanged.connect(self._on_auto_calculate)

        for combo in (
            self.diameter_input,
            self.steel_type_input,
            self.bond_input,
            self.effort_type_input,
            self.anchorage_type_input,
        ):
            combo.currentIndexChanged.connect(self._on_auto_calculate)

    def _setup_shortcuts(self) -> None:
        self._shortcuts = [
            QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.passive_tabs.setCurrentIndex(0)),
            QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.passive_tabs.setCurrentIndex(1)),
        ]

    def _populate_anchorage_types(self, effort_type: EffortType) -> None:
        available_types = [AnchorageType.STRAIGHT, AnchorageType.WELDED]
        if effort_type == EffortType.TENSION:
            available_types.insert(1, AnchorageType.HOOK)
            available_types.append(AnchorageType.HOOK_WELDED)

        self.anchorage_type_input.clear()
        for anchorage_type in available_types:
            self.anchorage_type_input.addItem(anchorage_type.value, anchorage_type)

    def _refresh_anchorage_options(self) -> None:
        effort_type = EffortType(self.effort_type_input.currentData())
        self.anchorage_rule_hint.setVisible(effort_type == EffortType.COMPRESSION)
        current_type = self.anchorage_type_input.currentData()
        if current_type is not None:
            current_type = AnchorageType(current_type)

        expected_types = [AnchorageType.STRAIGHT, AnchorageType.WELDED]
        if effort_type == EffortType.TENSION:
            expected_types.insert(1, AnchorageType.HOOK)
            expected_types.append(AnchorageType.HOOK_WELDED)

        current_types = [
            AnchorageType(self.anchorage_type_input.itemData(index))
            for index in range(self.anchorage_type_input.count())
        ]
        if current_types == expected_types:
            return

        self.anchorage_type_input.blockSignals(True)
        self._populate_anchorage_types(effort_type)
        if current_type in expected_types:
            next_index = self.anchorage_type_input.findData(current_type.value)
        else:
            next_index = self.anchorage_type_input.findData(AnchorageType.STRAIGHT.value)
        if next_index >= 0:
            self.anchorage_type_input.setCurrentIndex(next_index)
        self.anchorage_type_input.blockSignals(False)

    def _on_auto_calculate(self, *_: object) -> None:
        self._validate_as_relationship()
        self._refresh_anchorage_options()
        self._recalculate()

    def _validate_as_relationship(self) -> None:
        is_invalid = self.as_calc_input.value() > self.as_ef_input.value()
        self.as_calc_input.setProperty("invalid", is_invalid)
        self.as_calc_input.style().unpolish(self.as_calc_input)
        self.as_calc_input.style().polish(self.as_calc_input)
        if is_invalid:
            self.as_calc_input.setToolTip("As,calc não deve ser maior que As,ef.")
        else:
            self.as_calc_input.setToolTip("Área de aço calculada.")

    def _recalculate(self) -> None:
        try:
            data = self._read_input()
            result = self._service.calculate(data)
            memory_text = self._service.build_calculation_memory(data, result)
        except ValidationError as exc:
            self._show_validation_error(exc)
            return

        is_approved = result.anchorage_is_ok
        if is_approved:
            self.status_label.setText("VERIFICAÇÃO APROVADA")
            self.status_label.setStyleSheet(
                "background: #e8f5e9; color: #0b6b2b; padding: 5px 8px;"
                "border: 1px solid #b7dfc0; font-weight: 700;"
            )
            self._show_status("Aprovada")
        else:
            self.status_label.setText("VERIFICAÇÃO REPROVADA")
            self.status_label.setStyleSheet(
                "background: #fdecec; color: #9b1c1c; padding: 5px 8px;"
                "border: 1px solid #f0b8b8; font-weight: 700;"
            )
            if result.required_as_ef_cm2 is None:
                self._show_status(
                    "Reprovada | Ldisp menor que lb,min; aumentar As,ef nao resolve.",
                    9000,
                )
            else:
                self._show_status(
                    "Reprovada | "
                    f"As,ef necessaria = {result.required_as_ef_cm2:.2f} cm2",
                    9000,
                )

        self._update_result_fields(result, data.available_anchorage_cm)
        self.memory_text.setPlainText(memory_text)
        self.sketch_widget.update_sketch(
            anchorage_type=data.anchorage_type,
            diameter_mm=data.diameter_mm,
            available_anchorage_cm=data.available_anchorage_cm,
            required_anchorage_cm=result.lb_nec_cm,
            minimum_anchorage_cm=result.lb_min_cm,
            required_as_ef_cm2=result.required_as_ef_cm2,
            anchorage_is_ok=result.anchorage_is_ok,
        )

    def _show_validation_error(self, error: ValidationError) -> None:
        self.status_label.setText("ENTRADA INVÁLIDA")
        self.status_label.setStyleSheet(
            "background: #fff7ed; color: #9a3412; padding: 5px 8px;"
            "border: 1px solid #fed7aa; font-weight: 700;"
        )
        self._show_status(f"Ajuste os dados de entrada: {error}", 9000)
        self.memory_text.setPlainText(
            "ENTRADA INVÁLIDA\n\n"
            f"{error}\n\n"
            "A memória de cálculo será atualizada automaticamente após a correção."
        )
        for field in self.result_fields.values():
            field.clear()
            field.setStyleSheet(
                "QLineEdit { background-color: #efefef;"
                " border: 1px solid #d6d6d6;"
                " color: #111111; font-weight: 600; }"
            )
        self.sketch_widget.update_sketch(
            anchorage_type=AnchorageType.STRAIGHT,
            diameter_mm=0.0,
            available_anchorage_cm=0.0,
            required_anchorage_cm=0.0,
            minimum_anchorage_cm=0.0,
            required_as_ef_cm2=None,
            anchorage_is_ok=False,
        )

    def _read_input(self) -> AnchorageInput:
        return AnchorageInput(
            diameter_mm=float(self.diameter_input.currentData()),
            fck_mpa=self.fck_input.value(),
            steel_type=SteelType(self.steel_type_input.currentData()),
            bond_condition=BondCondition(self.bond_input.currentData()),
            effort_type=EffortType(self.effort_type_input.currentData()),
            anchorage_type=AnchorageType(self.anchorage_type_input.currentData()),
            as_calc_cm2=self.as_calc_input.value(),
            as_ef_cm2=self.as_ef_input.value(),
            available_anchorage_cm=self.available_anchorage_input.value(),
        )

    def _update_result_fields(
        self,
        result: AnchorageResult,
        available_anchorage_cm: float,
    ) -> None:
        values = {
            "fbd_mpa": f"{result.fbd_mpa:.3f}",
            "lb_cm": f"{result.lb_cm:.2f}",
            "lb_min_cm": f"{result.lb_min_cm:.2f}",
            "lb_nec_cm": f"{result.lb_nec_cm:.2f}",
            "required_as_ef_cm2": self._format_required_as_ef(result),
        }
        for key, value in values.items():
            self.result_fields[key].setText(value)

        for key in ("lb_nec_cm", "required_as_ef_cm2"):
            self._color_field(key, result.anchorage_is_ok)

    @staticmethod
    def _format_required_as_ef(result: AnchorageResult) -> str:
        if result.anchorage_is_ok:
            return "-"
        if result.required_as_ef_cm2 is None:
            return "N/A"
        return f"{result.required_as_ef_cm2:.2f}"

    def _color_field(self, key: str, is_ok: bool) -> None:
        field = self.result_fields[key]
        if is_ok:
            field.setStyleSheet(
                "QLineEdit { background-color: #efefef;"
                " border: 1px solid #d6d6d6;"
                " color: #0b6b2b; font-weight: 700; }"
            )
        else:
            field.setStyleSheet(
                "QLineEdit { background-color: #efefef;"
                " border: 1px solid #d6d6d6;"
                " color: #c62828; font-weight: 700; }"
            )

    def _copy_memory(self) -> None:
        text = self.memory_text.toPlainText()
        if not text.strip():
            self._show_status("Nenhuma memória disponível para copiar.", 4000)
            return
        QApplication.clipboard().setText(text)
        self._show_status("Memória copiada para a área de transferência.", 4000)

