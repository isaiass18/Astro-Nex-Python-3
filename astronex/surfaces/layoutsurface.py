# -*- coding: utf-8 -*-
import gtk,gobject
from gi.repository import Gtk
import cairo,pango
from ..pangocairo_compat import CairoContext
import math
from .. drawing.dispatcher import DrawMixin
from .. gui.plselector_dlg import PlanSelector
from .. gui.popup import PlanPopup, TextPopup
from .. gui.cycle_dlg import CycleSelector
from .. gui.aux_dlg import AuxWindow
from .. gui.bridgewin import BridgePEWindow
from .. extensions.path import path
from .. countries import cata_reg
from .. utils import parsestrtime
from .sdasurface import DrawDiagram, HouseSelector
from datetime import datetime, timedelta
from .. boss import boss
curr = boss.get_state()

MAGICK_COL = 65535.0
initmenu = (_('Ayuda'),_('Acercar'),_('Solo EA'),_('Ver zonas PE'),
        _('Ver zonas de casa'),_('Ver EA'),_('Activar goodwill'),
        _('Ocultar unilaterales'),_('Ego-clics'),_('Ver todos los aspectos'))
bios = ['bio_nat','bio_nod','bio_soul','bio_dharma']
peops = ['draw_nat','draw_nod','draw_soul','draw_local']
sheetops = ['dat_nat', 'dat_nod', 'dat_house', 'prog_nat', 'prog_nod', 'prog_local', 'prog_soul' ]
extended = ['prog_nat','prog_nod','prog_soul','prog_local','compo_one','compo_two']

_COMPACT_PANEL_STYLE = Gtk.CssProvider()
_COMPACT_PANEL_STYLE.load_from_data(b"""
.astronex-compact-calendar { font-size: 8.5pt; min-width: 230px; padding: 0px; }
.astronex-compact-date-control { min-width: 0px; min-height: 0px; padding: 0px; font-size: 7.5pt; }
entry.astronex-compact-date-control { min-width: 0px; min-height: 0px; padding: 0px 1px; border-radius: 0px; box-shadow: none; }
combobox.astronex-compact-date-control box { padding: 0px; }
combobox.astronex-compact-date-control button { min-width: 0px; min-height: 0px; padding: 0px 3px 0px 0px; }
combobox.astronex-compact-date-control arrow { min-width: 12px; min-height: 10px; }
""")
_compact_style_screens = set()


