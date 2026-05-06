"""UI styles."""


def base_style() -> str:
    """Returns a modern, clean engineering theme."""
    return """
    QWidget {
        background-color: #f8fafc;
        color: #334155;
        font-family: "Segoe UI", system-ui, sans-serif;
        font-size: 10pt;
    }
    QGroupBox {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin-top: 12px;
        padding: 12px 16px;
        font-weight: 600;
        color: #0f172a;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 4px;
        color: #475569;
    }
    QPushButton {
        background-color: #0f172a;
        color: #f8fafc;
        border: 1px solid #0f172a;
        border-radius: 6px;
        padding: 10px 16px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #334155;
        border-color: #334155;
    }
    QPushButton:pressed {
        background-color: #000000;
    }
    QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QTextEdit {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 6px 8px;
        color: #0f172a;
    }
    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {
        border: 1px solid #3b82f6;
        background-color: #f0fdf4; /* Very light tint on focus */
    }
    QComboBox::drop-down {
        border-left: 1px solid #cbd5e1;
        width: 24px;
    }
    QTextEdit {
        font-family: Consolas, 'Courier New', monospace;
        font-size: 9pt;
        background-color: #f8fafc;
    }
    QTabWidget::pane {
        border: 1px solid #e2e8f0;
        background: #ffffff;
        border-radius: 4px;
    }
    QTabBar::tab {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        color: #64748b;
    }
    QTabBar::tab:selected {
        background: #ffffff;
        border-bottom-color: #ffffff;
        color: #0f172a;
        font-weight: 600;
    }
    QScrollBar:vertical {
        border: none;
        background: #f1f5f9;
        width: 10px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #cbd5e1;
        min-height: 20px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical:hover {
        background: #94a3b8;
    }
    """
