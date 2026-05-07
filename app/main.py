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
        calculator_window = window.get_calculator_window("lifting")
        if calculator_window is None or not calculator_window.isVisible():
            return 1
        if window.isVisible():
            return 1
        lifting_calculator = window.get_calculator("lifting")
        if lifting_calculator is None:
            return 1
        memory_text = lifting_calculator.memory_text.toPlainText()
        if lifting_calculator._last_lifting_result is None:
            return 1
        if "MEMORIA DE CALCULO" not in memory_text:
            return 1
        calculator_window.close()
        app.processEvents()
        if not window.isVisible():
            return 1
        window.home_widget.calculator_selected.emit("lifting")
        app.processEvents()
        if window.get_calculator("lifting") is not lifting_calculator:
            return 1
        return 0

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
