"""Smoke tests for main window workflows."""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton

from app.ui.main_window import MainWindow


class MainWindowSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.window = MainWindow()

    def test_default_startup_calculates_approved_case(self) -> None:
        self.assertEqual(self.window.status_label.text(), "VERIFICAÇÃO APROVADA")
        self.assertIsNotNone(self.window._last_lifting_data)
        self.assertIsNotNone(self.window._last_lifting_result)
        self.assertIn("MEMORIA DE CALCULO", self.window.memory_text.toPlainText())

    def test_rejected_case_updates_status_without_modal(self) -> None:
        self.window.volume_input.setValue(100.0)
        self.window.anchorage_input.setValue(1.0)
        self.window.loops_input.setValue(1)
        self.app.processEvents()

        self.assertEqual(self.window.status_label.text(), "VERIFICAÇÃO REPROVADA")
        self.assertIsNotNone(self.window._last_lifting_result)
        self.assertFalse(self.window._last_lifting_result.capacity_is_ok)

    def test_calculation_button_is_not_visible(self) -> None:
        button_texts = [
            button.text()
            for button in self.window.findChildren(QPushButton)
        ]

        self.assertFalse(any("Calcular" in text for text in button_texts))

    def test_invalid_input_updates_status_without_modal(self) -> None:
        with patch("app.ui.main_window.QMessageBox.warning") as warning:
            self.window.fckj_input.setValue(50.0)
            self.app.processEvents()

        warning.assert_not_called()
        self.assertEqual(self.window.status_label.text(), "ENTRADA INVÁLIDA")
        self.assertIsNone(self.window._last_lifting_data)
        self.assertIsNone(self.window._last_lifting_result)
        self.assertIn("ENTRADA INVÁLIDA", self.window.memory_text.toPlainText())

    def test_copy_memory_places_text_on_clipboard(self) -> None:
        self.window._copy_memory()

        clipboard_text = QApplication.clipboard().text()
        self.assertIn("MEMORIA DE CALCULO", clipboard_text)

    def test_export_memory_uses_utf8_text_file(self) -> None:
        target = Path.cwd() / "memória_cálculo_ç.txt"

        with patch(
            "app.ui.main_window.QFileDialog.getSaveFileName",
            return_value=(str(target), "Arquivo de texto (*.txt)"),
        ), patch.object(Path, "write_text", autospec=True) as write_text:
            self.window._export_memory()

        write_text.assert_called_once()
        self.assertEqual(write_text.call_args.args[0], target)
        self.assertEqual(write_text.call_args.kwargs["encoding"], "utf-8")
        self.assertIn("MEMORIA DE CALCULO", write_text.call_args.args[1])

    def test_export_svg_uses_last_valid_calculation(self) -> None:
        target = Path.cwd() / "desenho_içamento_ç.svg"

        with patch(
            "app.ui.main_window.QFileDialog.getSaveFileName",
            return_value=(str(target), "Arquivo SVG (*.svg)"),
        ), patch("app.ui.main_window.export_lifting_svg") as export_svg:
            self.window._export_svg()

        export_svg.assert_called_once()
        self.assertEqual(export_svg.call_args.args[0], str(target))
        self.assertIs(export_svg.call_args.args[1], self.window._last_lifting_data)
        self.assertIs(export_svg.call_args.args[2], self.window._last_lifting_result)

    def test_export_svg_without_calculation_shows_warning(self) -> None:
        self.window._last_lifting_data = None
        self.window._last_lifting_result = None

        with patch("app.ui.main_window.QMessageBox.warning") as warning:
            self.window._export_svg()

        warning.assert_called_once()


if __name__ == "__main__":
    unittest.main()
