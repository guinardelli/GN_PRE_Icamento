"""Home screen for calculator selection."""

from __future__ import annotations

from collections.abc import Sequence
from functools import partial

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.calculators.registry import CalculatorDefinition
from app.ui.utilities.registry import UtilityDefinition


class HomeWidget(QWidget):
    """Simple home screen listing available calculators."""

    calculator_selected = Signal(str)
    utility_selected = Signal(str)

    def __init__(
        self,
        calculators: Sequence[CalculatorDefinition],
        utilities: Sequence[UtilityDefinition],
    ) -> None:
        super().__init__()
        self._calculators = tuple(calculators)
        self._utilities = tuple(utilities)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        title = QLabel("Calculadoras")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("font-size: 11pt; font-weight: 700;")
        layout.addWidget(title)

        subtitle = QLabel("Selecione uma opção.")
        subtitle.setStyleSheet("color: #444444;")
        layout.addWidget(subtitle)

        calculators_group = QGroupBox("NBR 9062")
        group_layout = QVBoxLayout(calculators_group)
        group_layout.setContentsMargins(12, 14, 12, 12)
        group_layout.setSpacing(8)

        for calculator in self._calculators:
            button = QPushButton(calculator.title)
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumWidth(180)
            button.setToolTip(calculator.description)
            button.clicked.connect(partial(self._select_calculator, calculator.id))
            group_layout.addWidget(button)

        layout.addWidget(calculators_group)

        utilities_group = QGroupBox("utilidades")
        utilities_layout = QVBoxLayout(utilities_group)
        utilities_layout.setContentsMargins(12, 14, 12, 12)
        utilities_layout.setSpacing(8)

        for utility in self._utilities:
            button = QPushButton(utility.title)
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumWidth(180)
            button.setToolTip(utility.description)
            button.clicked.connect(partial(self._select_utility, utility.id))
            utilities_layout.addWidget(button)

        layout.addWidget(utilities_group)
        layout.addStretch(1)

    def _select_calculator(self, calculator_id: str, _checked: bool = False) -> None:
        self.calculator_selected.emit(calculator_id)

    def _select_utility(self, utility_id: str, _checked: bool = False) -> None:
        self.utility_selected.emit(utility_id)
