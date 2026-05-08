"""Canvas sketch for passive anchorage verification."""

from __future__ import annotations

import tkinter as tk

from app.core.anchorage_models import AnchorageType
from app.tk_ui import styles


class AnchorageSketchCanvas(tk.Canvas):
    """Draw a lightweight passive anchorage sketch."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(
            master,
            width=330,
            height=210,
            bg=styles.SURFACE_COLOR,
            highlightthickness=1,
            highlightbackground=styles.SKETCH_CANVAS_BORDER,
        )
        self._anchorage_type = AnchorageType.STRAIGHT
        self._diameter_mm = 10.0
        self._available_anchorage_cm = 0.0
        self._required_anchorage_cm = 0.0
        self._minimum_anchorage_cm = 0.0
        self._required_as_ef_cm2: float | None = None
        self._anchorage_is_ok = True
        self.bind("<Configure>", lambda _event: self._redraw())
        self._redraw()

    def update_sketch(
        self,
        *,
        anchorage_type: AnchorageType,
        diameter_mm: float,
        available_anchorage_cm: float,
        required_anchorage_cm: float,
        minimum_anchorage_cm: float,
        required_as_ef_cm2: float | None,
        anchorage_is_ok: bool,
    ) -> None:
        """Store the current verification state and redraw the sketch."""
        self._anchorage_type = anchorage_type
        self._diameter_mm = max(0.0, diameter_mm)
        self._available_anchorage_cm = max(0.0, available_anchorage_cm)
        self._required_anchorage_cm = max(0.0, required_anchorage_cm)
        self._minimum_anchorage_cm = max(0.0, minimum_anchorage_cm)
        self._required_as_ef_cm2 = required_as_ef_cm2
        self._anchorage_is_ok = anchorage_is_ok
        self._redraw()

    def _redraw(self) -> None:
        self.delete("all")
        width = max(self.winfo_width(), 320)
        height = max(self.winfo_height(), 190)

        ok_color = styles.OK_TEXT_COLOR
        fail_color = styles.ERROR_TEXT_COLOR
        bar_color = ok_color if self._anchorage_is_ok else fail_color
        concrete_fill = styles.SKETCH_CONCRETE_FILL
        concrete_border = styles.SKETCH_CONCRETE_BORDER
        label_color = styles.SKETCH_LABEL_COLOR

        left = width * 0.10
        right = width * 0.90
        top = height * 0.20
        bottom = height * 0.70
        notch_x = left + width * 0.28
        notch_top = top + height * 0.20
        notch_bottom = bottom - height * 0.20
        bar_y = top + (bottom - top) * 0.47
        start_x = left + 14
        available_end_x = notch_x - 6
        required_ratio = 1.0
        if self._available_anchorage_cm > 0.0:
            required_ratio = max(1.0, self._required_anchorage_cm / self._available_anchorage_cm)
        required_end_x = min(right - 12, available_end_x + (right - available_end_x) * (required_ratio - 1.0))

        points = (
            left, top,
            notch_x, top,
            notch_x, notch_top,
            right, notch_top,
            right, notch_bottom,
            notch_x, notch_bottom,
            notch_x, bottom,
            left, bottom,
        )
        self.create_polygon(points, fill=concrete_fill, outline=concrete_border, width=2)

        hatch_x = left + 14
        while hatch_x < right:
            self.create_line(hatch_x, top, hatch_x - 25, bottom, fill=styles.SKETCH_HATCH_COLOR)
            hatch_x += 16

        self.create_line(start_x, bar_y, available_end_x, bar_y, fill=bar_color, width=4)
        if required_end_x > available_end_x + 1:
            self.create_line(
                available_end_x,
                bar_y,
                required_end_x,
                bar_y,
                fill=bar_color,
                width=3,
                dash=(5, 3),
            )

        if self._anchorage_type in (AnchorageType.HOOK, AnchorageType.HOOK_WELDED):
            hook_top = top + 10
            hook_left = start_x - 22
            self.create_line(start_x, bar_y, hook_left, bar_y, hook_left, hook_top, start_x + 28, hook_top, fill=bar_color, width=4)

        if self._anchorage_type in (AnchorageType.WELDED, AnchorageType.HOOK_WELDED):
            weld_x = start_x + (available_end_x - start_x) * 0.20
            self.create_line(weld_x, bar_y - 25, weld_x, bar_y + 25, fill=styles.SKETCH_WELD_COLOR, width=4)
            self.create_line(weld_x - 8, bar_y - 8, weld_x + 8, bar_y - 8, fill=styles.SKETCH_WELD_COLOR, width=2)
            self.create_line(weld_x - 8, bar_y + 8, weld_x + 8, bar_y + 8, fill=styles.SKETCH_WELD_COLOR, width=2)

        dim_y = height - 36
        dim_color = styles.SKETCH_DIMENSION_COLOR if self._anchorage_is_ok else fail_color
        self.create_line(start_x, dim_y, available_end_x, dim_y, fill=dim_color, width=2)
        self.create_line(start_x, dim_y - 7, start_x, dim_y + 7, fill=dim_color, width=2)
        self.create_line(available_end_x, dim_y - 7, available_end_x, dim_y + 7, fill=dim_color, width=2)
        self.create_text(
            (start_x + available_end_x) / 2,
            dim_y + 14,
            text=f"Ldisp = {self._available_anchorage_cm:.1f} cm",
            fill=dim_color,
            font=("Segoe UI", 8, "bold"),
        )

        status = "OK" if self._anchorage_is_ok else "INSUFICIENTE"
        self.create_text(
            left,
            13,
            anchor="w",
            text=f"Status: {status}",
            fill=ok_color if self._anchorage_is_ok else fail_color,
            font=("Segoe UI", 8, "bold"),
        )
        self.create_text(
            left,
            30,
            anchor="w",
            text=f"Phi {self._diameter_mm:.1f} mm | {self._anchorage_type.value}",
            fill=label_color,
            font=("Segoe UI", 8),
        )
        self.create_text(
            left,
            47,
            anchor="w",
            text=f"lb,nec = {self._required_anchorage_cm:.1f} cm | lb,min = {self._minimum_anchorage_cm:.1f} cm",
            fill=label_color,
            font=("Segoe UI", 8),
        )

        if not self._anchorage_is_ok:
            if self._required_as_ef_cm2 is None:
                text = "As,ef necessaria: N/A (Ldisp < lb,min)"
            else:
                text = f"As,ef necessaria = {self._required_as_ef_cm2:.2f} cm2"
            self.create_text(left, 64, anchor="w", text=text, fill=fail_color, font=("Segoe UI", 8))
