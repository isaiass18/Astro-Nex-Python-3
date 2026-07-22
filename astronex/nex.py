#!/usr/bin/python
# -*- coding: utf-8 -*- 
import sys, os
import glob
import gettext
import atexit
from pathlib import Path
from . import countries 
from .config import read_config
LOCALE_DIR = Path(__file__).resolve().parent / 'locale'
lang_es = gettext.translation('astronex', str(LOCALE_DIR), languages=['es'])
lang_en = gettext.translation('astronex', str(LOCALE_DIR), languages=['en'])
lang_ca = gettext.translation('astronex', str(LOCALE_DIR), languages=['ca'])
lang_de = gettext.translation('astronex', str(LOCALE_DIR), languages=['de'])
langs = { 'en': lang_en, 'es': lang_es, 'ca': lang_ca, 'de': lang_de }

from .extensions.path import path
version = "1.2"

def die(message):
    """Die in a command line way."""
    sys.exit(1)

try:
    import gtk
    import gobject
except ImportError:
    die('Astro-Nex requires the GTK 3 Python bindings. They were not found.')

if sys.version_info < (3, 9):
    die('Astro-Nex requires Python 3.9 or later. Only %s.%s was found.' %
            sys.version_info[:2])


home_dir = '.astronex'
config_file = 'cfg.ini'
default_db = 'charts.db'
ephe_path = 'ephe'
ephe_flag = 4

def check_home_dir(appath):
    """Set home dir, copying needed files"""
    global home_dir, ephe_flag
    default_home = path.joinpath(path.expanduser(path('~')), home_dir)
    
    if not path.exists(default_home):
        path.mkdir(default_home)
    ephepath = path.joinpath(default_home,ephe_path)
    if not path.exists(ephepath):
        path.mkdir(path.joinpath(default_home,ephe_path))
        path.copy(path.joinpath(appath,"astronex/resources/README"),ephepath)
    if ephepath.glob("*.se1"):
        ephe_flag = 2 
    if not path.exists(path.joinpath(default_home,default_db)):
        path.copy(path.joinpath(appath,"astronex/resources/charts.db"),default_home)

    home_dir = default_home
    

def init_config(homedir,opts,state): 
    ephepath = path.joinpath(homedir,opts.ephepath)
    from pysw import setpath
    setpath(str(ephepath))
    
    state.country = opts.country
    state.usa = {'false':False,'true':True}[opts.usa]
    state.database = opts.database
    state.setloc(opts.locality,opts.region)
    state.init_nowchart()
    state.curr_chart = state.now
    state.epheflag = ephe_flag
    opts.epheflag = ephe_flag

    if opts.favourites:
        try:
            tbl = opts.favourites
            nfav = int(opts.nfav)
            favs = state.datab.get_favlist(tbl,nfav,state.newchart())
            state.fav = favs
        except:
            pass
    
    from .chart import orbs as ch_orbs
    orbs = [opts.lum,opts.normal,opts.short,opts.far,opts.useless]
    for l in orbs:
        state.orbs.append(list(map(float,l)))
        ch_orbs.append(list(map(float,l))) 
    peorbs = [opts.pelum,opts.penormal,opts.peshort,opts.pefar,opts.peuseless]
    for l in peorbs:
        state.peorbs.append(list(map(float,l)))
    for l in opts.transits:
        state.transits.append(float(l)) 
    opts.discard = [ int(x) for x in opts.discard ]

class Splash (gtk.Window):
    def __init__(self,appath):
        gtk.Window.__init__(self,gtk.WINDOW_POPUP)
        self.set_default_size(400, 250) 
        self.set_position (gtk.WIN_POS_CENTER)
        vbox = gtk.VBox()
        img = gtk.Image()
        splashimg = path.joinpath(appath,"astronex/resources/splash.png")
        try:
            img.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(splashimg))
            vbox.pack_start(img)
        except Exception:
            # A damaged/missing system image loader must not prevent the
            # application from starting; the splash is decorative only.
            vbox.pack_start(gtk.Label("Astro-Nex"), True, True)
        self.add(vbox)

def init_ipshell():    
    ''' ipython suport (for linux)'''
    if sys.platform != 'win32': 
        try:
            __IPYTHON__
        except NameError:
            argv = ['']
            banner = exit_msg = ''
        else:
            argv = ['-pi1','In <\\#>:','-pi2','   .\\D.:','-po','Out<\\#>:']
            banner = '*** Nested interpreter ***'
            exit_msg = '*** Back in main IPython ***'

        #from IPython.Shell import IPShellEmbed
        #ipshell = IPShellEmbed(argv,banner=banner,exit_msg=exit_msg)
        #return ipshell 
        from traitlets.config import Config
        cfg = Config()
        cfg.InteractiveShellEmbed.prompt_in1="myprompt [\\#]> "
        cfg.InteractiveShellEmbed.prompt_out="myprompt [\\#]: "
        #cfg.InteractiveShellEmbed.profile=ipythonprofile 
        from IPython.terminal.embed import InteractiveShellEmbed
        shell = InteractiveShellEmbed(config=cfg, banner2=banner)
        shell.user_ns = {}
        return shell

class application(object):
    """The Nex Application."""

    def __init__(self,appath):
        self.home_dir = home_dir
        self.config_file = config_file
        self.default_db = default_db
        self.appath = appath
        self.version = version
        self.langs = langs

    def run(self):
        """Start Nex""" 
        splash = Splash(self.appath)
        splash.show_all()
        gobject.timeout_add(1000, splash.hide) # 5*1000 miliseconds
        gobject.idle_add(self.setup_app)
        gtk.main()

    def run_console(self):
        opts = read_config(self.home_dir)
        opts.home_dir = self.home_dir
        langs[opts.lang].install()
        countries.install(opts.lang)
        self.lang = opts.lang
        from .state import Current
        from .boss import Manager
        state = Current(self)
        init_config(self.home_dir,opts,state)
        boss = Manager(self,opts,state)
        boss.ipshell = init_ipshell() 
        boss.ipshell()

    def setup_app(self):
        opts = read_config(self.home_dir)
        opts.home_dir = self.home_dir
        langs[opts.lang].install()
        countries.install(opts.lang)
        self.lang = opts.lang
        from .state import Current
        from .boss import Manager
        state = Current(self)
        atexit.register(state.save_pool,self)
        init_config(self.home_dir,opts,state)
        boss = Manager(self,opts,state)
        from .gui.winnex import WinNex
        mainwin = WinNex(boss)
        boss.set_mainwin(mainwin)
        #if 'DEBUG_NEX' in os.environ:
        #    boss.ipshell = init_ipshell() 
    
    def stop(self):
        """Stop Nex."""
        gtk.main_quit()

def main(appath,console=False):
    check_home_dir(appath)
    app = application(appath)
    if console:
        app.run_console()
    else:
        app.run()


def cli():
    """Installed console entry point, independent of the working directory."""
    from argparse import ArgumentParser

    parser = ArgumentParser(prog='astronex')
    parser.add_argument('-c', '--console', action='store_true')
    args = parser.parse_args()
    # In a source checkout this is the checkout root; in an installed wheel it
    # is site-packages, both of which contain ``astronex/resources``.
    main(path(Path(__file__).resolve().parent.parent), args.console)
