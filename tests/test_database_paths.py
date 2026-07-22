"""Regression test for cross-platform SQLite database setup."""

import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from astronex import database


ROOT = Path(__file__).resolve().parents[1]


class DatabasePathTests(unittest.TestCase):
    def test_custom_database_attaches_when_home_path_contains_apostrophe(self):
        with tempfile.TemporaryDirectory(prefix="astro'nex-") as temp_dir:
            home = Path(temp_dir)
            shutil.copy2(ROOT / "astronex" / "resources" / "charts.db", home / "charts.db")
            app = SimpleNamespace(appath=str(ROOT), home_dir=str(home))

            database.connect(app)
            attached = database.local_conn.execute("PRAGMA database_list").fetchall()
            self.assertIn("custom", [row[1] for row in attached])

            database.save_attached_loc(("SP", "53", "Madrid", "40N25", "3W42", False))
            saved = database.local_conn.execute(
                "SELECT CC, AC, Ciudad, Latitud, Longitud FROM custom.cust_sp"
            ).fetchone()
            self.assertEqual(saved, ("SP", "53", "Madrid", "40N25", "3W42"))

            database.local_conn.close()
            database.chart_conn.close()
            database.local_conn = None
            database.chart_conn = None


if __name__ == "__main__":
    unittest.main()
