"""Smoke tests for the lifting sketch widget."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from app.core.models import AnchorageType
from app.ui.sketch_widget import LiftingSketchWidget


class LiftingSketchWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def _render_widget(self, widget: LiftingSketchWidget, size: int = 260) -> None:
        widget.resize(size, size)
        image = QImage(size, size, QImage.Format_ARGB32)
        widget.render(image)

    def test_update_sketch_clamps_loop_count_to_supported_range(self) -> None:
        widget = LiftingSketchWidget()

        widget.update_sketch(
            loops_count=0,
            anchorage_type=AnchorageType.STRAIGHT,
            inclination_deg=60.0,
        )
        self.assertEqual(widget._loops_count, 1)

        widget.update_sketch(
            loops_count=50,
            anchorage_type=AnchorageType.STRAIGHT,
            inclination_deg=60.0,
        )
        self.assertEqual(widget._loops_count, 20)

    def test_render_handles_supported_loop_counts(self) -> None:
        for loops_count in (1, 20, 50):
            with self.subTest(loops_count=loops_count):
                widget = LiftingSketchWidget()
                widget.update_sketch(
                    loops_count=loops_count,
                    anchorage_type=AnchorageType.HOOK_180,
                    inclination_deg=45.0,
                    anchorage_is_ok=False,
                    capacity_is_ok=False,
                    required_anchorage_cm=120.0,
                    available_anchorage_cm=40.0,
                )
                self._render_widget(widget)

    def test_render_handles_aggressive_small_resize(self) -> None:
        widget = LiftingSketchWidget()
        widget.update_sketch(
            loops_count=2,
            anchorage_type=AnchorageType.HOOK_90,
            inclination_deg=5.0,
        )
        self._render_widget(widget, size=8)


if __name__ == "__main__":
    unittest.main()
