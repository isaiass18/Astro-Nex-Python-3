# -*- coding: utf-8 -*-
import gtk, gobject
import re, time


class SearchView(gtk.TreeView):
    def __init__(self,model):
        gtk.TreeView.__init__(self,model)
        self.set_enable_search(False)
        self.connect('start-interactive-search', self.on_search_start)
        self.connect('button-press-event', self.on_buttonpress)
        self.connect('key-press-event', self.on_keypress)
        self.searchbox_on = False
        self.search_win = None
        self.start_time = 0
        self.timeout_handle = None

    def on_search_start(self,view):
        if not self.searchbox_on:
            self.interactive_search(view)

    def interactive_search(self,view,key=''):
        self.searchbox_on = True
        search_win = gtk.Window()
        vbox = gtk.VBox()
        search_win.add(vbox)
        search_win.set_modal(False)
        search_win.set_decorated(False)
        self.search_win = search_win

        frame = gtk.Frame()
        vbox.pack_start(frame,False,False)
        search_entry = gtk.Entry()
        frame.add(search_entry)
        search_entry.connect('key-press-event', self.on_entry_keypress)
        search_entry.connect('button-press-event', self.on_entry_buttonpress)

        view.set_search_entry(search_entry)
        view.set_search_column(0)
        search_entry.set_text(key)

        search_win.show_all()
        self.set_searchwin_pos(search_entry)
        search_entry.grab_focus()
        search_entry.set_position(-1)
        search_entry.select_region(0, 0)
        search_entry.set_position(-1)

        def focus_entry():
            search_win.present()
            search_entry.grab_focus()
            search_entry.set_position(-1)
            search_entry.select_region(0, 0)
            search_entry.set_position(-1)
            # Force X11 keyboard grab so the search box receives key events
            # inside VNC/Xvfb, where undecorated windows are not focused by
            # the window manager automatically.
            gdk_win = search_win.get_window()
            if gdk_win:
                try:
                    gtk.gdk.keyboard_grab(gdk_win, False, gtk.gdk.CURRENT_TIME)
                except Exception:
                    pass
            search_entry.set_position(-1)
            return False
        gobject.idle_add(focus_entry)

        self.start_time = time.time()
        self.timeout_handle = gobject.timeout_add(1000, self.check_idle)

    def on_entry_keypress(self,entry,event):
        self.start_time = time.time()
        if event.keyval == gtk.keysyms.Return or event.keyval == gtk.keysyms.Escape:
            self.destroy_searchwin()
            return True
        return False

    def on_buttonpress(self,view,event):
        # Always claim keyboard focus on click so that arrow keys work
        # immediately after selecting a row, without needing to click again.
        self.grab_focus()
        if self.searchbox_on:
            self.destroy_searchwin()

    def destroy_searchwin(self):
        if not self.searchbox_on:
            return
        # Release the X11 keyboard grab taken when the search window opened.
        try:
            gtk.gdk.keyboard_ungrab(gtk.gdk.CURRENT_TIME)
        except Exception:
            pass
        if self.timeout_handle is not None:
            gobject.source_remove(self.timeout_handle)
            self.timeout_handle = None
        self.set_search_entry(None)
        if self.search_win is not None:
            self.search_win.destroy()
            self.search_win = None
        self.searchbox_on = False
        self.grab_focus()

    def set_searchwin_pos(self,search_entry):
        # PyGTK exposed ``widget.parent`` as an attribute.  Ask GTK3 for the
        # toplevel instead; this also copes with intermediate scrolled-window
        # containers added by the GTK3 layout.
        parent = self.get_toplevel()
        if not isinstance(parent, gtk.Window):
            return
        win_pos = parent.get_position()
        x = win_pos[0] + self.allocation.width - search_entry.allocation.width
        y = win_pos[1] + self.allocation.height + self.allocation.y
        self.search_win.move(x,y)

    def on_keypress(self,view,event):
        keyval = getattr(event, 'keyval', None)
        char = getattr(event, 'string', '') or ''
        if self.searchbox_on:
            if keyval is not None and (keyval > 255 or keyval < 32) and keyval not in (gtk.keysyms.BackSpace, gtk.keysyms.Return, gtk.keysyms.Escape):
                return False
            search_entry = view.get_search_entry()
            if keyval == gtk.keysyms.BackSpace:
                text = search_entry.get_text()
                if len(text) > 0:
                    search_entry.set_text(text[:-1])
                    search_entry.set_position(-1)
                return True
            elif keyval == gtk.keysyms.Return or keyval == gtk.keysyms.Escape:
                self.destroy_searchwin()
                return True
            if not char and keyval is not None and keyval < 256:
                char = chr(keyval)
            if char and re.match(r'[^\x00-\x1f]', char):
                search_entry.set_text(search_entry.get_text() + char)
                search_entry.set_position(-1)
                return True
            return False

        # No search box open — let arrow keys and other navigation pass through
        if keyval is not None and (keyval > 255 or keyval < 32):
            return False
        if getattr(event, 'state', 0) & gtk.gdk.CONTROL_MASK:
            return False
        # Use event.string (GTK3 composed character) instead of chr(keyval)
        # so that accented letters and non-ASCII keyboards work correctly.
        if char and re.match(r'[^\x00-\x1f]', char):
            self.interactive_search(view, char)
            return True
        return False

    def on_entry_buttonpress(self,entry,event):
        self.start_time = time.time()

    def check_idle(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 3:
            self.timeout_handle = None
            self.destroy_searchwin()
            return False
        return True
