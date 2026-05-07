"""Registry of calculators available in the application."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget

from app.ui.calculators.anchorage_widget import AnchorageCalculatorWidget
from app.ui.calculators.lifting_calculator_widget import LiftingCalculatorWidget


@dataclass(frozen=True)
class CalculatorDefinition:
    """Metadata required to show and open a calculator."""

    id: str
    title: str
    window_title: str
    description: str
    widget_factory: Callable[[], QWidget]


def get_calculator_definitions() -> tuple[CalculatorDefinition, ...]:
    """Return calculators shown on the home screen."""
    return (
        CalculatorDefinition(
            id="lifting",
            title="Alça de içamento",
            window_title="GN Pré - Alça de Içamento V 1.0",
            description="Verificação de içamento com alças em cordoalha.",
            widget_factory=LiftingCalculatorWidget,
        ),
        CalculatorDefinition(
            id="anchorage",
            title="Comprimento de ancoragem",
            window_title="GN Pré - Ancoragem V 1.0",
            description="Ancoragem, transpasse e protensão aderente (NBR 6118).",
            widget_factory=AnchorageCalculatorWidget,
        ),
    )
