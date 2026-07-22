"""Regression tests for the native Swiss Ephemeris bridge."""

import unittest
from types import SimpleNamespace

import pysw
from astronex.chart import Chart


class SwissEphemerisTests(unittest.TestCase):
    def test_j2000_sun_and_houses(self):
        jd = pysw.julday(2000, 1, 1, 12.0)
        self.assertEqual(jd, 2451545.0)

        status, longitude, message = pysw.calc(jd, 0)
        self.assertGreaterEqual(status, 0, message)
        self.assertGreater(longitude, 279)
        self.assertLess(longitude, 282)
        self.assertEqual(len(pysw.houses(jd, 40.4168, -3.7038)), 12)

    def test_repeated_current_calculation_is_stable(self):
        jd = pysw.julday(2026, 7, 22, 5.671111111111111)
        for _ in range(1_000):
            status, longitude, message = pysw.calc(jd, 0, 4)
            self.assertGreaterEqual(status, 0, message)
            self.assertGreaterEqual(longitude, 0)
            self.assertLess(longitude, 360)

    def test_houses_for_real_historical_locations(self):
        chart = Chart()
        cases = [
            ((1912, 4, 15, 23.67), 51.5074, -0.1278),
            ((1976, 3, 24, 8.10), -34.6037, -58.3816),
            ((1944, 6, 17, 12.00), 64.1466, -21.9426),
        ]
        for date, latitude, longitude in cases:
            location = SimpleNamespace(latdec=latitude, longdec=longitude)
            planets, houses = chart.calc(date, location, 4)
            self.assertEqual(len(planets), 11)
            self.assertEqual(len(houses), 12)
            self.assertTrue(all(0 <= cusp < 360 for cusp in houses))


if __name__ == "__main__":
    unittest.main()
