"""Compatibility entry point for the Tkinter application."""

from __future__ import annotations

import sys
from pathlib import Path

# Allows running both:
# 1) from project root: python app/tk_main.py
# 2) from app folder:   python tk_main.py
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)

from app.main import main


if __name__ == "__main__":
    raise SystemExit(main())
