"""SVG export for lifting verification drawings."""

from __future__ import annotations

from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

from app.core.models import LiftingInput, LiftingResult, STRAND_SPECS

SVG_NS = "http://www.w3.org/2000/svg"
SVG_WIDTH = 900
SVG_HEIGHT = 560


def export_lifting_svg(
    file_path: str | Path,
    data: LiftingInput,
    result: LiftingResult,
) -> None:
    """Write a lifting verification SVG file."""
    target = Path(file_path)
    if target.exists() and target.is_dir():
        raise OSError("Caminho de exportacao SVG aponta para uma pasta.")
    if not target.parent.exists():
        raise OSError("Pasta de destino do SVG nao existe.")

    target.write_text(build_lifting_svg(data, result), encoding="utf-8")


def build_lifting_svg(data: LiftingInput, result: LiftingResult) -> str:
    """Build an SVG document from lifting input and result data."""
    strand = STRAND_SPECS[data.strand_key]
    is_approved = result.capacity_is_ok and result.anchorage_is_ok
    status_color = "#15803d" if is_approved else "#b91c1c"
    strand_color = "#10b981" if is_approved else "#dc2626"

    root = Element(
        "svg",
        {
            "xmlns": SVG_NS,
            "width": str(SVG_WIDTH),
            "height": str(SVG_HEIGHT),
            "viewBox": f"0 0 {SVG_WIDTH} {SVG_HEIGHT}",
            "role": "img",
        },
    )
    SubElement(root, "title").text = "Verificacao de icamento"
    SubElement(root, "desc").text = (
        "Desenho tecnico simplificado e resumo dos resultados de icamento."
    )
    style = SubElement(root, "style")
    style.text = """
        text { font-family: Segoe UI, Arial, sans-serif; fill: #111827; }
        .label { font-size: 16px; }
        .small { font-size: 13px; fill: #374151; }
        .title { font-size: 24px; font-weight: 700; }
        .mono { font-family: Consolas, monospace; font-size: 14px; }
    """

    _add_background(root)
    _add_header(root, data, is_approved, status_color)
    _add_lifting_drawing(root, data, result, strand_color)
    _add_result_summary(root, data, result, strand.label, status_color)

    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
        root,
        encoding="unicode",
        short_empty_elements=True,
    )


def _add_background(root: Element) -> None:
    SubElement(
        root,
        "rect",
        {
            "x": "0",
            "y": "0",
            "width": str(SVG_WIDTH),
            "height": str(SVG_HEIGHT),
            "fill": "#ffffff",
        },
    )


def _add_header(
    root: Element,
    data: LiftingInput,
    is_approved: bool,
    status_color: str,
) -> None:
    SubElement(
        root,
        "text",
        {"x": "32", "y": "42", "class": "title"},
    ).text = "Verificacao de icamento com cordoalhas"
    piece_id = data.piece_id.strip() or "-"
    SubElement(
        root,
        "text",
        {"x": "32", "y": "70", "class": "small"},
    ).text = f"Identificacao da peca: {piece_id}"
    SubElement(
        root,
        "text",
        {"x": "700", "y": "44", "class": "label", "fill": status_color},
    ).text = "APROVADO" if is_approved else "REPROVADO"


