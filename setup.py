"""Package Astro-Nex and build its Swiss Ephemeris extension for Python 3."""

import os
from pathlib import Path

from setuptools import Extension, find_packages, setup


ROOT = Path(__file__).parent
SWE = ROOT / "ext" / "ext32" / "src"
SWE_SOURCES = (
    "swedate.c", "swehouse.c", "swejpl.c", "swemmoon.c", "swemplan.c",
    "swepcalc.c", "sweph.c", "swepdate.c", "swephlib.c", "swecl.c",
)

extension = Extension(
    "_pysw",
    sources=[str(ROOT / "ext" / "ext64" / "pysw_wrap.c")]
    + [str(SWE / source) for source in SWE_SOURCES],
    include_dirs=[str(SWE), str(ROOT / "ext" / "ext64")],
    # ``libm`` is a separate library on Unix.  The MSVC runtime already
    # provides the math functions, and asking the Windows linker for ``m``
    # makes a native build fail with LNK1104.
    libraries=["m"] if os.name != "nt" else [],
)

setup(
    name="Astro-Nex",
    version="1.2.3",
    description="GPL API Software",
    long_description="Program to calculate and draw astrological charts in API method style.",
    author="Jose Antonio Rodríguez",
    author_email="jar@eideia.net",
    url="https://astro-nex.net/",
    license="GPL-3.0-or-later",
    python_requires=">=3.9",
    install_requires=["PyGObject>=3.42", "pycairo>=1.20", "pytz", "configobj", "Pillow", "ipython"],
    packages=find_packages(),
    py_modules=["pysw"],
    package_data={
        "astronex": ["db/*.db", "resources/*", "locale/*/LC_MESSAGES/*.mo"],
    },
    ext_modules=[extension],
    entry_points={"console_scripts": ["astronex=astronex.nex:cli"]},
)
