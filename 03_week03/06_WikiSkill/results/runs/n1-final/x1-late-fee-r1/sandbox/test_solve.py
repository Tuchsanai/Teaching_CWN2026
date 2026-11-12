import unittest
from solve import late_fee


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_boundary_below(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 0), 0)

    def test_boundary_at(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_half_up(self):
        # 100*0.0075*4 = 3.0 ; 150*0.0075*4=4.5 -> 5
        self.assertEqual(late_fee(150, 4), 5)
        # 10*0.0075*10 = 0.75 -> 1 ; 2*0.0075*4=0.06 -> 0
        self.assertEqual(late_fee(10, 10), 1)

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
        for a, d in [(True, 5), (100, True), ("100", 5), (100, None)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
