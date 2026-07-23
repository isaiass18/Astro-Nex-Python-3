"""Small, explicit GTK 2 to GTK 3 bridge used while porting Astro-Nex.

The application used the former PyGTK bindings.  This module deliberately
keeps the old import name only at the boundary; it is backed exclusively by
PyGObject/GTK 3 and is being reduced as modules are converted to native GTK 3.
"""

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gdk, GdkPixbuf, Gtk


def _set_legacy_data(widget, key, value):
    setattr(widget, "_astronex_data_" + key.replace("-", "_"), value)


def _get_legacy_data(widget, key):
    return getattr(widget, "_astronex_data_" + key.replace("-", "_"), None)


# PyGObject intentionally disables GObject's C data store.  Astro-Nex used it
# only for small Python-side callback values, for which attributes are the
# supported replacement.
Gtk.Widget.set_data = _set_legacy_data
Gtk.Widget.get_data = _get_legacy_data
# GTK 2 exposed these as attributes; GTK 3 exposes the equivalent getters.
Gtk.Widget.allocation = property(lambda widget: widget.get_allocation())
Gtk.Widget.window = property(lambda widget: widget.get_window())
Gtk.Bin.child = property(lambda widget: widget.get_child())
Gtk.ComboBox.child = property(lambda widget: widget.get_child())
Gtk.Adjustment.lower = property(Gtk.Adjustment.get_lower, Gtk.Adjustment.set_lower)
Gtk.Adjustment.upper = property(Gtk.Adjustment.get_upper, Gtk.Adjustment.set_upper)
Gtk.Adjustment.value = property(Gtk.Adjustment.get_value, Gtk.Adjustment.set_value)
Gtk.Adjustment.page_size = property(Gtk.Adjustment.get_page_size, Gtk.Adjustment.set_page_size)

# PyGTK accepted omitted ``padding`` arguments.  Dialogs expose their content
# area as a native Gtk.Box (rather than our VBox wrapper), therefore provide
# the same defaults on Gtk.Box itself.
_gtk_box_pack_start = Gtk.Box.pack_start
_gtk_box_pack_end = Gtk.Box.pack_end


def _legacy_pack_start(box, child, expand=True, fill=True, padding=0):
    return _gtk_box_pack_start(box, child, expand, fill, padding)


def _legacy_pack_end(box, child, expand=True, fill=True, padding=0):
    return _gtk_box_pack_end(box, child, expand, fill, padding)


Gtk.Box.pack_start = _legacy_pack_start
Gtk.Box.pack_end = _legacy_pack_end

_gtk_calendar_set_display_options = Gtk.Calendar.set_display_options


def _legacy_calendar_set_display_options(calendar, options):
    return _gtk_calendar_set_display_options(
        calendar, Gtk.CalendarDisplayOptions(options)
    )


Gtk.Calendar.set_display_options = _legacy_calendar_set_display_options


def _enum(enum, name):
    return getattr(enum, name)


class HBox(Gtk.Box):
    def __init__(self, homogeneous=False, spacing=0):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL,
                         homogeneous=homogeneous, spacing=spacing)

    def pack_start(self, child, expand=True, fill=True, padding=0):
        return Gtk.Box.pack_start(self, child, expand, fill, padding)

    def pack_end(self, child, expand=True, fill=True, padding=0):
        return Gtk.Box.pack_end(self, child, expand, fill, padding)


class VBox(Gtk.Box):
    def __init__(self, homogeneous=False, spacing=0):
        super().__init__(orientation=Gtk.Orientation.VERTICAL,
                         homogeneous=homogeneous, spacing=spacing)

    def pack_start(self, child, expand=True, fill=True, padding=0):
        return Gtk.Box.pack_start(self, child, expand, fill, padding)

    def pack_end(self, child, expand=True, fill=True, padding=0):
        return Gtk.Box.pack_end(self, child, expand, fill, padding)


