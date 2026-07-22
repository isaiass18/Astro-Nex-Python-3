"""Regression test for Python 3 AAF country-code import."""

import tempfile
import unittest
import builtins
from pathlib import Path
from types import SimpleNamespace

from astronex import state
from astronex.gui import import_dlg


class _Buffer:
    def set_text(self, text):
        self.text = text

    def get_bounds(self):
        return (None, None)

    def insert_at_cursor(self, text):
        pass

    def insert_with_tags(self, *args):
        pass

    def create_mark(self, *args):
        pass

    def get_insert(self):
        return None

    def get_mark(self, name):
        return None


class _Text:
    def scroll_to_mark(self, *args):
        pass


class _Database:
    def __init__(self):
        self.country_codes = []

    def fetch_blindly(self, country, city, location):
        self.country_codes.append(country)
        location.city = city
        location.zone = "Europe/Madrid"
        return location


class AafImportTests(unittest.TestCase):
    def test_spanish_aaf_code_is_translated_once_and_does_not_decode_str(self):
        database = _Database()
        fake_current = SimpleNamespace(
            datab=database,
            date=SimpleNamespace(settz=lambda zone: None, setdt=lambda dt: None),
            person=SimpleNamespace(first="", last=""),
            setchart=lambda: None,
            charts={"calc": SimpleNamespace(first="", planets=[], houses=[])},
        )
        console = SimpleNamespace(buffer=_Buffer(), error=object(), warning=object(), text=_Text())
        previous = import_dlg.curr
        previous_translation = getattr(builtins, "_", None)
        import_dlg.curr = fake_current
        builtins._ = lambda text: text
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                source = Path(temp_dir) / "sample.aaf"
                source.write_text(
                    "#A93:Perez, Ana,F,01.01.2000g,12:00:00,Madrid,E\n",
                    encoding="utf-8",
                )
                import_dlg.parse_aaf(str(source), "unused", console, True, None, "utf-8")
        finally:
            import_dlg.curr = previous
            if previous_translation is None:
                del builtins._
            else:
                builtins._ = previous_translation

        self.assertEqual(database.country_codes, ["SP"])


if __name__ == "__main__":
    unittest.main()
