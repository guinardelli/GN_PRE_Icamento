"""Main application window and calculator navigation."""

from __future__ import annotations

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

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


class MainWindow(QMainWindow):
    """Main application window that hosts calculator screens."""

    def __init__(self) -> None:
        super().__init__()
        self._calculator_definitions = get_calculator_definitions()
        self._definitions_by_id = {
            definition.id: definition for definition in self._calculator_definitions
        }
        self._calculator_widgets: dict[str, QWidget] = {}
        self._calculator_indexes: dict[str, int] = {}
        self._build_ui()
        self._build_menu_bar()
        self.show_home()

    def _build_ui(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.setStyleSheet(base_style())

        central = QWidget()
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        self.home_button = QPushButton("Início")
        self.home_button.clicked.connect(self.show_home)
        header_layout.addWidget(self.home_button, 0)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 12pt; font-weight: 700;")
        header_layout.addWidget(self.title_label, 1)

        root_layout.addLayout(header_layout)

        self.stack = QStackedWidget()
        self.home_widget = HomeWidget(self._calculator_definitions)
        self.home_widget.calculator_selected.connect(self.open_calculator)
        self._home_index = self.stack.addWidget(self.home_widget)
        root_layout.addWidget(self.stack, 1)

        self.setCentralWidget(central)
        self.statusBar().showMessage("Pronto.")

    def _build_menu_bar(self) -> None:
        menu = self.menuBar()

        file_menu = menu.addMenu("&Arquivo")
        export_memory_action = QAction("Exportar Memória (.txt)...", self)
        export_memory_action.setShortcut(QKeySequence("Ctrl+S"))
        export_memory_action.triggered.connect(self.export_active_memory)
        file_menu.addAction(export_memory_action)

        export_svg_action = QAction("Exportar Desenho (.svg)...", self)
        export_svg_action.triggered.connect(self.export_active_svg)
        file_menu.addAction(export_svg_action)

        tools_menu = menu.addMenu("&Ferramentas")
        restore_defaults_action = QAction("Restaurar Padrões", self)
        restore_defaults_action.setShortcut(QKeySequence("Ctrl+R"))
        restore_defaults_action.triggered.connect(self.restore_active_defaults)
        tools_menu.addAction(restore_defaults_action)

        help_menu = menu.addMenu("A&juda")
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def show_home(self) -> None:
        """Show the home screen."""
        self.stack.setCurrentIndex(self._home_index)
        self.home_button.setVisible(False)
        self.title_label.setText("Calculadoras")
        self.setWindowTitle(APP_NAME)
        self.statusBar().showMessage("Pronto.")

    def open_calculator(self, calculator_id: str) -> None:
        """Open a calculator by its registered id."""
        definition = self._definitions_by_id.get(calculator_id)
        if definition is None:
            QMessageBox.warning(
                self,
                APP_NAME,
                f"Calculadora não encontrada: {calculator_id}",
            )
            return

        widget = self._get_or_create_calculator(definition)
        self.stack.setCurrentIndex(self._calculator_indexes[calculator_id])
        self.home_button.setVisible(True)
        self.title_label.setText(definition.title)
        self.setWindowTitle(f"{definition.title} - {APP_NAME}")
        self.statusBar().showMessage(f"Calculadora aberta: {definition.title}")

    def get_calculator(self, calculator_id: str) -> QWidget | None:
        """Return an instantiated calculator widget, if it exists."""
        return self._calculator_widgets.get(calculator_id)

    def export_active_memory(self) -> None:
        """Export memory from the active calculator when supported."""
        calculator = self._active_calculator()
        if calculator is not None and hasattr(calculator, "export_memory"):
            calculator.export_memory()
            return
        self._show_calculator_action_warning()

    def export_active_svg(self) -> None:
        """Export SVG from the active calculator when supported."""
        calculator = self._active_calculator()
        if calculator is not None and hasattr(calculator, "export_svg"):
            calculator.export_svg()
            return
        self._show_calculator_action_warning()

    def restore_active_defaults(self) -> None:
        """Restore defaults in the active calculator when supported."""
        calculator = self._active_calculator()
        if calculator is not None and hasattr(calculator, "restore_defaults"):
            calculator.restore_defaults()
            return
        self._show_calculator_action_warning()

    def _get_or_create_calculator(self, definition: CalculatorDefinition) -> QWidget:
        widget = self._calculator_widgets.get(definition.id)
        if widget is not None:
            return widget

        widget = definition.widget_factory()
        status_signal = getattr(widget, "status_message_requested", None)
        if status_signal is not None:
            status_signal.connect(self.statusBar().showMessage)

        self._calculator_widgets[definition.id] = widget
        self._calculator_indexes[definition.id] = self.stack.addWidget(widget)
        return widget

    def _active_calculator(self) -> QWidget | None:
        widget = self.stack.currentWidget()
        if widget is self.home_widget:
            return None
        return widget

    def _show_calculator_action_warning(self) -> None:
        QMessageBox.information(
            self,
            APP_NAME,
            "Abra uma calculadora para usar esta ação.",
        )

    def _show_about_dialog(self) -> None:
        QMessageBox.information(
            self,
            "Sobre",
            f"{APP_NAME}\n"
            f"Versão {APP_VERSION}\n"
            "Aplicativo de calculadoras auxiliares para pré-fabricados.",
        )

