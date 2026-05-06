"""Tests for SVG export infrastructure."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

from app.core.models import AnchorageType, BondCondition, LiftingInput
from app.core.services import LiftingVerifierService
from app.infrastructure.svg_exporter import build_lifting_svg, export_lifting_svg


class LiftingSvgExporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = LiftingVerifierService()

    def _default_input(self, **overrides) -> LiftingInput:
        kwargs = dict(
            fckj_mpa=25.0,
            fck_28_mpa=40.0,
            volume_m3=2.0,
            concrete_unit_weight_tf_m3=2.5,
            strand_key="CP 190-RB 12,7 mm",
            inclination_deg=60.0,
            available_anchorage_cm=60.0,
            bond_condition=BondCondition.GOOD,
            anchorage_type=AnchorageType.STRAIGHT,
            loops_count=2,
            piece_id="VIGA-A1",
        )
        kwargs.update(overrides)
        return LiftingInput(**kwargs)

    def test_build_lifting_svg_returns_valid_xml(self) -> None:
        data = self._default_input()
        result = self.service.calculate(data)

        svg = build_lifting_svg(data, result)
        root = ElementTree.fromstring(svg)

        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertEqual(root.attrib["viewBox"], "0 0 900 560")

    def test_build_lifting_svg_escapes_special_characters(self) -> None:
        data = self._default_input(piece_id='Peca \u00e7 & <teste> "ok"')
        result = self.service.calculate(data)

        svg = build_lifting_svg(data, result)
        ElementTree.fromstring(svg)

        self.assertIn("&amp;", svg)
        self.assertIn("&lt;teste&gt;", svg)
        self.assertIn("Peca \u00e7", svg)

    def test_export_lifting_svg_writes_utf8_file(self) -> None:
        data = self._default_input(piece_id="Peca \u00e7")
        result = self.service.calculate(data)

        target = Path.cwd() / "desenho.svg"
        with patch.object(Path, "write_text", autospec=True) as write_text:
            export_lifting_svg(target, data, result)

        write_text.assert_called_once()
        self.assertEqual(write_text.call_args.kwargs["encoding"], "utf-8")
        content = write_text.call_args.args[1]
        self.assertIn("Verificacao de icamento", content)
        ElementTree.fromstring(content)

    def test_export_lifting_svg_rejects_invalid_paths(self) -> None:
        data = self._default_input()
        result = self.service.calculate(data)

        with self.assertRaises(OSError):
            export_lifting_svg(Path.cwd(), data, result)
        with self.assertRaises(OSError):
            export_lifting_svg(Path.cwd() / "nao_existe" / "desenho.svg", data, result)

    def test_build_lifting_svg_scales_to_multiple_loops(self) -> None:
        data = self._default_input(loops_count=8)
        result = self.service.calculate(data)

        svg = build_lifting_svg(data, result)
        root = ElementTree.fromstring(svg)
        paths = root.findall(".//{http://www.w3.org/2000/svg}path")

        self.assertEqual(len(paths), 8)
        self.assertIn("8 alca(s)", svg)


if __name__ == "__main__":
    unittest.main()