class Table(Gtk.Grid):
    def __init__(self, rows=1, columns=1, homogeneous=False):
        super().__init__(row_homogeneous=homogeneous,
                         column_homogeneous=homogeneous)
        self._legacy_rows = rows
        self._legacy_columns = columns

    def attach(self, child, left, right, top, bottom, *unused, **kwargs):
        return Gtk.Grid.attach(self, child, left, top, right - left, bottom - top)

    def set_row_spacings(self, spacing):
        Gtk.Grid.set_row_spacing(self, spacing)

    def set_col_spacings(self, spacing):
        Gtk.Grid.set_column_spacing(self, spacing)

    def set_row_spacing(self, *args):
        """GTK 2 accepted ``row, spacing``; GTK 3 has one global spacing."""
        Gtk.Grid.set_row_spacing(self, args[-1])

    def set_col_spacing(self, *args):
        """GTK 2 accepted ``column, spacing``; GTK 3 has global spacing."""
        Gtk.Grid.set_column_spacing(self, args[-1])

    def set_homogeneous(self, homogeneous):
        self.set_row_homogeneous(homogeneous)
        self.set_column_homogeneous(homogeneous)


class HButtonBox(Gtk.ButtonBox):
    def __init__(self, *unused):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)


class VButtonBox(Gtk.ButtonBox):
    def __init__(self, *unused):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)


class AccelGroup(Gtk.AccelGroup):
    def connect_group(self, accel_key, accel_mods, accel_flags, callback):
        return self.connect(
            accel_key,
            Gdk.ModifierType(accel_mods),
            Gtk.AccelFlags(accel_flags),
            callback,
        )


class Toolbar(Gtk.Toolbar):
    def set_tooltips(self, enabled):
        # GTK 3 removed the toolbar-wide switch; individual tool items retain
        # their tooltip text and the global setting is always effectively on.
        return None


class RadioButton(Gtk.RadioButton):
    def __init__(self, group=None, label=None):
        super().__init__(group=group, label=label)


class SpinButton(Gtk.SpinButton):
    def __init__(self, adjustment=None, climb_rate=0.0, digits=0):
        super().__init__(adjustment=adjustment, climb_rate=climb_rate, digits=digits)


class Frame(Gtk.Frame):
    """Accept the positional label used by the PyGTK ``Frame`` constructor."""
    def __init__(self, label=None):
        super().__init__()
        if label is not None:
            self.set_label(label)


class Alignment(Gtk.Alignment):
    """Keep the positional alignment constructor accepted by PyGTK."""
    def __init__(self, xalign=0.5, yalign=0.5, xscale=0.0, yscale=0.0):
        super().__init__()
        self.set(xalign, yalign, xscale, yscale)


class ColorButton(Gtk.ColorButton):
    """Accept GTK 2's ``Gdk.Color`` constructor argument."""
    def __init__(self, color=None):
        super().__init__()
        if color is not None:
            self.set_color(color)


class ComboBox(Gtk.ComboBox):
    """Allow the positional model argument used by PyGTK."""
    def __init__(self, model=None):
        super().__init__(model=model)

    def get_active_text(self):
        tree_iter = self.get_active_iter()
        if tree_iter is None:
            return None
        return self.get_model()[tree_iter][0]


def combo_box_new_text():
    return Gtk.ComboBoxText.new()


class ComboBoxEntry(Gtk.ComboBox):
    def __init__(self, model=None):
        super().__init__(model=model, has_entry=True)
        self.set_entry_text_column(0)

    def get_active_text(self):
        tree_iter = self.get_active_iter()
        if tree_iter is None:
            return None
        return self.get_model()[tree_iter][0]

    def pack_start(self, cell, expand=False):
        return Gtk.ComboBox.pack_start(self, cell, expand)


