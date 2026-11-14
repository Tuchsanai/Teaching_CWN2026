import unittest
from fractions import Fraction
from solve import bulk_price


def ref(p, q, c):
    # สูตรอ้างอิงแยกต่างหาก: ราคา*จำนวน*(ลดปริมาณ)*(คูปอง)*1.07 ปัดครึ่งขึ้น
    r = Fraction(p * q)
    r *= Fraction(925, 1000) if q >= 50 else Fraction(965, 1000) if q >= 10 else 1
    r *= Fraction(975, 1000) if c else 1
    r *= Fraction(107, 100)
    return int((r * 2 + 1) // 2)


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)  # 10000*1.07
        self.assertEqual(bulk_price(10000, 9, False), 96300)  # 90000*1.07

    def test_tier10(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)  # 100000*.965*1.07

    def test_tier50(self):
        self.assertEqual(bulk_price(10000, 50, False), 494875)  # 500000*.925*1.07

    def test_coupon_alone(self):
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10000*.975*1.07=10432.5

    def test_coupon_with_tiers(self):
        self.assertEqual(bulk_price(10000, 10, True), 100674)  # 103255*.975=100673.6
        self.assertEqual(bulk_price(10000, 50, True), 482503)  # 494875*.975=482503.1

    def test_matches_ref(self):
        for p in (0, 1, 99, 12345):
            for q in (1, 9, 10, 49, 50, 1000):
                for c in (False, True):
                    self.assertEqual(bulk_price(p, q, c), ref(p, q, c))


class Boundary(unittest.TestCase):
    def test_edges(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 49, False), 505950)  # 490000*.965*1.07=505949.5 -> half-up
        self.assertEqual(bulk_price(10000, 50, False), 494875)
        self.assertEqual(bulk_price(10000, 51, False), ref(10000, 51, False))

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_qty_limits(self):
        self.assertEqual(bulk_price(100, 1000, False), 98975)  # 100000*.925*1.07


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # .5 -> up
        self.assertEqual(bulk_price(50, 1, False), 54)  # 53.5 -> 54 (half-even would be 54; floor 53)
        self.assertEqual(bulk_price(10, 1, False), 11)  # 10.7
        self.assertEqual(bulk_price(1, 1, False), 1)  # 1.07

    def test_single_rounding(self):
        # ปัดทีละขั้นจะเพี้ยน
        self.assertEqual(bulk_price(333, 10, True), ref(333, 10, True))
        self.assertEqual(bulk_price(777, 50, True), ref(777, 50, True))


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            bulk_price(*a)

    def test_unit_price(self):
        for v in (1.5, 100.0, "100", True, None, -1):
            self.bad(v, 1, False)

    def test_qty(self):
        for v in (1.5, 5.0, "2", True, None, 0, -1, 1001):
            self.bad(100, v, False)

    def test_coupon(self):
        for v in (0, 1, "yes", None, 1.0):
            self.bad(100, 1, v)

    def test_invalid_with_other_branches(self):
        self.bad(-1, 50, True)
        self.bad(100, 2000, True)


if __name__ == "__main__":
    unittest.main()
