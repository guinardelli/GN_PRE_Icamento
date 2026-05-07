"""Widget for lap splice verification of passive rebars."""

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

from app.core.anchorage_models import (
    AnchorageType,
    BondCondition,
    COMMERCIAL_REBAR_DIAMETERS,
    EffortType,
    SteelType,
)
from app.core.exceptions import ValidationError
from app.core.lap_splice_models import ALPHA0T_BRACKETS, LapSpliceInput, LapSpliceResult
from app.core.lap_splice_services import LapSpliceService


class LapSpliceWidget(QWidget):
    """Calculator for lap splice length of isolated passive rebars."""

    status_message_requested = Signal(str, int)

    def __init__(self) -> None:
        super().__init__()
        self._service = LapSpliceService()
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

        self.diameter_1_input = self._diameter_combo()
        self.diameter_2_input = self._diameter_combo()
        self._set_combo_data(self.diameter_1_input, 10.0)
        self._set_combo_data(self.diameter_2_input, 10.0)

        self.fck_input = self._spinbox(5.0, 120.0, 30.0, " MPa")

        self.steel_type_input = QComboBox()
        self.steel_type_input.addItem(SteelType.CA25.value, SteelType.CA25)
        self.steel_type_input.addItem(SteelType.CA50.value, SteelType.CA50)
        self.steel_type_input.addItem(SteelType.CA60.value, SteelType.CA60)
        self._set_combo_data(self.steel_type_input, SteelType.CA50)

        self.bond_input = QComboBox()
        self.bond_input.addItem(BondCondition.GOOD.value, BondCondition.GOOD)
        self.bond_input.addItem(BondCondition.POOR.value, BondCondition.POOR)

        self.effort_type_input = QComboBox()
        self.effort_type_input.addItem(EffortType.TENSION.value, EffortType.TENSION)
        self.effort_type_input.addItem(EffortType.COMPRESSION.value, EffortType.COMPRESSION)

        self.anchorage_type_input = QComboBox()
        self._populate_anchorage_types(EffortType.TENSION)

        self.as_calc_input = self._spinbox(0.01, 100.0, 1.0, " cm2")
        self.as_ef_input = self._spinbox(0.01, 100.0, 1.0, " cm2")

        self.proportion_input = QComboBox()
        for bracket in ALPHA0T_BRACKETS:
            self.proportion_input.addItem(
                f"{bracket.label}  |  alpha0t = {bracket.value:.1f}",
                bracket.max_percent if bracket.max_percent is not None else 100.0,
            )
        self.proportion_input.setToolTip(
            "Faixa de barras emendadas na mesma secao. "
            "A selecao define alpha0t sem interpolacao."
        )

        self.alpha0t_display = QLineEdit()
        self.alpha0t_display.setReadOnly(True)
        self.alpha0t_display.setFocusPolicy(Qt.NoFocus)
        self.alpha0t_display.setFixedWidth(142)

        self.clear_distance_input = self._spinbox(0.0, 200.0, 0.0, " cm")
        self.available_lap_input = self._spinbox(1.0, 1000.0, 60.0, " cm")

        for widget in (
            self.diameter_1_input,
            self.diameter_2_input,
            self.fck_input,
            self.steel_type_input,
            self.bond_input,
            self.effort_type_input,
            self.anchorage_type_input,
            self.as_calc_input,
            self.as_ef_input,
            self.proportion_input,
            self.clear_distance_input,
            self.available_lap_input,
        ):
            widget.setFixedWidth(142)

        prop_group, prop_form = self._new_form_group("Propriedades")
        prop_form.addRow("Bitola barra 1", self.diameter_1_input)
        prop_form.addRow("Bitola barra 2", self.diameter_2_input)
        prop_form.addRow("Fck", self.fck_input)
        prop_form.addRow("Aco", self.steel_type_input)

        cond_group, cond_form = self._new_form_group("Condicoes")
        cond_form.addRow("Aderencia", self.bond_input)
        cond_form.addRow("Solicitacao", self.effort_type_input)
        cond_form.addRow("Ancoragem base", self.anchorage_type_input)
        self.anchorage_rule_hint = QLabel(
            "Ganchos nao sao considerados para barras comprimidas."
        )
        self.anchorage_rule_hint.setWordWrap(True)
        self.anchorage_rule_hint.setStyleSheet("color: #9a3412; font-size: 8pt;")
        self.anchorage_rule_hint.setVisible(False)
        cond_form.addRow("", self.anchorage_rule_hint)

        splice_group, splice_form = self._new_form_group("Transpasse")
        splice_form.addRow("As,calc", self.as_calc_input)
        splice_form.addRow("As,ef", self.as_ef_input)
        self.proportion_label = QLabel("Prop. emendada")
        splice_form.addRow(self.proportion_label, self.proportion_input)
        self.alpha0t_label = QLabel("alpha0t")
        splice_form.addRow(self.alpha0t_label, self.alpha0t_display)
        splice_form.addRow("Dist. livre", self.clear_distance_input)
        splice_form.addRow("Ldisp", self.available_lap_input)

        self.warning_label = QLabel("")
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("color: #7c2d12; font-size: 8pt;")

        outer.addWidget(prop_group)
        outer.addWidget(cond_group)
        outer.addWidget(splice_group)
        outer.addWidget(self.warning_label)
        outer.addStretch(1)
        return panel

    def _build_result_panel(self) -> QGroupBox:
        group = QGroupBox("Resultados")
        outer = QVBoxLayout(group)
        outer.setSpacing(6)
        outer.setContentsMargins(8, 14, 8, 8)

        self.status_label = QLabel("Aguardando calculo")
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
            ("fbd_mpa", "fbd (MPa)"),
            ("lb_cm", "lb (cm)"),
            ("lb_nec_cm", "lb,nec (cm)"),
            ("lap_min_cm", "l0,min (cm)"),
            ("clear_distance_addition_cm", "Acrescimo (cm)"),
            ("required_lap_cm", "l0 final (cm)"),
            ("available_lap_cm", "Ldisp (cm)"),
            ("deficit_cm", "Deficit (cm)"),
        ):
            field = self._result_field()
            self.result_fields[key] = field
            form.addRow(label + ":", field)
        outer.addLayout(form)

        memory_hint = QLabel("<a href='#'>Memoria completa</a>")
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
        copy_button = QPushButton("Copiar Memoria")
        copy_button.clicked.connect(self._copy_memory)
        toolbar.addWidget(copy_button)
        toolbar.addStretch(1)

        self.memory_text = QTextEdit()
        self.memory_text.setReadOnly(True)
        self.memory_text.setPlaceholderText("A memoria sera atualizada automaticamente.")

        layout.addLayout(toolbar)
        layout.addWidget(self.memory_text)
        return tab

    @staticmethod
    def _diameter_combo() -> QComboBox:
        combo = QComboBox()
        for diameter in COMMERCIAL_REBAR_DIAMETERS:
            combo.addItem(diameter.label, diameter.diameter_mm)
        return combo

    @staticmethod
    def _set_combo_data(combo: QComboBox, data: object) -> None:
        index = combo.findData(data)
        if index >= 0:
            combo.setCurrentIndex(index)

    @staticmethod
    def _spinbox(minimum: float, maximum: float, value: float, suffix: str) -> QDoubleSpinBox:
        spinbox = QDoubleSpinBox()
        spinbox.setButtonSymbols(QDoubleSpinBox.NoButtons)
        spinbox.setRange(minimum, maximum)
        spinbox.setDecimals(2)
        spinbox.setValue(value)
        spinbox.setSuffix(suffix)
        return spinbox

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
        for spinbox in (
            self.fck_input,
            self.as_calc_input,
            self.as_ef_input,
            self.clear_distance_input,
            self.available_lap_input,
        ):
            spinbox.valueChanged.connect(self._on_auto_calculate)

        for combo in (
            self.diameter_1_input,
            self.diameter_2_input,
            self.steel_type_input,
            self.bond_input,
            self.effort_type_input,
            self.anchorage_type_input,
            self.proportion_input,
        ):
            combo.currentIndexChanged.connect(self._on_auto_calculate)

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
        self.anchorage_rule_hint.setVisible(effort_type == EffortType.COMPRESSION)
        self._set_tension_controls_visible(effort_type == EffortType.TENSION)
        if current_types == expected_types:
            return

        self.anchorage_type_input.blockSignals(True)
        self._populate_anchorage_types(effort_type)
        next_type = current_type if current_type in expected_types else AnchorageType.STRAIGHT
        self._set_combo_data(self.anchorage_type_input, next_type)
        self.anchorage_type_input.blockSignals(False)

    def _set_tension_controls_visible(self, visible: bool) -> None:
        for widget in (
            self.proportion_label,
            self.proportion_input,
            self.alpha0t_label,
            self.alpha0t_display,
        ):
            widget.setVisible(visible)

    def _on_auto_calculate(self, *_: object) -> None:
        self._refresh_anchorage_options()
        self._validate_as_relationship()
        self._recalculate()

    def _validate_as_relationship(self) -> None:
        is_invalid = self.as_calc_input.value() > self.as_ef_input.value()
        self.as_calc_input.setProperty("invalid", is_invalid)
        self.as_calc_input.style().unpolish(self.as_calc_input)
        self.as_calc_input.style().polish(self.as_calc_input)
        self.as_calc_input.setToolTip(
            "As,calc nao deve ser maior que As,ef."
            if is_invalid
            else "Area de aco calculada."
        )

    def _recalculate(self) -> None:
        try:
            data = self._read_input()
            result = self._service.calculate(data)
            memory = self._service.build_calculation_memory(data, result)
        except ValidationError as exc:
            self._show_validation_error(exc)
            return

        self._update_status(result)
        self._update_result_fields(result, data.available_lap_cm)
        self._update_warnings(result)
        self._update_alpha0t_display(result)
        self.memory_text.setPlainText(memory)

    def _read_input(self) -> LapSpliceInput:
        return LapSpliceInput(
            diameter_1_mm=float(self.diameter_1_input.currentData()),
            diameter_2_mm=float(self.diameter_2_input.currentData()),
            fck_mpa=self.fck_input.value(),
            steel_type=SteelType(self.steel_type_input.currentData()),
            bond_condition=BondCondition(self.bond_input.currentData()),
            effort_type=EffortType(self.effort_type_input.currentData()),
            anchorage_type=AnchorageType(self.anchorage_type_input.currentData()),
            as_calc_cm2=self.as_calc_input.value(),
            as_ef_cm2=self.as_ef_input.value(),
            spliced_bars_percent=float(self.proportion_input.currentData()),
            clear_distance_cm=self.clear_distance_input.value(),
            available_lap_cm=self.available_lap_input.value(),
        )

    def _update_status(self, result: LapSpliceResult) -> None:
        if result.lap_is_ok:
            self.status_label.setText("VERIFICACAO APROVADA")
            self.status_label.setStyleSheet(
                "background: #e8f5e9; color: #0b6b2b; padding: 5px 8px;"
                "border: 1px solid #b7dfc0; font-weight: 700;"
            )
            self._show_status("Transpasse aprovado.")
            return

        self.status_label.setText("VERIFICACAO REPROVADA")
        self.status_label.setStyleSheet(
            "background: #fdecec; color: #9b1c1c; padding: 5px 8px;"
            "border: 1px solid #f0b8b8; font-weight: 700;"
        )
        self._show_status(f"Transpasse reprovado | Deficit = {result.deficit_cm:.2f} cm", 9000)

    def _update_result_fields(
        self,
        result: LapSpliceResult,
        available_lap_cm: float,
    ) -> None:
        values = {
            "fbd_mpa": f"{result.fbd_mpa:.3f}",
            "lb_cm": f"{result.lb_cm:.2f}",
            "lb_nec_cm": f"{result.lb_nec_cm:.2f}",
            "lap_min_cm": f"{result.lap_min_cm:.2f}",
            "clear_distance_addition_cm": f"{result.clear_distance_addition_cm:.2f}",
            "required_lap_cm": f"{result.required_lap_cm:.2f}",
            "available_lap_cm": f"{available_lap_cm:.2f}",
            "deficit_cm": f"{result.deficit_cm:.2f}",
        }
        for key, value in values.items():
            self.result_fields[key].setText(value)

        for key in ("required_lap_cm", "available_lap_cm", "deficit_cm"):
            self._color_field(key, result.lap_is_ok)

    def _update_warnings(self, result: LapSpliceResult) -> None:
        warnings: list[str] = []
        if result.requires_transverse_reinforcement:
            reasons = "; ".join(result.transverse_reinforcement_reasons)
            warnings.append(f"Armadura transversal: {reasons}.")
        if result.clear_distance_addition_cm > 0:
            warnings.append("Distancia livre > 4 phi: acrescimo aplicado.")
        if result.spacing_warning:
            warnings.append("Conferir distancia livre >= max(2 phi; 20 mm).")
        self.warning_label.setText("\n".join(warnings))

    def _update_alpha0t_display(self, result: LapSpliceResult) -> None:
        if result.alpha0t is None:
            self.alpha0t_display.setText("N/A")
            return
        self.alpha0t_display.setText(f"{result.alpha0t:.2f} ({result.alpha0t_label})")

    def _color_field(self, key: str, is_ok: bool) -> None:
        color = "#0b6b2b" if is_ok else "#c62828"
        self.result_fields[key].setStyleSheet(
            "QLineEdit { background-color: #efefef; border: 1px solid #d6d6d6;"
            f" color: {color}; font-weight: 700; }}"
        )

    def _show_validation_error(self, error: ValidationError) -> None:
        self.status_label.setText("ENTRADA INVALIDA")
        self.status_label.setStyleSheet(
            "background: #fff7ed; color: #9a3412; padding: 5px 8px;"
            "border: 1px solid #fed7aa; font-weight: 700;"
        )
        self._show_status(f"Ajuste os dados de transpasse: {error}", 9000)
        self.memory_text.setPlainText(
            "ENTRADA INVALIDA\n\n"
            f"{error}\n\n"
            "A memoria de calculo sera atualizada automaticamente apos a correcao."
        )
        self.warning_label.setText(str(error))
        self.alpha0t_display.clear()
        for field in self.result_fields.values():
            field.clear()

    def _show_status(self, message: str, timeout_ms: int = 0) -> None:
        self.status_message_requested.emit(message, timeout_ms)

    def _copy_memory(self) -> None:
        text = self.memory_text.toPlainText()
        if not text.strip():
            self._show_status("Nenhuma memoria de transpasse disponivel para copiar.", 4000)
            return
        QApplication.clipboard().setText(text)
        self._show_status("Memoria de transpasse copiada.", 4000)

