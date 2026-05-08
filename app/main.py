"""Official Tkinter application entry point."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allows running both:
# 1) from project root: python app/main.py
# 2) from app folder:   python main.py
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)


def _configure_frozen_tcl_paths() -> None:
    """Help frozen Tkinter builds find Tcl/Tk data before importing tkinter."""
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if not bundle_dir:
        return

    tcl_dir = Path(bundle_dir) / "_tcl_data"
    tk_dir = Path(bundle_dir) / "_tk_data"
    if tcl_dir.exists():
        os.environ.setdefault("TCL_LIBRARY", str(tcl_dir))
    if tk_dir.exists():
        os.environ.setdefault("TK_LIBRARY", str(tk_dir))
    os.environ.setdefault("TCLLIBPATH", str(Path(bundle_dir)))


def _run_frozen_smoke_test() -> int:
    """Validate the frozen Tk runtime without entering the full UI flow."""
    from app.tk_ui.main_window import TkMainWindow

    if TkMainWindow is None:
        return 1

    # Windowed PyInstaller executables may keep GUI/Tcl machinery alive when
    # launched by a build script. This path validates module loading, while the
    # full source smoke test validates window behavior.
    os._exit(0)


def main() -> int:
    _configure_frozen_tcl_paths()

    smoke_test = "--smoke-test" in sys.argv
    if smoke_test and getattr(sys, "frozen", False):
        return _run_frozen_smoke_test()

    from app.tk_ui.main_window import TkMainWindow

    app = TkMainWindow()
    if smoke_test:
        return app.run_smoke_test()

    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
