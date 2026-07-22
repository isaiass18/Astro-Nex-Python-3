import unittest
from unittest.mock import patch

from astronex.chart import Chart
from astronex.export_aaf import export_chart


class AafExportTest(unittest.TestCase):
    def test_export_chart_preserves_non_ascii_text(self):
        chart = Chart()
        chart.first = "Élodie"
        chart.last = "Muñoz"
        chart.city = "Bogotá"
        chart.country = "España"
        chart.date = "1985-11-03T14:25:00+00:00"

        with patch("astronex.export_aaf.datab.get_code_from_name", return_value="SP"):
            exported = export_chart(chart)

        self.assertIsInstance(exported, str)
        self.assertIn("Muñoz", exported)
        self.assertIn("Élodie", exported)
        self.assertIn("Bogotá", exported)
