"""Tests for RebarConverterWidget."""

import os

import pytest
from PySide6.QtWidgets import QApplication, QCheckBox

from app.ui.utilities.rebar_converter_widget import RebarConverterWidget


@pytest.fixture(scope="module")
def app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    existing = QApplication.instance()
    if existing is not None:
        return existing
    return QApplication([])


def test_converter_calculates_expected_spacing(app: QApplication) -> None:
    widget = RebarConverterWidget()
    app.processEvents()

    widget.original_rebar_input.setCurrentIndex(
        widget.original_rebar_input.findText("CA-50 - 8.0 mm")
    )
    widget.original_spacing_input.setValue(10.0)
    widget.equivalent_rebar_input.setCurrentIndex(
        widget.equivalent_rebar_input.findText("CA-50 - 16.0 mm")
    )

    widget.convert_button.click()
    app.processEvents()

    assert widget.equivalent_spacing_output.text() == "40.00"


def test_converter_uses_steel_grade_from_selected_option(app: QApplication) -> None:
    widget = RebarConverterWidget()
    app.processEvents()

    widget.original_rebar_input.setCurrentIndex(
        widget.original_rebar_input.findText("CA-50 - 8.0 mm")
    )
    widget.original_spacing_input.setValue(10.0)
    widget.equivalent_rebar_input.setCurrentIndex(
        widget.equivalent_rebar_input.findText("CA-60 - 8.0 mm")
    )

    widget.convert_button.click()
    app.processEvents()

    assert widget.equivalent_spacing_output.text() == "12.00"


def test_converter_has_no_option_checkboxes(app: QApplication) -> None:
    widget = RebarConverterWidget()
    app.processEvents()

    assert widget.findChildren(QCheckBox) == []
