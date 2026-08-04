# -*- coding: utf-8 -*-
import time
import sys
from distutils.core import setup 

name = 'Astro-Nex'
desc = 'GPL API Software' 
longdesc = 'Program to calculate and draw astrological charts in API method style.'
version='1.2.3'
author='Jose Antonio Rodríguez'
author_email='jar@eideia.net'
url = 'http://astro-nex.com'
license = 'GPL'



setup( 
    name = name,
    description = desc,
    long_description = longdesc,
    version = version, 
    author = author,
    author_email = author_email ,
    url = url,
    license = license,
    requires = ['pygtk (>2.8)','pygobject','pycairo','pytz','configobj','ipython','PIL'],
    packages = ['astronex','astronex.gui','astronex.drawing','astronex.surfaces','astronex.extensions','astronex.scripts'],
    package_dir = { 'astronex': 'astronex' },
    package_data = {'astronex':['astronex/db/local.db','astronex/resources/*','astronex/locale/*',]},
    scripts = ['nex.py'],
    data_files = [
        ('/usr/share/locale/es/LC_MESSAGES','astronex/locale/es/LC_MESSAGES/astronex.mo'),
        ('/usr/share/locale/en/LC_MESSAGES','astronex/locale/en/LC_MESSAGES/astronex.mo'),
        ('/usr/share/locale/ca/LC_MESSAGES','astronex/locale/ca/LC_MESSAGES/astronex.mo'),
        ('/usr/share/locale/de/LC_MESSAGES','astronex/locale/de/LC_MESSAGES/astronex.mo') ]

)



