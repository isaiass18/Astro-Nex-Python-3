"""macOS process-local Astro-Nex font registration."""

import sys
import subprocess
import unittest
from pathlib import Path


@unittest.skipUnless(sys.platform == "darwin", "macOS-specific font test")
class MacosFontTests(unittest.TestCase):
    def test_symbol_font_is_available_to_pango_without_user_installation(self):
        root = Path(__file__).parents[1]
        script = '''
from pathlib import Path
from macos_font import register_process_font
register_process_font(Path("astronex/resources/Astro-Nex.ttf").resolve())
import gi
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo
font_map = PangoCairo.FontMap.get_default()
font = font_map.load_font(font_map.create_context(), Pango.FontDescription("Astro-Nex 12"))
print(font.describe().get_family())
'''
        result = subprocess.run(
            [sys.executable, "-c", script], cwd=root, check=True,
            capture_output=True, text=True,
        )
        self.assertTrue(result.stdout.strip().startswith("Astro-Nex"))