def _add_lifting_drawing(
    root: Element,
    data: LiftingInput,
    result: LiftingResult,
    strand_color: str,
) -> None:
    drawing = SubElement(root, "g", {"id": "desenho"})
    concrete_x = 72
    concrete_y = 280
    concrete_w = 470
    concrete_h = 160
    hook_x = concrete_x + concrete_w / 2
    hook_y = 130

    SubElement(
        drawing,
        "rect",
        {
            "x": str(concrete_x),
            "y": str(concrete_y),
            "width": str(concrete_w),
            "height": str(concrete_h),
            "fill": "#e2e8f0",
            "stroke": "#64748b",
            "stroke-width": "2",
        },
    )
    SubElement(
        drawing,
        "text",
        {
            "x": str(concrete_x + concrete_w / 2),
            "y": "465",
            "class": "small",
            "text-anchor": "middle",
        },
    ).text = "CONCRETO"

    loops_count = max(1, min(20, data.loops_count))
    margin = concrete_w * 0.14
    usable = concrete_w - 2 * margin
    if loops_count == 1:
        positions = [concrete_x + concrete_w / 2]
    else:
        spacing = usable / (loops_count - 1)
        positions = [concrete_x + margin + i * spacing for i in range(loops_count)]

    for cx in positions:
        _add_loop(drawing, cx, concrete_y, concrete_h, hook_x, hook_y, strand_color)

    SubElement(
        drawing,
        "circle",
        {
            "cx": str(hook_x),
            "cy": str(hook_y),
            "r": "10",
            "fill": "none",
            "stroke": "#0f172a",
            "stroke-width": "3",
        },
    )
    SubElement(
        drawing,
        "text",
        {"x": str(hook_x + 16), "y": str(hook_y - 10), "class": "label"},
    ).text = "T"
    SubElement(
        drawing,
        "text",
        {"x": "72", "y": "505", "class": "small"},
    ).text = (
        f"{loops_count} alca(s), {result.total_legs} perna(s), "
        f"inclinacao {data.inclination_deg:.1f} graus"
    )


def _add_loop(
    drawing: Element,
    cx: float,
    concrete_y: float,
    concrete_h: float,
    hook_x: float,
    hook_y: float,
    strand_color: str,
) -> None:
    leg_gap = 14
    top_y = concrete_y
    bottom_y = concrete_y + concrete_h * 0.72
    curve_y = concrete_y - 48
    left_x = cx - leg_gap
    right_x = cx + leg_gap

    SubElement(
        drawing,
        "path",
        {
            "d": (
                f"M {left_x:.1f} {top_y:.1f} "
                f"C {left_x:.1f} {curve_y:.1f}, {right_x:.1f} {curve_y:.1f}, "
                f"{right_x:.1f} {top_y:.1f}"
            ),
            "fill": "none",
            "stroke": strand_color,
            "stroke-width": "4",
        },
    )
    for x in (left_x, right_x):
        SubElement(
            drawing,
            "line",
            {
                "x1": f"{x:.1f}",
                "y1": f"{top_y:.1f}",
                "x2": f"{x:.1f}",
                "y2": f"{bottom_y:.1f}",
                "stroke": strand_color,
                "stroke-width": "4",
            },
        )
    SubElement(
        drawing,
        "line",
        {
            "x1": f"{cx:.1f}",
            "y1": f"{curve_y:.1f}",
            "x2": f"{hook_x:.1f}",
            "y2": f"{hook_y:.1f}",
            "stroke": "#475569",
            "stroke-width": "2",
        },
    )


def _add_result_summary(
    root: Element,
    data: LiftingInput,
    result: LiftingResult,
    strand_label: str,
    status_color: str,
) -> None:
    summary = SubElement(root, "g", {"id": "resumo"})
    x = 585
    y = 112
    lines = [
        f"Cordoalha: {strand_label}",
        f"Peso peca: {result.piece_weight_tf:.3f} tf",
        f"Peso majorado: {result.majorated_weight_tf:.3f} tf",
        f"Capacidade governante: {result.max_supported_load_tf:.3f} tf",
        f"Utilizacao: {result.utilization_ratio:.1%}",
        f"FS: {result.safety_factor:.2f}",
        f"Anc. necessaria: {result.required_anchorage_cm:.2f} cm",
        f"Anc. disponivel: {data.available_anchorage_cm:.2f} cm",
        f"fbpd,j: {result.fbpd_j_mpa:.3f} MPa",
        f"fbpd,28: {result.fbpd_28_mpa:.3f} MPa",
    ]
    SubElement(
        summary,
        "rect",
        {
            "x": str(x - 18),
            "y": str(y - 34),
            "width": "285",
            "height": "330",
            "fill": "#f8fafc",
            "stroke": "#cbd5e1",
        },
    )
    SubElement(
        summary,
        "text",
        {"x": str(x), "y": str(y), "class": "label", "fill": status_color},
    ).text = "Resumo do calculo"
    for index, line in enumerate(lines, start=1):
        SubElement(
            summary,
            "text",
            {"x": str(x), "y": str(y + index * 28), "class": "mono"},
        ).text = line