class _GdkBridge:
    _names = {
        "ACTION_COPY": Gdk.DragAction.COPY,
        "ACTION_DEFAULT": Gdk.DragAction.DEFAULT,
        "ACTION_MOVE": Gdk.DragAction.MOVE,
        "BUTTON1_MASK": Gdk.ModifierType.BUTTON1_MASK,
        "BUTTON_PRESS": Gdk.EventType.BUTTON_PRESS,
        "BUTTON_PRESS_MASK": Gdk.EventMask.BUTTON_PRESS_MASK,
        "BUTTON_RELEASE": Gdk.EventType.BUTTON_RELEASE,
        "BUTTON_RELEASE_MASK": Gdk.EventMask.BUTTON_RELEASE_MASK,
        "CONTROL_MASK": Gdk.ModifierType.CONTROL_MASK,
        "FLEUR": Gdk.CursorType.FLEUR,
        "KEY_PRESS_MASK": Gdk.EventMask.KEY_PRESS_MASK,
        "MOD1_MASK": Gdk.ModifierType.MOD1_MASK,
        "MOTION_NOTIFY": Gdk.EventType.MOTION_NOTIFY,
        "MOTION_NOTIFY_MASK": Gdk.EventMask.POINTER_MOTION_MASK,
        "POINTER_MOTION_HINT_MASK": Gdk.EventMask.POINTER_MOTION_HINT_MASK,
        "POINTER_MOTION_MASK": Gdk.EventMask.POINTER_MOTION_MASK,
        "SCROLL": Gdk.EventType.SCROLL,
        "SCROLL_DOWN": Gdk.ScrollDirection.DOWN,
        "SCROLL_UP": Gdk.ScrollDirection.UP,
        "SHIFT_MASK": Gdk.ModifierType.SHIFT_MASK,
        "WINDOW_TYPE_HINT_DIALOG": Gdk.WindowTypeHint.DIALOG,
        "WINDOW_TYPE_HINT_NORMAL": Gdk.WindowTypeHint.NORMAL,
        "_2BUTTON_PRESS": Gdk.EventType._2BUTTON_PRESS,
    }

    Rectangle = Gdk.Rectangle
    Cursor = Gdk.Cursor
    Color = Gdk.Color

    @staticmethod
    def Event(event_type):
        return Gdk.Event.new(event_type)

    @staticmethod
    def screen_width():
        screen = Gdk.Screen.get_default()
        return screen.get_monitor_geometry(screen.get_primary_monitor()).width

    @staticmethod
    def screen_height():
        screen = Gdk.Screen.get_default()
        return screen.get_monitor_geometry(screen.get_primary_monitor()).height

    @staticmethod
    def pixbuf_new_from_file(filename):
        return GdkPixbuf.Pixbuf.new_from_file(filename)

    def __getattr__(self, name):
        if name in self._names:
            return self._names[name]
        return getattr(Gdk, name)


class _Keysyms:
    def __getattr__(self, name):
        return getattr(Gdk, "KEY_" + name)


gdk = _GdkBridge()
keysyms = _Keysyms()

# Names that kept their class/function name between PyGTK and GTK 3.
for _name in (
    "AboutDialog", "Adjustment", "Arrow",
    "Button", "Calendar", "CellRendererText", "CheckButton",
    "CheckMenuItem", "Dialog", "DrawingArea",
    "Entry", "EntryCompletion", "EventBox", "FileChooserDialog", "HSeparator",
    "FileChooserWidget", "FileFilter", "FontButton", "HandleBox",
    "Image", "ImageMenuItem", "Label", "Layout", "ListStore", "Menu",
    "MenuItem", "MessageDialog", "Notebook", "PrintOperation",
    "ScrolledWindow", "SeparatorMenuItem", "SizeGroup",
    "TextView", "ToggleButton", "ToggleToolButton", "ToolButton",
    "TreeView", "TreeViewColumn", "VSeparator", "Window",
):
    globals()[_name] = getattr(Gtk, _name)

