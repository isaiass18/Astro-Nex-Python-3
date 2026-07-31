# -*- coding: utf-8 -*-
import gtk
import pango
from gi.repository import Gtk
from .. drawing.dispatcher import DrawMixin

class PlanSelector(gtk.Dialog):
    '''Planet selector'''

    def __init__(self,parent):
        gtk.Dialog.__init__(self,
                _("Selector de aspectos"), parent,
                gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CLOSE, gtk.RESPONSE_NONE,))
        self.connect("key-press-event", lambda w,e: self.destroy() if e.keyval == gtk.keysyms.Escape else False)
        self.parnt = parent
        self.notwanted = set()
        self.plet = ['d','f','h','j','k','l','g','z','x','c','v']

        #self.set_size_request(400,580)
        self.vbox.set_border_width(3)
        frame = gtk.Frame(_("Ocultar"))
        frame.set_border_width(3)
        
        frame.add(self.create_buttonlist())
        self.vbox.pack_start(frame,False)
        
        self.connect("response", self.dlg_response)
        self.connect('key-press-event', self.on_key_press_event,parent) 

        self.show_all()
        self.parnt.da.redraw()

    def create_buttonlist(self):
        font = pango.FontDescription("Astro-Nex")
        self._button_style = Gtk.CssProvider()
        self._button_style.load_from_data(
            b"button { min-width: 0px; min-height: 0px; padding: 0px; }"
        )
        vbuttonbox = gtk.VButtonBox() 
        vbuttonbox.set_layout(gtk.BUTTONBOX_SPREAD)
        for let in self.plet:
            but = gtk.ToggleButton(let)
            but.get_style_context().add_provider(
                self._button_style, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )
            but.set_size_request(80,24)
            but.get_child().modify_font(font)
            but.set_mode(True)
            but.connect("toggled",self.on_but_toggled)
            vbuttonbox.pack_start(but,False,False)
        return vbuttonbox

    def on_but_toggled(self,but):
        let = but.get_label()
        if but.get_active():
            self.notwanted.add(self.plet.index(let))
        else:
            self.notwanted.discard(self.plet.index(let))
        DrawMixin.notwanted = list(self.notwanted)
        self.parnt.da.redraw()
        self.parnt.da.redraw_auxwins() 

    def dlg_response(self,dialog,rid):
        self.parnt.boss.mpanel.toolbar.get_nth_item(3).set_active(False) 
        return
    
    def on_key_press_event(self,window,event,parent): 
        if event.keyval == gtk.keysyms.Escape:
            parent.boss.mpanel.toolbar.get_nth_item(3).set_active(False) 
        return True

    def exit(self):
        DrawMixin.notwanted  = []
        #self.parnt.da.drawer.notwanted
        self.parnt.da.redraw()
        self.parnt.da.plselector = None
        self.destroy()
