"""Regression tests for 72-year PE cycle boundaries."""

import unittest
from datetime import datetime, timedelta, timezone

from astronex.chart import Chart


class AgeCycleTests(unittest.TestCase):
    def make_chart(self, birth):
        chart = Chart()
        chart.date = birth
        return chart

    def assert_cycle_boundary(self, birth, before, anniversary):
        chart = self.make_chart(birth)
        self.assertEqual(chart.get_cycles(before), 0)
        self.assertEqual(chart.which_house_today(before)[0], 11)

        new_year = datetime(anniversary.year, 1, 1, 12, 0)
        self.assertEqual(chart.get_cycles(new_year), 0)
        self.assertEqual(chart.which_house_today(new_year)[0], 11)

        self.assertEqual(chart.get_cycles(anniversary), 1)
        self.assertEqual(chart.which_house_today(anniversary)[0], 0)

    def test_nuria_does_not_change_cycle_on_new_year_2026(self):
        self.assert_cycle_boundary(
            "1954-11-12T09:05:00+0100CET",
            datetime(2025, 12, 31, 12, 0),
            datetime(2026, 11, 12, 9, 5),
        )

    def test_joan_does_not_change_cycle_on_new_year_2029(self):
        self.assert_cycle_boundary(
            "1957-12-30T01:48:00+0100CET",
            datetime(2028, 12, 31, 12, 0),
            datetime(2029, 12, 30, 1, 48),
        )

    def test_aware_vnc_date_uses_the_same_cycle_boundary(self):
        chart = self.make_chart("1957-12-30T01:48:00+0100CET")
        cet = timezone(timedelta(hours=1))
        self.assertEqual(chart.get_cycles(datetime(2029, 1, 1, 12, 0, tzinfo=cet)), 0)
        self.assertEqual(chart.which_house_today(datetime(2029, 1, 1, 12, 0, tzinfo=cet))[0], 11)


if __name__ == "__main__":
    unittest.main()
