import unittest
from solve import late_fee


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(100000, 0), 0)


class Boundary(unittest.TestCase):
    def test_grace(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(0, 10), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 10 * 0.0075 * 4 = 0.3 -> 0 ; 50*0.0075*4=1.5 -> 2
        self.assertEqual(late_fee(50, 4), 2)
        self.assertEqual(late_fee(10, 4), 0)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100.0, 5), ("1", 5), (True, 5), (None, 5),
                     (100, -1), (100, 366), (100, 5.0), (100, True), (100, "5")]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
