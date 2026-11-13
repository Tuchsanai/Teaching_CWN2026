import unittest
from solve import late_fee


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(100000, 10), 7500)   # 0.75%*10 = 7.5%
    def test_no_fee(self):
        self.assertEqual(late_fee(100000, 2), 0)
    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_day3(self):
        self.assertEqual(late_fee(100000, 3), 0)
    def test_day4(self):
        self.assertEqual(late_fee(100000, 4), 3000)    # counts all 4 days
    def test_cap_exact(self):
        self.assertEqual(late_fee(100000, 20), 15000)  # 15% exactly
    def test_cap(self):
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
    def test_zero_days(self):
        self.assertEqual(late_fee(100000, 0), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 2*0.0075*4 = 0.06 -> 0 ; 50*0.03=1.5 -> 2
        self.assertEqual(late_fee(50, 4), 2)
        self.assertEqual(late_fee(2, 4), 0)
    def test_half_up_2(self):
        # 10*0.0075*10 = 0.75 -> 1; 130*0.03=3.9 -> 4; 150*0.0075*5=5.625 -> 6
        self.assertEqual(late_fee(10, 10), 1)
        self.assertEqual(late_fee(150, 5), 6)
    def test_big(self):
        self.assertEqual(late_fee(10**15 + 1, 4), round(((10**15 + 1) * 3 + 50) // 100))


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), ("100", 5),
                     (True, 5), (100, 5.0), (100, "5"), (100, True), (None, 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
