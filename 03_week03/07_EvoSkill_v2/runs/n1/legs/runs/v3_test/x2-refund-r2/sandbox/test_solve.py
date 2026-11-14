import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_no_restock(self):
        self.assertEqual(refund(10000, 25, False), 7500)   # 10000*75%
        self.assertEqual(refund(10000, 0, False), 10000)   # ยังไม่ได้เรียน
    def test_restock(self):
        self.assertEqual(refund(10000, 25, True), 6562)    # 7500*0.875=6562.5 → floor
        self.assertEqual(refund(8000, 50, True), 3500)     # 4000*0.875
    def test_over_80(self):
        self.assertEqual(refund(10000, 90, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)
    def test_zero_paid(self):
        self.assertEqual(refund(0, 10, True), 0)


class Boundary(unittest.TestCase):
    def test_80_still_refunds(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 80, True), 1750)
    def test_81_zero(self):
        self.assertEqual(refund(10000, 81, False), 0)
    def test_79(self):
        self.assertEqual(refund(10000, 79, False), 2100)
    def test_range_ends(self):
        self.assertEqual(refund(100, 0, False), 100)
        self.assertEqual(refund(100, 100, False), 0)


class NoDrift(unittest.TestCase):
    def test_floor_not_half_up(self):
        self.assertEqual(refund(10000, 25, True), 6562)    # .5 → ลง
        self.assertEqual(refund(1, 0, True), 0)            # 0.875 → 0
        self.assertEqual(refund(999, 33, False), 669)      # 669.33 → 669 (floor)
        self.assertEqual(refund(199, 1, False), 197)       # 197.01
        self.assertEqual(refund(3, 10, False), 2)          # 2.7 → 2 (half-up จะได้ 3)
    def test_single_rounding(self):
        # 101*0.7=70.7 → *0.875=61.8625 → 61 ; ปัดทีละขั้นจะได้ 71*.875=62.1→62
        self.assertEqual(refund(101, 30, True), 61)


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            refund(*a)
    def test_paid(self):
        for v in (4500.0, 10.5, "100", True, None, -1):
            self.bad(v, 10, False)
    def test_used(self):
        for v in (10.0, 10.5, "10", True, False if False else None, -1, 101):
            self.bad(1000, v, False)
        self.bad(1000, 90.0, False)
    def test_restock(self):
        for v in (0, 1, "yes", None, 1.0):
            self.bad(1000, 10, v)
    def test_invalid_even_when_zero_branch(self):
        self.bad(1000, 101, False)
        self.bad(1000.0, 90, False)
        self.bad(1000, 90, 1)


if __name__ == "__main__":
    unittest.main()
