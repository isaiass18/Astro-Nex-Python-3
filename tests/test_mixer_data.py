"""Regression tests for the chart data operations used by the mixer."""

import pickle
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from astronex import database
from astronex.chart import Chart


ROOT = Path(__file__).resolve().parents[1]


def sample_chart():
    chart = Chart()
    chart.first = "Ada"
    chart.last = "Lovelace"
    chart.category = "Test"
    chart.date = "10/12/1815 00:00:00 UTC"
    chart.city = "London"
    chart.region = "England"
    chart.country = "GB"
    chart.longitud = -0.1278
    chart.latitud = 51.5074
    chart.zone = "Europe/London"
    chart.planets = [float(index) for index in range(11)]
    chart.houses = [float(index * 30) for index in range(12)]
    chart.comment = "Round-trip through the mixer tables"
    return chart


class MixerDataTests(unittest.TestCase):
    def test_chart_copy_move_and_legacy_export_round_trip(self):
        with tempfile.TemporaryDirectory(prefix="astronex-mixer-") as temp_dir:
            home = Path(temp_dir)
            shutil.copy2(ROOT / "astronex" / "resources" / "charts.db", home / "charts.db")
            app = SimpleNamespace(appath=str(ROOT), home_dir=str(home))
            database.connect(app)
            try:
                database.create_table("source")
                database.create_table("destination")
                original_id = database.store_chart("source", sample_chart())

                copied = Chart()
                database.load_chart("source", original_id, copied)
                copied_id = database.store_chart("destination", copied)
                self.assertEqual(database.get_chartlist("source"), [(original_id, "Ada", "Lovelace")])
                self.assertEqual(database.get_chartlist("destination"), [(copied_id, "Ada", "Lovelace")])
                self.assertEqual(copied.planets, [float(index) for index in range(11)])
                self.assertEqual(copied.houses, [float(index * 30) for index in range(12)])

                # Mixer exports .nxt files as pickle.  Protocol 2 represents
                # the old Python 2 format; latin1 loading keeps it readable.
                export_file = home / "destination.nxt"
                with export_file.open("wb") as output:
                    pickle.dump([copied], output, protocol=2)
                with export_file.open("rb") as source:
                    imported = pickle.load(source, encoding="latin1")
                self.assertEqual(imported[0].first, "Ada")
                self.assertEqual(imported[0].longitud, -0.1278)

                database.delete_chart("source", original_id)
                self.assertEqual(database.get_chartlist("source"), [])
                self.assertEqual(database.get_chartlist("destination"), [(copied_id, "Ada", "Lovelace")])
            finally:
                database.local_conn.close()
                database.chart_conn.close()
                database.local_conn = None
                database.chart_conn = None


if __name__ == "__main__":
    unittest.main()
