#!/usr/bin/env python3
from optparse import OptionParser
parser = OptionParser()

parser.add_option("-c", "--console", action="store_true", default=False)
(options, args) = parser.parse_args()

from pathlib import Path
from astronex.extensions.path import path

# Resources belong to this checkout, not to whichever directory the user was
# in when launching the program.
appath = path(Path(__file__).resolve().parent)
from astronex import nex
nex.main(appath,options.console)
