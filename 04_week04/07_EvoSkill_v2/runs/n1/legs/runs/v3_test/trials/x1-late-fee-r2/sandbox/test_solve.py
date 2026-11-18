"""python3 -m unittest -q test_solve"""
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_a(self):
        self.assertEqual(late_fee(10000, 4), 300)

    def test_b(self):
        self.assertEqual(late_fee(12345, 5), 463)  # 462.9375

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_3_days(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 0), 0)

    def test_4_days(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap_line(self):
        self.assertEqual(late_fee(1000, 20), 150)
        self.assertEqual(late_fee(1000, 19), 143)  # 142.5 half-up
    def test_cap(self):
        self.assertEqual(late_fee(1000, 365), 150)
        self.assertEqual(late_fee(1000, 21), 150)


class NoDrift(unittest.TestCase):
    def test_half(self):
        self.assertEqual(late_fee(50, 4), 2)   # 1.5
        self.assertEqual(late_fee(10, 10), 1)  # 0.75
        self.assertEqual(late_fee(20, 5), 1)   # 0.75 -> 1
        self.assertEqual(late_fee(6, 4), 0)    # 0.18


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     ('100', 5), (100, '5'), (True, 5), (100, True), (None, 5), (100, None)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)
        with self.assertRaises(ValueError):
            late_fee(100, 0.0)


if __name__ == "__main__":
    unittest.main()
