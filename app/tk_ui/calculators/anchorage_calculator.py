"""Tkinter anchorage calculators."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.core.anchorage_models import (
    COMMERCIAL_REBAR_DIAMETERS,
    AnchorageInput,
    AnchorageResult,
    AnchorageType,
    BondCondition,
    EffortType,
    SteelType,
)
from app.core.anchorage_services import AnchorageVerifierService
from app.core.exceptions import ValidationError
from app.core.lap_splice_models import ALPHA0T_BRACKETS, LapSpliceInput, LapSpliceResult
from app.core.lap_splice_services import LapSpliceService
from app.core.prestressing_anchorage_models import (
    PRESTRESSING_STEEL_SPECS,
    PrestressingAnchorageInput,
    PrestressingAnchorageResult,
    PrestressingBondCondition,
)
from app.core.prestressing_anchorage_services import PrestressingAnchorageService
from app.tk_ui import styles
from app.tk_ui.sketches.anchorage_sketch import AnchorageSketchCanvas


STEEL_OPTIONS = tuple(item.value for item in SteelType)
BOND_OPTIONS = tuple(item.value for item in BondCondition)
EFFORT_OPTIONS = tuple(item.value for item in EffortType)
ANCHORAGE_TENSION_OPTIONS = (
    AnchorageType.STRAIGHT.value,
    AnchorageType.HOOK.value,
    AnchorageType.WELDED.value,
    AnchorageType.HOOK_WELDED.value,
)
ANCHORAGE_COMPRESSION_OPTIONS = (
    AnchorageType.STRAIGHT.value,
    AnchorageType.WELDED.value,
)
PRESTRESSING_BOND_OPTIONS = tuple(item.value for item in PrestressingBondCondition)


class AnchorageCalculatorFrame(ttk.Frame):
    """Tkinter port of the full anchorage calculator window."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=styles.WINDOW_PAD)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.family_tabs = ttk.Notebook(self)
        self.family_tabs.grid(row=0, column=0, sticky="nsew")

        self.passive_frame = PassiveAnchorageFrame(self.family_tabs)
        self.lap_splice_frame = LapSpliceFrame(self.family_tabs)
        self.prestressing_frame = PrestressingAnchorageFrame(self.family_tabs)

        self.family_tabs.add(self.passive_frame, text="Armadura passiva")
        self.family_tabs.add(self.lap_splice_frame, text="Emenda por transpasse")
        self.family_tabs.add(self.prestressing_frame, text="Cordoalhas/Fios")

    def select_tab(self, index: int) -> None:
        if 0 <= index < len(self.family_tabs.tabs()):
            self.family_tabs.select(index)


