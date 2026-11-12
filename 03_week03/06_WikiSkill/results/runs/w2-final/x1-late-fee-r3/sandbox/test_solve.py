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
        # 200*3*4/400 = 6 ; 10*3*4/400=0.3 ; 50*3*5/400=1.875 ; 200*3*5/400=7.5 -> 8
        self.assertEqual(late_fee(200, 5), 8)
        self.assertEqual(late_fee(10, 4), 0)
        self.assertEqual(late_fee(50, 5), 2)

    def test_reject_value(self):
        for a, d in [(-1, 5), (100, -1), (100, 366)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_reject_type(self):
        for a, d in [(1000.0, 5), (100, 5.0), (True, 5), ("100", 5), (None, 5), (100, False)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_zero_or_cap(self):
        self.assertEqual(late_fee(0, 100), 0)
        self.assertEqual(late_fee(10000, 20), 1500)
        self.assertEqual(late_fee(10000, 365), 1500)
        self.assertEqual(late_fee(10, 365), 2)  # cap 1.5 -> 2


if __name__ == "__main__":
    unittest.main()
