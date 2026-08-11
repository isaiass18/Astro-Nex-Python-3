import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

w = Gtk.Window()
w.set_default_size(720, 720)
sw = Gtk.ScrolledWindow()
l = Gtk.Layout()
sw.add(l)
w.add(sw)
w.show_all()

while Gtk.events_pending(): Gtk.main_iteration()
ha = l.get_hadjustment()
print(f"Before: Upper={ha.get_upper()}, Page size={ha.get_page_size()}")

l.set_size(1440, 1440)
while Gtk.events_pending(): Gtk.main_iteration()
print(f"After set_size: Upper={ha.get_upper()}, Page size={ha.get_page_size()}")
