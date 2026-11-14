import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_no_restock(self):
        self.assertEqual(refund(10000, 50, False), 5000)   # 10000*50%
    def test_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)    # 5000*0.875
    def test_unused(self):
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(10000, 0, True), 8750)
    def test_zero_paid(self):
        self.assertEqual(refund(0, 10, True), 0)


class Boundary(unittest.TestCase):
    def test_80_refunds(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 80, True), 1750)    # 2000*0.875
    def test_81_zero(self):
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 81, True), 0)
    def test_100_zero(self):
        self.assertEqual(refund(10000, 100, False), 0)


class NoDrift(unittest.TestCase):
    def test_floor_no_restock(self):
        self.assertEqual(refund(1, 50, False), 0)          # 0.5 -> 0
        self.assertEqual(refund(999, 33, False), 669)      # 669.33
    def test_floor_restock(self):
        self.assertEqual(refund(10, 0, True), 8)           # 8.75 -> 8 (ไม่ใช่ 9)
        self.assertEqual(refund(1001, 7, True), 814)       # 930.93*0.875=814.56 -> 814


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [4500.0, 5.0, "2", True, None, -1]
        for b in bad:
            with self.assertRaises(ValueError):
                refund(b, 10, False)
        for b in [10.0, 10.5, "2", True, None, -1, 101]:
            with self.assertRaises(ValueError):
                refund(100, b, False)
        for b in [0, 1, "yes", None, 1.0]:
            with self.assertRaises(ValueError):
                refund(100, 10, b)
    def test_invalid_with_zero_branch(self):
        with self.assertRaises(ValueError):
            refund(-5, 90, False)
        with self.assertRaises(ValueError):
            refund(100, 90, 1)


if __name__ == "__main__":
    unittest.main()
