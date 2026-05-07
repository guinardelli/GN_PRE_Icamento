"""Dynamic sketch widget for passive rebar anchorage verification."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPaintEvent,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QWidget

from app.core.anchorage_models import AnchorageType

_BG_COLOR = QColor("#ffffff")
_CONCRETE_FILL = QColor("#e2e8f0")
_CONCRETE_BORDER = QColor("#7c8794")
_BAR_OK_COLOR = QColor("#10b981")
_BAR_FAIL_COLOR = QColor("#dc2626")
_BAR_NEUTRAL_COLOR = QColor("#475569")
_DIMENSION_COLOR = QColor("#1d4ed8")
_DIMENSION_FAIL_COLOR = QColor("#dc2626")
_LABEL_COLOR = QColor("#334155")
_WELD_COLOR = QColor("#0f172a")


class AnchorageSketchWidget(QWidget):
    """Renders a schematic anchorage detail for passive reinforcement."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._anchorage_type = AnchorageType.STRAIGHT
        self._diameter_mm = 10.0
        self._available_anchorage_cm = 0.0
        self._required_anchorage_cm = 0.0
        self._minimum_anchorage_cm = 0.0
        self._required_as_ef_cm2: float | None = None
        self._anchorage_is_ok = True
        self.setMinimumSize(300, 210)

    def update_sketch(
        self,
        anchorage_type: AnchorageType,
        diameter_mm: float,
        available_anchorage_cm: float,
        required_anchorage_cm: float,
        minimum_anchorage_cm: float,
        required_as_ef_cm2: float | None,
        anchorage_is_ok: bool,
    ) -> None:
        """Update sketch parameters and trigger repaint."""
        self._anchorage_type = anchorage_type
        self._diameter_mm = max(0.0, diameter_mm)
        self._available_anchorage_cm = max(0.0, available_anchorage_cm)
        self._required_anchorage_cm = max(0.0, required_anchorage_cm)
        self._minimum_anchorage_cm = max(0.0, minimum_anchorage_cm)
        self._required_as_ef_cm2 = required_as_ef_cm2
        self._anchorage_is_ok = anchorage_is_ok
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing, True)
            area = self.rect().adjusted(6, 6, -6, -6)
            if area.width() <= 0 or area.height() <= 0:
                return
            painter.fillRect(area, _BG_COLOR)
            concrete = self._build_concrete_profile(area)

            self._draw_concrete(painter, concrete)
            geometry = self._calculate_bar_geometry(area)
            self._draw_bar(painter, geometry)
            self._draw_dimensions(painter, area, geometry)
            self._draw_labels(painter, area)
        finally:
            painter.end()

    @staticmethod
    def _build_concrete_profile(area: QRectF) -> QPainterPath:
        left = area.left() + area.width() * 0.10
        top = area.top() + area.height() * 0.18
        right = area.right() - area.width() * 0.08
        bottom = area.bottom() - area.height() * 0.18
        notch_x = left + area.width() * 0.30
        notch_y_top = top + area.height() * 0.22
        notch_y_bottom = bottom - area.height() * 0.26

        path = QPainterPath()
        path.moveTo(left, top)
        path.lineTo(notch_x, top)
        path.lineTo(notch_x, notch_y_top)
        path.lineTo(right, notch_y_top)
        path.lineTo(right, notch_y_bottom)
        path.lineTo(notch_x, notch_y_bottom)
        path.lineTo(notch_x, bottom)
        path.lineTo(left, bottom)
        path.closeSubpath()
        return path

    def _draw_concrete(self, painter: QPainter, profile: QPainterPath) -> None:
        painter.setPen(QPen(_CONCRETE_BORDER, 3))
        painter.setBrush(QBrush(_CONCRETE_FILL))
        painter.drawPath(profile)

        painter.setPen(QPen(QColor("#b8bcc2"), 1, Qt.DashLine))
        rect = profile.boundingRect()
        step = 14
        x = rect.left() + step
        while x < rect.right():
            painter.drawLine(
                QPointF(x, rect.top()),
                QPointF(max(rect.left(), x - rect.height() * 0.3), rect.bottom()),
            )
            x += step

    def _calculate_bar_geometry(self, area: QRectF) -> dict[str, float]:
        left = area.left() + area.width() * 0.10
        top = area.top() + area.height() * 0.18
        right = area.right() - area.width() * 0.08
        bottom = area.bottom() - area.height() * 0.18
        notch_x = left + area.width() * 0.30
        bar_y = top + (bottom - top) * 0.44
        anchor_start_x = left + area.width() * 0.04
        max_available_width = max(20.0, notch_x - anchor_start_x)
        available_end_x = anchor_start_x + max_available_width
        ratio = 1.0
        if self._available_anchorage_cm > 0:
            ratio = max(1.0, self._required_anchorage_cm / self._available_anchorage_cm)
        extension = min((right - available_end_x) * 0.90, max_available_width * (ratio - 1.0))
        bar_end_x = max(available_end_x, min(right - 12.0, available_end_x + extension))
        return {
            "bar_y": bar_y,
            "anchor_start_x": anchor_start_x,
            "available_end_x": available_end_x,
            "bar_end_x": bar_end_x,
            "weld_x": anchor_start_x + max_available_width * 0.18,
            "hook_top_y": top + 8.0,
        }

    def _draw_bar(self, painter: QPainter, geometry: dict[str, float]) -> None:
        bar_color = _BAR_OK_COLOR if self._anchorage_is_ok else _BAR_FAIL_COLOR
        bar_y = geometry["bar_y"]
        start_x = geometry["anchor_start_x"]
        available_end_x = geometry["available_end_x"]
        bar_end_x = geometry["bar_end_x"]

        painter.setPen(QPen(bar_color, 4))
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(QPointF(start_x, bar_y), QPointF(available_end_x, bar_y))

        if bar_end_x > available_end_x + 1.0:
            painter.setPen(QPen(bar_color, 3, Qt.DashLine))
            painter.drawLine(QPointF(available_end_x, bar_y), QPointF(bar_end_x, bar_y))

        if self._anchorage_type in (AnchorageType.HOOK, AnchorageType.HOOK_WELDED):
            self._draw_hook(painter, start_x, bar_y, geometry["hook_top_y"], bar_color)

        if self._anchorage_type in (AnchorageType.WELDED, AnchorageType.HOOK_WELDED):
            self._draw_welded_bar(painter, geometry["weld_x"], bar_y)

    @staticmethod
    def _draw_hook(
        painter: QPainter,
        start_x: float,
        bar_y: float,
        hook_top_y: float,
        bar_color: QColor,
    ) -> None:
        hook_left_x = start_x - 20.0
        path = QPainterPath()
        path.moveTo(start_x, bar_y)
        path.lineTo(hook_left_x, bar_y)
        path.lineTo(hook_left_x, hook_top_y)
        path.lineTo(start_x + 28.0, hook_top_y)
        painter.setPen(QPen(bar_color, 4))
        painter.drawPath(path)

    @staticmethod
    def _draw_welded_bar(painter: QPainter, weld_x: float, bar_y: float) -> None:
        painter.setPen(QPen(_WELD_COLOR, 4))
        painter.drawLine(QPointF(weld_x, bar_y - 26), QPointF(weld_x, bar_y + 26))

        painter.setPen(QPen(_WELD_COLOR, 1.5))
        for offset in (-8.0, 8.0):
            painter.drawLine(
                QPointF(weld_x - 7, bar_y + offset),
                QPointF(weld_x + 7, bar_y + offset),
            )

    def _draw_dimensions(
        self,
        painter: QPainter,
        area: QRectF,
        geometry: dict[str, float],
    ) -> None:
        dim_color = _DIMENSION_COLOR if self._anchorage_is_ok else _DIMENSION_FAIL_COLOR
        painter.setPen(QPen(dim_color, 1.6))
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)

        dim_y = area.bottom() - 18
        x1 = geometry["anchor_start_x"]
        x2 = geometry["available_end_x"]

        painter.drawLine(QPointF(x1, dim_y), QPointF(x2, dim_y))
        painter.drawLine(QPointF(x1, dim_y - 8), QPointF(x1, dim_y + 8))
        painter.drawLine(QPointF(x2, dim_y - 8), QPointF(x2, dim_y + 8))
        painter.drawLine(QPointF(x1, dim_y), QPointF(x1 - 8, dim_y + 8))
        painter.drawLine(QPointF(x1, dim_y), QPointF(x1 + 8, dim_y + 8))
        painter.drawLine(QPointF(x2, dim_y), QPointF(x2 - 8, dim_y + 8))
        painter.drawLine(QPointF(x2, dim_y), QPointF(x2 + 8, dim_y + 8))

        painter.setPen(QPen(dim_color, 1))
        painter.drawText(
            QRectF(x1, dim_y + 8, x2 - x1, 16),
            Qt.AlignCenter,
            f"Ldisp = {self._available_anchorage_cm:.1f} cm",
        )

    def _draw_labels(self, painter: QPainter, area: QRectF) -> None:
        font = QFont()
        font.setPointSize(7)
        painter.setFont(font)

        status = "OK" if self._anchorage_is_ok else "INSUFICIENTE"
        painter.setPen(QPen(_BAR_OK_COLOR if self._anchorage_is_ok else _BAR_FAIL_COLOR, 1))
        painter.drawText(
            QRectF(area.left() + 8, area.top() + 4, area.width() - 16, 14),
            Qt.AlignLeft,
            f"Status: {status}",
        )

        painter.setPen(QPen(_LABEL_COLOR, 1))
        painter.drawText(
            QRectF(area.left() + 8, area.top() + 20, area.width() - 16, 14),
            Qt.AlignLeft,
            f"Ø {self._diameter_mm:.1f} mm | {self._anchorage_type.value}",
        )
        painter.drawText(
            QRectF(area.left() + 8, area.top() + 36, area.width() - 16, 14),
            Qt.AlignLeft,
            f"lb,nec = {self._required_anchorage_cm:.1f} cm | lb,min = {self._minimum_anchorage_cm:.1f} cm",
        )

        if not self._anchorage_is_ok:
            if self._required_as_ef_cm2 is None:
                as_text = "As,ef necessaria: N/A (Ldisp < lb,min)"
            else:
                as_text = f"As,ef necessaria = {self._required_as_ef_cm2:.2f} cm2"
            painter.setPen(QPen(_BAR_FAIL_COLOR, 1))
            painter.drawText(
                QRectF(area.left() + 8, area.top() + 52, area.width() - 16, 14),
                Qt.AlignLeft,
                as_text,
            )
