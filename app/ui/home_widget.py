"""Home screen for calculator selection."""

from __future__ import annotations

from collections.abc import Sequence
from functools import partial

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QPushButton,
    QSizePolicy,
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
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Calculadoras")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("font-size: 16pt; font-weight: 700;")
        layout.addWidget(title)

        subtitle = QLabel("Selecione uma calculadora para iniciar.")
        subtitle.setStyleSheet("color: #444444;")
        layout.addWidget(subtitle)

        group = QGroupBox("Disponíveis")
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(12, 18, 12, 12)
        group_layout.setSpacing(8)

        for calculator in self._calculators:
            button = QPushButton(calculator.title)
            button.setCursor(Qt.PointingHandCursor)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button.setToolTip(calculator.description)
            button.clicked.connect(partial(self._select_calculator, calculator.id))
            group_layout.addWidget(button)

            description = QLabel(calculator.description)
            description.setWordWrap(True)
            description.setStyleSheet("color: #555555;")
            group_layout.addWidget(description)

        group_layout.addStretch(1)
        layout.addWidget(group)
        layout.addStretch(1)

    def _select_calculator(self, calculator_id: str, _checked: bool = False) -> None:
        self.calculator_selected.emit(calculator_id)
