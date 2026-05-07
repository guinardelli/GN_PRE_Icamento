"""Home screen for calculator selection."""

from __future__ import annotations

from collections.abc import Sequence
from functools import partial

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.calculators.registry import CalculatorDefinition


class HomeWidget(QWidget):
    """Simple home screen listing available calculators."""

    calculator_selected = Signal(str)

    def __init__(self, calculators: Sequence[CalculatorDefinition]) -> None:
        super().__init__()
        self._calculators = tuple(calculators)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("Calculadoras")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("font-size: 11pt; font-weight: 700;")
        layout.addWidget(title)

        subtitle = QLabel("Selecione uma opção.")
        subtitle.setStyleSheet("color: #444444;")
        layout.addWidget(subtitle)

        for calculator in self._calculators:
            button = QPushButton(calculator.title)
            button.setCursor(Qt.PointingHandCursor)
            button.setFixedWidth(150)
            button.setToolTip(calculator.description)
            button.clicked.connect(partial(self._select_calculator, calculator.id))
            layout.addWidget(button, 0, Qt.AlignLeft)

        layout.addStretch(1)

    def _select_calculator(self, calculator_id: str, _checked: bool = False) -> None:
        self.calculator_selected.emit(calculator_id)