class CalculatorBase(ttk.Frame):
    """Shared Tkinter helpers for calculator frames."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._input_fields_by_var: dict[int, ttk.Entry] = {}
        self._invalid_variable_id: int | None = None

    def _parse_float(self, variable: tk.StringVar, label: str) -> float:
        raw_value = variable.get().strip().replace(",", ".")
        try:
            return float(raw_value)
        except ValueError as exc:
            self._invalid_variable_id = id(variable)
            raise ValidationError(f"{label} deve ser numerico.") from exc

    def _result_field(self, parent: tk.Misc, width: int = 13) -> tk.Entry:
        field = tk.Entry(
            parent,
            width=width,
            justify="right",
            relief="solid",
            bd=1,
            readonlybackground=styles.RESULT_BG_COLOR,
            fg=styles.TEXT_COLOR,
            font=("Segoe UI", 9, "bold"),
        )
        field.configure(state="readonly")
        return field

    def _set_result(self, field: tk.Entry, value: str, color: str = styles.TEXT_COLOR) -> None:
        field.configure(state="normal", fg=color)
        field.delete(0, "end")
        field.insert(0, value)
        field.configure(state="readonly")

    def _clear_results(self, fields: dict[str, tk.Entry]) -> None:
        for field in fields.values():
            self._set_result(field, "")

    def _set_text(self, widget: tk.Text, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def _copy_text(self, widget: tk.Text, feedback: tk.StringVar, empty_message: str) -> None:
        text = widget.get("1.0", "end").strip()
        if not text:
            feedback.set(empty_message)
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        feedback.set("Memória copiada.")

    @staticmethod
    def _status_label(parent: tk.Misc) -> tk.Label:
        return tk.Label(
            parent,
            text="Aguardando calculo",
            bg=styles.RESULT_BG_COLOR,
            fg="#222222",
            relief="solid",
            bd=1,
            font=("Segoe UI", 9, "bold"),
            padx=6,
            pady=5,
        )

    @staticmethod
    def _set_status(label: tk.Label, text: str, bg: str, fg: str) -> None:
        label.configure(text=text, bg=bg, fg=fg)

    @staticmethod
    def _new_group(parent: tk.Misc, title: str) -> ttk.LabelFrame:
        group = ttk.LabelFrame(parent, text=title, padding=styles.GROUP_PAD)
        group.columnconfigure(1, weight=1)
        return group

    def _add_entry_row(
        self,
        parent: ttk.LabelFrame,
        row: int,
        label: str,
        variable: tk.StringVar,
        suffix: str = "",
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
        entry = ttk.Entry(parent, textvariable=variable, width=14, justify="right")
        entry.grid(row=row, column=1, sticky="e", padx=(styles.GAP, 0), pady=2)
        self._input_fields_by_var[id(variable)] = entry
        if suffix:
            ttk.Label(parent, text=suffix).grid(row=row, column=2, sticky="w", padx=(4, 0), pady=2)

    def _add_combo_row(
        self,
        parent: ttk.LabelFrame,
        row: int,
        label: str,
        variable: tk.StringVar,
        values: tuple[str, ...],
        width: int = 24,
    ) -> ttk.Combobox:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
        combo = ttk.Combobox(
            parent,
            textvariable=variable,
            values=values,
            state="readonly",
            width=width,
        )
        combo.grid(row=row, column=1, columnspan=2, sticky="e", padx=(styles.GAP, 0), pady=2)
        return combo

    def _apply_invalid_input_style(self) -> None:
        self._clear_invalid_input_styles()
        if self._invalid_variable_id is None:
            return
        field = self._input_fields_by_var.get(self._invalid_variable_id)
        if field is not None:
            field.configure(style=styles.INVALID_ENTRY_STYLE)
            field.focus_set()

    def _clear_invalid_input_styles(self) -> None:
        for field in self._input_fields_by_var.values():
            field.configure(style=styles.DEFAULT_ENTRY_STYLE)


class PassiveAnchorageFrame(CalculatorBase):
    """Passive rebar anchorage verification."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=styles.GAP)
        self._service = AnchorageVerifierService()
        self.last_result: AnchorageResult | None = None
        self.memory_feedback_var = tk.StringVar(value="")
        self.result_fields: dict[str, tk.Entry] = {}
        self._vars = {
            "diameter": tk.StringVar(value=self._diameter_label(10.0)),
            "fck": tk.StringVar(value="30.00"),
            "steel": tk.StringVar(value=SteelType.CA50.value),
            "bond": tk.StringVar(value=BondCondition.GOOD.value),
            "effort": tk.StringVar(value=EffortType.TENSION.value),
            "anchorage": tk.StringVar(value=AnchorageType.STRAIGHT.value),
            "as_calc": tk.StringVar(value="1.00"),
            "as_ef": tk.StringVar(value="1.00"),
            "available": tk.StringVar(value="50.00"),
        }
        self._build_ui()
        self._bind_vars()
        self.recalculate()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=0, column=0, sticky="nsew")
        self.tabs.add(self._verification_tab(), text="Verificação")
        self.tabs.add(self._memory_tab(), text="Memória de cálculo")

    def _verification_tab(self) -> ttk.Frame:
        tab = ttk.Frame(self.tabs, padding=(0, styles.GAP, 0, 0))
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)

        inputs = ttk.Frame(tab)
        inputs.grid(row=0, column=0, sticky="nsw", padx=(0, styles.GAP))
        for row, group in enumerate(
            (self._properties_group(inputs), self._conditions_group(inputs), self._steel_area_group(inputs))
        ):
            group.grid(row=row, column=0, sticky="ew", pady=(0 if row == 0 else styles.GAP, 0))

        right = ttk.Frame(tab)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        self._results_group(right).grid(row=0, column=0, sticky="ew")

        sketch_group = ttk.LabelFrame(right, text="Representação Gráfica", padding=(6, 10, 6, 6))
        sketch_group.grid(row=1, column=0, sticky="nsew", pady=(styles.GAP, 0))
        sketch_group.columnconfigure(0, weight=1)
        sketch_group.rowconfigure(0, weight=1)
        self.sketch = AnchorageSketchCanvas(sketch_group)
        self.sketch.grid(row=0, column=0, sticky="nsew")
        return tab

    def _properties_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = self._new_group(parent, "Propriedades")
        self._add_combo_row(group, 0, "Bitola", self._vars["diameter"], self._diameter_labels())
        self._add_entry_row(group, 1, "Fck", self._vars["fck"], "MPa")
        self._add_combo_row(group, 2, "Aço", self._vars["steel"], STEEL_OPTIONS)
        return group

    def _conditions_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = self._new_group(parent, "Condicoes")
        self._add_combo_row(group, 0, "Aderencia", self._vars["bond"], BOND_OPTIONS)
        self._add_combo_row(group, 1, "Solicitacao", self._vars["effort"], EFFORT_OPTIONS)
        self.anchorage_combo = self._add_combo_row(
            group,
            2,
            "Ancoragem",
            self._vars["anchorage"],
            ANCHORAGE_TENSION_OPTIONS,
        )
        self.anchorage_rule_hint = ttk.Label(
            group,
            text="Ganchos nao sao considerados para barras comprimidas.",
            foreground=styles.INVALID_TEXT_COLOR,
            wraplength=190,
        )
        return group

    def _steel_area_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = self._new_group(parent, "Armadura e Espaco")
        self._add_entry_row(group, 0, "As,calc", self._vars["as_calc"], "cm2")
        self._add_entry_row(group, 1, "As,ef", self._vars["as_ef"], "cm2")
        self._add_entry_row(group, 2, "Comp. disp.", self._vars["available"], "cm")
        return group

    def _results_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = ttk.LabelFrame(parent, text="Resultados", padding=styles.GROUP_PAD)
        group.columnconfigure(1, weight=1)
        self.status_label = self._status_label(group)
        self.status_label.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, styles.GAP))
        rows = (
            ("fbd_mpa", "Tensão aderência fbd (MPa)"),
            ("lb_cm", "C. básico lb (cm)"),
            ("lb_min_cm", "C. mínimo lb,min (cm)"),
            ("lb_nec_cm", "C. necessário lb,nec (cm)"),
            ("required_as_ef_cm2", "As,ef necessária (cm2)"),
        )
        for row, (key, label) in enumerate(rows, start=1):
            ttk.Label(group, text=f"{label}:").grid(row=row, column=0, sticky="w", pady=2)
            field = self._result_field(group)
            field.grid(row=row, column=1, sticky="e", pady=2)
            self.result_fields[key] = field
        link = ttk.Label(group, text="Memória completa", foreground=styles.LINK_COLOR)
        link.grid(row=len(rows) + 1, column=0, columnspan=2, pady=(styles.GAP, 0))
        link.bind("<Button-1>", lambda _event: self.tabs.select(1))
        return group

    def _memory_tab(self) -> ttk.Frame:
        tab, self.memory_text = build_memory_tab(self.tabs, self.copy_memory, self.memory_feedback_var)
        return tab

    def _bind_vars(self) -> None:
        for variable in self._vars.values():
            variable.trace_add("write", lambda *_args: self.recalculate())

    def recalculate(self) -> None:
        self._invalid_variable_id = None
        self._refresh_anchorage_options()
        try:
            data = self._read_input()
            result = self._service.calculate(data)
            memory = self._service.build_calculation_memory(data, result)
        except ValidationError as exc:
            self.last_result = None
            self._show_validation_error(exc)
            return
        self._clear_invalid_input_styles()
        self.last_result = result
        self._update_status(result.anchorage_is_ok)
        self._update_results(result)
        self._set_text(self.memory_text, memory)
        self.sketch.update_sketch(
            anchorage_type=data.anchorage_type,
            diameter_mm=data.diameter_mm,
            available_anchorage_cm=data.available_anchorage_cm,
            required_anchorage_cm=result.lb_nec_cm,
            minimum_anchorage_cm=result.lb_min_cm,
            required_as_ef_cm2=result.required_as_ef_cm2,
            anchorage_is_ok=result.anchorage_is_ok,
        )

    def copy_memory(self) -> None:
        self._copy_text(self.memory_text, self.memory_feedback_var, "Nenhuma memória disponível.")

    def _read_input(self) -> AnchorageInput:
        return AnchorageInput(
            diameter_mm=self._diameter_value(self._vars["diameter"].get()),
            fck_mpa=self._parse_float(self._vars["fck"], "Fck"),
            steel_type=SteelType(self._vars["steel"].get()),
            bond_condition=BondCondition(self._vars["bond"].get()),
            effort_type=EffortType(self._vars["effort"].get()),
            anchorage_type=AnchorageType(self._vars["anchorage"].get()),
            as_calc_cm2=self._parse_float(self._vars["as_calc"], "As,calc"),
            as_ef_cm2=self._parse_float(self._vars["as_ef"], "As,ef"),
            available_anchorage_cm=self._parse_float(self._vars["available"], "Comprimento disponivel"),
        )

    def _refresh_anchorage_options(self) -> None:
        effort = self._vars["effort"].get()
        options = (
            ANCHORAGE_COMPRESSION_OPTIONS
            if effort == EffortType.COMPRESSION.value
            else ANCHORAGE_TENSION_OPTIONS
        )
        if tuple(self.anchorage_combo["values"]) != options:
            self.anchorage_combo.configure(values=options)
        if self._vars["anchorage"].get() not in options:
            self._vars["anchorage"].set(AnchorageType.STRAIGHT.value)
            return
        if effort == EffortType.COMPRESSION.value:
            self.anchorage_rule_hint.grid(row=3, column=0, columnspan=3, sticky="w", pady=(4, 0))
        else:
            self.anchorage_rule_hint.grid_remove()

    def _update_status(self, ok: bool) -> None:
        if ok:
            self._set_status(self.status_label, "VERIFICAÇÃO APROVADA", styles.OK_BG_COLOR, styles.OK_TEXT_COLOR)
        else:
            self._set_status(self.status_label, "VERIFICAÇÃO REPROVADA", styles.FAIL_BG_COLOR, styles.FAIL_TEXT_COLOR)

    def _update_results(self, result: AnchorageResult) -> None:
        values = {
            "fbd_mpa": f"{result.fbd_mpa:.3f}",
            "lb_cm": f"{result.lb_cm:.2f}",
            "lb_min_cm": f"{result.lb_min_cm:.2f}",
            "lb_nec_cm": f"{result.lb_nec_cm:.2f}",
            "required_as_ef_cm2": self._required_as_text(result),
        }
        for key, value in values.items():
            color = styles.TEXT_COLOR
            if key in {"lb_nec_cm", "required_as_ef_cm2"}:
                color = styles.OK_TEXT_COLOR if result.anchorage_is_ok else styles.ERROR_TEXT_COLOR
            self._set_result(self.result_fields[key], value, color)

    @staticmethod
    def _required_as_text(result: AnchorageResult) -> str:
        if result.anchorage_is_ok:
            return "-"
        if result.required_as_ef_cm2 is None:
            return "N/A"
        return f"{result.required_as_ef_cm2:.2f}"

    def _show_validation_error(self, error: ValidationError) -> None:
        self._apply_invalid_input_style()
        self._set_status(self.status_label, "ENTRADA INVÁLIDA", styles.INVALID_BG_COLOR, styles.INVALID_TEXT_COLOR)
        self._clear_results(self.result_fields)
        self._set_text(
            self.memory_text,
            "ENTRADA INVÁLIDA\n\n"
            f"{error}\n\n"
            "A memória de cálculo será atualizada automaticamente após a correção.",
        )
        self.sketch.update_sketch(
            anchorage_type=AnchorageType.STRAIGHT,
            diameter_mm=0.0,
            available_anchorage_cm=0.0,
            required_anchorage_cm=0.0,
            minimum_anchorage_cm=0.0,
            required_as_ef_cm2=None,
            anchorage_is_ok=False,
        )

    @staticmethod
    def _diameter_labels() -> tuple[str, ...]:
        return tuple(PassiveAnchorageFrame._diameter_label(item.diameter_mm) for item in COMMERCIAL_REBAR_DIAMETERS)

    @staticmethod
    def _diameter_label(value: float) -> str:
        return f"{value:.1f} mm".replace(".", ",")

    @staticmethod
    def _diameter_value(label: str) -> float:
        return float(label.replace(" mm", "").replace(",", "."))


