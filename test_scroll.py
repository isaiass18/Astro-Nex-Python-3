import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

w = Gtk.Window()
w.set_default_size(400, 400)
sw = Gtk.ScrolledWindow()
l = Gtk.Layout()
sw.add(l)
w.add(sw)

def on_draw(widget, cr):
    cr.set_source_rgb(1, 0, 0)
    cr.rectangle(0, 0, 1440, 1440)
    cr.fill()
    cr.set_source_rgb(0, 0, 1)
    cr.rectangle(720, 720, 100, 100) # blue square in center
    cr.fill()

l.connect("draw", on_draw)
l.set_size(1440, 1440)

# Simulate zooming by setting a size request
l.set_size_request(1440, 1440)

def scroll_timeout():
    ha = l.get_hadjustment()
    va = l.get_vadjustment()
    print("Before:", ha.get_value(), va.get_value())
    ha.set_value(ha.get_value() + 100)
    va.set_value(va.get_value() + 100)
    print("After:", ha.get_value(), va.get_value())
    return True

from gi.repository import GLib
GLib.timeout_add(1000, scroll_timeout)

w.show_all()
# We don't actually run Gtk.main() because we don't have a display, 
# but wait! We can just check the values!
# We can't see the screen, but we can verify if the adjustment accepts the value!

while GLib.MainContext.default().iteration(False): pass
scroll_timeout()

