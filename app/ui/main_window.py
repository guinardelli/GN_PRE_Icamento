"""Main application window and calculator windows."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import QMainWindow, QMessageBox, QWidget

from app.config.settings import (
    APP_NAME,
    APP_VERSION,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
)
from app.ui.calculators.registry import (
    CalculatorDefinition,
    get_calculator_definitions,
)
from app.ui.home_widget import HomeWidget
from app.ui.styles import base_style

HOME_WINDOW_WIDTH = 340
HOME_WINDOW_HEIGHT = 190


class CalculatorWindow(QMainWindow):
    """Window that hosts one calculator widget."""

    closed = Signal(str)

    def __init__(self, definition: CalculatorDefinition) -> None:
        super().__init__()
        self.definition = definition
        self.calculator = definition.widget_factory()
        self._build_ui()
        self._build_menu_bar()

    def _build_ui(self) -> None:
        self.setWindowTitle(f"{self.definition.title} - {APP_NAME}")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.setStyleSheet(base_style())
        self.setCentralWidget(self.calculator)

        status_signal = getattr(self.calculator, "status_message_requested", None)
        if status_signal is not None:
            status_signal.connect(self.statusBar().showMessage)

        self.statusBar().showMessage("Pronto.")

    def _build_menu_bar(self) -> None:
        menu = self.menuBar()

        file_menu = menu.addMenu("&Arquivo")
        export_memory_action = QAction("Exportar Memória (.txt)...", self)
        export_memory_action.setShortcut(QKeySequence("Ctrl+S"))
        export_memory_action.triggered.connect(self.export_memory)
        file_menu.addAction(export_memory_action)

        export_svg_action = QAction("Exportar Desenho (.svg)...", self)
        export_svg_action.triggered.connect(self.export_svg)
        file_menu.addAction(export_svg_action)

        tools_menu = menu.addMenu("&Ferramentas")
        restore_defaults_action = QAction("Restaurar Padrões", self)
        restore_defaults_action.setShortcut(QKeySequence("Ctrl+R"))
        restore_defaults_action.triggered.connect(self.restore_defaults)
        tools_menu.addAction(restore_defaults_action)

        help_menu = menu.addMenu("A&juda")
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def export_memory(self) -> None:
        if hasattr(self.calculator, "export_memory"):
            self.calculator.export_memory()

    def export_svg(self) -> None:
        if hasattr(self.calculator, "export_svg"):
            self.calculator.export_svg()

    def restore_defaults(self) -> None:
        if hasattr(self.calculator, "restore_defaults"):
            self.calculator.restore_defaults()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.closed.emit(self.definition.id)
        super().closeEvent(event)

    def _show_about_dialog(self) -> None:
        QMessageBox.information(
            self,
            "Sobre",
            f"{APP_NAME}\n"
            f"Versão {APP_VERSION}\n"
            "Aplicativo de calculadoras auxiliares para pré-fabricados.",
        )


class MainWindow(QMainWindow):
    """Compact home window for choosing calculators."""

    def __init__(self) -> None:
        super().__init__()
        self._calculator_definitions = get_calculator_definitions()
        self._definitions_by_id = {
            definition.id: definition for definition in self._calculator_definitions
        }
        self._calculator_windows: dict[str, CalculatorWindow] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.setStyleSheet(base_style())
        self.setFixedSize(HOME_WINDOW_WIDTH, HOME_WINDOW_HEIGHT)

        self.home_widget = HomeWidget(self._calculator_definitions)
        self.home_widget.calculator_selected.connect(self.open_calculator)
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

