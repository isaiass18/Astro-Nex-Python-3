"""Opt-in GTK 3 smoke tests for the principal interactive dialogs.

Run on a graphical desktop or with Xvfb:
    ASTRONEX_GUI_SMOKE=1 xvfb-run -a python -m unittest tests.test_gui_smoke
"""

import os
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest import mock


@unittest.skipUnless(
    os.environ.get("ASTRONEX_GUI_SMOKE") == "1",
    "set ASTRONEX_GUI_SMOKE=1 to run GTK integration tests",
)
class GtkSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from astronex import countries, database, nex
        from astronex.config import read_config
        from astronex.extensions.path import path
        from astronex.state import Current

        app_path = path(Path(nex.__file__).resolve().parent.parent)
        nex.check_home_dir(app_path)
        cls.app = nex.application(app_path)
        database.connect(cls.app)
        opts = read_config(cls.app.home_dir)
        opts.home_dir = cls.app.home_dir
        nex.langs[opts.lang].install()
        countries.install(opts.lang)
        # These modules create translated labels while their classes are
        # declared, so load them only after installing the selected language.
        from astronex.boss import Manager
        state = Current(cls.app)
        nex.init_config(cls.app.home_dir, opts, state)
        cls.manager = Manager(cls.app, opts, state)
        from astronex.gui.winnex import WinNex
        cls.window = WinNex(cls.manager)
        cls.manager.set_mainwin(cls.window)
        cls._flush_events()

    @classmethod
    def tearDownClass(cls):
        for window in list(cls._gtk.Window.list_toplevels()):
            window.destroy()
        cls._flush_events()
        from astronex import database
        database.close()

    @classmethod
    def _flush_events(cls):
        if not hasattr(cls, "_gtk"):
            import gtk
            cls._gtk = gtk
        while cls._gtk.events_pending():
            cls._gtk.main_iteration()

    def _assert_visible(self, dialog):
        self._flush_events()
        self.assertTrue(dialog.get_visible())
        dialog.destroy()
        self._flush_events()

    def test_interactive_dialogs_open(self):
        from astronex.gui.config_dlg import ConfigDlg
        from astronex.gui.customloc_dlg import CustomLocDlg
        from astronex.gui.cycle_dlg import CycleSelector
        from astronex.gui.localsel import LocSelector
        from astronex.gui.plselector_dlg import PlanSelector
        from astronex.surfaces.pngsurface import ImageExportDialog

        self.window.on_entry_clicked(None)
        entry = self.window.entry
        self._flush_events()
        entry.pframe.child.first.set_text("Élodie")
        self.assertEqual(entry.pframe.child.first.get_text(), "Élodie")
        self._assert_visible(entry)
        self.window.entry = None

        self._assert_visible(ConfigDlg(self.window))
        self._assert_visible(LocSelector(self.window))
        self._assert_visible(CustomLocDlg(self.window.boss))
        self._assert_visible(PlanSelector(self.window))
        self._assert_visible(CycleSelector(self.window))
        self._assert_visible(ImageExportDialog())

        self.window.on_about_clicked(None, self.window.boss.app.appath.joinpath("astronex"))
        self._flush_events()
        about = next(
            window for window in self._gtk.Window.list_toplevels()
            if isinstance(window, self._gtk.AboutDialog)
        )
        self._assert_visible(about)

        self.window.launch_chartbrowser_from_mpanel()
        self.assertIsNotNone(self.window.browser)
        self._assert_visible(self.window.browser)
        self.window.browser = None

    def test_chart_canvas_receives_available_width(self):
        """A legacy omitted ``pack_start`` must still expand under GTK 3."""
        self._flush_events()
        self.assertGreaterEqual(self.window.da.ha.get_page_size(), 500)
        # On Windows Gdk.Screen.get_width() is the virtual desktop width.
        # The main window must use one monitor, otherwise drawings are placed
        # several screens to the right of the visible area.
        self.assertLessEqual(self.window.get_allocated_width(), 2500)

    def test_legacy_context_menus_open_under_gtk3(self):
        """PyGTK's five-argument Menu.popup form remains usable."""
        import gtk

        menu = gtk.Menu()
        menu.append(gtk.MenuItem("Prueba"))
        menu.show_all()
        try:
            # This is the form used by chart, eye, list and planetogram menus.
            menu.popup(None, None, None, 1, 0)
            self._flush_events()
        finally:
            menu.popdown()
            menu.destroy()
            self._flush_events()

    def test_f1_help_window_renders_under_gtk3(self):
        """F1 must render the keyboard and mouse help rather than a blank dialog."""
        import gc
        import cairo
        from gi.repository import Gdk, Gtk
        from astronex.gui.quickhelp import HelpWindow

        # F1 has no accelerator callback of its own, but GTK still scans the
        # main window's accelerator group after a key event.  Force the
        # lifetime edge that previously crashed in gtk_accel_groups_activate.
        gc.collect()
        self.assertFalse(Gtk.accel_groups_activate(
            self.window, Gdk.KEY_F1, Gdk.ModifierType(0)
        ))
        self.assertTrue(self.window.on_key_press_event(
            self.window, type("F1Event", (), {
                "keyval": self._gtk.keysyms.F1,
            })()
        ))
        help_window = next(
            window for window in self._gtk.Window.list_toplevels()
            if isinstance(window, HelpWindow)
        )
        self.assertIsNotNone(self.window.accel_group)
        self.assertIsNotNone(help_window.accel_group)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 710, 500)
        context = cairo.Context(surface)
        try:
            help_window.da.dispatch(help_window.da, context)
            self.assertTrue(help_window.da.surface.get_width() > 0)
            self.assertTrue(help_window.da.surface.get_height() > 0)
        finally:
            help_window.destroy()
            self._flush_events()

    def test_calendar_house_selector_uses_manager(self):
        """Calendar navigation must not rely on GTK2's widget.parent."""
        from astronex.surfaces import sdasurface

        selector = sdasurface.HouseSelector(self.window.boss)
        with mock.patch.object(
            sdasurface.curr.curr_chart,
            "which_house_today",
            return_value=(3, 0.25),
        ), mock.patch.object(
            self.window.boss.da.drawer, "set_bio_from_date"
        ) as set_bio:
            selector.set_house_from_date(datetime(2026, 7, 24, 12, 0))
        set_bio.assert_called_once_with(3, 0.25)

    def test_pe_bridge_labels_render_under_gtk3(self):
        """PE bridge labels use the PangoCairo adapter, not raw Cairo."""
        import cairo
        from astronex.gui.bridgewin import BridgePEWindow
        from astronex.pangocairo_compat import CairoContext

        bridge = BridgePEWindow(self.window)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 450, 450)
        context = CairoContext(cairo.Context(surface))
        bridge.sda.dt = datetime(2026, 7, 24, 12, 0)
        try:
            bridge.sda.draw_pelabel(context, 450, 450)
            bridge.sda.draw_label(context, 450, 450)
        finally:
            bridge.destroy()
            self._flush_events()

    def test_planet_popup_renders_under_gtk3(self):
        """The planet-position popup must adapt Cairo to PangoCairo."""
        import cairo
        from astronex.gui.popup import PlanPopup

        popup = PlanPopup(self.window.boss)
        area = popup.get_child()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 115, 195)
        context = cairo.Context(surface)
        try:
            area.dispatch(area, context)
        finally:
            popup.destroy()
            self._flush_events()

    def test_date_popup_uses_gtk3_widget_state(self):
        """The date selector opens without GTK2 Widget.flags checks."""
        import gtk
        from astronex.gui.datewidget import DateEntry

        host = gtk.Window()
        entry = DateEntry(self.window.boss)
        host.add(entry)
        host.show_all()
        self._flush_events()
        try:
            entry._popup.popup(date(2026, 7, 24))
            self._flush_events()
            self.assertTrue(entry._popup.get_visible())
        finally:
            entry._popup.popdown()
            host.destroy()
            self._flush_events()

    def test_masked_entries_accept_programmatic_dates_and_coordinates(self):
        """Loading saved values must not replay them as GTK3 keystrokes."""
        from astronex.extensions.validation import MaskEntry

        date_entry = MaskEntry()
        date_entry.set_mask("00/00/0000")
        date_entry.set_text("24/07/2026")
        self.assertEqual(date_entry.get_text(), "24/07/2026")

        coordinate = MaskEntry()
        coordinate.set_mask("000.00.00")
        coordinate.set_text("074.03.15")
        self.assertEqual(coordinate.get_text(), "074.03.15")

    def test_png_and_pdf_exports(self):
        """Exercise native Cairo export without PyGTK/winshell helpers."""
        from astronex.surfaces.pdfsurface import DrawPdf
        from astronex.surfaces.pngsurface import DrawPng
        response_ok = self._gtk.RESPONSE_OK

        class _Chooser:
            def __init__(self, filename):
                self.filename = filename

            def get_filename(self):
                return self.filename

        class _ImageDialog:
            def __init__(self, filename):
                self.chooser = _Chooser(filename)

            def run(self):
                return response_ok

            def destroy(self):
                pass

        with tempfile.TemporaryDirectory(prefix="astronex-export-") as temp_dir:
            png = Path(temp_dir) / "carta_ñ.png"
            pdf = Path(temp_dir) / "carta_ñ.pdf"
            with mock.patch("astronex.surfaces.pngsurface.ImageExportDialog",
                            return_value=_ImageDialog(str(png))), \
                    mock.patch("astronex.surfaces.pngsurface.sys.platform", "linux"), \
                    mock.patch("astronex.surfaces.pngsurface.os.system"):
                DrawPng.clicked(self.window.boss)
            self.assertGreater(png.stat().st_size, 0)

            surface = DrawPdf.dispatch(str(pdf))
            surface.finish()
            self.assertGreater(pdf.stat().st_size, 0)

    def test_theme_colors_and_glyph_style(self):
        """GTK3 colour widgets keep RGB config and glyph styles reversible."""
        import gtk
        from astronex import config
        from astronex.gui.config_dlg import ColorsPage, FontsPage

        opts = self.window.boss.opts
        original_fire = opts.fire
        original_style = opts.transtyle
        try:
            color_page = ColorsPage()
            color_button = gtk.ColorButton(gtk.gdk.color_parse("#123456"))
            color_page.color_set_cb(color_button, "fire")
            self.assertEqual(opts.fire, "123456")
            self.assertEqual(config.cfgcols["fire"], "#123456")

            font_page = FontsPage()
            alternate = "classic" if original_style == "huber" else "huber"
            font_page.style_set_cb(type("Combo", (), {
                "get_active": lambda self: ["huber", "classic"].index(alternate)
            })())
            self.assertEqual(opts.transtyle, alternate)
        finally:
            opts.fire = original_fire
            config.cfgcols["fire"] = "#" + original_fire
            opts.zodiac.set_zodcolors()
            if opts.transtyle != original_style:
                FontsPage().style_set_cb(type("Combo", (), {
                    "get_active": lambda self: ["huber", "classic"].index(original_style)
                })())
