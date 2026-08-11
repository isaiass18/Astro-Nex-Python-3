import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import cairo

class MyLayout(Gtk.Layout):
    def do_draw(self, cr):
        ha = self.get_hadjustment().get_value()
        print(f"do_draw called! ha={ha}")
        # Let's see if the origin of cr is translated!
        mat = cr.get_matrix()
        print(f"Matrix translation: x0={mat.x0}, y0={mat.y0}")
        return False

w = Gtk.Window()
sw = Gtk.ScrolledWindow()
l = MyLayout()
sw.add(l)
w.add(sw)
l.set_size(1440, 1440)
w.show_all()

while Gtk.events_pending(): Gtk.main_iteration()
l.get_hadjustment().set_value(500)
while Gtk.events_pending(): Gtk.main_iteration()

