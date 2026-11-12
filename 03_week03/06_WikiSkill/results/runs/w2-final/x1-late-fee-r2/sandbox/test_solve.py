import unittest
from solve import late_fee


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(10000, 10), 750)

    def test_boundary_exact(self):
        self.assertEqual(late_fee(10000, 3), 0)

    def test_boundary_below(self):
        self.assertEqual(late_fee(10000, 2), 0)

    def test_boundary_above(self):
        self.assertEqual(late_fee(10000, 4), 300)

    def test_half_up(self):
        # 200*0.0075*5 = 7.5 -> 8
        self.assertEqual(late_fee(200, 5), 8)

    def test_reject_value(self):
        for a, d in [(-1, 5), (100, -1), (100, 366)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_reject_type(self):
        for a, d in [(1000.0, 5), (True, 5), ("1", 5), (None, 5), (100, 5.0), (100, False), (100, None)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_zero_or_cap(self):
        self.assertEqual(late_fee(0, 100), 0)
        self.assertEqual(late_fee(10000, 20), 1500)
        self.assertEqual(late_fee(10000, 365), 1500)


if __name__ == "__main__":
    unittest.main()
