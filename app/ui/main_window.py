"""Main application window and calculator windows."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox, QWidget

from app.config.settings import (
    APP_NAME,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
)
from app.ui.calculators.registry import (
    CalculatorDefinition,
    get_calculator_definitions,
)
from app.ui.home_widget import HomeWidget
from app.ui.styles import base_style
from app.ui.utilities.registry import UtilityDefinition, get_utility_definitions

HOME_WINDOW_WIDTH = 360
HOME_WINDOW_HEIGHT = 320


class CalculatorWindow(QMainWindow):
    """Window that hosts one calculator widget."""

    closed = Signal(str)

    def __init__(self, definition: CalculatorDefinition) -> None:
        super().__init__()
        self.definition = definition
        self.calculator = definition.widget_factory()
        self._build_ui()

    def _build_ui(self) -> None:
        self.setWindowTitle(self.definition.window_title)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.setStyleSheet(base_style())
        self.setCentralWidget(self.calculator)

        status_signal = getattr(self.calculator, "status_message_requested", None)
        if status_signal is not None:
            status_signal.connect(self.statusBar().showMessage)

        self.statusBar().showMessage("Pronto.")

    def closeEvent(self, event: QCloseEvent) -> None:
        self.closed.emit(self.definition.id)
        super().closeEvent(event)


class UtilityWindow(QMainWindow):
    """Window that hosts one utility widget."""

    closed = Signal(str)

    def __init__(self, definition: UtilityDefinition) -> None:
        super().__init__()
        self.definition = definition
        self.utility = definition.widget_factory()
        self._build_ui()

    def _build_ui(self) -> None:
        self.setWindowTitle(self.definition.window_title)
        self.setStyleSheet(base_style())
        self.setFixedSize(self.definition.window_width, self.definition.window_height)
        self.setCentralWidget(self.utility)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.closed.emit(self.definition.id)
        super().closeEvent(event)


class MainWindow(QMainWindow):
    """Compact home window for choosing calculators."""

    def __init__(self) -> None:
        super().__init__()
        self._calculator_definitions = get_calculator_definitions()
        self._utility_definitions = get_utility_definitions()
        self._definitions_by_id = {
            definition.id: definition for definition in self._calculator_definitions
        }
        self._utility_definitions_by_id = {
            definition.id: definition for definition in self._utility_definitions
        }
        self._calculator_windows: dict[str, CalculatorWindow] = {}
        self._utility_windows: dict[str, UtilityWindow] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.setStyleSheet(base_style())
        self.setFixedSize(HOME_WINDOW_WIDTH, HOME_WINDOW_HEIGHT)

        self.home_widget = HomeWidget(
            self._calculator_definitions,
            self._utility_definitions,
        )
        self.home_widget.calculator_selected.connect(self.open_calculator)
        self.home_widget.utility_selected.connect(self.open_utility)
        self.setCentralWidget(self.home_widget)

    def open_calculator(self, calculator_id: str) -> None:
        """Open the selected calculator in its own window."""
        definition = self._definitions_by_id.get(calculator_id)
        if definition is None:
            QMessageBox.warning(
                self,
                APP_NAME,
                f"Calculadora não encontrada: {calculator_id}",
            )
            return

        calculator_window = self._get_or_create_calculator_window(definition)
        self.hide()
        calculator_window.show()
        calculator_window.raise_()
        calculator_window.activateWindow()

    def get_calculator(self, calculator_id: str) -> QWidget | None:
        """Return an instantiated calculator widget, if it exists."""
        calculator_window = self._calculator_windows.get(calculator_id)
        if calculator_window is None:
            return None
        return calculator_window.calculator

    def get_calculator_window(self, calculator_id: str) -> CalculatorWindow | None:
        """Return an instantiated calculator window, if it exists."""
        return self._calculator_windows.get(calculator_id)

    def get_utility_window(self, utility_id: str) -> UtilityWindow | None:
        """Return an instantiated utility window, if it exists."""
        return self._utility_windows.get(utility_id)

    def open_utility(self, utility_id: str) -> None:
        """Open the selected utility in its own window."""
        definition = self._utility_definitions_by_id.get(utility_id)
        if definition is None:
            QMessageBox.warning(
                self,
                APP_NAME,
                f"Utilitario nao encontrado: {utility_id}",
            )
            return

        utility_window = self._get_or_create_utility_window(definition)
        self.hide()
        utility_window.show()
        utility_window.raise_()
        utility_window.activateWindow()

    def _get_or_create_calculator_window(
        self,
        definition: CalculatorDefinition,
    ) -> CalculatorWindow:
        calculator_window = self._calculator_windows.get(definition.id)
        if calculator_window is not None:
            return calculator_window

        calculator_window = CalculatorWindow(definition)
        calculator_window.closed.connect(self._show_home_after_calculator_close)
        self._calculator_windows[definition.id] = calculator_window
        return calculator_window

    def _show_home_after_calculator_close(self, _calculator_id: str) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def _get_or_create_utility_window(
        self,
        definition: UtilityDefinition,
    ) -> UtilityWindow:
        utility_window = self._utility_windows.get(definition.id)
        if utility_window is not None:
            return utility_window

        utility_window = UtilityWindow(definition)
        utility_window.closed.connect(self._show_home_after_utility_close)
        self._utility_windows[definition.id] = utility_window
        return utility_window

    def _show_home_after_utility_close(self, _utility_id: str) -> None:
        self.show()
        self.raise_()
        self.activateWindow()
