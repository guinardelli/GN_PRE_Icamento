"""UI styles."""


def base_style() -> str:
    """Returns a compact light theme for a desktop engineering calculator."""
    return """
    QWidget {
        background-color: #f5f5f5;
        color: #111111;
        font-family: "Segoe UI", system-ui, sans-serif;
        font-size: 9pt;
    }
    QGroupBox {
        background: #fbfbfb;
        border: 1px solid #cfcfcf;
        border-radius: 0;
        margin-top: 10px;
        font-weight: 400;
        color: #111111;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 8px;
        padding: 0 4px;
        color: #111111;
        background: #f5f5f5;
    }
    QPushButton {
        background-color: #ffffff;
        color: #111111;
        border: 1px solid #0078d7;
        border-radius: 3px;
        padding: 8px 14px;
        min-height: 28px;
    }
    QPushButton:hover {
        background-color: #f0f7ff;
    }
    QPushButton:pressed {
        background-color: #dbeeff;
    }
    QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QTextEdit {
        background-color: #ffffff;
        border: 1px solid #c8c8c8;
        border-radius: 0;
        padding: 2px 4px;
        color: #111111;
        selection-background-color: #0078d7;
        selection-color: #ffffff;
    }
    QDoubleSpinBox, QSpinBox {
        min-height: 22px;
    }
    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {
        border: 1px solid #0078d7;
        background-color: #ffffff;
    }
    QLineEdit[invalid="true"],
    QDoubleSpinBox[invalid="true"],
    QSpinBox[invalid="true"],
    QComboBox[invalid="true"] {
        border: 1px solid #c62828;
        background-color: #fff0f0;
    }
    QComboBox::drop-down {
        border-left: 1px solid #c8c8c8;
        width: 20px;
    }
    QTextEdit {
        font-family: Consolas, 'Courier New', monospace;
        font-size: 9pt;
        background-color: #ffffff;
    }
    QTabWidget::pane {
        border: 1px solid #d8d8d8;
        background: #f5f5f5;
    }
    QTabBar::tab {
        background: #eeeeee;
        border: 1px solid #d8d8d8;
        padding: 6px 14px;
        margin-right: 2px;
        color: #333333;
    }
    QTabBar::tab:selected {
        background: #f5f5f5;
        border-bottom-color: #f5f5f5;
        color: #111111;
        font-weight: 700;
    }
    QScrollBar:vertical {
        border: none;
        background: #eeeeee;
        width: 10px;
    }
    QScrollBar::handle:vertical {
        background: #c0c0c0;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #a8a8a8;
    }
    """
