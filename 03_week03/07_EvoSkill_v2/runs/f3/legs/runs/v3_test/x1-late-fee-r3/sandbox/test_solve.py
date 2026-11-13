import unittest
from solve import late_fee


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(10000, 10), 750)
        self.assertEqual(late_fee(10000, 0), 0)


class Boundary(unittest.TestCase):
    def test_edges(self):
        self.assertEqual(late_fee(10000, 3), 0)
        self.assertEqual(late_fee(10000, 4), 300)
        self.assertEqual(late_fee(10000, 20), 1500)
        self.assertEqual(late_fee(10000, 365), 1500)
        self.assertEqual(late_fee(0, 10), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(late_fee(10, 10), 1)   # 0.75 -> 1
        self.assertEqual(late_fee(2, 4), 0)     # 0.06
        self.assertEqual(late_fee(100, 5), 4)   # 3.75 -> 4
        self.assertEqual(late_fee(20, 10), 2)   # 1.5 -> 2


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100.0, 5), ("1", 5), (True, 5), (None, 5),
                     (100, -1), (100, 366), (100, 5.0), (100, "5"), (100, True)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
