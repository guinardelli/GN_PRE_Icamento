"""Tests for AnchorageCalculatorWidget UI state."""

import os

import pytest
from PySide6.QtWidgets import QApplication

from app.ui.calculators.anchorage_widget import AnchorageCalculatorWidget


@pytest.fixture(scope="module")
def app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    existing = QApplication.instance()
    if existing is not None:
        return existing
    return QApplication([])


def _anchorage_options(widget: AnchorageCalculatorWidget) -> list[str]:
    return [
        widget.anchorage_type_input.itemText(index)
        for index in range(widget.anchorage_type_input.count())
    ]


def test_tension_shows_all_anchorage_types(app: QApplication) -> None:
    widget = AnchorageCalculatorWidget()
    app.processEvents()

    assert widget.effort_type_input.currentText() == "Tracao"
    assert _anchorage_options(widget) == [
        "Reta",
        "Com Gancho",
        "Soldada",
        "Com Gancho e Soldada",
    ]
    assert widget.anchorage_rule_hint.isHidden()


def test_compression_hides_hook_options_and_shows_hint(app: QApplication) -> None:
    widget = AnchorageCalculatorWidget()
    widget.effort_type_input.setCurrentIndex(1)
    app.processEvents()

    assert widget.effort_type_input.currentText() == "Compressao"
    assert _anchorage_options(widget) == ["Reta", "Soldada"]
    assert not widget.anchorage_rule_hint.isHidden()


def test_switching_back_to_tension_restores_all_options(app: QApplication) -> None:
    widget = AnchorageCalculatorWidget()
    widget.effort_type_input.setCurrentIndex(1)
    app.processEvents()
    widget.effort_type_input.setCurrentIndex(0)
    app.processEvents()

    assert widget.effort_type_input.currentText() == "Tracao"
    assert _anchorage_options(widget) == [
        "Reta",
        "Com Gancho",
        "Soldada",
        "Com Gancho e Soldada",
    ]
    assert widget.anchorage_rule_hint.isHidden()


def test_anchorage_widget_uses_family_tabs(app: QApplication) -> None:
    widget = AnchorageCalculatorWidget()
    app.processEvents()

    assert widget.family_tabs.tabText(0) == "Armadura passiva"
    assert widget.family_tabs.tabText(1) == "Emenda por transpasse"
    assert widget.family_tabs.tabText(2) == "Cordoalhas/Fios"
    assert widget.passive_tabs.tabText(0) == "Verificação"
    assert widget.passive_tabs.tabText(1) == "Memória de cálculo"
    assert widget.lap_splice_widget.tabs.tabText(0) == "Verificação"
    assert widget.lap_splice_widget.tabs.tabText(1) == "Memória de cálculo"
    assert widget.prestressing_widget.tabs.tabText(0) == "Verificação"
    assert widget.prestressing_widget.tabs.tabText(1) == "Memória de cálculo"


def test_prestressing_tab_has_detailed_memory(app: QApplication) -> None:
    widget = AnchorageCalculatorWidget()
    app.processEvents()

    assert widget.family_tabs.tabText(2) == "Cordoalhas/Fios"
    prestressing_widget = widget.prestressing_widget
    memory = prestressing_widget.memory_text.toPlainText()

    assert "MEMORIA DE CALCULO - ANCORAGEM DE PROTENSAO ADERENTE" in memory
    assert "PREMISSAS ADOTADAS E LIMITACOES" in memory
    assert "COEFICIENTES DE ADERENCIA" in memory


def test_family_switching_preserves_memories(app: QApplication) -> None:
    widget = AnchorageCalculatorWidget()
    app.processEvents()

    passive_memory = widget.memory_text.toPlainText()
    widget.family_tabs.setCurrentIndex(2)
    app.processEvents()
    prestressing_memory = widget.prestressing_widget.memory_text.toPlainText()
    widget.family_tabs.setCurrentIndex(0)
    app.processEvents()

    assert "MEMORIA DE CALCULO - COMPRIMENTO DE ANCORAGEM" in passive_memory
    assert "MEMORIA DE CALCULO - ANCORAGEM DE PROTENSAO ADERENTE" in prestressing_memory
    assert "MEMORIA DE CALCULO - COMPRIMENTO DE ANCORAGEM" in widget.memory_text.toPlainText()


def test_lap_splice_tab_has_memory_and_compression_hides_alpha0t(
    app: QApplication,
) -> None:
    widget = AnchorageCalculatorWidget()
    app.processEvents()

    lap_widget = widget.lap_splice_widget
    assert "MEMORIA DE CALCULO - EMENDA POR TRANSPASSE" in lap_widget.memory_text.toPlainText()
    assert not lap_widget.proportion_input.isHidden()
    assert not lap_widget.alpha0t_display.isHidden()

    lap_widget.effort_type_input.setCurrentIndex(1)
    app.processEvents()

    assert lap_widget.effort_type_input.currentText() == "Compressao"
    assert lap_widget.proportion_input.isHidden()
    assert lap_widget.alpha0t_display.isHidden()
    assert lap_widget.anchorage_type_input.count() == 2
