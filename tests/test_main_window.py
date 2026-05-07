"""Tests for main and calculator windows."""

import os

import pytest
from PySide6.QtWidgets import QApplication, QGroupBox

from app.ui.main_window import MainWindow


@pytest.fixture(scope="module")
def app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    existing = QApplication.instance()
    if existing is not None:
        return existing
    return QApplication([])


def test_main_window_title_and_home_groupbox(app: QApplication) -> None:
    window = MainWindow()
    app.processEvents()

    assert window.windowTitle() == "GN Estruturas - Calculadoras"
    group_titles = [group.title() for group in window.home_widget.findChildren(QGroupBox)]
    assert "NBR 9062" in group_titles
    assert "utilidades" in group_titles


def test_calculator_windows_titles_and_no_menus(app: QApplication) -> None:
    window = MainWindow()
    app.processEvents()

    window.home_widget.calculator_selected.emit("lifting")
    app.processEvents()
    lifting_window = window.get_calculator_window("lifting")
    assert lifting_window is not None
    assert lifting_window.windowTitle() == "GN Pré - Alça de Içamento V 1.0"
    assert not lifting_window.menuBar().actions()
    lifting_window.close()
    app.processEvents()

    window.home_widget.calculator_selected.emit("anchorage")
    app.processEvents()
    anchorage_window = window.get_calculator_window("anchorage")
    assert anchorage_window is not None
    assert anchorage_window.windowTitle() == "GN Pré - Ancoragem V 1.0"
    assert not anchorage_window.menuBar().actions()
    anchorage_window.close()


def test_utility_window_title_and_no_menus(app: QApplication) -> None:
    window = MainWindow()
    app.processEvents()

    window.home_widget.utility_selected.emit("rebar_converter")
    app.processEvents()
    utility_window = window.get_utility_window("rebar_converter")
    assert utility_window is not None
    assert utility_window.windowTitle() == "GN Pre - Conversor de Armadura V 1.0"
    assert not utility_window.menuBar().actions()
    utility_window.close()
