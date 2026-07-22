"""Compatibility import for the former ``pangocairo`` module."""

import gi

gi.require_version("PangoCairo", "1.0")
from gi.repository import PangoCairo


class CairoContext:
    """Restore the two Pango helpers that PyGTK added to cairo.Context."""

    def __init__(self, context):
        self._context = context

    def create_layout(self):
        return PangoCairo.create_layout(self._context)

    def show_layout(self, layout):
        return PangoCairo.show_layout(self._context, layout)

    def layout_path(self, layout):
        return PangoCairo.layout_path(self._context, layout)

    def __getattr__(self, name):
        return getattr(self._context, name)
