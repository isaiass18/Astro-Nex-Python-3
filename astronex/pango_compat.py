"""Compatibility import for the former ``pango`` module."""

from gi.repository import Pango

# PyGTK represented Pango rectangles as indexable tuples.  Rendering code uses
# that convention extensively; GTK 3 exposes named rectangle fields instead.
Pango.Rectangle.__getitem__ = lambda rectangle, index: (
    rectangle.x, rectangle.y, rectangle.width, rectangle.height
)[index]

ALIGN_LEFT = Pango.Alignment.LEFT
ALIGN_CENTER = Pango.Alignment.CENTER
ALIGN_RIGHT = Pango.Alignment.RIGHT
ELLIPSIZE_END = Pango.EllipsizeMode.END
SCALE = Pango.SCALE
STYLE_ITALIC = Pango.Style.ITALIC
STYLE_NORMAL = Pango.Style.NORMAL
TAB_LEFT = Pango.TabAlign.LEFT
WEIGHT_BOLD = Pango.Weight.BOLD
WEIGHT_NORMAL = Pango.Weight.NORMAL
FontDescription = Pango.FontDescription
TabArray = Pango.TabArray
