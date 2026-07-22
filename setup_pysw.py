"""Build the Swiss Ephemeris extension for the active Python interpreter.

Run ``python3 setup_pysw.py build_ext --inplace`` from the project root.
The produced _pysw module is specific to the OS, CPU architecture and Python
ABI used for the build, so it must never be committed or copied between them.
"""

from pathlib import Path

from setuptools import Extension, setup


ROOT = Path(__file__).parent
SWE = ROOT / "ext" / "ext32" / "src"
SOURCES = [
    "swedate.c",
    "swehouse.c",
    "swejpl.c",
    "swemmoon.c",
    "swemplan.c",
    "swepcalc.c",
    "sweph.c",
    "swepdate.c",
    "swephlib.c",
    "swecl.c",
]

extension = Extension(
    "_pysw",
    sources=[str(ROOT / "ext" / "ext64" / "pysw_wrap.c")]
    + [str(SWE / source) for source in SOURCES],
    include_dirs=[str(SWE), str(ROOT / "ext" / "ext64")],
    libraries=["m"],
)

setup(name="astronex-pysw", version="1.2.3", ext_modules=[extension])
