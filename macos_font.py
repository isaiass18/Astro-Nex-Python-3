"""Register Astro-Nex's symbol font for the current macOS process."""

import ctypes
import sys
from pathlib import Path


def register_process_font(font_path):
    """Make *font_path* visible to CoreText without changing user fonts.

    Pango on macOS uses CoreText. Bundling a TTF in a PyInstaller app is not
    sufficient on its own: the font must be registered in the running process
    before GTK creates its font map. Process scope avoids copying files into
    ``~/Library/Fonts`` and requires no administrator permission.
    """
    if sys.platform != "darwin":
        return False

    font_path = Path(font_path)
    if not font_path.is_file():
        return False
    raw_path = str(font_path).encode("utf-8")

    try:
        core_foundation = ctypes.CDLL(
            "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
        )
        core_text = ctypes.CDLL(
            "/System/Library/Frameworks/CoreText.framework/CoreText"
        )
        core_foundation.CFURLCreateFromFileSystemRepresentation.argtypes = (
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_long,
            ctypes.c_bool,
        )
        core_foundation.CFURLCreateFromFileSystemRepresentation.restype = ctypes.c_void_p
        core_foundation.CFRelease.argtypes = (ctypes.c_void_p,)
        core_text.CTFontManagerRegisterFontsForURL.argtypes = (
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_void_p),
        )
        core_text.CTFontManagerRegisterFontsForURL.restype = ctypes.c_bool

        url = core_foundation.CFURLCreateFromFileSystemRepresentation(
            None, raw_path, len(raw_path), False
        )
        if not url:
            return False
        try:
            error = ctypes.c_void_p()
            # kCTFontManagerScopeProcess: visible only to Astro-Nex.
            return bool(core_text.CTFontManagerRegisterFontsForURL(
                url, 1, ctypes.byref(error)
            ))
        finally:
            core_foundation.CFRelease(url)
    except OSError:
        return False
