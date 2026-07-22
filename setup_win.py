# -*- coding: utf-8 -*-
import time
import sys

try:
    import modulefinder
    import win32com
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell"]: #,"win32com.mapi"
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass

name = 'Astro-Nex'
desc = 'GPL API Software' 
longdesc = 'Program to calculate and draw astrological charts in API method style.'
version='1.2'
author='Jose Antonio Rodríguez'
author_email='jar@eideia.net'
url = 'http://astro-nex.com'
license = 'GPL'

from distutils.core import setup 
import glob
import os

import py2exe 
setup( 
    name = name,
    description = desc,
    long_description = longdesc,
    version = version, 
    author = author,
    author_email = author_email ,
    url = url,
    license = license,
    windows = [{'script':'nex.py',
        'icon_resources': [(1,'astronex/resources/nex.ico')]}], 
    options = {'py2exe':{
        'packages':'encodings,pytz,cairo,PIL,IPython,astronex', 'includes':
        'configobj,winshell,pango,atk,pangocairo,gobject,pysw','excludes':'Numeric,numpy,Tkinter,tk,PyQt4,_ssl',
        'dll_excludes': 'tk85.dll,tcl85.dll'}},
    data_files=[('astronex/db',['astronex/db/local.db',]),('astronex/resources',glob.glob('astronex/resources/*')),
        ('astronex/locale/ca/LC_MESSAGES',glob.glob('astronex/locale/ca/LC_MESSAGES/*')),
        ('astronex/locale/es/LC_MESSAGES',glob.glob('astronex/locale/es/LC_MESSAGES/*')),
        ('astronex/locale/en/LC_MESSAGES',glob.glob('astronex/locale/en/LC_MESSAGES/*')),
        ('astronex/locale/de/LC_MESSAGES',glob.glob('astronex/locale/de/LC_MESSAGES/*')),
        ('astronex/zoneinfo',[f for f in  glob.glob('pytz/zoneinfo/*') if os.path.isfile(f)]), 
        ('astronex/zoneinfo/US',glob.glob('pytz/zoneinfo/US/*')),
        ('astronex/zoneinfo/Etc',glob.glob('pytz/zoneinfo/Etc/*')),
        ('astronex/zoneinfo/Asia',glob.glob('pytz/zoneinfo/Asia/*')),
        ('astronex/zoneinfo/Arctic',glob.glob('pytz/zoneinfo/Arctic/*')),
        ('astronex/zoneinfo/Canada',glob.glob('pytz/zoneinfo/Canada/*')),
        ('astronex/zoneinfo/Brazil',glob.glob('pytz/zoneinfo/Brazil/*')),
        ('astronex/zoneinfo/Europe',glob.glob('pytz/zoneinfo/Europe/*')),
        ('astronex/zoneinfo/Pacific',glob.glob('pytz/zoneinfo/Pacific/*')),
        ('astronex/zoneinfo/Chile',glob.glob('pytz/zoneinfo/Chile/*')),
        ('astronex/zoneinfo/Indian',glob.glob('pytz/zoneinfo/Indian/*')),
        ('astronex/zoneinfo/Mexico',glob.glob('pytz/zoneinfo/Mexico/*')),
        ('astronex/zoneinfo/Antarctica',glob.glob('pytz/zoneinfo/Antarctica/*')),
        ('astronex/zoneinfo/Australia',glob.glob('pytz/zoneinfo/Australia/*')), 
        ('astronex/zoneinfo/Atlantic',glob.glob('pytz/zoneinfo/Atlantic/*')), 
        ('astronex/zoneinfo/Mideast',glob.glob('pytz/zoneinfo/Mideast/*')), 
        ('astronex/zoneinfo/Africa',glob.glob('pytz/zoneinfo/Africa/*')),
        ('astronex/zoneinfo/America',[f for f in  glob.glob('pytz/zoneinfo/America/*') if os.path.isfile(f)]),
        ('astronex/zoneinfo/America/Argentina',glob.glob('pytz/zoneinfo/America/Argentina/*')),
        ('astronex/zoneinfo/America/Indiana',glob.glob('pytz/zoneinfo/America/Indiana/*')),
        ('astronex/zoneinfo/America/Kentucky',glob.glob('pytz/zoneinfo/America/Kentucky/*')),
        ('astronex/zoneinfo/America/North_Dakota',glob.glob('pytz/zoneinfo/America/North_Dakota/*'))
        ])

