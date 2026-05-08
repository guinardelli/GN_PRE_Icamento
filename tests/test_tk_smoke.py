"""Smoke tests for the parallel Tkinter UI."""

from __future__ import annotations

import subprocess
import sys
import tkinter as tk

import pytest

from app.tk_ui import styles
from app.tk_ui.calculators.lifting_calculator import LiftingCalculatorFrame
from app.tk_ui.main_window import TkMainWindow
from app.tk_ui.utilities.rebar_converter import RebarConverterFrame


def test_tk_main_window_smoke() -> None:
    try:
        window = TkMainWindow()
    except tk.TclError as exc:
        pytest.skip(f"Tkinter display is not available: {exc}")

    assert window.run_smoke_test() == 0


def test_tk_entrypoint_does_not_import_pyside6() -> None:
    command = [
        sys.executable,
        "-c",
        "import sys; import app.tk_main; raise SystemExit('PySide6' in sys.modules)",
    ]
    result = subprocess.run(command, check=False)

    assert result.returncode == 0


def test_tk_invalid_fields_and_tab_navigation() -> None:
    try:
        window = TkMainWindow()
    except tk.TclError as exc:
        pytest.skip(f"Tkinter display is not available: {exc}")

    try:
        window.open_child_window("rebar_converter")
        converter = window.get_child_content("rebar_converter")
        assert isinstance(converter, RebarConverterFrame)

        converter.original_spacing_var.set("abc")
        converter.convert()
        assert converter.original_spacing_entry.cget("style") == styles.INVALID_ENTRY_STYLE

        converter.original_spacing_var.set("10")
        converter.convert()
        assert converter.original_spacing_entry.cget("style") == styles.DEFAULT_ENTRY_STYLE
        window.close_child_window("rebar_converter")

        window.open_child_window("lifting")
        lifting = window.get_child_content("lifting")
        assert isinstance(lifting, LiftingCalculatorFrame)

        lifting.select_tab(1)
        assert lifting.tabs.index("current") == 1

        lifting._input_vars["volume"].set("abc")
        window.update_idletasks()
        window.update()
        assert lifting.input_fields["volume"].cget("style") == styles.INVALID_ENTRY_STYLE
    finally:
        if window.winfo_exists():
            window.destroy()