class LapSpliceFrame(CalculatorBase):
    """Lap splice verification."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=styles.GAP)
        self._service = LapSpliceService()
        self.last_result: LapSpliceResult | None = None
        self.memory_feedback_var = tk.StringVar(value="")
        self.result_fields: dict[str, tk.Entry] = {}
        self.warning_var = tk.StringVar(value="")
        self.alpha0t_var = tk.StringVar(value="")
        self._vars = {
            "diameter_1": tk.StringVar(value=PassiveAnchorageFrame._diameter_label(10.0)),
            "diameter_2": tk.StringVar(value=PassiveAnchorageFrame._diameter_label(10.0)),
            "fck": tk.StringVar(value="30.00"),
            "steel": tk.StringVar(value=SteelType.CA50.value),
            "bond": tk.StringVar(value=BondCondition.GOOD.value),
            "effort": tk.StringVar(value=EffortType.TENSION.value),
            "anchorage": tk.StringVar(value=AnchorageType.STRAIGHT.value),
            "as_calc": tk.StringVar(value="1.00"),
            "as_ef": tk.StringVar(value="1.00"),
            "proportion": tk.StringVar(value=self._proportion_labels()[0]),
            "clear_distance": tk.StringVar(value="0.00"),
            "available": tk.StringVar(value="60.00"),
        }
        self._build_ui()
        self._bind_vars()
        self.recalculate()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=0, column=0, sticky="nsew")
        self.tabs.add(self._verification_tab(), text="Verificação")
        self.tabs.add(self._memory_tab(), text="Memória de cálculo")

    def _verification_tab(self) -> ttk.Frame:
        tab = ttk.Frame(self.tabs, padding=(0, styles.GAP, 0, 0))
        tab.columnconfigure(1, weight=1)
        inputs = ttk.Frame(tab)
        inputs.grid(row=0, column=0, sticky="nw", padx=(0, styles.GAP))
        for row, group in enumerate(
            (self._properties_group(inputs), self._conditions_group(inputs), self._splice_group(inputs))
        ):
            group.grid(row=row, column=0, sticky="ew", pady=(0 if row == 0 else styles.GAP, 0))
        ttk.Label(
            inputs,
            textvariable=self.warning_var,
            foreground=styles.WARNING_TEXT_COLOR,
            wraplength=240,
        ).grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(styles.GAP, 0),
        )
        self._results_group(tab).grid(row=0, column=1, sticky="new")
        return tab

    def _properties_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = self._new_group(parent, "Propriedades")
        labels = PassiveAnchorageFrame._diameter_labels()
        self._add_combo_row(group, 0, "Bitola barra 1", self._vars["diameter_1"], labels)
        self._add_combo_row(group, 1, "Bitola barra 2", self._vars["diameter_2"], labels)
        self._add_entry_row(group, 2, "Fck", self._vars["fck"], "MPa")
        self._add_combo_row(group, 3, "Aço", self._vars["steel"], STEEL_OPTIONS)
        return group

    def _conditions_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = self._new_group(parent, "Condicoes")
        self._add_combo_row(group, 0, "Aderencia", self._vars["bond"], BOND_OPTIONS)
        self._add_combo_row(group, 1, "Solicitacao", self._vars["effort"], EFFORT_OPTIONS)
        self.anchorage_combo = self._add_combo_row(group, 2, "Ancoragem base", self._vars["anchorage"], ANCHORAGE_TENSION_OPTIONS)
        self.anchorage_rule_hint = ttk.Label(
            group,
            text="Ganchos nao sao considerados para barras comprimidas.",
            foreground=styles.INVALID_TEXT_COLOR,
            wraplength=190,
        )
        return group

    def _splice_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = self._new_group(parent, "Transpasse")
        self._add_entry_row(group, 0, "As,calc", self._vars["as_calc"], "cm2")
        self._add_entry_row(group, 1, "As,ef", self._vars["as_ef"], "cm2")
        self.proportion_label = ttk.Label(group, text="Prop. emendada")
        self.proportion_label.grid(row=2, column=0, sticky="w", pady=2)
        self.proportion_combo = ttk.Combobox(
            group,
            textvariable=self._vars["proportion"],
            values=self._proportion_labels(),
            state="readonly",
            width=24,
        )
        self.proportion_combo.grid(row=2, column=1, columnspan=2, sticky="e", padx=(styles.GAP, 0), pady=2)
        self.alpha0t_label = ttk.Label(group, text="alpha0t")
        self.alpha0t_label.grid(row=3, column=0, sticky="w", pady=2)
        self.alpha0t_entry = tk.Entry(
            group,
            textvariable=self.alpha0t_var,
            width=14,
            justify="right",
            relief="solid",
            bd=1,
        )
        self.alpha0t_entry.configure(state="readonly", readonlybackground=styles.RESULT_BG_COLOR)
        self.alpha0t_entry.grid(row=3, column=1, sticky="e", padx=(styles.GAP, 0), pady=2)
        self._add_entry_row(group, 4, "Dist. livre", self._vars["clear_distance"], "cm")
        self._add_entry_row(group, 5, "Ldisp", self._vars["available"], "cm")
        return group

    def _results_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = ttk.LabelFrame(parent, text="Resultados", padding=styles.GROUP_PAD)
        group.columnconfigure(1, weight=1)
        self.status_label = self._status_label(group)
        self.status_label.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, styles.GAP))
        rows = (
            ("fbd_mpa", "fbd (MPa)"),
            ("lb_cm", "lb (cm)"),
            ("lb_nec_cm", "lb,nec (cm)"),
            ("lap_min_cm", "l0,min (cm)"),
            ("clear_distance_addition_cm", "Acrescimo (cm)"),
            ("required_lap_cm", "l0 final (cm)"),
            ("available_lap_cm", "Ldisp (cm)"),
            ("deficit_cm", "Deficit (cm)"),
        )
        for row, (key, label) in enumerate(rows, start=1):
            ttk.Label(group, text=f"{label}:").grid(row=row, column=0, sticky="w", pady=2)
            field = self._result_field(group)
            field.grid(row=row, column=1, sticky="e", pady=2)
            self.result_fields[key] = field
        link = ttk.Label(group, text="Memória completa", foreground=styles.LINK_COLOR)
        link.grid(row=len(rows) + 1, column=0, columnspan=2, pady=(styles.GAP, 0))
        link.bind("<Button-1>", lambda _event: self.tabs.select(1))
        return group

    def _memory_tab(self) -> ttk.Frame:
        tab, self.memory_text = build_memory_tab(self.tabs, self.copy_memory, self.memory_feedback_var)
        return tab

    def _bind_vars(self) -> None:
        for variable in self._vars.values():
            variable.trace_add("write", lambda *_args: self.recalculate())

    def recalculate(self) -> None:
        self._invalid_variable_id = None
        self._refresh_anchorage_options()
        try:
            data = self._read_input()
            result = self._service.calculate(data)
            memory = self._service.build_calculation_memory(data, result)
        except ValidationError as exc:
            self.last_result = None
            self._show_validation_error(exc)
            return
        self._clear_invalid_input_styles()
        self.last_result = result
        self._set_status(
            self.status_label,
            "VERIFICAÇÃO APROVADA" if result.lap_is_ok else "VERIFICAÇÃO REPROVADA",
            styles.OK_BG_COLOR if result.lap_is_ok else styles.FAIL_BG_COLOR,
            styles.OK_TEXT_COLOR if result.lap_is_ok else styles.FAIL_TEXT_COLOR,
        )
        self._update_results(result, data.available_lap_cm)
        self._update_warnings(result)
        self._set_text(self.memory_text, memory)

    def copy_memory(self) -> None:
        self._copy_text(self.memory_text, self.memory_feedback_var, "Nenhuma memória disponível.")

    def _read_input(self) -> LapSpliceInput:
        return LapSpliceInput(
            diameter_1_mm=PassiveAnchorageFrame._diameter_value(self._vars["diameter_1"].get()),
            diameter_2_mm=PassiveAnchorageFrame._diameter_value(self._vars["diameter_2"].get()),
            fck_mpa=self._parse_float(self._vars["fck"], "Fck"),
            steel_type=SteelType(self._vars["steel"].get()),
            bond_condition=BondCondition(self._vars["bond"].get()),
            effort_type=EffortType(self._vars["effort"].get()),
            anchorage_type=AnchorageType(self._vars["anchorage"].get()),
            as_calc_cm2=self._parse_float(self._vars["as_calc"], "As,calc"),
            as_ef_cm2=self._parse_float(self._vars["as_ef"], "As,ef"),
            spliced_bars_percent=self._proportion_value(self._vars["proportion"].get()),
            clear_distance_cm=self._parse_float(self._vars["clear_distance"], "Distancia livre"),
            available_lap_cm=self._parse_float(self._vars["available"], "Comprimento disponivel"),
        )

    def _refresh_anchorage_options(self) -> None:
        effort = self._vars["effort"].get()
        options = (
            ANCHORAGE_COMPRESSION_OPTIONS
            if effort == EffortType.COMPRESSION.value
            else ANCHORAGE_TENSION_OPTIONS
        )
        if tuple(self.anchorage_combo["values"]) != options:
            self.anchorage_combo.configure(values=options)
        if self._vars["anchorage"].get() not in options:
            self._vars["anchorage"].set(AnchorageType.STRAIGHT.value)
            return
        visible = effort == EffortType.TENSION.value
        if visible:
            self.proportion_label.grid()
            self.proportion_combo.grid()
            self.alpha0t_label.grid()
            self.alpha0t_entry.grid()
        else:
            self.proportion_label.grid_remove()
            self.proportion_combo.grid_remove()
            self.alpha0t_label.grid_remove()
            self.alpha0t_entry.grid_remove()
        if effort == EffortType.COMPRESSION.value:
            self.anchorage_rule_hint.grid(row=3, column=0, columnspan=3, sticky="w", pady=(4, 0))
        else:
            self.anchorage_rule_hint.grid_remove()

    def _update_results(self, result: LapSpliceResult, available_lap_cm: float) -> None:
        self.alpha0t_var.set("N/A" if result.alpha0t is None else f"{result.alpha0t:.2f} ({result.alpha0t_label})")
        values = {
            "fbd_mpa": f"{result.fbd_mpa:.3f}",
            "lb_cm": f"{result.lb_cm:.2f}",
            "lb_nec_cm": f"{result.lb_nec_cm:.2f}",
            "lap_min_cm": f"{result.lap_min_cm:.2f}",
            "clear_distance_addition_cm": f"{result.clear_distance_addition_cm:.2f}",
            "required_lap_cm": f"{result.required_lap_cm:.2f}",
            "available_lap_cm": f"{available_lap_cm:.2f}",
            "deficit_cm": f"{result.deficit_cm:.2f}",
        }
        for key, value in values.items():
            color = styles.TEXT_COLOR
            if key in {"required_lap_cm", "available_lap_cm", "deficit_cm"}:
                color = styles.OK_TEXT_COLOR if result.lap_is_ok else styles.ERROR_TEXT_COLOR
            self._set_result(self.result_fields[key], value, color)

    def _update_warnings(self, result: LapSpliceResult) -> None:
        warnings: list[str] = []
        if result.requires_transverse_reinforcement:
            warnings.append("Armadura transversal: " + "; ".join(result.transverse_reinforcement_reasons) + ".")
        if result.clear_distance_addition_cm > 0:
            warnings.append("Distancia livre > 4 phi: acrescimo aplicado.")
        if result.spacing_warning:
            warnings.append("Conferir distancia livre >= max(2 phi; 20 mm).")
        self.warning_var.set("\n".join(warnings))

    def _show_validation_error(self, error: ValidationError) -> None:
        self._apply_invalid_input_style()
        self._set_status(self.status_label, "ENTRADA INVÁLIDA", styles.INVALID_BG_COLOR, styles.INVALID_TEXT_COLOR)
        self._clear_results(self.result_fields)
        self.alpha0t_var.set("")
        self.warning_var.set(str(error))
        self._set_text(self.memory_text, "ENTRADA INVÁLIDA\n\n" f"{error}")

    @staticmethod
    def _proportion_labels() -> tuple[str, ...]:
        labels = []
        for bracket in ALPHA0T_BRACKETS:
            labels.append(f"{bracket.label} | alpha0t = {bracket.value:.1f}")
        return tuple(labels)

    @staticmethod
    def _proportion_value(label: str) -> float:
        for bracket in ALPHA0T_BRACKETS:
            if label.startswith(bracket.label):
                return bracket.max_percent if bracket.max_percent is not None else 100.0
        raise ValidationError("Proporcao de barras emendadas invalida.")


class PrestressingAnchorageFrame(CalculatorBase):
    """Bonded prestressing anchorage verification."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=styles.GAP)
        self._service = PrestressingAnchorageService()
        self.last_result: PrestressingAnchorageResult | None = None
        self.memory_feedback_var = tk.StringVar(value="")
        self.result_fields: dict[str, tk.Entry] = {}
        self._steel_labels = {spec.label: key for key, spec in PRESTRESSING_STEEL_SPECS.items()}
        self._vars = {
            "steel": tk.StringVar(value=PRESTRESSING_STEEL_SPECS["STRAND_CP190_RB_12_7"].label),
            "fck": tk.StringVar(value="30.00"),
            "stress": tk.StringVar(value="1000.00"),
            "available": tk.StringVar(value="80.00"),
            "bond": tk.StringVar(value=PrestressingBondCondition.GOOD.value),
        }
        self._build_ui()
        self._bind_vars()
        self.recalculate()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=0, column=0, sticky="nsew")
        self.tabs.add(self._verification_tab(), text="Verificação")
        self.tabs.add(self._memory_tab(), text="Memória de cálculo")

    def _verification_tab(self) -> ttk.Frame:
        tab = ttk.Frame(self.tabs, padding=(0, styles.GAP, 0, 0))
        tab.columnconfigure(1, weight=1)
        inputs = ttk.Frame(tab)
        inputs.grid(row=0, column=0, sticky="nw", padx=(0, styles.GAP))
        data_group = self._new_group(inputs, "Dados")
        data_group.grid(row=0, column=0, sticky="ew")
        self._add_combo_row(data_group, 0, "Produto", self._vars["steel"], tuple(self._steel_labels.keys()), width=30)
        self._add_entry_row(data_group, 1, "Fck", self._vars["fck"], "MPa")
        self._add_entry_row(data_group, 2, "Tensão no aço", self._vars["stress"], "MPa")
        self._add_entry_row(data_group, 3, "Ldisp", self._vars["available"], "cm")
        self._add_combo_row(data_group, 4, "Aderencia", self._vars["bond"], PRESTRESSING_BOND_OPTIONS)
        ttk.Label(
            inputs,
            text=(
                "A tensão informada deve ser definida pelo engenheiro "
                "para a etapa de verificação desejada."
            ),
            style="Muted.TLabel",
            wraplength=260,
        ).grid(row=1, column=0, sticky="ew", pady=(styles.GAP, 0))
        self._results_group(tab).grid(row=0, column=1, sticky="new")
        return tab

    def _results_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = ttk.LabelFrame(parent, text="Resultados", padding=styles.GROUP_PAD)
        group.columnconfigure(1, weight=1)
        self.status_label = self._status_label(group)
        self.status_label.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, styles.GAP))
        rows = (
            ("fbpd_mpa", "fbpd (MPa)"),
            ("steel_force_kn", "Fp,d (kN)"),
            ("required_anchorage_cm", "Lnec (cm)"),
            ("available_anchorage_cm", "Ldisp (cm)"),
            ("deficit_cm", "Deficit (cm)"),
        )
        for row, (key, label) in enumerate(rows, start=1):
            ttk.Label(group, text=f"{label}:").grid(row=row, column=0, sticky="w", pady=2)
            field = self._result_field(group)
            field.grid(row=row, column=1, sticky="e", pady=2)
            self.result_fields[key] = field
        link = ttk.Label(group, text="Memória detalhada", foreground=styles.LINK_COLOR)
        link.grid(row=len(rows) + 1, column=0, columnspan=2, pady=(styles.GAP, 0))
        link.bind("<Button-1>", lambda _event: self.tabs.select(1))
        return group

    def _memory_tab(self) -> ttk.Frame:
        tab, self.memory_text = build_memory_tab(self.tabs, self.copy_memory, self.memory_feedback_var)
        return tab

    def _bind_vars(self) -> None:
        for variable in self._vars.values():
            variable.trace_add("write", lambda *_args: self.recalculate())

    def recalculate(self) -> None:
        self._invalid_variable_id = None
        try:
            data = self._read_input()
            result = self._service.calculate(data)
            memory = self._service.build_calculation_memory(data, result)
        except ValidationError as exc:
            self.last_result = None
            self._show_validation_error(exc)
            return
        self._clear_invalid_input_styles()
        self.last_result = result
        self._set_status(
            self.status_label,
            "VERIFICAÇÃO APROVADA" if result.anchorage_is_ok else "VERIFICAÇÃO REPROVADA",
            styles.OK_BG_COLOR if result.anchorage_is_ok else styles.FAIL_BG_COLOR,
            styles.OK_TEXT_COLOR if result.anchorage_is_ok else styles.FAIL_TEXT_COLOR,
        )
        self._update_results(result)
        self._set_text(self.memory_text, memory)

    def copy_memory(self) -> None:
        self._copy_text(self.memory_text, self.memory_feedback_var, "Nenhuma memória disponível.")

    def _read_input(self) -> PrestressingAnchorageInput:
        return PrestressingAnchorageInput(
            steel_key=self._steel_labels[self._vars["steel"].get()],
            fck_mpa=self._parse_float(self._vars["fck"], "Fck"),
            steel_stress_mpa=self._parse_float(self._vars["stress"], "Tensão no aço"),
            available_anchorage_cm=self._parse_float(self._vars["available"], "Comprimento disponivel"),
            bond_condition=PrestressingBondCondition(self._vars["bond"].get()),
        )

    def _update_results(self, result: PrestressingAnchorageResult) -> None:
        values = {
            "fbpd_mpa": f"{result.fbpd_mpa:.3f}",
            "steel_force_kn": f"{result.steel_force_kn:.3f}",
            "required_anchorage_cm": f"{result.required_anchorage_cm:.2f}",
            "available_anchorage_cm": f"{result.available_anchorage_cm:.2f}",
            "deficit_cm": f"{result.deficit_cm:.2f}",
        }
        for key, value in values.items():
            color = styles.TEXT_COLOR
            if key in {"required_anchorage_cm", "deficit_cm"}:
                color = styles.OK_TEXT_COLOR if result.anchorage_is_ok else styles.ERROR_TEXT_COLOR
            self._set_result(self.result_fields[key], value, color)

    def _show_validation_error(self, error: ValidationError) -> None:
        self._apply_invalid_input_style()
        self._set_status(self.status_label, "ENTRADA INVÁLIDA", styles.INVALID_BG_COLOR, styles.INVALID_TEXT_COLOR)
        self._clear_results(self.result_fields)
        self._set_text(self.memory_text, "ENTRADA INVÁLIDA\n\n" f"{error}")


