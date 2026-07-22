"""Coordinate conversion and display regressions."""

import unittest

from astronex.utils import dectodeg, degtodec, format_latitud, format_longitud


class CoordinateTests(unittest.TestCase):
    def test_decimal_coordinates_round_trip(self):
        for coordinate in (-3.7038, -0.5, 0.0, 40.4168):
            self.assertAlmostEqual(degtodec(dectodeg(coordinate)), coordinate, places=3)

    def test_display_uses_correct_cardinal_direction(self):
        self.assertEqual(format_longitud(-3.7038), "3W42")
        self.assertEqual(format_longitud(3.7038), "3E42")
        self.assertEqual(format_latitud(-40.4168), "40S25")
        self.assertEqual(format_latitud(40.4168), "40N25")


if __name__ == "__main__":
    unittest.main()
