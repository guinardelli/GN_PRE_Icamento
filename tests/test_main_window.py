"""Tests for the official Tkinter main and child windows."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import pytest

from app.tk_ui.main_window import TkMainWindow


@pytest.fixture()
def window() -> TkMainWindow:
    try:
        app = TkMainWindow()
    except tk.TclError as exc:
        pytest.skip(f"Tkinter display is not available: {exc}")
    yield app
    if app.winfo_exists():
        app.destroy()


def test_main_window_title_and_home_groupboxes(window: TkMainWindow) -> None:
    window.update_idletasks()

    assert window.title() == "GN Estruturas - Calculadoras"
    group_titles = [
        child.cget("text")
        for child in _walk_children(window)
        if isinstance(child, ttk.LabelFrame)
    ]
    assert "NBR 9062" in group_titles
    assert "utilidades" in group_titles


def test_calculator_windows_titles_and_no_menus(window: TkMainWindow) -> None:
    lifting_window = window.open_child_window("lifting")
    window.update_idletasks()
    assert lifting_window.title() == "GN Pré - Alça de Içamento V 1.0"
    assert _menus(lifting_window) == []
    window.close_child_window("lifting")

    anchorage_window = window.open_child_window("anchorage")
    window.update_idletasks()
    assert anchorage_window.title() == "GN Pré - Ancoragem V 1.0"
    assert _menus(anchorage_window) == []
    window.close_child_window("anchorage")


def test_utility_window_title_and_no_menus(window: TkMainWindow) -> None:
    utility_window = window.open_child_window("rebar_converter")
    window.update_idletasks()

    assert utility_window.title() == "GN Pré - Conversor de Armadura V 1.0"
    assert _menus(utility_window) == []
    window.close_child_window("rebar_converter")


def _walk_children(widget: tk.Misc) -> list[tk.Misc]:
    children = list(widget.winfo_children())
    for child in list(children):
        children.extend(_walk_children(child))
    return children


def _menus(widget: tk.Misc) -> list[tk.Menu]:
    return [child for child in _walk_children(widget) if isinstance(child, tk.Menu)]
