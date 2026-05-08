"""Tkinter main window for the parallel UI migration."""

from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk
from typing import Callable

from app.tk_ui import styles
from app.tk_ui.calculators.anchorage_calculator import AnchorageCalculatorFrame
from app.tk_ui.calculators.lifting_calculator import LiftingCalculatorFrame
from app.tk_ui.utilities.rebar_converter import RebarConverterFrame


@dataclass(frozen=True)
class TkWindowDefinition:
    """Metadata required to show and open a placeholder Tkinter window."""

    id: str
    title: str
    window_title: str
    width: int = styles.PLACEHOLDER_WIDTH
    height: int = styles.PLACEHOLDER_HEIGHT
    frame_factory: Callable[[tk.Misc], ttk.Frame] | None = None


CALCULATOR_DEFINITIONS: tuple[TkWindowDefinition, ...] = (
    TkWindowDefinition(
        id="lifting",
        title="Alça de içamento",
        window_title="GN Pré - Alça de Içamento V 1.0",
        width=styles.LIFTING_WIDTH,
        height=styles.LIFTING_HEIGHT,
        frame_factory=LiftingCalculatorFrame,
    ),
    TkWindowDefinition(
        id="anchorage",
        title="Comprimento de ancoragem",
        window_title="GN Pré - Ancoragem V 1.0",
        width=styles.ANCHORAGE_WIDTH,
        height=styles.ANCHORAGE_HEIGHT,
        frame_factory=AnchorageCalculatorFrame,
    ),
)

UTILITY_DEFINITIONS: tuple[TkWindowDefinition, ...] = (
    TkWindowDefinition(
        id="rebar_converter",
        title="Conversor bitola/espaçamento",
        window_title="GN Pré - Conversor de Armadura V 1.0",
        width=styles.REBAR_CONVERTER_WIDTH,
        height=styles.REBAR_CONVERTER_HEIGHT,
        frame_factory=RebarConverterFrame,
    ),
)