def _add_compact_style(widget, style_class):
    screen = widget.get_screen()
    screen_id = id(screen)
    if screen_id not in _compact_style_screens:
        Gtk.StyleContext.add_provider_for_screen(
            screen, _COMPACT_PANEL_STYLE, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        _compact_style_screens.add(screen_id)
    widget.get_style_context().add_class(style_class)


class CompactCalendar(gtk.Calendar):
    """Keep the in-canvas date selector within its historical width."""

    def do_get_preferred_width(self):
        return 230, 230


class DrawMaster(gtk.Layout):
    fullscreen = False
    panning = False
    zoom_in = False
    panelvisible = False
    diadavisible = False
    hselvisible = False
    pepending = [False,None,None]
    rulinepending = None
    bridge = None
    sec_alltimes = False
    overlay = False

    def __init__(self,boss):
        self.boss = boss
        self.opts = boss.opts
        gtk.Layout.__init__(self)
        self.menu = gtk.Menu()
        self.hidden_op = {}
        for buf in initmenu:
            menu_item = gtk.MenuItem(buf)
            self.menu.append(menu_item)
            menu_item.connect("activate", self.on_menuitem_activate)
            if buf in [_('Ayuda'),_('Ver EA')]:
                sep_item = gtk.SeparatorMenuItem()
                self.menu.append(sep_item)
                sep_item.show()
            if buf not in [_('Ver EA'),_('Ver zonas PE'),_('Ver zonas de casa'),
                    _('Ver todos los aspectos'),_('Ego-clics')]:
                menu_item.show()
            elif buf == _('Ver EA'):
                self.hidden_op['ea'] = menu_item
            elif buf == _('Ver zonas PE'):
                self.hidden_op['pez'] = menu_item
            elif buf == _('Ver zonas de casa'):
                self.hidden_op['hz'] = menu_item
            elif buf == _('Ver todos los aspectos'):
                self.hidden_op['acl'] = menu_item 
            elif buf == _('Ego-clics'):
                self.hidden_op['ego'] = menu_item 
        
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK | 
                gtk.gdk.BUTTON_RELEASE_MASK | 
                gtk.gdk.POINTER_MOTION_MASK | 
                gtk.gdk.POINTER_MOTION_HINT_MASK |
                gtk.gdk.SCROLL_MASK)
        self.connect("draw", self.dispatch)
        self.connect("button_press_event", self.on_da_clicked)
        self.connect("button_release_event", self.on_da_clicked)
        self.connect("motion_notify_event", self.on_da_clicked)
        self.connect("scroll-event", self.on_scroll)
        self.panel = ChangeDatePanel(self)
        self.put(self.panel,-200,-200)

        self.create_special_area()
        self.create_hselector()
        self.drawer = DrawMixin(boss.opts,self) 
        self.plselector = None
        self.cycleselector = None
        self.planpopup = None
        self.textspopup = None
        self.where_diada = 0
        self.where_hsel = 0
        self.auxwins = []

        self.ha = None
        self.va = None
        self.m_x = 0
        self.m_y = 0
        self._last_extended_op = None
        self._overlay_reanchor_pending = False
        self._overlay_reanchor_source = None
        self.overlay_host = None

    def _reset_viewport_to_origin(self):
        if self.ha:
            self.ha.set_value(0)
        if self.va:
            self.va.set_value(0)

    def attach_overlay_host(self, overlay):
        self.overlay_host = overlay
        for widget, halign in ((self.panel, Gtk.Align.START), (self.diada, Gtk.Align.END)):
            parent = widget.get_parent()
            if parent is self:
                self.remove(widget)
            if parent is not overlay:
                overlay.add_overlay(widget)
            widget.set_halign(halign)
            widget.set_valign(Gtk.Align.START)
        self._sync_overlay_positions()

    def _schedule_overlay_reanchor(self):
        self._overlay_reanchor_pending = curr.curr_op == 'compo_two'
        if not self._overlay_reanchor_pending:
            return
        if self._overlay_reanchor_source:
            gobject.source_remove(self._overlay_reanchor_source)
        self._overlay_reanchor_source = gobject.idle_add(self._apply_overlay_reanchor)

    def _apply_overlay_reanchor(self):
        self._overlay_reanchor_source = None
        if curr.curr_op != 'compo_two':
            self._overlay_reanchor_pending = False
            return False
        self._reset_viewport_to_origin()
        self._sync_overlay_positions()
        self.queue_draw()
        self._overlay_reanchor_pending = False
        return False

    def _visible_origin(self):
        x = self.ha.value if self.ha else 0
        y = self.va.value if self.va else 0
        return x, y

    def _visible_width(self):
        if self.ha and self.ha.page_size:
            return self.ha.page_size
        return self.allocation.width

    def _sync_overlay_positions(self):
        if self.overlay_host:
            if self.panelvisible:
                self.panel.show()
            else:
                self.panel.hide()

            if self.diadavisible:
                self.diada.show()
            else:
                self.diada.hide()
            return
        origin_x, origin_y = self._visible_origin()
        if self.panelvisible:
            self.move(self.panel,int(origin_x),int(origin_y))
            self.panel.show()
        else:
            self.move(self.panel,-200,-200)
            self.panel.hide()

        if self.diadavisible:
            where = origin_x + self._visible_width() - self.diada.allocation.width
            self.move(self.diada,int(where),int(origin_y))
            self.diada.show()
        else:
            self.move(self.diada,-280,0)
            self.diada.hide()

    def _sync_overlay_visibility_from_toolbar(self):
        toolbar = getattr(boss.mpanel, 'toolbar', None)
        if not toolbar:
            return
        self.panelvisible = toolbar.get_nth_item(0).get_active()
        self.diadavisible = toolbar.get_nth_item(5).get_active()

    def sync_overlays_with_toolbar(self):
        self._sync_overlay_visibility_from_toolbar()
        self._sync_overlay_positions()
    
    def create_special_area(self):
        frame = gtk.Frame()
        diada = DrawDiagram(self.boss)
        diada.set_size_request(275,275) 
        frame.add(diada)
        self.put(frame,-280,0)
        self.diada = frame

    def create_hselector(self):
        frame = gtk.Frame()
        hsel = HouseSelector(self.boss)
        hsel.set_size_request(120,120) 
        frame.add(hsel)
        self.put(frame,-160,612)
        self.hsel = frame

    def on_da_clicked(self,da,event):
        showAP = DrawMixin.get_showAP()
        x, y = event.x,event.y
        info = self.get_data("move-info")
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.menu.popup(None, None, None, event.button, event.time)
            return True
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            # Biographies own ruler clicks. BioMixin allows editing only with
            # Punto de Edad active and restores the current moment on an
            # inactive-ruler double click.
            if curr.curr_op in bios and curr.opmode == 'simple':
                return False
            if showAP or curr.curr_chart == curr.now or curr.curr_op in ['draw_transits','rad_and_transit']:
                self.panel.nowbut.emit('clicked')
                info['button'] = 100; #now
                if self.cycleselector:
                    cycles = curr.curr_chart.get_cycles()
                    self.cycleselector.adj.set_value(cycles+1) 
            elif curr.curr_op == 'sec_prog':
                self.sec_alltimes = not(self.sec_alltimes)
            return True
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            if curr.curr_op in bios and curr.opmode == 'simple':
                return False
            if event.button != 1: return False
            if info['button'] < 0:
                info['button'] = event.button
                if getattr(self, 'panning', False):
                    # Use set_cursor instead of pointer_grab, as implicit grab works natively in GTK3
                    # and pointer_grab breaks absolute coordinates on macOS.
                    try:
                        fleur = gtk.gdk.Cursor.new_for_display(gtk.gdk.Display.get_default(), gtk.gdk.CursorType.FLEUR)
                        if self.get_window():
                            self.get_window().set_cursor(fleur)
                    except Exception:
                        pass
                    info['click_x'] = event.x_root
                    info['click_y'] = event.y_root
            elif info['button'] == 100:
                info['button'] = -1
            if showAP is None:
                return True 
            w = da.allocation.width/2; h = da.allocation.height/2
            if curr.opmode == 'simple' and curr.curr_op in peops:
                pass
                #if event.state & gtk.gdk.CONTROL_MASK:
                #    self.drawer.set_op_AP(curr.curr_op,event.state )
                #    dt = curr.date.dt
                #    dt = datetime.combine(dt.date(),dt.time())
                #    self.hsel.get_child().set_house_from_date(dt)
                #    self.redraw()
                #    self.redraw_auxwins()
                #    return
            elif curr.opmode == 'double' or curr.curr_op == 'rad_and_transit':
                deg = math.degrees(math.atan2(y-h, (x%w)-(w/2) )) 
                for_op = [curr.opleft,curr.opright][x > w]
                if curr.clickmode == 'click':
                    for_ch = ['chart','click'][x > w]
                else:
                    for_ch = 'chart'
                if deg == 0.0: deg = 0.0001
                self.drawer.set_AP(deg,for_op,for_ch)
                self.redraw()
                dt = curr.date.dt
                dt = datetime.combine(dt.date(),dt.time())
                self.hsel.get_child().set_house_from_date(dt)
                self.redraw_auxwins()
                info['button'] = -1
            else:
                return False
            return True
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 2:
            if curr.clickmode == 'click' and curr.opmode != 'simple':
                return
            if curr.opmode == 'double':
                boss.mpanel.chooser.swap_ops() 
                boss.da.redraw_auxwins(True)
            elif curr.opmode == 'triple':
                x, y = event.x,event.y 
                w, h = da.allocation.width, da.allocation.height
                side = ['up',None][y > (h/2)] 
                if not side:
                    side = ['left','right'][x > (w/2)] 
                boss.mpanel.chooser.swap_ops(side) 
            elif curr.opmode == 'simple':
                if self.zoom_in:
                    self.panning = not self.panning
                elif not showAP:
                    nb = boss.mpanel.chooser.notebook
                    page = nb.get_current_page()
                    sel = nb.get_nth_page(page).get_selection()
                    m,i = sel.get_selected()
                    ix = m.get_path(i)[0]
                    if ix == 0 and not self.planpopup:
                        self.planpopup = PlanPopup(boss)
                    elif page == 3 and ix in [2,3,4]:
                        if not self.textspopup:
                            self.textspopup = TextPopup(ix)
                    #else:
                    #    sel.select_path(0)
                    #    sel.emit('changed') 
                else:
                    self.drawer.set_op_AP(curr.curr_op,event.state )
                    dt = curr.date.dt
                    dt = datetime.combine(dt.date(),dt.time())
                    self.hsel.get_child().set_house_from_date(dt)
                    self.redraw()
                    self.redraw_auxwins()
        elif event.type == gtk.gdk.BUTTON_RELEASE:
            if self.planpopup:
                self.planpopup.destroy()
                self.planpopup = None 
            if curr.curr_op in bios or curr.opmode != 'simple':
                return False
            if info['button'] < 0 or info['button'] == 100:
                return True
            if info['button'] == event.button:
                info['button'] = -1
                if getattr(self, 'panning', False):
                    try:
                        if self.get_window():
                            self.get_window().set_cursor(None)
                    except Exception:
                        pass
                if not getattr(self, 'panning', False):
                    self.drawer.ruline = None
                    self.rulinepending = None
                    if showAP:
                        w = da.allocation.width/2; h = da.allocation.height/2
                        deg = math.degrees(math.atan2(y-h,x-w))
                        for_op = curr.curr_op
                        for_ch = 'chart'
                        self.drawer.set_AP(deg,for_op,for_ch)
                        dt = curr.date.dt
                        dt = datetime.combine(dt.date(),dt.time())
                        self.hsel.get_child().set_house_from_date(dt)
                    self.redraw()
                    boss.redraw(both=False)
                    self.redraw_auxwins()
        elif event.type == gtk.gdk.MOTION_NOTIFY:
            if curr.curr_op in bios or curr.opmode != 'simple':
                return False
            _, x, y, state = event.window.get_pointer()
            if DrawMaster.overlay:
                self.m_x = x
                self.m_y = y
                self.queue_draw()
            if info['button'] < 0 or info['button'] == 100:
                info['button'] = -1
                return False
            w = da.allocation.width/2; h = da.allocation.height/2
            if getattr(self, 'panning', False):
                x_delta = info.get('click_x', event.x_root) - event.x_root
                y_delta = info.get('click_y', event.y_root) - event.y_root
                info['click_x'] = event.x_root
                info['click_y'] = event.y_root
                
                req_w, req_h = self.get_size()
                w = max(req_w, self.allocation.width)
                h = max(req_h, self.allocation.height)
                wrange = w - self.ha.get_page_size()
                hrange = h - self.va.get_page_size()
                
                if x_delta + self.ha.get_value() < 0:
                    self.ha.set_value(0)
                elif x_delta + self.ha.get_value() > wrange: 
                    self.ha.set_value(wrange)
                else:
                    self.ha.set_value(self.ha.get_value() + x_delta)
                    
                if y_delta + self.va.get_value() < 0:
                    self.va.set_value(0)
                elif y_delta + self.va.get_value() > hrange: 
                    self.va.set_value(hrange)
                else:
                    self.va.set_value(self.va.get_value() + y_delta)
                    
                self.queue_draw()
            else:
                self.drawer.ruline = (x-w,y-h)
                self.queue_draw()
            #self.queue_draw()

    def toggle_overlay(self):
        DrawMaster.overlay = not DrawMaster.overlay 
        if DrawMaster.overlay:
            pixmap = gtk.gdk.Pixmap(None, 1, 1, 1)
            color = gtk.gdk.Color()
            cursor = gtk.gdk.Cursor(pixmap, pixmap, color, color, 0, 0)
            self.window.set_cursor(cursor)
        else:
            self.window.set_cursor(None)
        self.queue_draw()

    def on_scroll(self,da,event):
        print("SCROLL EVENT RECEIVED!", "zoom_in:", getattr(self, 'zoom_in', False))
        if getattr(self, 'zoom_in', False):
            return False
            
        x, y = event.x,event.y 
        w, h = da.allocation.width, da.allocation.height
        side = None
        
        scroll_delta = gtk.gdk.scroll_delta(event)
        if scroll_delta > 0:
            delta = -1
        elif scroll_delta < 0:
            delta = 1
        else:
            return False

        if self.textspopup:
            self.textspopup.destroy()
            self.textspopup = None 
            nb = boss.mpanel.chooser.notebook
            page = nb.get_current_page()
            m,i = nb.get_nth_page(page).get_selection().get_selected()
            ix = m.get_path(i)[0] + delta 
            if page == 3 and ix in [2,3,4]:
                self.textspopup = TextPopup(ix)
        
        if  curr.opmode == 'simple':
            boss.mpanel.chooser.delta_select(delta) 
        elif  curr.opmode == 'triple':
            side = ['up',None][y > (h/2)] 
            if not side:
                side = ['left','right'][x > (w/2)] 
            curr.set_opdelta(delta,side)
            boss.mpanel.chooser.delta_triple_select(delta,side) 
        elif  curr.opmode == 'double':
            side = ['left','right'][x > (w/2)] 
            curr.set_opdelta(delta,side)
            boss.mpanel.chooser.delta_double_select(delta,side) 
        
        self.redraw()
        return True

    def on_menuitem_activate(self,menuitem): 
        if menuitem.get_child().get_text() == _('Acercar'):
            scrw, scrh = self.get_size()
            if scrw <= 100: scrw = 720
            if scrh <= 100: scrh = 720
            self.set_size(int(scrw*2), int(scrh*2))
            self.queue_draw()
            self.zoom_in = True
            self.panning = True
            menuitem.get_child().set_text(_('Alejar'))
        elif menuitem.get_child().get_text() == _('Alejar'):
            scrw, scrh = self.get_size()
            if scrw <= 100: scrw = 720
            if scrh <= 100: scrh = 720
            self.set_size(int(scrw/2), int(scrh/2))
            self.queue_draw()
            self.zoom_in = False
            self.panning = False
            menuitem.get_child().set_text(_('Acercar'))
        elif menuitem.get_child().get_text() == _('Ayuda'):
            boss.mainwin.show_help()
        elif menuitem.get_child().get_text() == _('Ver zonas PE'):
            self.drawer.pe_zones = True
            self.redraw_auxwins(True)
            menuitem.get_child().set_text(_('Ocultar zonas PE'))
        elif menuitem.get_child().get_text() == _('Ocultar zonas PE'):
            self.drawer.pe_zones = False
            self.redraw_auxwins(True)
            menuitem.get_child().set_text(_('Ver zonas PE')) 
        elif menuitem.get_child().get_text() == _('Ver zonas de casa'):
            self.drawer.hzones = True
            menuitem.get_child().set_text(_('Ocultar zonas de casa'))
        elif menuitem.get_child().get_text() == _('Ocultar zonas de casa'):
            self.drawer.hzones = False
            menuitem.get_child().set_text(_('Ver zonas de casa'))
        elif menuitem.get_child().get_text() == _('Solo EA'):
            DrawMixin.set_onlyEA(True)
            menuitem.get_child().set_text(_('Mostrar todo')) 
        elif menuitem.get_child().get_text() == _('Mostrar todo'):
            DrawMixin.set_onlyEA(False)
            menuitem.get_child().set_text(_('Solo EA'))
        elif menuitem.get_child().get_text() == _('Activar goodwill'):
            self.drawer.goodwill = True
            menuitem.get_child().set_text(_('Desactivar goodwill'))
        elif menuitem.get_child().get_text() == _('Desactivar goodwill'):
            self.drawer.goodwill = False
            menuitem.get_child().set_text(_('Activar goodwill'))
        elif menuitem.get_child().get_text() == _('Ocultar unilaterales'):
            self.drawer.uniaspect = False
            menuitem.get_child().set_text(_('Mostrar unilaterales'))
        elif menuitem.get_child().get_text() == _('Mostrar unilaterales'):
            self.drawer.uniaspect = True
            menuitem.get_child().set_text(_('Ocultar unilaterales'))
        elif menuitem.get_child().get_text() == _('Ver EA'):
            DrawMixin.set_showEA(True)
            menuitem.get_child().set_text(_('Ocultar EA'))
        elif menuitem.get_child().get_text() == _('Ocultar EA'):
            DrawMixin.set_showEA(False)
            menuitem.get_child().set_text(_('Ver EA'))
        elif menuitem.get_child().get_text() == _('Ver todos los aspectos'):
            self.drawer.allclick = True
            menuitem.get_child().set_text(_('Ver solo clics'))
        elif menuitem.get_child().get_text() == _('Ver solo clics'):
            self.drawer.allclick = False
            menuitem.get_child().set_text(_('Ver todos los aspectos'))
        elif menuitem.get_child().get_text() == _('Ego-clics'):
            self.drawer.egoclick = True
            menuitem.get_child().set_text(_('Clics sin ego'))
        elif menuitem.get_child().get_text() == _('Clics sin ego'):
            self.drawer.egoclick = False
            menuitem.get_child().set_text(_('Ego-clics'))

        self.redraw()

    def toggle_menulist(self,men,dothing):
        if dothing == 'add':
            self.hidden_op[men].show()
        elif dothing == 'remove':
            self.hidden_op[men].hide() 
    
    def popup_menu(self):
        event = gtk.gdk.Event(gtk.gdk.BUTTON_PRESS)
        self.menu.popup(None, None, None, 1, event.time)

    def redraw(self): 
        self.queue_draw()
        #if self.panning:
        #    w = int(self.ha.upper - self.ha.lower)
        #    h = int(self.va.upper - self.va.lower)
        #    x = int(self.ha.lower)
        #    y = int(self.va.lower)
        #    self.bin_window.invalidate_rect(gtk.gdk.Rectangle(x,y,w,h),False) 
        #else:
        #    w = self.allocation.width
        #    h = self.allocation.height
        #    self.bin_window.invalidate_rect(gtk.gdk.Rectangle(0,0,w,h),False)
        if self.diadavisible:
            w = self.diada.get_child().allocation.width
            h = self.diada.get_child().allocation.height
            self.diada.get_child().window.invalidate_rect(gtk.gdk.Rectangle(0,0,w,h),False)
        if boss.da.hselvisible:
            boss.da.hsel.get_child().queue_draw()

    def redraw_auxwins(self,onlybridge=False):
        if self.bridge:
            self.bridge.sda.redraw()
        if onlybridge:
            return
        for aux in self.auxwins:
            aux.sda.redraw()

    def show_panel(self,menuitem=None):
        if curr.curr_op in ['compo_one', 'compo_two']:
            self._reset_viewport_to_origin()
            self._schedule_overlay_reanchor()
        self.panelvisible = True
        self._sync_overlay_positions()
        self.redraw()
        #boss.mpanel.stop_timeout()

    def hide_panel(self,menuitem=None):
        self.panelvisible = False
        self._sync_overlay_positions()
        self.redraw()
        if curr.curr_chart == curr.now:
            self.panel.nowbut.emit('clicked')
            #boss.mpanel.start_timeout()

    def show_pe(self,menuitem=None):
        if curr.curr_chart == curr.now:
            boss.mpanel.toolbar.get_nth_item(1).set_active(False)
            return
        DrawMixin.set_showAP('now')
        #self.panel.nowbut.emit('clicked')
        self.redraw()
        self.redraw_auxwins()
        
    def hide_pe(self,menuitem=None):
        DrawMixin.set_showAP(None)
        self.redraw()
        self.redraw_auxwins()
    
    def show_diada(self,menuitem=None):
        if curr.curr_op in ['compo_one', 'compo_two']:
            self._reset_viewport_to_origin()
            self._schedule_overlay_reanchor()
        self.diadavisible = True 
        self._sync_overlay_positions()
        self.redraw()
    
    def hide_diada(self,menuitem=None):
        self.diadavisible = False
        self._sync_overlay_positions()
        self.redraw()
    
    def make_auxwin(self):
        self.auxwins.append(AuxWindow(boss.mainwin)) 
        sda = self.auxwins[-1].sda
        sda.drawer.hoff = sda.allocation.width * 0.125
        sda.drawer.gridw = sda.drawer.hoff * 6

    def make_pebridge(self):
        if not self.bridge:
            self.bridge = BridgePEWindow(boss.mainwin)
    
    def hide_pebridge(self):
        self.bridge.exit()
        self.bridge = None


    def make_plsel(self):
        if not self.plselector:
            self.plselector = PlanSelector(self.boss.mainwin)
            # Keep the selector at Astro-Nex's upper-left corner, as in the
            # original UI.  Absolute (0, 0) may place it behind the title bar
            # on Windows, so anchor it below the parent window decoration.
            wx, wy = self.boss.mainwin.get_position()
            self.plselector.move(wx + 8, wy + 36)
            self.plselector.present()

    def make_cycleswin(self): 
        if not self.cycleselector:
            self.cycleselector = CycleSelector(self.boss.mainwin)
            wx,wy = self.boss.mainwin.pos_x,self.boss.mainwin.pos_y
            ww,wh =self.boss.mainwin.get_size()
            w,h= self.cycleselector.allocation.width, self.cycleselector.allocation.height
            self.cycleselector.move(wx+ww-w-10,wh+wy-h-24)

    def dispatch(self, da, cr):
        cr = CairoContext(cr)
        cr.save()
        # GTK3 layout rendering intercepts the draw signal at the widget level,
        # so we must manually offset by the scroll adjustments to visually pan.
        cr.translate(-self.ha.get_value(), -self.va.get_value())
        self._sync_overlay_visibility_from_toolbar()
        if self.diadavisible:
            where = self.allocation.width - self.diada.allocation.width
            if self.where_diada != where:
                self.move(self.diada,where,0)
                self.where_diada = where
        
        op = curr.curr_op
        if self.fullscreen:
            DrawMixin.extended_canvas = False
            #self.set_size(720,720)
        elif op in extended and curr.opmode == 'simple' :
            if not DrawMixin.extended_canvas:
                DrawMixin.extended_canvas = True
                pad = 160; 
                if op in ['compo_one','compo_two']: 
                    if boss.mainwin.scr_width <= 1024:
                        pad = self.allocation.width * 0.4
                    else:
                        pad = self.allocation.width * 0.55
                self.set_size(720,int(720+pad))
            if op != self._last_extended_op:
                self._reset_viewport_to_origin()
                self._schedule_overlay_reanchor()
                self._last_extended_op = op
        else:
            self._overlay_reanchor_pending = False
            if self._overlay_reanchor_source:
                gobject.source_remove(self._overlay_reanchor_source)
                self._overlay_reanchor_source = None
            self._last_extended_op = None
            if DrawMixin.extended_canvas:
                DrawMixin.extended_canvas = False
                self.set_size(720,720)

        if op == 'compo_two' and self._overlay_reanchor_pending:
            self._reset_viewport_to_origin()
        self._sync_overlay_positions()
        if op == 'compo_two' and not self._overlay_reanchor_source:
            self._overlay_reanchor_pending = False
    
        if op in bios and not self.hselvisible and curr.opmode == 'simple':
            where = self.allocation.height - self.hsel.allocation.height - 35
            self.move(self.hsel,10,where)
            self.hselvisible = True
        elif self.hselvisible and curr.opmode != 'simple' or op not in bios:
            self.move(self.hsel,-160,650) 
            self.hselvisible = False

        if self.hselvisible:
            where = self.allocation.height - self.hsel.allocation.height - 35
            if self.where_hsel != where:
                self.move(self.hsel,10,where)
                self.where_hsel = where
        
        req_w, req_h = self.get_size()
        w = max(req_w, self.allocation.width)
        h = max(req_h, self.allocation.height)
        cr.rectangle(0,0,w,h)
        cr.clip()
        cr.set_source_rgb(1.0,1.0,1.0)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(float(self.opts.base))
        
        if self.diadavisible:
            cr.translate(0,h*0.15)
            w *= 0.85; h *= 0.85
        self.drawer.dispatch_pres(cr,w,h)
        if self.diadavisible:
            w /= 0.85; h /= 0.85
        
        cr.restore()
        cr.save()
        header_w = self._header_width(w)
        if self.pepending[0]:
            self.draw_pelabel(cr,header_w,h)
            self.pepending = [False,None,None]
        elif curr.curr_chart == curr.now or curr.curr_op in ['draw_transits','solar_rev']:
            self.d_now_date(cr,header_w,h)
        if self.rulinepending:
            self.d_ruldegree(cr,header_w,h)
        self.draw_label(cr,w,h) 
        if self.check_local_label():
            self.d_loclbl(cr,w,h)
                
        if DrawMaster.overlay:
            col = gtk.gdk.color_parse('#'+self.opts.overlay) 
            ovcol = [col.red/MAGICK_COL,col.green/MAGICK_COL,col.blue/MAGICK_COL,0.5]
            cr.set_source_rgba(*ovcol)
            radial = cairo.RadialGradient(self.m_x,self.m_y,45,self.m_x,self.m_y,50)
            radial.add_color_stop_rgba(0.0,0,0,1,0)
            radial.add_color_stop_rgba(0.9,1,0,0,1)
            cr.mask(radial)

        cr.restore()

    def _header_width(self, chart_width):
        toplevel = self.get_toplevel()
        if isinstance(toplevel, gtk.Window):
            return max(chart_width, toplevel.get_allocated_width())
        return chart_width

    def check_local_label(self):
        if curr.opmode == 'simple' and curr.curr_op == 'draw_local': 
            return True
        labelyes = curr.opleft == 'draw_local' or curr.opright == 'draw_local'
        if curr.opmode == 'double' and labelyes:
            return True 
        if curr.opmode == 'triple' and labelyes or curr.opup == 'draw_local':
            return True 
        return False 

    def d_ruldegree(self,cr,w,h):
        if self.diadavisible:
            return
        sign,deg = divmod(self.rulinepending,30)
        mint = int((deg - int(deg)) * 60)
        sign = int(sign)
        deg = int(deg)
        let = self.drawer.zodlet[sign]
        col = boss.opts.zodiac.zod[sign].col
        signs = "%s\u00b0 %s\u00b4" % (deg,mint)
        layout = cr.create_layout()
        cr.set_source_rgb(0,0,0.6) 
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        layout.set_text(signs)
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        cr.move_to(w-xpos-20,20)
        cr.show_layout(layout)
        
        font = pango.FontDescription("Astro-Nex")
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        cr.set_source_rgb(*col)
        layout.set_text(let)
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        cr.move_to(w-xpos-5,20)
        cr.show_layout(layout)

    def draw_pelabel(self,cr,w,h):
        if self.diadavisible:
            return

        date = curr.date.ld
        date = date.__str__().split(' ')[0].split('-')
        date.reverse()
        date = "/".join(date) 
        layout = cr.create_layout()
        
        signs = ['','']
        collet = [0,0]
        for i in [1,2]:
            pe = self.pepending[i]
            if not pe: break
            sign,deg = divmod(pe,30)
            mint = int((deg - int(deg)) * 60)
            sign = int(sign)
            deg = int(deg)
            let = self.drawer.zodlet[sign]
            col = boss.opts.zodiac.zod[sign].col
            collet[i-1] = (col,let,i%2)
            signs[i-1] = "%s\u00b0 %s\u00b4" % (deg,mint)
        if signs[1]:
            signs[0],signs[1] = signs[1],signs[0]

        cr.set_source_rgb(0,0,0.6) 
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        layout.set_text(signs[1]+" "+date+" "+signs[0])
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        cr.move_to(w-xpos-20,5)
        cr.show_layout(layout)

        font = pango.FontDescription("Astro-Nex")
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        if collet[1]: 
            off = xpos+22
            for col,let,f in collet:
                cr.set_source_rgb(*col)
                layout.set_text(let)
                ink,logical = layout.get_extents()
                xpos = logical[2]/pango.SCALE
                cr.move_to(w-xpos-5-f*off,5)
                cr.show_layout(layout)
        else:
            cr.set_source_rgb(*col)
            layout.set_text(let)
            ink,logical = layout.get_extents()
            xpos = logical[2]/pango.SCALE
            cr.move_to(w-xpos-5,5)
            cr.show_layout(layout)
        
    def d_now_date(self,cr,w,h):
        if self.diadavisible:
            return
        strdate = curr.charts['now'].date
        date,time = parsestrtime(strdate)
        date = date + " " + time.split(" ")[0]
        layout = cr.create_layout()
        cr.set_source_rgb(0,0,0.6)
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        layout.set_text(date)
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        cr.move_to(w-xpos-18,5) 
        cr.show_layout(layout)
    
        font = pango.FontDescription("Astro-Nex")
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        regent = curr.year_regent()
        pl = boss.opts.zodiac.plan[regent]
        cr.set_source_rgb(*pl.col)
        layout.set_text(pl.let)
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        cr.move_to(w-xpos-5,5)
        cr.show_layout(layout)


    def d_loclbl(self,cr,w,h):
        layout = cr.create_layout()
        cr.set_source_rgb(0,0.5,0.3) 
        font = pango.FontDescription(self.opts.font)
        font.set_size(8*pango.SCALE)
        layout.set_font_description(font)
        region = curr.loc.region
        if boss.opts.lang == 'ca' and curr.loc.country == 'España':
            region = cata_reg[region]
        layout.set_text(curr.loc.city+' ('+region+'-'+t(curr.loc.country)[0]+')')
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        cr.move_to(w/2-xpos/2,h-15)
        cr.show_layout(layout)

    def draw_label(self,cr,w,h): 
        if curr.curr_op in sheetops:
            return
        layout = cr.create_layout()
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        h -= 20 if self.fullscreen else 15

        cols = [(0,0,0.4),(0.8,0,0.1)]
        ix = [0,1][curr.clickmode == 'click']
        charts = (curr.curr_chart,curr.curr_click) 
        for i in range(ix+1):
            name = "%s %s" % (charts[i].first,charts[i].last) 
            layout.set_text(name)
            ink,logical = layout.get_extents()
            xpos = logical[2]/pango.SCALE
            if ix and not i:
                pos = 0 + 5
            else:
                pos = w - xpos - 5 
            cr.set_source_rgb(*cols[i]) 
            cr.move_to(pos,h)
            cr.show_layout(layout)
        if self.diadavisible and curr.clickmode == 'click':
            where = self.allocation.width - self.diada.allocation.width
            name = "%s %s" % (charts[0].first,charts[0].last) 
            layout.set_text(name)
            ink,logical = layout.get_extents()
            xpos = logical[2]/pango.SCALE
            cr.move_to(where-20,5+xpos)
            cr.rotate(-90*math.pi/180)
            cr.set_source_rgb(*cols[0]) 
            cr.show_layout(layout)


