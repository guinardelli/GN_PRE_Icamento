"""Canvas sketch for the Tkinter lifting calculator."""

from __future__ import annotations

import math
import tkinter as tk

from app.core.models import AnchorageType


class LiftingSketchCanvas(tk.Canvas):
    """Draw a lightweight lifting loop sketch using Tkinter Canvas."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(
            master,
            width=320,
            height=190,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#d8d8d8",
        )
        self._loops_count = 2
        self._anchorage_type = AnchorageType.HOOK_90
        self._inclination_deg = 90.0
        self._anchorage_is_ok = True
        self._capacity_is_ok = True
        self._required_anchorage_cm = 0.0
        self._available_anchorage_cm = 0.0
        self.bind("<Configure>", lambda _event: self._redraw())
        self._redraw()

    def update_sketch(
        self,
        *,
        loops_count: int,
        anchorage_type: AnchorageType,
        inclination_deg: float,
        anchorage_is_ok: bool,
        capacity_is_ok: bool,
        required_anchorage_cm: float,
        available_anchorage_cm: float,
    ) -> None:
        """Store current verification state and redraw the sketch."""
        self._loops_count = max(1, loops_count)
        self._anchorage_type = anchorage_type
        self._inclination_deg = inclination_deg
        self._anchorage_is_ok = anchorage_is_ok
        self._capacity_is_ok = capacity_is_ok
        self._required_anchorage_cm = required_anchorage_cm
        self._available_anchorage_cm = available_anchorage_cm
        self._redraw()

    def _redraw(self) -> None:
        self.delete("all")
        width = max(self.winfo_width(), 300)
        height = max(self.winfo_height(), 170)

        ok_color = "#0b6b2b"
        fail_color = "#c62828"
        status_color = ok_color if self._capacity_is_ok and self._anchorage_is_ok else fail_color
        concrete_top = height * 0.58
        concrete_bottom = height * 0.78
        concrete_left = width * 0.12
        concrete_right = width * 0.88

        self.create_text(
            width / 2,
            15,
            text="Representacao grafica",
            fill="#334155",
            font=("Segoe UI", 9, "bold"),
        )
        self.create_rectangle(
            concrete_left,
            concrete_top,
            concrete_right,
            concrete_bottom,
            fill="#e2e8f0",
            outline="#94a3b8",
            width=2,
        )
        self.create_text(
            concrete_left + 8,
            concrete_bottom + 12,
            anchor="w",
            text="Peca de concreto",
            fill="#475569",
            font=("Segoe UI", 8),
        )

        loop_centers = self._loop_centers(concrete_left, concrete_right)
        hook_y = height * 0.17
        sling_color = "#475569"
        strand_color = status_color
        angle = min(max(self._inclination_deg, 1.0), 90.0)
        horizontal_shift = (90.0 - angle) / 90.0 * 42.0

        for center_x in loop_centers:
            leg_gap = 26
            left_leg = center_x - leg_gap / 2
            right_leg = center_x + leg_gap / 2
            top_y = concrete_top - 48
            hook_x = center_x - horizontal_shift

            self.create_line(
                hook_x,
                hook_y,
                left_leg,
                top_y,
                fill=sling_color,
                width=2,
            )
            self.create_line(
                hook_x,
                hook_y,
                right_leg,
                top_y,
                fill=sling_color,
                width=2,
            )
            self.create_oval(
                hook_x - 5,
                hook_y - 5,
                hook_x + 5,
                hook_y + 5,
                outline=sling_color,
                width=2,
            )
            self.create_line(
                left_leg,
                top_y,
                left_leg,
                concrete_bottom - 12,
                right_leg,
                concrete_bottom - 12,
                right_leg,
                top_y,
                smooth=True,
                fill=strand_color,
                width=3,
            )
            self._draw_anchorage_end(left_leg, concrete_bottom - 12, strand_color, -1)
            self._draw_anchorage_end(right_leg, concrete_bottom - 12, strand_color, 1)

        self.create_text(
            width / 2,
            height - 29,
            text=(
                f"Anc. disp. {self._available_anchorage_cm:.1f} cm  |  "
                f"Anc. nec. {self._required_anchorage_cm:.1f} cm"
            ),
            fill="#1d4ed8" if self._anchorage_is_ok else fail_color,
            font=("Segoe UI", 8, "bold"),
        )
        self.create_text(
            width / 2,
            height - 12,
            text=(
                f"{self._loops_count} alca(s) - inclinacao {self._inclination_deg:.1f} graus"
            ),
            fill="#475569",
            font=("Segoe UI", 8),
        )

    def _loop_centers(self, left: float, right: float) -> list[float]:
        if self._loops_count == 1:
            return [(left + right) / 2]
        count = min(self._loops_count, 4)
        span = right - left
        margin = span * 0.18
        usable = span - 2 * margin
        return [
            left + margin + (usable * index / (count - 1))
            for index in range(count)
        ]

    def _draw_anchorage_end(
        self,
        x_coord: float,
        y_coord: float,
        color: str,
        direction: int,
    ) -> None:
        if self._anchorage_type == AnchorageType.STRAIGHT:
            self.create_line(x_coord, y_coord, x_coord, y_coord - 30, fill=color, width=3)
            return

        if self._anchorage_type == AnchorageType.HOOK_90:
            self.create_line(x_coord, y_coord, x_coord, y_coord - 24, fill=color, width=3)
            self.create_line(
                x_coord,
                y_coord,
                x_coord + direction * 24,
                y_coord,
                fill=color,
                width=3,
            )
            return

        radius = 11
        start = 0 if direction < 0 else 180
        self.create_arc(
            x_coord - radius,
            y_coord - radius,
            x_coord + radius,
            y_coord + radius,
            start=start,
            extent=180,
            style=tk.ARC,
            outline=color,
            width=3,
        )
        self.create_line(x_coord, y_coord - radius, x_coord, y_coord - 28, fill=color, width=3)


def inclination_to_radians(inclination_deg: float) -> float:
    """Return inclination in radians for smoke tests and future refinements."""
    return math.radians(inclination_deg)
