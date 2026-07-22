"""Regression tests for fixed-offset time zones such as UTC."""

from datetime import datetime
from types import SimpleNamespace
import unittest

from astronex.nexdate import NeXDate


class NexDateUtcTests(unittest.TestCase):
    def test_utc_can_be_selected_and_assigned_a_datetime(self):
        current = SimpleNamespace(loc=SimpleNamespace(longdec=0.0))
        value = NeXDate(current)
        value.settz("UTC")
        value.setdt(datetime(2024, 6, 21, 12, 0, 0))
        self.assertEqual(value.dt.year, 2024)
        self.assertEqual(value.dt.hour, 12)


if __name__ == "__main__":
    unittest.main()
