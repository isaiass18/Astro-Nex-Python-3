"""Integration coverage for configured location and the current chart."""

import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from astronex import countries, database, nex
from astronex.config import read_config
from astronex.state import Current


ROOT = Path(__file__).resolve().parents[1]


class CurrentChartTests(unittest.TestCase):
    def test_current_chart_uses_configured_location_and_has_houses(self):
        with tempfile.TemporaryDirectory(prefix="astronex-current-") as temp_dir:
            home = Path(temp_dir)
            (home / "ephe").mkdir()
            shutil.copy2(ROOT / "astronex" / "resources" / "charts.db", home / "charts.db")
            app = SimpleNamespace(appath=str(ROOT), home_dir=str(home))

            options = read_config(app.home_dir)
            options.home_dir = app.home_dir
            nex.langs[options.lang].install()
            countries.install(options.lang)

            try:
                state = Current(app)
                nex.init_config(app.home_dir, options, state)

                self.assertEqual(state.curr_chart, state.now)
                self.assertTrue(state.loc.city)
                self.assertTrue(state.loc.zone)
                self.assertEqual(len(state.now.planets), 11)
                self.assertEqual(len(state.now.houses), 12)
                self.assertTrue(all(0 <= cusp < 360 for cusp in state.now.houses))
            finally:
                # Windows retains an exclusive SQLite file handle until it is
                # explicitly closed; TemporaryDirectory therefore needs this.
                database.close()


if __name__ == "__main__":
    unittest.main()
