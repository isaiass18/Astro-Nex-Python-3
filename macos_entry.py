"""PyInstaller entry point for the macOS application bundle."""

import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    app_root = Path(sys._MEIPASS)
else:
    app_root = Path(__file__).resolve().parent

# Register the bundled symbol font before importing GTK/Pango through nex.
# This is process-local and avoids asking the user to install a font manually.
# This module intentionally lives beside the entry point, not inside the
# ``astronex`` package: importing that package initializes GTK/Pango before a
# process-local font can be registered.
from macos_font import register_process_font

register_process_font(app_root / "astronex" / "resources" / "Astro-Nex.ttf")

from astronex import nex
from astronex.extensions.path import path

app_path = path(app_root)

nex.main(app_path)