def build_memory_tab(
    master: tk.Misc,
    copy_command: object,
    feedback_variable: tk.StringVar,
) -> tuple[ttk.Frame, tk.Text]:
    """Create a memory tab with a copy button and scrollable text."""
    tab = ttk.Frame(master, padding=styles.GAP)
    tab.columnconfigure(0, weight=1)
    tab.rowconfigure(1, weight=1)

    toolbar = ttk.Frame(tab)
    toolbar.grid(row=0, column=0, sticky="ew", pady=(0, styles.GAP))
    ttk.Button(toolbar, text="Copiar Memória", command=copy_command).grid(row=0, column=0, sticky="w")
    ttk.Label(toolbar, textvariable=feedback_variable, style="Muted.TLabel").grid(
        row=0,
        column=1,
        sticky="w",
        padx=(styles.GAP, 0),
    )

    text_frame = ttk.Frame(tab)
    text_frame.grid(row=1, column=0, sticky="nsew")
    text_frame.columnconfigure(0, weight=1)
    text_frame.rowconfigure(0, weight=1)
    text = tk.Text(
        text_frame,
        wrap="none",
        font=("Consolas", 9),
        bg=styles.SURFACE_COLOR,
        fg=styles.TEXT_COLOR,
        relief="solid",
        bd=1,
    )
    text.grid(row=0, column=0, sticky="nsew")
    scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    text.configure(yscrollcommand=scrollbar.set)
    return tab, text