############################################
############################################

class ChangeDatePanel(gtk.VBox):
    changes = ['minutes','hours','days']
    def __init__(self,parent):
        gtk.VBox.__init__(self)
        
        frame = gtk.Frame()
        self.time = curr.date.ld.time()
        self.internal_signal = True
        self.needsredrawing = True
        self.calendar = CompactCalendar()
        # GTK3 themes use a much larger natural calendar than the GTK2
        # reference.  Scope this compact style to the in-canvas calendar so
        # its historical proportions do not enlarge the chart area.
        _add_compact_style(self.calendar, 'astronex-compact-calendar')
        self.calendar.set_display_options(gtk.CALENDAR_SHOW_HEADING | gtk.CALENDAR_WEEK_START_MONDAY)
        self.calendar.connect('day-selected', self.on_calendar_day_selected,parent)
        self.mth_hid = self.calendar.connect('month-changed',self.on_calendar_day_selected,parent)
        frame.add(self.calendar)
        self.pack_start(frame, False, False)
        
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect("button_press_event", lambda s,but: True)
        
        butbox = gtk.HBox()

        def compact(widget):
            _add_compact_style(widget, 'astronex-compact-date-control')
            return widget
        
        stepbox = gtk.HBox(False, 0)
        self.spin = compact(gtk.Entry())
        self.spin.set_alignment(1.0)
        self.spin.set_width_chars(2)
        self.spin.set_max_length(2)
        self.spin.set_text('1')
        self.spin.set_size_request(52,24)
        stepbox.pack_start(self.spin, False, False)

        spinner = gtk.VBox(False, 0)
        up = compact(gtk.Button())
        up.set_size_request(12,10)
        up.add(gtk.Label(u'\u25b4'))
        up.connect('clicked', self.on_step_adjust, 1)
        spinner.pack_start(up, False, False)

        down = compact(gtk.Button())
        down.set_size_request(12,10)
        down.add(gtk.Label(u'\u25be'))
        down.connect('clicked', self.on_step_adjust, -1)
        spinner.pack_start(down, False, False)

        stepbox.pack_start(spinner, False, False)
        butbox.pack_start(stepbox,False,False)

        button = compact(gtk.Button())
        button.set_size_request(24,20)
        button.set_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.BUTTON_RELEASE_MASK)
        arrow = gtk.Label(u'\u25c0')
        button.add(arrow)
        button.set_data('dir','<')
        button.connect("button_press_event",self.on_panel_clicked,parent)
        button.connect("button_release_event",self.on_panel_clicked,parent)
        butbox.pack_start(button,False,False)
        
        self.combo = compact(gtk.combo_box_new_text())
        self.combo.append_text(_("minutos"))
        self.combo.append_text(_("horas"))
        self.combo.append_text(_("dias"))
        self.combo.set_active(2)
        self.combo.set_size_request(54,20)
        butbox.pack_start(self.combo,True,True)
        
        button = compact(gtk.Button())
        button.set_size_request(24,20)
        button.set_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.BUTTON_RELEASE_MASK)
        arrow = gtk.Label(u'\u25b6')
        button.add(arrow)
        button.set_data('dir','>')
        button.connect("button_press_event",self.on_panel_clicked,parent)
        button.connect("button_release_event",self.on_panel_clicked,parent)
        butbox.pack_start(button,False,False)

        but = compact(gtk.Button())
        but.set_size_request(24,20)
        img = gtk.Image()
        appath = boss.app.appath
        imgfile = path.joinpath(appath,"astronex/resources/refresh-18.png")
        img.set_from_file(str(imgfile))
        but.set_image(img)
        butbox.pack_start(but,False,False)
        but.connect('clicked',self.on_now_clicked)
        self.nowbut = but
        self.pack_start(butbox,False,False) 
        self.set_size_request(230,160)
    
    def on_calendar_day_selected(self,cal,parent):
        y,m,d = cal.get_date()
        time = self.time
        try:
            date = datetime.combine(datetime(y,m+1,d),time)
        except ValueError:
            try:
                date = datetime.combine(datetime(y,m+1,d-1),time) 
            except ValueError:
                date = datetime.combine(datetime(y,m+1,d-3),time) 
        curr.date.setdt(date)
        curr.refresh_nowchart()
        boss.mpanel.act_now(curr.now)
        if parent.cycleselector:
            cycles = curr.curr_chart.get_cycles(date)
            parent.cycleselector.adj.set_value(cycles+1) 
        if self.internal_signal:
            boss.da.hsel.get_child().set_house_from_date(date) 
        if self.needsredrawing:
            parent.redraw()
            boss.da.redraw_auxwins()
        else:
            self.needsredrawing = True
        self.internal_signal = True

    def on_panel_clicked(self,but,event,parent):
        delta = self.get_step_value()
        if but.get_data('dir') == '<':
            delta = -delta
        change = self.changes[self.combo.get_active()] 
        if event.type == gtk.gdk.BUTTON_PRESS:
            self.timeout_sid = gobject.timeout_add(80,self.start_spining,delta,change)
        elif event.type == gtk.gdk.BUTTON_RELEASE:
            gobject.source_remove(self.timeout_sid)

    def get_step_value(self):
        raw = self.spin.get_text().strip()
        try:
            value = int(raw)
        except (TypeError, ValueError):
            value = 1
        value = max(1, min(10, value))
        self.spin.set_text(str(value))
        return value

    def on_step_adjust(self, button, delta):
        value = self.get_step_value()
        value = max(1, min(10, value + delta))
        self.spin.set_text(str(value))

    def start_spining(self,delta,change):
        dt = self.set_delta((delta,change))
        self.set_date(dt,True)
        return True

    def on_now_clicked(self,but):
        self.set_date(datetime.now(),True)

    def update_cycles(self,delta):
        y,m,d = self.calendar.get_date()
        y = y + 72*delta
        self.set_date(datetime(y,m+1,d))

    def set_date(self,date,timechanged=False):
        if timechanged:
            self.time = date.time()
            self.internal_signal = True
        else:
            self.time = curr.date.ld.time() 
            self.internal_signal = False
        self.set_cal(date)

    def set_cal(self,date):
        self.calendar.handler_block(self.mth_hid)
        self.calendar.select_month(date.month - 1, date.year)
        self.calendar.handler_unblock(self.mth_hid)
        self.calendar.select_day(date.day)
        self.calendar.clear_marks()
        self.calendar.mark_day(date.day)
    
    def set_date_only(self,date):
        self.time = date.time()
        self.internal_signal = True
        self.set_cal(date)
        self.needsredrawing = False

    def set_delta(self,delta):
        amount = delta[0]
        what = delta[1]
        dt = datetime.combine(curr.date.ld.date(),curr.date.ld.time())
        if what == 'minutes':
            dt = dt + timedelta(minutes=amount)
        elif what == 'hours':
            dt = dt + timedelta(hours=amount)
        elif what == 'days':
            dt = dt + timedelta(days=amount)
        return dt
