"""Registry of utilities available in the application."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget

from app.ui.utilities.rebar_converter_widget import RebarConverterWidget


@dataclass(frozen=True)
class UtilityDefinition:
    """Metadata required to show and open a utility window."""

    id: str
    title: str
    window_title: str
    description: str
    window_width: int
    window_height: int
    widget_factory: Callable[[], QWidget]


def get_utility_definitions() -> tuple[UtilityDefinition, ...]:
    """Return utilities shown on the home screen."""
    return (
        UtilityDefinition(
            id="rebar_converter",
            title="Conversor bitola/espacamento",
            window_title="GN Pre - Conversor de Armadura V 1.0",
            description="Converte bitola e espacamento para armadura equivalente.",
            window_width=280,
            window_height=320,
            widget_factory=RebarConverterWidget,
        ),
    )
