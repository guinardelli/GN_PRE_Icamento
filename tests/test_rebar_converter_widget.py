"""Tests for the Tkinter rebar converter widget."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import pytest

from app.tk_ui.utilities.rebar_converter import RebarConverterFrame


@pytest.fixture(scope="module")
def root() -> tk.Tk:
    try:
        app = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tkinter display is not available: {exc}")
    app.withdraw()
    yield app


@pytest.fixture()
def widget(root: tk.Tk) -> RebarConverterFrame:
    frame = RebarConverterFrame(root)
    frame.grid()
    root.update_idletasks()
    yield frame
    frame.destroy()
    root.update_idletasks()


def test_converter_calculates_expected_spacing(widget: RebarConverterFrame) -> None:
    widget.original_rebar_var.set("CA-50 - 8.0 mm")
    widget.original_spacing_var.set("10")
    widget.equivalent_rebar_var.set("CA-50 - 16.0 mm")

    widget.convert()

    assert widget.equivalent_spacing_var.get() == "40.00"


def test_converter_uses_steel_grade_from_selected_option(widget: RebarConverterFrame) -> None:
    widget.original_rebar_var.set("CA-50 - 8.0 mm")
    widget.original_spacing_var.set("10")
    widget.equivalent_rebar_var.set("CA-60 - 8.0 mm")

    widget.convert()

    assert widget.equivalent_spacing_var.get() == "12.00"


def test_converter_has_no_option_checkboxes(widget: RebarConverterFrame) -> None:
    checkboxes = [
        child
        for child in _walk_children(widget)
        if isinstance(child, (tk.Checkbutton, ttk.Checkbutton))
    ]

    assert checkboxes == []


def _walk_children(widget: tk.Misc) -> list[tk.Misc]:
    children = list(widget.winfo_children())
    for child in list(children):
        children.extend(_walk_children(child))
    return children