_CONSTANTS = {
    "ACCEL_LOCKED": Gtk.AccelFlags.LOCKED,
    "ARROW_DOWN": Gtk.ArrowType.DOWN,
    "ARROW_LEFT": Gtk.ArrowType.LEFT,
    "ARROW_RIGHT": Gtk.ArrowType.RIGHT,
    "BUTTONBOX_EDGE": Gtk.ButtonBoxStyle.EDGE,
    "BUTTONBOX_END": Gtk.ButtonBoxStyle.END,
    "BUTTONBOX_SPREAD": Gtk.ButtonBoxStyle.SPREAD,
    "BUTTONS_OK": Gtk.ButtonsType.OK,
    "BUTTONS_OK_CANCEL": Gtk.ButtonsType.OK_CANCEL,
    "CALENDAR_SHOW_HEADING": Gtk.CalendarDisplayOptions.SHOW_HEADING,
    # GTK 3 follows the locale's first weekday; GTK 2's explicit Monday flag
    # no longer exists.
    "CALENDAR_WEEK_START_MONDAY": 0,
    "DIALOG_DESTROY_WITH_PARENT": Gtk.DialogFlags.DESTROY_WITH_PARENT,
    "DIALOG_MODAL": Gtk.DialogFlags.MODAL,
    "FILE_CHOOSER_ACTION_OPEN": Gtk.FileChooserAction.OPEN,
    "FILE_CHOOSER_ACTION_SAVE": Gtk.FileChooserAction.SAVE,
    "JUSTIFY_CENTER": Gtk.Justification.CENTER,
    "MESSAGE_ERROR": Gtk.MessageType.ERROR,
    "MESSAGE_INFO": Gtk.MessageType.INFO,
    "MESSAGE_WARNING": Gtk.MessageType.WARNING,
    "ORIENTATION_VERTICAL": Gtk.Orientation.VERTICAL,
    "POLICY_AUTOMATIC": Gtk.PolicyType.AUTOMATIC,
    "POS_LEFT": Gtk.PositionType.LEFT,
    "POS_TOP": Gtk.PositionType.TOP,
    "PRINT_OPERATION_ACTION_PRINT": Gtk.PrintOperationAction.PRINT_DIALOG,
    "RESPONSE_CANCEL": Gtk.ResponseType.CANCEL,
    "RESPONSE_DELETE_EVENT": Gtk.ResponseType.DELETE_EVENT,
    "RESPONSE_NONE": Gtk.ResponseType.NONE,
    "RESPONSE_OK": Gtk.ResponseType.OK,
    "SELECTION_SINGLE": Gtk.SelectionMode.SINGLE,
    "SHADOW_ETCHED_IN": Gtk.ShadowType.ETCHED_IN,
    "SHADOW_NONE": Gtk.ShadowType.NONE,
    "SIZE_GROUP_HORIZONTAL": Gtk.SizeGroupMode.HORIZONTAL,
    "STATE_NORMAL": Gtk.StateType.NORMAL,
    "TARGET_SAME_WIDGET": Gtk.TargetFlags.SAME_WIDGET,
    "TOOLBAR_ICONS": Gtk.ToolbarStyle.ICONS,
    "TREE_VIEW_DROP_BEFORE": Gtk.TreeViewDropPosition.BEFORE,
    "TREE_VIEW_DROP_INTO_OR_BEFORE": Gtk.TreeViewDropPosition.INTO_OR_BEFORE,
    "UNIT_POINTS": Gtk.Unit.POINTS,
    "WINDOW_POPUP": Gtk.WindowType.POPUP,
    "WIN_POS_CENTER": Gtk.WindowPosition.CENTER,
    "WIN_POS_MOUSE": Gtk.WindowPosition.MOUSE,
    "WRAP_CHAR": Gtk.WrapMode.CHAR,
    "WRAP_WORD": Gtk.WrapMode.WORD,
    "STOCK_CANCEL": "gtk-cancel",
    "STOCK_CLOSE": "gtk-close",
    "STOCK_OK": "gtk-ok",
    "STOCK_OPEN": "gtk-open",
    "STOCK_SAVE": "gtk-save",
}
globals().update(_CONSTANTS)

pygtk_version = (3, 24, 0)
main = Gtk.main
main_quit = Gtk.main_quit
main_iteration = Gtk.main_iteration
events_pending = Gtk.events_pending
drag_finish = Gtk.drag_finish
accelerator_get_default_mod_mask = Gtk.accelerator_get_default_mod_mask
