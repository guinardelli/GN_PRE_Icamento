"""Utility widget for converting rebar diameter and spacing."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.exceptions import ValidationError
from app.core.utility_rebar_models import RebarConversionInput, RebarConversionOption
from app.core.utility_rebar_services import (
    REBAR_CONVERSION_OPTIONS,
    RebarConversionService,
)


class RebarConverterWidget(QWidget):
    """Converts equivalent spacing based on diameter and steel grade."""

    def __init__(self) -> None:
        super().__init__()
        self._service = RebarConversionService()
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        root.addWidget(self._build_original_group())
        root.addWidget(self._build_equivalent_group())

        self.convert_button = QPushButton("Converter")
        self.convert_button.clicked.connect(self._convert)
        root.addWidget(self.convert_button)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #c62828;")
        root.addWidget(self.status_label)

        root.addStretch(1)

    def _build_original_group(self) -> QGroupBox:
        group = QGroupBox("Armadura Original")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignLeft)

        self.original_rebar_input = QComboBox()
        self._fill_rebars(self.original_rebar_input, default_label="CA-50 - 8.0 mm")
        form.addRow("Bitola", self.original_rebar_input)

        self.original_spacing_input = QDoubleSpinBox()
        self.original_spacing_input.setRange(0.1, 1000.0)
        self.original_spacing_input.setDecimals(2)
        self.original_spacing_input.setValue(10.0)
        form.addRow("Espacamento (cm)", self.original_spacing_input)
        return group

    def _build_equivalent_group(self) -> QGroupBox:
        group = QGroupBox("Armadura Equivalente")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignLeft)

        self.equivalent_rebar_input = QComboBox()
        self._fill_rebars(self.equivalent_rebar_input, default_label="CA-50 - 16.0 mm")
        form.addRow("Bitola", self.equivalent_rebar_input)

        self.equivalent_spacing_output = QLineEdit()
        self.equivalent_spacing_output.setReadOnly(True)
        form.addRow("Espacamento (cm)", self.equivalent_spacing_output)
        return group

    @staticmethod
    def _fill_rebars(combo: QComboBox, default_label: str) -> None:
        for option in REBAR_CONVERSION_OPTIONS:
            combo.addItem(option.label, option)
        idx = combo.findText(default_label)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def _convert(self) -> None:
        self.status_label.clear()

        original_option = self._current_option(self.original_rebar_input)
        equivalent_option = self._current_option(self.equivalent_rebar_input)
        data = RebarConversionInput(
            original_diameter_mm=original_option.diameter_mm,
            original_spacing_cm=self.original_spacing_input.value(),
            original_fyk_mpa=original_option.fyk_mpa,
            equivalent_diameter_mm=equivalent_option.diameter_mm,
            equivalent_fyk_mpa=equivalent_option.fyk_mpa,
        )

        try:
            result = self._service.convert(data)
        except ValidationError as exc:
            self.equivalent_spacing_output.clear()
            self.status_label.setText(str(exc))
            return

        self.equivalent_spacing_output.setText(f"{result.equivalent_spacing_cm:.2f}")

    @staticmethod
    def _current_option(combo: QComboBox) -> RebarConversionOption:
        option = combo.currentData()
        if not isinstance(option, RebarConversionOption):
            raise ValidationError("Selecao de bitola invalida.")
        return option
