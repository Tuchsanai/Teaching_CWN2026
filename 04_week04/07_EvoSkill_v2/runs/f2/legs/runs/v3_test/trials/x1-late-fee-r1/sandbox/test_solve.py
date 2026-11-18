import unittest
from solve import late_fee


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(100000, 4), 3000)


class Boundary(unittest.TestCase):
    def test_grace(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(0, 10), 0)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(100000, 19), 14250)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(late_fee(200, 4), 6)    # 6.0
        self.assertEqual(late_fee(10, 10), 1)    # 0.75 -> 1
        self.assertEqual(late_fee(2, 20), 0)     # 0.3 -> 0
        self.assertEqual(late_fee(1, 4), 0)      # 0.03
        self.assertEqual(late_fee(100, 5), 4)    # 3.75 -> 4
        self.assertEqual(late_fee(2000, 5) , 75)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     ("100", 5), (True, 5), (100, True), (None, 5), (100, None)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)
        with self.assertRaises(ValueError):
            late_fee(100, 1000)


if __name__ == "__main__":
    unittest.main()
