"""python3 -m unittest -q test_solve"""
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_grace(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_after_grace(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(late_fee(200, 4), 6)      # 6.0
        self.assertEqual(late_fee(10, 10), 1)      # 0.75 -> 1
        self.assertEqual(late_fee(2, 10), 0)       # 0.15 -> 0
        self.assertEqual(late_fee(2002, 4), 60)    # 60.06
        self.assertEqual(late_fee(2000, 5), 75)
        self.assertEqual(late_fee(1000, 10), 75)   # 75.0
        self.assertEqual(late_fee(66, 10), 5)      # 4.95 -> 5
        self.assertEqual(late_fee(34, 20), 5)      # cap 5.1 -> 5
        self.assertEqual(late_fee(10, 20), 2)      # cap 1.5 -> 2 (half-up)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     ("100", 5), (100, "5"), (None, 5), (100, None),
                     (True, 5), (100, True)]:
            with self.subTest(a=a, d=d):
                with self.assertRaises(ValueError):
                    late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
