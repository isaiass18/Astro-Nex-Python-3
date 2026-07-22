"""Solar-return regression coverage, including the Aries boundary."""

import unittest

import pysw

from astronex.directions import _angular_difference, solar_return_julday


class SolarReturnTests(unittest.TestCase):
    def assert_return(self, target, year, month, day):
        jd = solar_return_julday(target, year, month, day)
        _, longitude, message = pysw.calc(jd, 0)
        self.assertFalse(message)
        self.assertLess(abs(_angular_difference(target, longitude)), 1e-6)

    def test_return_converges_near_aries_boundary(self):
        self.assert_return(359.9, 2027, 3, 20)

    def test_return_converges_for_opposite_half_of_zodiac(self):
        self.assert_return(180.0, 2027, 9, 22)


if __name__ == "__main__":
    unittest.main()
