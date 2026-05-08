"""Tests for Tkinter anchorage calculator UI state."""

from __future__ import annotations

import tkinter as tk

import pytest

from app.tk_ui.calculators.anchorage_calculator import AnchorageCalculatorFrame


@pytest.fixture(scope="module")
def root() -> tk.Tk:
    try:
        app = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tkinter display is not available: {exc}")
    app.withdraw()
    yield app


@pytest.fixture()
def widget(root: tk.Tk) -> AnchorageCalculatorFrame:
    frame = AnchorageCalculatorFrame(root)
    frame.grid()
    root.update_idletasks()
    root.update()
    yield frame
    frame.destroy()
    root.update_idletasks()


def _anchorage_options(widget: AnchorageCalculatorFrame) -> tuple[str, ...]:
    return tuple(widget.passive_frame.anchorage_combo["values"])


def test_tension_shows_all_anchorage_types(widget: AnchorageCalculatorFrame) -> None:
    assert widget.passive_frame._vars["effort"].get() == "Tracao"
    assert _anchorage_options(widget) == (
        "Reta",
        "Com Gancho",
        "Soldada",
        "Com Gancho e Soldada",
    )
    assert not widget.passive_frame.anchorage_rule_hint.winfo_ismapped()


def test_compression_hides_hook_options_and_shows_hint(widget: AnchorageCalculatorFrame) -> None:
    widget.passive_frame._vars["effort"].set("Compressao")
    widget.update_idletasks()

    assert widget.passive_frame._vars["effort"].get() == "Compressao"
    assert _anchorage_options(widget) == ("Reta", "Soldada")
    assert widget.passive_frame.anchorage_rule_hint.grid_info()


def test_switching_back_to_tension_restores_all_options(widget: AnchorageCalculatorFrame) -> None:
    widget.passive_frame._vars["effort"].set("Compressao")
    widget.update_idletasks()
    widget.passive_frame._vars["effort"].set("Tracao")
    widget.update_idletasks()

    assert _anchorage_options(widget) == (
        "Reta",
        "Com Gancho",
        "Soldada",
        "Com Gancho e Soldada",
    )
    assert not widget.passive_frame.anchorage_rule_hint.grid_info()


def test_anchorage_widget_uses_family_tabs(widget: AnchorageCalculatorFrame) -> None:
    assert widget.family_tabs.tab(0, "text") == "Armadura passiva"
    assert widget.family_tabs.tab(1, "text") == "Emenda por transpasse"
    assert widget.family_tabs.tab(2, "text") == "Cordoalhas/Fios"
    assert widget.passive_frame.tabs.tab(0, "text") == "Verificação"
    assert widget.passive_frame.tabs.tab(1, "text") == "Memória de cálculo"
    assert widget.lap_splice_frame.tabs.tab(0, "text") == "Verificação"
    assert widget.lap_splice_frame.tabs.tab(1, "text") == "Memória de cálculo"
    assert widget.prestressing_frame.tabs.tab(0, "text") == "Verificação"
    assert widget.prestressing_frame.tabs.tab(1, "text") == "Memória de cálculo"


def test_prestressing_tab_has_detailed_memory(widget: AnchorageCalculatorFrame) -> None:
    memory = widget.prestressing_frame.memory_text.get("1.0", "end")

    assert "MEMORIA DE CALCULO - ANCORAGEM DE PROTENSAO ADERENTE" in memory
    assert "PREMISSAS ADOTADAS E LIMITACOES" in memory
    assert "COEFICIENTES DE ADERENCIA" in memory


def test_family_switching_preserves_memories(widget: AnchorageCalculatorFrame) -> None:
    passive_memory = widget.passive_frame.memory_text.get("1.0", "end")
    widget.family_tabs.select(2)
    widget.update_idletasks()
    prestressing_memory = widget.prestressing_frame.memory_text.get("1.0", "end")
    widget.family_tabs.select(0)
    widget.update_idletasks()

    assert "MEMORIA DE CALCULO - COMPRIMENTO DE ANCORAGEM" in passive_memory
    assert "MEMORIA DE CALCULO - ANCORAGEM DE PROTENSAO ADERENTE" in prestressing_memory
    assert (
        "MEMORIA DE CALCULO - COMPRIMENTO DE ANCORAGEM"
        in widget.passive_frame.memory_text.get("1.0", "end")
    )


def test_lap_splice_tab_has_memory_and_compression_hides_alpha0t(
    widget: AnchorageCalculatorFrame,
) -> None:
    widget.family_tabs.select(1)
    widget.update_idletasks()
    lap_widget = widget.lap_splice_frame

    assert "MEMORIA DE CALCULO - EMENDA POR TRANSPASSE" in lap_widget.memory_text.get("1.0", "end")
    assert lap_widget.proportion_combo.grid_info()
    assert lap_widget.alpha0t_entry.grid_info()

    lap_widget._vars["effort"].set("Compressao")
    widget.update_idletasks()

    assert lap_widget._vars["effort"].get() == "Compressao"
    assert not lap_widget.proportion_combo.grid_info()
    assert not lap_widget.alpha0t_entry.grid_info()
    assert tuple(lap_widget.anchorage_combo["values"]) == ("Reta", "Soldada")
