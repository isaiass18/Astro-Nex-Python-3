"""PyInstaller entry point for the macOS application bundle."""

import sys
from pathlib import Path

from astronex import nex
from astronex.extensions.path import path


if getattr(sys, "frozen", False):
    app_path = path(Path(sys._MEIPASS))
else:
    app_path = path(Path(__file__).resolve().parent)

nex.main(app_path)
