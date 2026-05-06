"""Dynamic lifting sketch widget that adapts to loop count and anchorage diagnostics."""

from __future__ import annotations

import math

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

from app.core.models import AnchorageType

_CONCRETE_FILL = QColor("#e2e8f0")
_CONCRETE_BORDER = QColor("#94a3b8")
_STRAND_OK_COLOR = QColor("#10b981")
_STRAND_FAIL_COLOR = QColor("#dc2626")
_SLING_COLOR = QColor("#475569")
_LABEL_COLOR = QColor("#334155")
_BG_COLOR = QColor("#ffffff")
_SURFACE_COLOR = QColor("#64748b")
_HOOK_POINT_COLOR = QColor("#0f172a")
_DIMENSION_COLOR = QColor("#1d4ed8")
_MAX_LOOPS = 20


class LiftingSketchWidget(QWidget):
    """Renders a cross-section sketch of the lifting configuration."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._loops_count: int = 2
        self._anchorage_type: AnchorageType = AnchorageType.STRAIGHT
        self._inclination_deg: float = 60.0
        self._anchorage_is_ok: bool = True
        self._capacity_is_ok: bool = True
        self._required_anchorage_cm: float = 0.0
        self._available_anchorage_cm: float = 0.0
        self.setMinimumSize(260, 220)

    def update_sketch(
        self,
        loops_count: int,
        anchorage_type: AnchorageType,
        inclination_deg: float,
        anchorage_is_ok: bool = True,
        capacity_is_ok: bool = True,
        required_anchorage_cm: float = 0.0,
        available_anchorage_cm: float = 0.0,
    ) -> None:
        """Update sketch parameters and trigger repaint."""
        self._loops_count = min(_MAX_LOOPS, max(1, loops_count))
        self._anchorage_type = anchorage_type
        self._inclination_deg = max(5.0, min(90.0, inclination_deg))
        self._anchorage_is_ok = anchorage_is_ok
        self._capacity_is_ok = capacity_is_ok
        self._required_anchorage_cm = max(0.0, required_anchorage_cm)
        self._available_anchorage_cm = max(0.0, available_anchorage_cm)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.Antialiasing, True)

            area = self.rect().adjusted(6, 6, -6, -6)
            if area.width() <= 0 or area.height() <= 0:
                return
            p.fillRect(area, _BG_COLOR)

            w = area.width()
            h = area.height()

            concrete = QRectF(
                area.left() + w * 0.10,
                area.top() + h * 0.42,
                w * 0.80,
                h * 0.46,
            )

            self._draw_concrete(p, concrete)
            self._draw_loops_and_slings(p, area, concrete)
            self._draw_anchorage_dimensions(p, area, concrete)
            self._draw_labels(p, area, concrete)
        finally:
            p.end()

    def _draw_concrete(self, p: QPainter, rect: QRectF) -> None:
        p.setPen(QPen(_CONCRETE_BORDER, 2))
        p.setBrush(QBrush(_CONCRETE_FILL))
        p.drawRect(rect)

        p.setPen(QPen(QColor("#b8bcc2"), 1, Qt.DashLine))
        step = 12
        x = rect.left() + step
        while x < rect.right():
            y_start = rect.top()
            y_end = rect.bottom()
            x_end = x - (rect.height() * 0.3)
            p.drawLine(QPointF(x, y_start), QPointF(max(rect.left(), x_end), y_end))
            x += step

        p.setPen(QPen(_SURFACE_COLOR, 2, Qt.DashDotLine))
        p.drawLine(
            QPointF(rect.left() - 6, rect.top()),
            QPointF(rect.right() + 6, rect.top()),
        )

    def _draw_loops_and_slings(self, p: QPainter, area: QRectF, concrete: QRectF) -> None:
        n = self._loops_count
        cw = concrete.width()
        cl = concrete.left()
        is_ok = self._anchorage_is_ok and self._capacity_is_ok
        strand_color = _STRAND_OK_COLOR if is_ok else _STRAND_FAIL_COLOR

        margin = cw * 0.12
        usable = cw - 2 * margin
        if n == 1:
            positions = [cl + cw / 2]
        else:
            spacing = usable / (n - 1)
            positions = [cl + margin + i * spacing for i in range(n)]

        leg_gap = min(16.0, cw * 0.06)
        loop_height_above = min(28.0, (concrete.top() - area.top()) * 0.35)
        leg_depth = concrete.height() * 0.75

        hook_x = area.left() + area.width() / 2
        hook_y = area.top() + 14

        loop_tops: list[QPointF] = []

        inclination_rad = math.radians(self._inclination_deg)
        if self._inclination_deg < 89.5:
            tan_incl = math.tan(inclination_rad)
            tilt_offset_curve = min(loop_height_above / tan_incl, leg_gap * 3)
            tilt_offset_legs = min(leg_depth / tan_incl, leg_gap * 4)
        else:
            tilt_offset_curve = 0.0
            tilt_offset_legs = 0.0

        for cx in positions:
            left_leg_x = cx - leg_gap
            right_leg_x = cx + leg_gap
            top_y = concrete.top()
            bottom_y = top_y + leg_depth

            tilt_dir = 1.0 if hook_x >= cx else -1.0
            dx_legs = -tilt_dir * tilt_offset_legs
            dx_curve = tilt_dir * tilt_offset_curve

            curve_top_y = top_y - loop_height_above

            strand_pen = QPen(strand_color, 3)
            p.setPen(strand_pen)
            p.setBrush(Qt.NoBrush)

            path = QPainterPath()
            path.moveTo(left_leg_x, top_y)
            path.cubicTo(
                left_leg_x + dx_curve,
                curve_top_y,
                right_leg_x + dx_curve,
                curve_top_y,
                right_leg_x,
                top_y,
            )
            p.drawPath(path)

            loop_top = QPointF(cx + dx_curve, curve_top_y)
            loop_tops.append(loop_top)

            left_bot_x = left_leg_x + dx_legs
            right_bot_x = right_leg_x + dx_legs

            p.save()
            p.setClipRect(concrete)

            p.setPen(strand_pen)
            p.setBrush(Qt.NoBrush)
            p.drawLine(QPointF(left_leg_x, top_y), QPointF(left_bot_x, bottom_y))
            p.drawLine(QPointF(right_leg_x, top_y), QPointF(right_bot_x, bottom_y))

            self._draw_anchorage_end(
                p,
                left_bot_x,
                bottom_y,
                leg_gap,
                is_left=True,
                leg_dx=dx_legs,
                leg_dy=leg_depth,
                strand_color=strand_color,
            )
            self._draw_anchorage_end(
                p,
                right_bot_x,
                bottom_y,
                leg_gap,
                is_left=False,
                leg_dx=dx_legs,
                leg_dy=leg_depth,
                strand_color=strand_color,
            )

            p.restore()

        p.setPen(QPen(_SLING_COLOR, 2))
        p.setBrush(Qt.NoBrush)
        for pt in loop_tops:
            p.drawLine(pt, QPointF(hook_x, hook_y))

        self._draw_hook(p, hook_x, hook_y)

        if len(loop_tops) >= 1 and self._inclination_deg < 89.5:
            self._draw_inclination_arc(p, loop_tops[0], hook_x, hook_y, concrete.top())

    def _draw_anchorage_end(
        self,
        p: QPainter,
        x: float,
        y: float,
        leg_gap: float,
        is_left: bool,
        leg_dx: float,
        leg_dy: float,
        strand_color: QColor,
    ) -> None:
        hook_len = max(8, leg_gap * 0.8)

        if self._anchorage_type == AnchorageType.STRAIGHT:
            return

        leg_len = math.hypot(leg_dx, leg_dy)
        if leg_len < 1e-6:
            leg_len = 1.0

        direction = -1.0 if is_left else 1.0
        perp_x = direction * leg_dy / leg_len
        perp_y = direction * (-leg_dx) / leg_len
        along_x = leg_dx / leg_len
        along_y = leg_dy / leg_len

        p.setPen(QPen(strand_color, 3))
        p.setBrush(Qt.NoBrush)

        if self._anchorage_type == AnchorageType.HOOK_90:
            p.drawLine(
                QPointF(x, y),
                QPointF(x + hook_len * perp_x, y + hook_len * perp_y),
            )
        elif self._anchorage_type == AnchorageType.HOOK_180:
            radius = hook_len * 0.5
            path = QPainterPath()
            path.moveTo(x, y)
            path.cubicTo(
                x + perp_x * radius * 0.5 + along_x * radius * 1.2,
                y + perp_y * radius * 0.5 + along_y * radius * 1.2,
                x + perp_x * radius * 1.5 + along_x * radius * 0.4,
                y + perp_y * radius * 1.5 + along_y * radius * 0.4,
                x + perp_x * radius - along_x * radius * 0.6,
                y + perp_y * radius - along_y * radius * 0.6,
            )
            p.drawPath(path)

    def _draw_hook(self, p: QPainter, x: float, y: float) -> None:
        r = 6.0
        p.setPen(QPen(_HOOK_POINT_COLOR, 2.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(x, y), r, r)

        tri_h = 8
        p.setPen(QPen(_SLING_COLOR, 1.5))
        p.drawLine(QPointF(x, y - r), QPointF(x, y - r - tri_h))
        p.drawLine(QPointF(x - 5, y - r - tri_h), QPointF(x + 5, y - r - tri_h))

    def _draw_inclination_arc(
        self,
        p: QPainter,
        loop_pt: QPointF,
        hook_x: float,
        hook_y: float,
        concrete_top: float,
    ) -> None:
        arc_radius = 22.0
        base_y = concrete_top
        ref_x = loop_pt.x()

        dx = hook_x - ref_x
        dy = base_y - hook_y
        if dy <= 0:
            return

        angle_from_vertical = math.degrees(math.atan2(abs(dx), dy))

        p.setPen(QPen(QColor("#9ca3af"), 1, Qt.DashLine))
        horiz_end_x = ref_x + (30 if dx >= 0 else -30)
        p.drawLine(QPointF(ref_x, base_y), QPointF(horiz_end_x, base_y))

        p.setPen(QPen(QColor("#6366f1"), 1.5))
        arc_rect = QRectF(ref_x - arc_radius, base_y - arc_radius, arc_radius * 2, arc_radius * 2)
        start_angle_qt = 90 * 16
        span = int(angle_from_vertical * 16) if dx >= 0 else -int(angle_from_vertical * 16)
        p.drawArc(arc_rect, start_angle_qt, span)

        label_angle = math.radians(90 - angle_from_vertical / 2)
        label_x = ref_x + arc_radius * 1.3 * math.cos(label_angle) * (1 if dx >= 0 else -1)
        label_y = base_y - arc_radius * 1.3 * math.sin(label_angle)
        p.setPen(QPen(QColor("#6366f1"), 1))
        font = QFont()
        font.setPointSize(7)
        font.setBold(True)
        p.setFont(font)
        p.drawText(QPointF(label_x - 8, label_y + 3), f"{self._inclination_deg:.0f}°")

    def _draw_anchorage_dimensions(self, p: QPainter, area: QRectF, concrete: QRectF) -> None:
        if self._required_anchorage_cm <= 0 and self._available_anchorage_cm <= 0:
            return

        p.setPen(QPen(_DIMENSION_COLOR, 1.2))
        font = QFont()
        font.setPointSize(7)
        font.setBold(True)
        p.setFont(font)

        x = concrete.right() - 6
        y1 = concrete.top() + 8
        y2 = concrete.bottom() - 14

        p.drawLine(QPointF(x, y1), QPointF(x, y2))
        p.drawLine(QPointF(x - 4, y1), QPointF(x + 4, y1))
        p.drawLine(QPointF(x - 4, y2), QPointF(x + 4, y2))

        required_text = f"Anc. nec.: {self._required_anchorage_cm:.1f} cm"
        available_text = f"Anc. disp.: {self._available_anchorage_cm:.1f} cm"
        status_text = "OK" if self._anchorage_is_ok else "INSUFICIENTE"

        p.setPen(QPen(_DIMENSION_COLOR, 1))
        p.drawText(
            QRectF(area.left() + 10, area.top() + 4, area.width() - 20, 14),
            Qt.AlignLeft,
            required_text,
        )
        p.drawText(
            QRectF(area.left() + 10, area.top() + 18, area.width() - 20, 14),
            Qt.AlignLeft,
            available_text,
        )

        p.setPen(QPen(_STRAND_OK_COLOR if self._anchorage_is_ok else _STRAND_FAIL_COLOR, 1))
        p.drawText(
            QRectF(area.left() + 10, area.top() + 32, area.width() - 20, 14),
            Qt.AlignLeft,
            f"Status: {status_text}",
        )

    def _draw_labels(self, p: QPainter, area: QRectF, concrete: QRectF) -> None:
        font = QFont()
        font.setPointSize(7)
        p.setFont(font)
        p.setPen(QPen(_LABEL_COLOR, 1))

        text_rect = QRectF(concrete.left(), concrete.bottom() - 18, concrete.width(), 16)
        p.drawText(text_rect, Qt.AlignCenter, "CONCRETO")

        loop_text = f"{self._loops_count} alça{'s' if self._loops_count > 1 else ''}"
        p.drawText(
            QRectF(area.left(), area.bottom() - 16, area.width() / 2, 14),
            Qt.AlignLeft | Qt.AlignBottom,
            loop_text,
        )

        anc_labels = {
            AnchorageType.STRAIGHT: "Anc. reta",
            AnchorageType.HOOK_90: "Anc. dobra 90°",
            AnchorageType.HOOK_180: "Anc. gancho 180°",
        }
        anc_text = anc_labels.get(self._anchorage_type, "")
        p.drawText(
            QRectF(area.left() + area.width() / 2, area.bottom() - 16, area.width() / 2, 14),
            Qt.AlignRight | Qt.AlignBottom,
            anc_text,
        )

        legend_rect = QRectF(area.left(), area.bottom() - 30, area.width(), 12)
        is_ok = self._anchorage_is_ok and self._capacity_is_ok
        p.setPen(QPen(_STRAND_OK_COLOR if is_ok else _STRAND_FAIL_COLOR, 1))

        if is_ok:
            legend_text = "Cordoalha: OK"
        else:
            if not self._capacity_is_ok and not self._anchorage_is_ok:
                legend_text = "Cordoalha: Cap. e Anc. insuficientes"
            elif not self._capacity_is_ok:
                legend_text = "Cordoalha: Capacidade insuficiente"
            else:
                legend_text = "Cordoalha: Ancoragem insuficiente"

        p.drawText(legend_rect, Qt.AlignLeft | Qt.AlignBottom, legend_text)

        hook_x = area.left() + area.width() / 2
        hook_y = area.top() + 14
        font.setPointSize(8)
        font.setBold(True)
        p.setFont(font)
        p.setPen(QPen(_SLING_COLOR, 1))
        p.drawText(QPointF(hook_x + 12, hook_y - 4), "T")

        arrow_top = QPointF(hook_x, hook_y - 22)
        p.setPen(QPen(_SLING_COLOR, 1.5))
        p.drawLine(QPointF(hook_x, hook_y - 6), arrow_top)
        p.drawLine(arrow_top, QPointF(hook_x - 4, arrow_top.y() + 5))
        p.drawLine(arrow_top, QPointF(hook_x + 4, arrow_top.y() + 5))
