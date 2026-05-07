"""Application entry point."""

from __future__ import annotations

import sys
from pathlib import Path

# Allows running both:
# 1) from project root: python app/main.py
# 2) from app folder:   python main.py
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)

from app.ui.main_window import MainWindow


def main() -> int:
    smoke_test = "--smoke-test" in sys.argv
    if smoke_test:
        import os

        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from PySide6.QtWidgets import QApplication

    app_args = [arg for arg in sys.argv if arg != "--smoke-test"]
    app = QApplication(app_args)
    window = MainWindow()
    if smoke_test:
        window.show()
        app.processEvents()
        if not window.isVisible():
            return 1
        if window.menuBar().actions():
            return 1

        window.home_widget.calculator_selected.emit("lifting")
        app.processEvents()
        lifting_window = window.get_calculator_window("lifting")
        if lifting_window is None or not lifting_window.isVisible():
            return 1
        if lifting_window.menuBar().actions():
            return 1
        if window.isVisible():
            return 1
        lifting_calculator = window.get_calculator("lifting")
        if lifting_calculator is None:
            return 1
        if lifting_calculator._last_lifting_result is None:
            return 1
        lifting_memory = lifting_calculator.memory_text.toPlainText()
        if "MEMORIA DE CALCULO" not in lifting_memory:
            return 1

        lifting_window.close()
        app.processEvents()
        if not window.isVisible():
            return 1

        window.home_widget.calculator_selected.emit("anchorage")
        app.processEvents()
        anchorage_window = window.get_calculator_window("anchorage")
        if anchorage_window is None or not anchorage_window.isVisible():
            return 1
        if anchorage_window.menuBar().actions():
            return 1
        anchorage_calculator = window.get_calculator("anchorage")
        if anchorage_calculator is None:
            return 1
        anchorage_memory = anchorage_calculator.memory_text.toPlainText()
        if "MEMORIA DE CALCULO" not in anchorage_memory:
            return 1
        if "ENTRADA INVAL" in anchorage_memory:
            return 1

        anchorage_window.close()
        app.processEvents()
        if not window.isVisible():
            return 1

        window.home_widget.utility_selected.emit("rebar_converter")
        app.processEvents()
        utility_window = window.get_utility_window("rebar_converter")
        if utility_window is None or not utility_window.isVisible():
            return 1
        if utility_window.menuBar().actions():
            return 1
        if window.isVisible():
            return 1

        return 0

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
