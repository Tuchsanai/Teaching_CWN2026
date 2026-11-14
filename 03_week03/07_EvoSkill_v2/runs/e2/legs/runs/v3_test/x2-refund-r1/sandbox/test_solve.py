import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(0, 10, True), 0)
        self.assertEqual(refund(10000, 100, False), 0)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(refund(10000, 79, False), 2100)
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 81, True), 0)
        self.assertEqual(refund(10000, 80, True), 1750)
        self.assertEqual(refund(10000, 0, True), 8750)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        # 5001*67/100 = 3350.67 -> 3350
        self.assertEqual(refund(5001, 33, False), 3350)
        # 5001*67/100*7/8 = 2931.8363 -> 2931
        self.assertEqual(refund(5001, 33, True), 2931)
        # 1*50/100 = 0.5 -> 0 ; 0.4375 -> 0
        self.assertEqual(refund(1, 50, False), 0)
        self.assertEqual(refund(1, 50, True), 0)
        # 25075*80/100 = 20060 ; *7/8 = 17552.5 -> 17552 (ไม่ปัดขึ้น)
        self.assertEqual(refund(25075, 20, True), 17552)
        # 10*75/100=7.5 -> 7 ; 6.5625 -> 6
        self.assertEqual(refund(10, 25, False), 7)
        self.assertEqual(refund(10, 25, True), 6)
        self.assertEqual(refund(10**18 + 1, 1, False), (10**18 + 1) * 99 // 100)


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            refund(*a)

    def test_paid(self):
        for v in (-1, 1000.0, "1000", True, None):
            self.bad(v, 10, False)

    def test_used(self):
        for v in (-1, 101, 10.0, "10", True, False, None):
            self.bad(1000, v, False)

    def test_restock(self):
        for v in (0, 1, "True", None, 1.0):
            self.bad(1000, 10, v)

    def test_order(self):
        self.bad(1000, 101, False)  # เกิน 100 ต้อง error ไม่ใช่ 0
        self.bad(-1, 90, False)


if __name__ == "__main__":
    unittest.main()
