# -*- mode: python ; coding: utf-8 -*-
"""Lean PyInstaller spec for the GN_PRE_Icamento Windows executable."""

from __future__ import annotations

from fnmatch import fnmatch


EXCLUDED_BINARY_PATTERNS = (
    "PySide6/opengl32sw.dll",
    "PySide6/Qt6Network.dll",
    "PySide6/QtNetwork.pyd",
    "PySide6/Qt6OpenGL.dll",
    "PySide6/Qt6Pdf.dll",
    "PySide6/Qt6Qml*.dll",
    "PySide6/Qt6Quick*.dll",
    "PySide6/Qt6Svg.dll",
    "PySide6/plugins/generic/*",
    "PySide6/plugins/iconengines/*",
    "PySide6/plugins/imageformats/*",
    "PySide6/plugins/platforminputcontexts/*",
    "PySide6/plugins/platforms/qdirect2d.dll",
    "PySide6/plugins/platforms/qminimal.dll",
    "PySide6/Qt6VirtualKeyboard.dll",
)


def keep_binary(entry: tuple[str, str, str]) -> bool:
    target = entry[0].replace("\\", "/")
    return not any(fnmatch(target, pattern) for pattern in EXCLUDED_BINARY_PATTERNS)


def keep_data(entry: tuple[str, str, str]) -> bool:
    target = entry[0].replace("\\", "/")
    if fnmatch(target, "PySide6/translations/*"):
        return target.endswith("_pt_BR.qm")
    return True


a = Analysis(
    ["../app/main.py"],
    pathex=[".."],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PySide6.QtNetwork",
        "PySide6.QtOpenGL",
        "PySide6.QtPdf",
        "PySide6.QtPrintSupport",
        "PySide6.QtQml",
        "PySide6.QtQuick",
        "PySide6.QtSvg",
    ],
    noarchive=False,
    optimize=2,
)
a.binaries = [entry for entry in a.binaries if keep_binary(entry)]
a.datas = [entry for entry in a.datas if keep_data(entry)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="GN_PRE_Icamento",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="GN_PRE_Icamento",
)
