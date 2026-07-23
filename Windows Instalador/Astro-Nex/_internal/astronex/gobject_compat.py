"""Compatibility import for the former ``gobject`` module."""

from gi.repository import GObject, GLib

PARAM_READWRITE = GObject.ParamFlags.READWRITE
SIGNAL_RUN_FIRST = GObject.SignalFlags.RUN_FIRST
TYPE_NONE = GObject.TYPE_NONE
TYPE_STRING = GObject.TYPE_STRING
idle_add = GLib.idle_add
timeout_add = GLib.timeout_add
source_remove = GLib.source_remove
