"""Regression tests for historical chart date serialization."""

from datetime import datetime, timedelta, tzinfo
from types import SimpleNamespace
import unittest

from astronex.directions import strdate_to_date as direction_date
from astronex.nexdate import NeXDate
from astronex.utils import strdate_to_date as utility_date


class FixedZone(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=5, minutes=30)

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "IST"


class LegacyChartDateTests(unittest.TestCase):
    def test_pre_1900_date_is_written_with_integer_offset(self):
        current = SimpleNamespace(loc=SimpleNamespace(longdec=0.0))
        value = NeXDate(current)
        value.ld = datetime(1890, 1, 2, 3, 4, 5, tzinfo=FixedZone())

        self.assertEqual(value.dateforstore(), "1890-01-02T03:04:05+05:30IST")

    def test_progressions_accept_existing_decimal_offset_dates(self):
        stored = "1890-01-02T03:04:05+5.5:30.0IST"
        expected = datetime(1890, 1, 2, 3, 4)

        self.assertEqual(direction_date(stored).replace(tzinfo=None), expected)
        self.assertEqual(utility_date(stored), expected)


if __name__ == "__main__":
    unittest.main()
