import unittest
from solve import late_fee


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_boundary_exact(self):
        self.assertEqual(late_fee(100000, 3), 0)

    def test_boundary_below(self):
        self.assertEqual(late_fee(100000, 2), 0)

    def test_boundary_above(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_half_up(self):
        # 200*0.0075*4 = 6 ; 50*0.0075*4=1.5 -> 2 ; 10*0.0075*4=0.3 -> 0
        self.assertEqual(late_fee(50, 4), 2)
        self.assertEqual(late_fee(10, 4), 0)

    def test_reject_value(self):
        for a, d in [(-1, 5), (100, -1), (100, 366)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_reject_type(self):
        for a, d in [(1000.0, 5), (100, 5.0), (True, 5), ("1", 5), (None, 5), (100, False)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_zero_or_cap(self):
        self.assertEqual(late_fee(0, 100), 0)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_cap_boundary(self):
        self.assertEqual(late_fee(100000, 19), 14250)


if __name__ == "__main__":
    unittest.main()
