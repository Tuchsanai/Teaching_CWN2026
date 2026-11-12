import unittest
from solve import late_fee


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(10000, 10), 750)

    def test_boundary_below(self):
        self.assertEqual(late_fee(10000, 3), 0)
        self.assertEqual(late_fee(10000, 0), 0)

    def test_boundary_at(self):
        self.assertEqual(late_fee(10000, 4), 300)
        self.assertEqual(late_fee(10000, 5), 375)

    def test_half_up(self):
        # 200 * 6 * 0.75% = 9.0 ; 10*4*0.75% =0.3 ; 50*4*.75%=1.5 -> 2
        self.assertEqual(late_fee(50, 4), 2)
        self.assertEqual(late_fee(10, 4), 0)

    def test_cap(self):
        self.assertEqual(late_fee(10000, 20), 1500)
        self.assertEqual(late_fee(10000, 365), 1500)

    def test_reject_range(self):
        for a, d in [(-1, 5), (100, -1), (100, 366)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            late_fee(100.0, 5)
        with self.assertRaises(ValueError):
            late_fee(100, 5.0)

    def test_reject_bool_or_type(self):
        for a, d in [(True, 5), (100, False), ("1", 5), (100, None)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
