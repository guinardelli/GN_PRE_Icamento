"""Tkinter rebar diameter/spacing converter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.core.exceptions import ValidationError
from app.core.utility_rebar_models import RebarConversionInput, RebarConversionOption
from app.core.utility_rebar_services import (
    REBAR_CONVERSION_OPTIONS,
    RebarConversionService,
)
from app.tk_ui import styles

DEFAULT_ORIGINAL = "CA-50 - 8.0 mm"
DEFAULT_EQUIVALENT = "CA-50 - 16.0 mm"


class RebarConverterFrame(ttk.Frame):
    """Frame that converts equivalent spacing for selected rebar options."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=styles.WINDOW_PAD)
        self._service = RebarConversionService()
        self._options_by_label = {
            option.label: option for option in REBAR_CONVERSION_OPTIONS
        }
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)

        self.original_rebar_var = tk.StringVar(value=DEFAULT_ORIGINAL)
        self.original_spacing_var = tk.StringVar(value="10")
        self.equivalent_rebar_var = tk.StringVar(value=DEFAULT_EQUIVALENT)
        self.equivalent_spacing_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="")

        original_group = ttk.LabelFrame(
            self,
            text="Armadura Original",
            padding=styles.GROUP_PAD,
        )
        original_group.grid(row=0, column=0, sticky="ew")
        self._build_original_group(original_group)

        equivalent_group = ttk.LabelFrame(
            self,
            text="Armadura Equivalente",
            padding=styles.GROUP_PAD,
        )
        equivalent_group.grid(row=1, column=0, sticky="ew", pady=(styles.GAP, 0))
        self._build_equivalent_group(equivalent_group)

        self.convert_button = ttk.Button(self, text="Converter", command=self.convert)
        self.convert_button.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        self.status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            foreground="#c62828",
        )
        self.status_label.grid(row=3, column=0, sticky="ew", pady=(6, 0))

    def _build_original_group(self, group: ttk.LabelFrame) -> None:
        group.columnconfigure(1, weight=1)

        ttk.Label(group, text="Bitola").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.original_rebar_combo = ttk.Combobox(
            group,
            textvariable=self.original_rebar_var,
            values=self._option_labels(),
            state="readonly",
            width=20,
        )
        self.original_rebar_combo.grid(row=0, column=1, sticky="ew")

        ttk.Label(group, text="Espacamento (cm)").grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 8),
            pady=(8, 0),
        )
        self.original_spacing_entry = ttk.Entry(
            group,
            textvariable=self.original_spacing_var,
            width=12,
        )
        self.original_spacing_entry.grid(row=1, column=1, sticky="ew", pady=(8, 0))

    def _build_equivalent_group(self, group: ttk.LabelFrame) -> None:
        group.columnconfigure(1, weight=1)

        ttk.Label(group, text="Bitola").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.equivalent_rebar_combo = ttk.Combobox(
            group,
            textvariable=self.equivalent_rebar_var,
            values=self._option_labels(),
            state="readonly",
            width=20,
        )
        self.equivalent_rebar_combo.grid(row=0, column=1, sticky="ew")

        ttk.Label(group, text="Espacamento (cm)").grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 8),
            pady=(8, 0),
        )
        self.equivalent_spacing_entry = ttk.Entry(
            group,
            textvariable=self.equivalent_spacing_var,
            state="readonly",
            width=12,
        )
        self.equivalent_spacing_entry.grid(row=1, column=1, sticky="ew", pady=(8, 0))

    @staticmethod
    def _option_labels() -> tuple[str, ...]:
        return tuple(option.label for option in REBAR_CONVERSION_OPTIONS)

    def convert(self) -> None:
        """Calculate and show the equivalent spacing."""
        self.status_var.set("")
        self.equivalent_spacing_var.set("")

        try:
            original_option = self._selected_option(self.original_rebar_var)
            equivalent_option = self._selected_option(self.equivalent_rebar_var)
            original_spacing = float(self.original_spacing_var.get().replace(",", "."))
            result = self._service.convert(
                RebarConversionInput(
                    original_diameter_mm=original_option.diameter_mm,
                    original_spacing_cm=original_spacing,
                    original_fyk_mpa=original_option.fyk_mpa,
                    equivalent_diameter_mm=equivalent_option.diameter_mm,
                    equivalent_fyk_mpa=equivalent_option.fyk_mpa,
                )
            )
        except ValueError:
            self.status_var.set("Espacamento original deve ser numerico.")
            return
        except ValidationError as exc:
            self.status_var.set(str(exc))
            return

        self.equivalent_spacing_var.set(f"{result.equivalent_spacing_cm:.2f}")

    def _selected_option(self, value: tk.StringVar) -> RebarConversionOption:
        label = value.get()
        try:
            return self._options_by_label[label]
        except KeyError as exc:
            raise ValidationError(f"Bitola invalida: {label}") from exc
