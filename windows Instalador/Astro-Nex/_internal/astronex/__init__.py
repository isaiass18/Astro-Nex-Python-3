"""Astro-Nex package bootstrap."""

# Install the GTK 3 bridge before any legacy GUI module is imported.  PyGObject
# deliberately rejects the old top-level module names, so they must already be
# present in sys.modules when legacy modules execute their imports.
import sys

from . import gobject_compat as _gobject
from . import gtk_compat as _gtk
from . import pango_compat as _pango
from . import pangocairo_compat as _pangocairo

sys.modules["gtk"] = _gtk
sys.modules["gobject"] = _gobject
sys.modules["pango"] = _pango
sys.modules["pangocairo"] = _pangocairo
