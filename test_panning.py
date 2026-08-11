import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

w = Gtk.Window()
w.set_default_size(720, 720)
sw = Gtk.ScrolledWindow()
l = Gtk.Layout()
sw.add(l)
w.add(sw)
l.set_size(1440, 1440)
w.show_all()

# process events
while Gtk.events_pending():
    Gtk.main_iteration()

ha = l.get_hadjustment()
print(f"Page size: {ha.get_page_size()}, Upper: {ha.get_upper()}")
print(f"wrange: {1440 - ha.get_page_size()}")
