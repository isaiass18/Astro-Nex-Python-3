"""Opt-in GTK 3 smoke tests for the principal interactive dialogs.

Run on a graphical desktop or with Xvfb:
    ASTRONEX_GUI_SMOKE=1 xvfb-run -a python -m unittest tests.test_gui_smoke
"""

import os
import sys
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

    def test_aspect_selector_keeps_compact_button_layout(self):
        """Aspect glyphs have the same explicit GTK3 dimensions."""
        from astronex.gui.plselector_dlg import PlanSelector

        selector = PlanSelector(self.window)
        try:
            button_box = selector.vbox.get_children()[0].get_child()
            self.assertEqual(button_box.get_layout(), self._gtk.BUTTONBOX_SPREAD)
            for button in button_box.get_children():
                self.assertEqual(button.get_size_request(), (80, 24))
        finally:
            selector.destroy()
            self._flush_events()

    def test_migration_credit_title_is_not_locale_dependent(self):
        """The Spanish GTK Credits button updates the documenter heading."""
        original_language = self.window.boss.opts.lang
        try:
            self.window.boss.opts.lang = 'es'
            credit_row = self._gtk.HBox()
            credits_button = self._gtk.Button("Créditos")
            heading = self._gtk.Label("Documentado por")
            credit_row.add(credits_button)
            credit_row.add(heading)

            self.window._connect_migration_credit(credit_row)
            credits_button.emit("clicked")
            self._flush_events()

            self.assertEqual(heading.get_text(), "Migración a Python 3")
        finally:
            self.window.boss.opts.lang = original_language

    def test_migration_credit_title_follows_the_active_language(self):
        titles = {
            'en': 'Python 3 Migration',
            'es': 'Migración a Python 3',
            'ca': 'Migració a Python 3',
            'de': 'Migration zu Python 3',
        }
        original_language = self.window.boss.opts.lang
        try:
            for language, expected in titles.items():
                self.window.boss.opts.lang = language
                self.assertEqual(self.window._migration_credit_title(), expected)
        finally:
            self.window.boss.opts.lang = original_language

    def test_chart_canvas_receives_available_width(self):
        """A legacy omitted ``pack_start`` must still expand under GTK 3."""
        self._flush_events()
        self.assertGreaterEqual(self.window.da.ha.get_page_size(), 500)
        self.assertTrue(self.window.da.get_hexpand())
        self.assertTrue(self.window.da.get_vexpand())
        # On Windows Gdk.Screen.get_width() is the virtual desktop width.
        # The main window must use one monitor, otherwise drawings are placed
        # several screens to the right of the visible area.
        self.assertLessEqual(self.window.get_allocated_width(), 2500)

    def test_chart_canvas_uses_scrolled_window_directly(self):
        """Extended charts must not be wrapped in a GtkViewport on GTK3."""
        parent = self.window.da.get_parent()
        self.assertIsInstance(parent, self._gtk.ScrolledWindow)

    def test_scroll_delta_supports_mouse_wheels_and_macos_trackpads(self):
        """The GTK3 bridge normalizes discrete and smooth scrolling."""
        import gtk

        wheel = type("Scroll", (), {"direction": gtk.gdk.SCROLL_UP})()
        smooth = type("Scroll", (), {
            "direction": gtk.gdk.SCROLL_SMOOTH,
            "get_scroll_deltas": lambda self: (True, 0.0, -20.0),
        })()
        self.assertEqual(gtk.gdk.scroll_delta(wheel), 1.0)
        self.assertEqual(gtk.gdk.scroll_delta(smooth), 0.25)

    def test_planetogram_trackpad_zoom_is_gradual_and_bounded(self):
        """A short smooth gesture cannot make Cairo draw an enormous chart."""
        from astronex.gui.plagram_dlg import DrawPlagram, MAX_ZOOM

        drawer = type("Zoom", (), {"zoom": 1.0})()
        for _ in range(10):
            DrawPlagram.apply_zoom_delta(drawer, 0.25, smooth=True)
        self.assertLess(drawer.zoom, 1.2)
        for _ in range(100):
            DrawPlagram.apply_zoom_delta(drawer, 0.25, smooth=True)
        self.assertLessEqual(drawer.zoom, MAX_ZOOM)

    def test_chart_header_uses_the_visible_canvas_right_edge(self):
        """Date/regent labels use the full window right edge in normal mode."""
        self._flush_events()
        canvas_width = self.window.da.get_allocated_width()
        window_width = self.window.get_allocated_width()
        self.assertEqual(
            self.window.da._header_width(canvas_width * 0.85), window_width
        )

    def test_data_cards_keep_legacy_dimensions_and_left_text(self):
        """GTK3 toolbar sizing must not stretch the two data-entry cards."""
        for slot in self.window.boss.mpanel.pool.values():
            # Gtk.EventBox/frame borders can add four pixels around the
            # 320-pixel historical content row.
            # The fixed request is the legacy 320-pixel data card. GTK can
            # allocate a few extra pixels on macOS for its native frame.
            self.assertEqual(slot.get_size_request()[0], 320)
            self.assertGreaterEqual(slot.get_allocated_width(), 320)
            self.assertGreaterEqual(slot.storage_but.get_allocated_width(), 120)
            self.assertEqual(slot.namelbl.get_property("xalign"), 0.0)
            self.assertEqual(slot.datelbl.get_property("xalign"), 0.0)

        # The card is centred within the GTK3 toolbar frame, as it was in the
        # GTK2 presentation. The textual data remains left aligned.
        alignment = self.window.boss.mpanel.pool['master'].get_parent()
        self.assertEqual(alignment.get_property("xalign"), 0.5)

        master = self.window.boss.mpanel.pool['master']
        click = self.window.boss.mpanel.pool['click']
        master_table = master.eb.get_child()
        click_table = click.eb.get_child()
        master_action = master_table.get_child_at(1, 0)
        click_action = click_table.get_child_at(1, 0)
        self.assertEqual(master_action.get_size_request()[0], 195)
        self.assertEqual(click_action.get_size_request()[0], 195)
        self.assertEqual(
            master_action.get_allocation().x + master_action.get_allocated_width(),
            click_action.get_allocation().x + click_action.get_allocated_width(),
        )

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

    def test_calendar_toolbar_toggle_opens_on_first_use(self):
        """The GTK3 calendar toggle opens and closes on its first use."""
        calendar_button = self.window.boss.mpanel.toolbar.get_nth_item(0)
        self.assertIsInstance(calendar_button, self._gtk.ToggleToolButton)
        calendar_button.set_active(True)
        self._flush_events()
        self.assertTrue(self.window.boss.da.panelvisible)
        self.assertEqual(
            self.window.boss.da.panel.get_size_request(), (230, 160)
        )
        self.assertLessEqual(self.window.boss.da.panel.get_allocated_width(), 232)
        self.assertEqual(
            self.window.boss.da.panel.calendar.get_allocated_width(), 230
        )
        self.assertEqual(
            self.window.boss.da.panel.spin.get_size_request(), (52, 24)
        )
        self.assertEqual(
            self.window.boss.da.panel.get_allocation().y, 0
        )
        calendar_button.set_active(False)
        self._flush_events()
        self.assertFalse(self.window.boss.da.panelvisible)
        self.assertFalse(self.window.boss.da.panel.get_visible())

    def test_calendar_toggle_invalidates_the_chart_immediately(self):
        """Opening the panel must request a canvas repaint in the same turn."""
        calendar_button = self.window.boss.mpanel.toolbar.get_nth_item(0)
        with mock.patch.object(self.window.boss.da, "queue_draw") as redraw:
            calendar_button.set_active(True)
            self.assertTrue(redraw.called)
        calendar_button.set_active(False)

    def test_calendar_is_drawn_inside_the_chart_canvas(self):
        """The calendar remains in-window instead of opening a GTK popup."""
        calendar_button = self.window.boss.mpanel.toolbar.get_nth_item(0)
        calendar_button.set_active(True)
        self._flush_events()
        self.assertTrue(self.window.boss.da.panelvisible)
        calendar_button.set_active(False)

    def test_clock_card_can_be_clicked_twice(self):
        """The current-chart clock must tolerate a physical double click."""
        clock = self.window.boss.mpanel.pool['master'].clock
        clock.emit('clicked')
        self._flush_events()
        clock.emit('clicked')
        self._flush_events()
        self.assertEqual(self.window.boss.mpanel.pool['master'].chart_id, 'now')

    def test_biography_ruler_matches_python2_interaction(self):
        """Biography charts keep the original drag/double-click behaviour."""
        import gtk
        from astronex.drawing import biograph

        class PointerWindow:
            def __init__(self, x, y=0):
                self.x = x
                self.y = y

            def get_pointer(self):
                return None, self.x, self.y, 0

        class Event:
            def __init__(self, event_type, button=1, x=0, y=0, pointer_x=None):
                self.type = event_type
                self.button = button
                self.x = x
                self.y = y
                self.window = PointerWindow(pointer_x if pointer_x is not None else x, y)

            def get_state(self):
                return 0

        drawer = self.window.boss.da.drawer
        surface = self.window.boss.da
        pe_button = self.window.boss.mpanel.toolbar.get_nth_item(1)
        original_op = biograph.curr.curr_op
        original_mode = biograph.curr.opmode
        original_chart = biograph.curr.curr_chart
        original_gridw = drawer.gridw
        original_hoff = drawer.hoff
        original_house_t = drawer.house_t
        original_ruler = biograph.ruler[:]
        original_release = biograph.release
        width = surface.allocation.width or 800

        try:
            pe_button.set_active(False)
            self._flush_events()
            biograph.curr.curr_op = 'bio_nat'
            biograph.curr.opmode = 'simple'
            biograph.curr.curr_chart = object()
            drawer.gridw = float(width)
            drawer.hoff = 0.0
            drawer.house_t = {
                'begin': datetime(2000, 1, 1),
                'lapsus': date(2000, 4, 10) - date(2000, 1, 1),
            }
            biograph.ruler[0] = 0.25
            biograph.release = False
            surface.set_data("move-info", {'button': -1})

            with mock.patch.object(surface, "queue_draw"), mock.patch.object(
                self.window.boss.da.panel, "set_date"
            ) as set_date, mock.patch.object(
                self.window.boss.da.panel.nowbut, "emit"
            ) as now_emit:
                drawer.pe_rulercb(
                    surface,
                    Event(gtk.gdk.BUTTON_PRESS, x=width * 0.25),
                    surface,
                )
                drawer.pe_rulercb(
                    surface,
                    Event(
                        gtk.gdk.MOTION_NOTIFY,
                        x=width * 0.25,
                        pointer_x=width * 0.6,
                    ),
                    surface,
                )
                drawer.pe_rulercb(
                    surface,
                    Event(gtk.gdk.BUTTON_RELEASE, x=width * 0.6),
                    surface,
                )

                self.assertAlmostEqual(biograph.ruler[0], 0.6, places=2)
                self.assertTrue(biograph.release)
                self.assertTrue(set_date.called)

                drawer.pe_rulercb(
                    surface,
                    Event(gtk.gdk._2BUTTON_PRESS, x=width * 0.6),
                    surface,
                )
                now_emit.assert_called_with('clicked')
        finally:
            pe_button.set_active(False)
            biograph.curr.curr_op = original_op
            biograph.curr.opmode = original_mode
            biograph.curr.curr_chart = original_chart
            drawer.gridw = original_gridw
            drawer.hoff = original_hoff
            drawer.house_t = original_house_t
            biograph.ruler[:] = original_ruler
            biograph.release = original_release
            surface.set_data("move-info", {'button': -1})
            self._flush_events()

    def test_accelerator_callbacks_are_strongly_retained(self):
        """GTK must never dispatch an accelerator to a released callback."""
        handlers = self.window.accel_group._legacy_accel_handlers
        self.assertGreater(len(handlers), 20)
        self.assertTrue(all(callable(callback) for callback, _ in handlers))

    def test_popup_canvases_receive_wheel_events(self):
        """Auxiliary, diagram and PE-bridge canvases request GTK3 scrolling."""
        import gtk
        from astronex.gui.bridgewin import BridgePEWindow
        from astronex.surfaces.sdasurface import DrawAux, DrawDiagram

        scroll_mask = gtk.gdk.SCROLL_MASK
        diagram = DrawDiagram(self.window.boss)
        auxiliary = DrawAux(self.window.boss)
        auxiliary_host = self._gtk.Window()
        auxiliary_host.add(auxiliary)
        auxiliary_host.show_all()
        self._flush_events()
        bridge = BridgePEWindow(self.window)
        try:
            self.assertTrue(diagram.get_events() & scroll_mask)
            self.assertTrue(auxiliary.get_events() & scroll_mask)
            self.assertTrue(bridge.sda.get_events() & scroll_mask)

            before = auxiliary.opaux[0]
            auxiliary.on_scroll(auxiliary, type("Scroll", (), {
                "direction": gtk.gdk.SCROLL_DOWN,
            })())
            self.assertNotEqual(auxiliary.opaux[0], before)

            # The right-click menu is not merely displayed: activating an
            # entry changes the auxiliary chart family as it did in GTK2.
            clicks_item = next(
                item for item in auxiliary.menu.get_children()
                if getattr(item.get_child(), "get_text", lambda: "")() == "Clics"
            )
            clicks_item.activate()
            self.assertIs(auxiliary.opaux, auxiliary.opclicks)
        finally:
            bridge.destroy()
            auxiliary_host.destroy()
            self._flush_events()

    def test_extended_pair_chart_anchors_overlays_to_the_visible_area(self):
        """Extended pair charts pin overlays to the visible viewport."""
        surface = self.window.boss.da
        state = self.window.boss.get_state()
        original_op = state.curr_op
        original_mode = state.opmode
        original_clickmode = state.clickmode

        try:
            state.curr_op = 'compo_two'
            state.opmode = 'simple'
            state.clickmode = 'click'
            surface.set_size_request(720, 1080)
            surface.ha.value = 0
            surface.va.value = 260
            self._flush_events()

            surface.show_panel()
            surface.show_diada()
            self._flush_events()

            self.assertEqual(surface.ha.value, 0)
            self.assertEqual(surface.va.value, 0)
            self.assertTrue(surface.panel.get_visible())
            self.assertTrue(surface.diada.get_visible())
            self.assertIs(surface.panel.get_parent(), surface.overlay_host)
            self.assertIs(surface.diada.get_parent(), surface.overlay_host)
        finally:
            surface.hide_panel()
            surface.hide_diada()
            surface.set_size_request(720, 720)
            state.curr_op = original_op
            state.opmode = original_mode
            state.clickmode = original_clickmode
            self._flush_events()

    def test_chart_browser_height_matches_backend_layout(self):
        """The left browser adapts to small screens without crushing the chooser."""
        browser = self.window.boss.mpanel.browser
        scroller = next(
            child for child in browser.get_children()
            if isinstance(child, self._gtk.ScrolledWindow)
        )
        screen_height = self._gtk.gdk.screen_height()
        if screen_height <= 800:
            expected_height = 220
        elif sys.platform == 'darwin':
            expected_height = 260
        else:
            expected_height = 330
        self.assertEqual(scroller.get_size_request(), (-1, expected_height))
        if hasattr(scroller, "get_propagate_natural_height"):
            self.assertFalse(scroller.get_propagate_natural_height())
        if hasattr(scroller, "get_max_content_height"):
            self.assertEqual(scroller.get_max_content_height(), expected_height)

    def test_toolbar_state_hides_stale_overlays(self):
        """The canvas must drop stale overlay flags when the toolbar is off."""
        surface = self.window.boss.da
        toolbar = self.window.boss.mpanel.toolbar
        calendar_button = toolbar.get_nth_item(0)
        diagram_button = toolbar.get_nth_item(5)

        surface.panelvisible = True
        surface.diadavisible = True
        calendar_button.set_active(False)
        diagram_button.set_active(False)
        self._flush_events()

        surface.sync_overlays_with_toolbar()

        self.assertFalse(surface.panelvisible)
        self.assertFalse(surface.diadavisible)
        self.assertFalse(surface.panel.get_visible())
        self.assertFalse(surface.diada.get_visible())

    def test_type_to_select_accepts_unicode_names(self):
        """Typing accented names opens the record/locality selector search."""
        from astronex.gui.searchview import SearchView

        model = self._gtk.ListStore(str)
        model.append(["Álvaro"])
        model.append(["Élodie"])
        view = SearchView(model)
        host = self._gtk.Window()
        host.add(view)
        host.show_all()
        self._flush_events()
        try:
            handled = view.on_keypress(view, type("Key", (), {
                "state": 0,
                "string": "É",
            })())
            self.assertTrue(handled)
            self.assertTrue(view.searchbox_on)
            frame = view.search_win.get_child().get_children()[0]
            self.assertEqual(frame.get_child().get_text(), "É")
            selected_model, selected_iter = view.get_selection().get_selected()
            self.assertEqual(selected_model.get_value(selected_iter, 0), "Élodie")
        finally:
            if view.searchbox_on:
                view.destroy_searchwin()
            host.destroy()
            self._flush_events()

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

    def test_floating_windows_have_reliable_close_paths(self):
        """Auxiliary charts and PE bridge stay closable in remote sessions."""
        from astronex.gui.bridgewin import BridgePEWindow

        self.window.boss.da.make_auxwin()
        auxiliary = self.window.boss.da.auxwins[-1]
        self.assertEqual(auxiliary.get_transient_for(), self.window)
        auxiliary.escape(None, None, None, None)
        self._flush_events()
        self.assertNotIn(auxiliary, self.window.boss.da.auxwins)

        bridge = BridgePEWindow(self.window)
        try:
            self.assertTrue(bridge.get_decorated())
            self.assertTrue(bridge.escape(None, None, None, None))
            self._flush_events()
            self.assertFalse(bridge.get_visible())
        finally:
            if bridge.get_visible():
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

    def test_double_catalog_uses_tree_path_index(self):
        """Selecting a double catalog must not compare Gtk.TreePath to tuples."""
        panel = self.window.mpanel.chooser
        button = next(
            child for child in panel.groups_table.get_children()
            if child.get_data("name") == "double1"
        )
        button.set_active(True)
        self._flush_events()
        self.assertEqual(panel.notebook.get_current_page(), button.get_data("page"))
