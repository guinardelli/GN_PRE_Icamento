"""Tkinter lifting calculator."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.core.exceptions import ValidationError
from app.core.models import (
    STRAND_SPECS,
    AnchorageType,
    BondCondition,
    LiftingInput,
    LiftingResult,
)
from app.core.services import LiftingVerifierService
from app.tk_ui import styles
from app.tk_ui.sketches.lifting_sketch import LiftingSketchCanvas


BOND_OPTIONS: dict[str, BondCondition] = {
    "Boa aderencia": BondCondition.GOOD,
    "Ma aderencia": BondCondition.POOR,
}

ANCHORAGE_OPTIONS: dict[str, AnchorageType] = {
    "Reta (sem dobra) - alpha = 1,00": AnchorageType.STRAIGHT,
    "Dobra 90 graus - alpha = 0,70": AnchorageType.HOOK_90,
    "Gancho 180 graus - alpha = 0,50": AnchorageType.HOOK_180,
}


class LiftingCalculatorFrame(ttk.Frame):
    """Tkinter port of the lifting verification calculator."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=styles.WINDOW_PAD)
        self._service = LiftingVerifierService()
        self.last_lifting_data: LiftingInput | None = None
        self.last_lifting_result: LiftingResult | None = None
        self.result_fields: dict[str, tk.Entry] = {}
        self.input_fields: dict[str, ttk.Entry] = {}
        self._invalid_input_key: str | None = None
        self._input_vars = self._create_input_vars()
        self.memory_feedback_var = tk.StringVar(value="")
        self._build_ui()
        self._bind_auto_calculation()
        self.recalculate()

    def _create_input_vars(self) -> dict[str, tk.StringVar]:
        return {
            "fckj": tk.StringVar(value="15.00"),
            "fck_28": tk.StringVar(value="40.00"),
            "volume": tk.StringVar(value="1.000"),
            "unit_weight": tk.StringVar(value="2.500"),
            "strand": tk.StringVar(value="CP 190-RB 12,7 mm"),
            "inclination": tk.StringVar(value="90.0"),
            "available_anchorage": tk.StringVar(value="60.00"),
            "bond": tk.StringVar(value="Boa aderencia"),
            "anchorage_type": tk.StringVar(value="Dobra 90 graus - alpha = 0,70"),
            "loops": tk.StringVar(value="2"),
            "beta_a": tk.StringVar(value="3.00"),
            "gamma_n": tk.StringVar(value="1.30"),
        }

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=0, column=0, sticky="nsew")
        self.tabs.add(self._build_verification_tab(), text="Verificação")
        self.tabs.add(self._build_memory_tab(), text="Memória de Cálculo")

    def select_tab(self, index: int) -> None:
        if 0 <= index < len(self.tabs.tabs()):
            self.tabs.select(index)

    def _build_verification_tab(self) -> ttk.Frame:
        tab = ttk.Frame(self.tabs, padding=(0, styles.GAP, 0, 0))
        tab.columnconfigure(0, weight=0)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)

        input_panel = self._build_input_panel(tab)
        input_panel.grid(row=0, column=0, sticky="nsw", padx=(0, styles.GAP))

        right_panel = ttk.Frame(tab)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)

        results = self._build_results_panel(right_panel)
        results.grid(row=0, column=0, sticky="ew")

        sketch_group = ttk.LabelFrame(
            right_panel,
            text="Representação Gráfica",
            padding=(6, 10, 6, 6),
        )
        sketch_group.grid(row=1, column=0, sticky="nsew", pady=(styles.GAP, 0))
        sketch_group.columnconfigure(0, weight=1)
        sketch_group.rowconfigure(0, weight=1)
        self.sketch = LiftingSketchCanvas(sketch_group)
        self.sketch.grid(row=0, column=0, sticky="nsew")

        return tab

    def _build_input_panel(self, parent: tk.Misc) -> ttk.Frame:
        panel = ttk.Frame(parent)
        for row, group in enumerate(
            (
                self._build_piece_group(panel),
                self._build_materials_group(panel),
                self._build_lifting_group(panel),
                self._build_anchorage_group(panel),
                self._build_coefficients_group(panel),
            )
        ):
            group.grid(row=row, column=0, sticky="ew", pady=(0 if row == 0 else styles.GAP, 0))
        return panel

    def _build_piece_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = self._new_group(parent, "Peça")
        self._add_entry_row(group, 0, "Volume", "volume", "m3")
        self._add_entry_row(group, 1, "Peso especifico", "unit_weight", "tf/m3")
        return group

    def _build_materials_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = self._new_group(parent, "Materiais")
        self._add_entry_row(group, 0, "Fck,j", "fckj", "MPa")
        self._add_entry_row(group, 1, "Fck,28", "fck_28", "MPa")
        self._add_combo_row(group, 2, "Cordoalha", "strand", tuple(STRAND_SPECS.keys()))
        return group

    def _build_lifting_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = self._new_group(parent, "Içamento")
        self._add_entry_row(group, 0, "Inclinação", "inclination", "graus")
        self._add_entry_row(group, 1, "Número de alças", "loops", "")
        return group

    def _build_anchorage_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = self._new_group(parent, "Ancoragem")
        self._add_entry_row(group, 0, "Comprimento", "available_anchorage", "cm")
        self._add_combo_row(group, 1, "Tipo", "anchorage_type", tuple(ANCHORAGE_OPTIONS.keys()))
        self._add_combo_row(group, 2, "Aderencia", "bond", tuple(BOND_OPTIONS.keys()))
        return group

    def _build_coefficients_group(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = self._new_group(parent, "Coeficientes")
        self._add_entry_row(group, 0, "Beta a", "beta_a", "")
        self._add_entry_row(group, 1, "Gamma n", "gamma_n", "")
        return group

    def _build_results_panel(self, parent: tk.Misc) -> ttk.LabelFrame:
        group = ttk.LabelFrame(parent, text="Resultados", padding=styles.GROUP_PAD)
        group.columnconfigure(1, weight=1)

        self.status_label = tk.Label(
            group,
            text="Aguardando calculo",
            bg=styles.RESULT_BG_COLOR,
            fg="#222222",
            relief="solid",
            bd=1,
            font=("Segoe UI", 9, "bold"),
            padx=6,
            pady=5,
        )
        self.status_label.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, styles.GAP))

        result_rows = (
            ("utilization", "Taxa de utilizacao"),
            ("safety_factor", "Fator de seguranca (FS)"),
            ("piece_weight_tf", "Peso da peca (tf)"),
            ("majorated_weight_tf", "Peso majorado (tf)"),
            ("tension_per_loop_tf", "Carga por alca (tf)"),
            ("required_anchorage_cm", "Anc. necessaria (cm)"),
            ("available_anchorage_cm", "Anc. disponivel (cm)"),
        )
        for row, (key, label) in enumerate(result_rows, start=1):
            ttk.Label(group, text=f"{label}:").grid(row=row, column=0, sticky="w", pady=2)
            field = self._result_field(group)
            field.grid(row=row, column=1, sticky="e", pady=2)
            self.result_fields[key] = field

        memory_link = ttk.Label(group, text="Memória completa", foreground=styles.LINK_COLOR)
        memory_link.grid(row=len(result_rows) + 1, column=0, columnspan=2, pady=(styles.GAP, 0))
        memory_link.bind("<Button-1>", lambda _event: self.tabs.select(1))
        return group

    def _build_memory_tab(self) -> ttk.Frame:
        tab = ttk.Frame(self.tabs, padding=styles.GAP)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(tab)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, styles.GAP))
        copy_button = ttk.Button(toolbar, text="Copiar Memória", command=self.copy_memory)
        copy_button.grid(row=0, column=0, sticky="w")
        feedback = ttk.Label(toolbar, textvariable=self.memory_feedback_var, style="Muted.TLabel")
        feedback.grid(row=0, column=1, sticky="w", padx=(styles.GAP, 0))

        text_frame = ttk.Frame(tab)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.memory_text = tk.Text(
            text_frame,
            wrap="none",
            font=("Consolas", 9),
            bg=styles.SURFACE_COLOR,
            fg=styles.TEXT_COLOR,
            relief="solid",
            bd=1,
        )
        self.memory_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.memory_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.memory_text.configure(yscrollcommand=scrollbar.set)
        return tab

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
        key: str,
        suffix: str,
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
        field = ttk.Entry(parent, textvariable=self._input_vars[key], width=14, justify="right")
        field.grid(row=row, column=1, sticky="e", padx=(styles.GAP, 0), pady=2)
        self.input_fields[key] = field
        if suffix:
            ttk.Label(parent, text=suffix).grid(row=row, column=2, sticky="w", padx=(4, 0), pady=2)

    def _add_combo_row(
        self,
        parent: ttk.LabelFrame,
        row: int,
        label: str,
        key: str,
        values: tuple[str, ...],
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
        combo = ttk.Combobox(
            parent,
            textvariable=self._input_vars[key],
            values=values,
            state="readonly",
            width=24,
        )
        combo.grid(row=row, column=1, columnspan=2, sticky="e", padx=(styles.GAP, 0), pady=2)

    @staticmethod
    def _result_field(parent: tk.Misc) -> tk.Entry:
        field = tk.Entry(
            parent,
            width=13,
            justify="right",
            relief="solid",
            bd=1,
            readonlybackground=styles.RESULT_BG_COLOR,
            fg=styles.TEXT_COLOR,
            font=("Segoe UI", 9, "bold"),
        )
        field.configure(state="readonly")
        return field

    def _bind_auto_calculation(self) -> None:
        for variable in self._input_vars.values():
            variable.trace_add("write", lambda *_args: self.recalculate())

    def recalculate(self) -> None:
        """Read fields, calculate and refresh all result widgets."""
        self._invalid_input_key = None
        try:
            data = self._read_input()
            result = self._service.calculate(data)
            memory = self._service.build_calculation_memory(data, result)
        except ValidationError as exc:
            self._show_validation_error(exc)
            return

        self._clear_invalid_input_styles()
        self.last_lifting_data = data
        self.last_lifting_result = result
        self._update_status(result)
        self._update_result_fields(result, data.available_anchorage_cm)
        self._set_memory(memory)
        self.sketch.update_sketch(
            loops_count=data.loops_count,
            anchorage_type=data.anchorage_type,
            inclination_deg=data.inclination_deg,
            anchorage_is_ok=result.anchorage_is_ok,
            capacity_is_ok=result.capacity_is_ok,
            required_anchorage_cm=result.required_anchorage_cm,
            available_anchorage_cm=data.available_anchorage_cm,
        )

    def copy_memory(self) -> None:
        """Copy the current calculation memory to the clipboard."""
        text = self.memory_text.get("1.0", "end").strip()
        if not text:
            self.memory_feedback_var.set("Nenhuma memória disponível.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.memory_feedback_var.set("Memória copiada.")

    def _read_input(self) -> LiftingInput:
        bond = BOND_OPTIONS.get(self._input_vars["bond"].get())
        anchorage_type = ANCHORAGE_OPTIONS.get(self._input_vars["anchorage_type"].get())
        if bond is None:
            raise ValidationError("Condicao de aderencia invalida.")
        if anchorage_type is None:
            raise ValidationError("Tipo de ancoragem invalido.")

        return LiftingInput(
            fckj_mpa=self._parse_float("fckj", "Fck,j"),
            fck_28_mpa=self._parse_float("fck_28", "Fck,28"),
            volume_m3=self._parse_float("volume", "Volume"),
            concrete_unit_weight_tf_m3=self._parse_float(
                "unit_weight",
                "Peso especifico",
            ),
            strand_key=self._input_vars["strand"].get(),
            inclination_deg=self._parse_float("inclination", "Inclinação"),
            available_anchorage_cm=self._parse_float(
                "available_anchorage",
                "Ancoragem disponível",
            ),
            bond_condition=bond,
            anchorage_type=anchorage_type,
            loops_count=self._parse_int("loops", "Número de alças"),
            beta_a=self._parse_float("beta_a", "Beta a"),
            gamma_n=self._parse_float("gamma_n", "Gamma n"),
            piece_id="",
        )

    def _parse_float(self, key: str, label: str) -> float:
        raw_value = self._input_vars[key].get().strip().replace(",", ".")
        try:
            return float(raw_value)
        except ValueError as exc:
            self._invalid_input_key = key
            raise ValidationError(f"{label} deve ser numerico.") from exc

    def _parse_int(self, key: str, label: str) -> int:
        raw_value = self._input_vars[key].get().strip()
        try:
            return int(raw_value)
        except ValueError as exc:
            self._invalid_input_key = key
            raise ValidationError(f"{label} deve ser inteiro.") from exc

    def _update_status(self, result: LiftingResult) -> None:
        if result.capacity_is_ok and result.anchorage_is_ok:
            self._set_status(
                "VERIFICAÇÃO APROVADA",
                styles.OK_BG_COLOR,
                styles.OK_TEXT_COLOR,
                styles.OK_BORDER_COLOR,
            )
        else:
            self._set_status(
                "VERIFICAÇÃO REPROVADA",
                styles.FAIL_BG_COLOR,
                styles.FAIL_TEXT_COLOR,
                styles.FAIL_BORDER_COLOR,
            )

    def _set_status(self, text: str, bg: str, fg: str, border: str) -> None:
        self.status_label.configure(text=text, bg=bg, fg=fg, highlightbackground=border)

    def _update_result_fields(
        self,
        result: LiftingResult,
        available_anchorage_cm: float,
    ) -> None:
        values = {
            "utilization": f"{result.utilization_ratio:.1%}",
            "safety_factor": f"{result.safety_factor:.2f}",
            "piece_weight_tf": f"{result.piece_weight_tf:.3f}",
            "majorated_weight_tf": f"{result.majorated_weight_tf:.3f}",
            "tension_per_loop_tf": f"{result.tension_per_loop_tf:.3f}",
            "required_anchorage_cm": f"{result.required_anchorage_cm:.2f}",
            "available_anchorage_cm": f"{available_anchorage_cm:.2f}",
        }
        field_status = {
            "utilization": result.utilization_ratio <= 1.0,
            "safety_factor": result.safety_factor >= 1.0,
            "required_anchorage_cm": result.anchorage_is_ok,
        }
        for key, value in values.items():
            is_ok = field_status.get(key)
            color = styles.TEXT_COLOR
            if is_ok is True:
                color = styles.OK_TEXT_COLOR
            elif is_ok is False:
                color = styles.ERROR_TEXT_COLOR
            self._set_result_field(key, value, color)

    def _set_result_field(self, key: str, value: str, color: str = styles.TEXT_COLOR) -> None:
        field = self.result_fields[key]
        field.configure(state="normal", fg=color)
        field.delete(0, "end")
        field.insert(0, value)
        field.configure(state="readonly")

    def _set_memory(self, text: str) -> None:
        self.memory_text.configure(state="normal")
        self.memory_text.delete("1.0", "end")
        self.memory_text.insert("1.0", text)
        self.memory_text.configure(state="disabled")

    def _show_validation_error(self, error: ValidationError) -> None:
        self._apply_invalid_input_style()
        self.last_lifting_data = None
        self.last_lifting_result = None
        self._set_status(
            "ENTRADA INVÁLIDA",
            styles.INVALID_BG_COLOR,
            styles.INVALID_TEXT_COLOR,
            styles.INVALID_BORDER_COLOR,
        )
        self._clear_result_fields()
        self._set_memory(
            "ENTRADA INVÁLIDA\n\n"
            f"{error}\n\n"
            "A memória de cálculo será atualizada automaticamente após a correção."
        )

    def _clear_result_fields(self) -> None:
        for key in self.result_fields:
            self._set_result_field(key, "")

    def _apply_invalid_input_style(self) -> None:
        self._clear_invalid_input_styles()
        if self._invalid_input_key is None:
            return
        field = self.input_fields.get(self._invalid_input_key)
        if field is not None:
            field.configure(style=styles.INVALID_ENTRY_STYLE)
            field.focus_set()

    def _clear_invalid_input_styles(self) -> None:
        for field in self.input_fields.values():
            field.configure(style=styles.DEFAULT_ENTRY_STYLE)
