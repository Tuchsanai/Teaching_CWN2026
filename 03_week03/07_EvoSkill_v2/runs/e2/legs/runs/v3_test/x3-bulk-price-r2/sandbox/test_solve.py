import unittest
from fractions import Fraction as F
from solve import bulk_price


def ref(p, q, c):
    v = F(p * q)
    if q >= 50:
        v = v * 925 / 1000
    elif q >= 10:
        v = v * 965 / 1000
    if c:
        v = v * 975 / 1000
    v = v * 107 / 100
    return v


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(25075, 1, False), 26830)  # 26830.25
        self.assertEqual(bulk_price(5333, 9, True), 50073)  # 50072.87
    def test_tier10(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5
        self.assertEqual(bulk_price(1000, 10, True), 10067)  # 10067.3625
    def test_tier50(self):
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 49487.5 -> 49488
        self.assertEqual(bulk_price(1000, 50, True), 48250)  # 48250.3125


class Boundary(unittest.TestCase):
    def test_edges(self):
        for q in (1, 9, 10, 11, 49, 50, 51, 1000):
            for c in (False, True):
                self.assertEqual(bulk_price(5001, q, c), int((ref(5001, q, c) * 2 + 1) // 2))
    def test_tier_is_not_stacked(self):
        self.assertNotEqual(bulk_price(10000, 50, False), bulk_price(10000, 10, False))
        self.assertEqual(bulk_price(10000, 50, False), int((F(10000*50*925*107, 1000*100) * 2 + 1) // 2))
    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)


class NoDrift(unittest.TestCase):
    def test_half(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)
        self.assertEqual(bulk_price(1000, 50, False), 49488)
    def test_hand_values(self):
        # 5333*9*1.07*0.975 = 50075... computed by Fraction
        self.assertEqual(bulk_price(5333, 9, True), int((F(5333 * 9 * 975 * 107, 1000 * 100) * 2 + 1) // 2))
    def test_large(self):
        self.assertEqual(bulk_price(10**7, 1000, True), 10**7 * 1000 * 925 * 975 * 107 // (1000 * 1000 * 100))


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            bulk_price(*a)
    def test_price(self):
        for v in (-1, 10.0, "100", True, None):
            self.bad(v, 5, False)
    def test_qty(self):
        for v in (0, -1, 1001, 5.0, "5", True, None):
            self.bad(100, v, False)
    def test_coupon(self):
        for v in (0, 1, "True", None, 1.0):
            self.bad(100, 5, v)


if __name__ == "__main__":
    unittest.main()
