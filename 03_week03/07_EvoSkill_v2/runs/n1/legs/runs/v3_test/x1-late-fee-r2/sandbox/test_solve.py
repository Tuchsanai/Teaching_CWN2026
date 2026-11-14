import unittest
from solve import late_fee


class Normal(unittest.TestCase):
    def test_10_days(self):
        # 100000 * 10 * 0.75% = 7500
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_4_days(self):
        # 100000 * 4 * 0.75% = 3000 (นับรวม 3 วันแรก)
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap(self):
        # 30 วัน = 22.5% -> เพดาน 15% = 15000
        self.assertEqual(late_fee(100000, 30), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_grace(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)


class Boundary(unittest.TestCase):
    def test_grace_edge(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap_edge(self):
        # 20 วัน = 15% พอดี; 19 วัน = 14.25%; 21 วัน ชนเพดาน
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)
        self.assertEqual(late_fee(0, 0), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 200 * 4 * 0.0075 = 6.0 ; 50 * 4 * 0.0075 = 1.5 -> 2 (floor=1, even=2)
        self.assertEqual(late_fee(50, 4), 2)
        # 70*5*0.0075 = 2.625 -> 3
        self.assertEqual(late_fee(70, 5), 3)
        # 10*5*0.0075 = 0.375 -> 0
        self.assertEqual(late_fee(10, 5), 0)
        # 130*4*0.0075 = 3.9 -> 4
        self.assertEqual(late_fee(130, 4), 4)
        # 10 * 0.15 = 1.5 -> 2 (cap, half-up)
        self.assertEqual(late_fee(10, 30), 2)
        # 30 * 0.15 = 4.5 -> 5
        self.assertEqual(late_fee(30, 20), 5)
        # 70*0.15 = 10.5 -> 11
        self.assertEqual(late_fee(70, 99), 11)


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            late_fee(*a)

    def test_amount(self):
        for v in (1000.0, 1000.5, "1000", True, None, -1):
            self.bad(v, 10)
            self.bad(v, 0)  # ต้อง raise แม้เข้า early-return

    def test_days(self):
        for v in (5.0, 4.5, "5", True, False, None, -1, 366):
            self.bad(1000, v)

    def test_both_bad_in_grace(self):
        self.bad(-1, 2)
        self.bad(1000, 2.0)


if __name__ == "__main__":
    unittest.main()