class TkMainWindow(tk.Tk):
    """Home window and navigation controller for the Tkinter migration."""

    def __init__(self) -> None:
        super().__init__()
        self._child_windows: dict[str, tk.Toplevel] = {}
        self._definitions = {
            definition.id: definition
            for definition in (*CALCULATOR_DEFINITIONS, *UTILITY_DEFINITIONS)
        }
        self._configure_root()
        self._configure_style()
        self._build_home()

    def _configure_root(self) -> None:
        self.title(styles.APP_TITLE)
        self.configure(bg=styles.BG_COLOR)
        self.resizable(False, False)
        self.geometry(f"{styles.HOME_WIDTH}x{styles.HOME_HEIGHT}")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 9), foreground=styles.TEXT_COLOR)
        style.configure("TFrame", background=styles.BG_COLOR)
        style.configure("TLabelframe", background=styles.PANEL_COLOR)
        style.configure("TLabelframe.Label", background=styles.BG_COLOR)
        style.configure("TLabel", background=styles.BG_COLOR)
        style.configure("Title.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Muted.TLabel", foreground=styles.MUTED_TEXT_COLOR)
        style.configure(
            "TButton",
            padding=(10, 6),
            background=styles.SURFACE_COLOR,
            bordercolor="#9ca3af",
            lightcolor=styles.SURFACE_COLOR,
            darkcolor="#9ca3af",
        )
        style.map(
            "TButton",
            background=[("active", "#f3f4f6"), ("pressed", "#e5e7eb")],
            bordercolor=[("focus", "#2563eb")],
        )
        style.configure("TNotebook", background=styles.BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(12, 5), background="#f3f4f6")
        style.map("TNotebook.Tab", background=[("selected", styles.SURFACE_COLOR)])
        style.configure(
            styles.INVALID_ENTRY_STYLE,
            fieldbackground=styles.INVALID_BG_COLOR,
            foreground=styles.INVALID_TEXT_COLOR,
            bordercolor=styles.INVALID_BORDER_COLOR,
            lightcolor=styles.INVALID_BORDER_COLOR,
            darkcolor=styles.INVALID_BORDER_COLOR,
        )

    def _build_home(self) -> None:
        content = ttk.Frame(self, padding=styles.WINDOW_PAD)
        content.grid(row=0, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)

        title = ttk.Label(content, text="Calculadoras", style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w")

        subtitle = ttk.Label(content, text="Selecione uma opção.", style="Muted.TLabel")
        subtitle.grid(row=1, column=0, sticky="w", pady=(4, styles.GAP))

        calculators_group = ttk.LabelFrame(
            content,
            text="NBR 9062",
            padding=styles.GROUP_PAD,
        )
        calculators_group.grid(row=2, column=0, sticky="ew")
        calculators_group.columnconfigure(0, weight=1)
        self._add_window_buttons(calculators_group, CALCULATOR_DEFINITIONS)

        utilities_group = ttk.LabelFrame(
            content,
            text="utilidades",
            padding=styles.GROUP_PAD,
        )
        utilities_group.grid(row=3, column=0, sticky="ew", pady=(styles.GAP, 0))
        utilities_group.columnconfigure(0, weight=1)
        self._add_window_buttons(utilities_group, UTILITY_DEFINITIONS)

    def _add_window_buttons(
        self,
        parent: ttk.LabelFrame,
        definitions: tuple[TkWindowDefinition, ...],
    ) -> None:
        for row, definition in enumerate(definitions):
            button = ttk.Button(
                parent,
                text=definition.title,
                width=styles.BUTTON_WIDTH,
                command=lambda item=definition: self.open_child_window(item.id),
            )
            button.grid(row=row, column=0, sticky="ew", pady=(0 if row == 0 else styles.GAP, 0))

    def open_child_window(self, window_id: str) -> tk.Toplevel:
        """Open a child window and hide the home window."""
        definition = self._definitions[window_id]
        existing_window = self._child_windows.get(window_id)
        if existing_window is not None and existing_window.winfo_exists():
            existing_window.lift()
            return existing_window

        child = tk.Toplevel(self)
        child.title(definition.window_title)
        child.resizable(False, False)
        child.geometry(f"{definition.width}x{definition.height}")
        child.configure(bg=styles.BG_COLOR)
        child.columnconfigure(0, weight=1)
        child.rowconfigure(0, weight=1)
        child.protocol("WM_DELETE_WINDOW", lambda item=window_id: self.close_child_window(item))

        if definition.frame_factory is None:
            frame = ttk.Frame(child, padding=styles.WINDOW_PAD)
            frame.grid(row=0, column=0, sticky="nsew")
            label = ttk.Label(
                frame,
                text=f"{definition.title}\n\nTela reservada para a próxima fase.",
                justify="center",
            )
            label.grid(row=0, column=0, sticky="nsew")
        else:
            frame = definition.frame_factory(child)
            frame.grid(row=0, column=0, sticky="nsew")

        child.bind("<Escape>", lambda _event, item=window_id: self.close_child_window(item))
        child.bind("<Control-Key-1>", lambda _event, item=frame: self._select_child_tab(item, 0))
        child.bind("<Control-Key-2>", lambda _event, item=frame: self._select_child_tab(item, 1))
        child.bind("<Control-Key-3>", lambda _event, item=frame: self._select_child_tab(item, 2))
        self._child_windows[window_id] = child
        self.withdraw()
        child.lift()
        child.focus_force()
        return child

    @staticmethod
    def _select_child_tab(frame: ttk.Frame, index: int) -> str:
        if hasattr(frame, "select_tab"):
            frame.select_tab(index)
        return "break"

    def get_child_content(self, window_id: str) -> ttk.Frame | None:
        """Return the first content frame for a child window, if available."""
        child = self._child_windows.get(window_id)
        if child is None or not child.winfo_exists():
            return None
        for item in child.winfo_children():
            if isinstance(item, ttk.Frame):
                return item
        return None

    def close_child_window(self, window_id: str) -> None:
        """Close a child window and show the home window again."""
        child = self._child_windows.pop(window_id, None)
        if child is not None and child.winfo_exists():
            child.destroy()
        self.deiconify()
        self.lift()
        self.focus_force()

    def run_smoke_test(self) -> int:
        """Validate the Fase 1 navigation contract without entering mainloop."""
        self.update_idletasks()
        self.update()
        if self.state() != "normal":
            return 1
        if self.title() != styles.APP_TITLE:
            return 1

        for definition in (*CALCULATOR_DEFINITIONS, *UTILITY_DEFINITIONS):
            child = self.open_child_window(definition.id)
            self.update_idletasks()
            self.update()
            if not child.winfo_exists():
                return 1
            if child.title() != definition.window_title:
                return 1
            if self.state() != "withdrawn":
                return 1

            self.close_child_window(definition.id)
            self.update_idletasks()
            self.update()
            if self.state() != "normal":
                return 1

        child = self.open_child_window("lifting")
        self.update_idletasks()
        self.update()
        lifting_content = self.get_child_content("lifting")
        if not isinstance(lifting_content, LiftingCalculatorFrame):
            return 1
        if lifting_content.last_lifting_result is None:
            return 1
        memory = lifting_content.memory_text.get("1.0", "end")
        if "MEMORIA DE CALCULO - VERIFICACAO DE ICAMENTO" not in memory:
            return 1
        self.close_child_window("lifting")
        if child.winfo_exists():
            return 1

        child = self.open_child_window("anchorage")
        self.update_idletasks()
        self.update()
        anchorage_content = self.get_child_content("anchorage")
        if not isinstance(anchorage_content, AnchorageCalculatorFrame):
            return 1
        if anchorage_content.passive_frame.last_result is None:
            return 1
        if anchorage_content.lap_splice_frame.last_result is None:
            return 1
        if anchorage_content.prestressing_frame.last_result is None:
            return 1
        passive_memory = anchorage_content.passive_frame.memory_text.get("1.0", "end")
        lap_memory = anchorage_content.lap_splice_frame.memory_text.get("1.0", "end")
        prestressing_memory = anchorage_content.prestressing_frame.memory_text.get("1.0", "end")
        if "MEMORIA DE CALCULO - COMPRIMENTO DE ANCORAGEM" not in passive_memory:
            return 1
        if "MEMORIA DE CALCULO - EMENDA POR TRANSPASSE" not in lap_memory:
            return 1
        if "MEMORIA DE CALCULO - ANCORAGEM DE PROTENSAO ADERENTE" not in prestressing_memory:
            return 1
        anchorage_content.passive_frame._vars["effort"].set("Compressao")
        self.update_idletasks()
        self.update()
        values = tuple(anchorage_content.passive_frame.anchorage_combo["values"])
        if "Com Gancho" in values or "Com Gancho e Soldada" in values:
            return 1
        self.close_child_window("anchorage")
        if child.winfo_exists():
            return 1

        child = self.open_child_window("rebar_converter")
        self.update_idletasks()
        self.update()
        content = self.get_child_content("rebar_converter")
        if not isinstance(content, RebarConverterFrame):
            return 1
        content.original_rebar_var.set("CA-50 - 8.0 mm")
        content.original_spacing_var.set("10")
        content.equivalent_rebar_var.set("CA-50 - 16.0 mm")
        content.convert()
        self.update_idletasks()
        self.update()
        if content.equivalent_spacing_var.get() != "40.00":
            return 1
        self.close_child_window("rebar_converter")
        if child.winfo_exists():
            return 1

        self.destroy()
        return 0
