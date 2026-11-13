import unittest
from fractions import Fraction as F
from solve import bulk_price


def ref(p, q, c):
    r = F(p * q)
    d = 1 - (F(75, 1000) if q >= 50 else F(35, 1000) if q >= 10 else 0)
    r = r * d * (F(975, 1000) if c else 1) * F(107, 100)
    return int((r + F(1, 2)) // 1)


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_ref(self):
        for p in (0, 1, 99, 12345):
            for q in (1, 9, 10, 49, 50, 1000):
                for c in (False, True):
                    self.assertEqual(bulk_price(p, q, c), ref(p, q, c))


class Boundary(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10000 * 965 * 107 // 100000 + (1 if (10000 * 965 * 107 % 100000) >= 50000 else 0))
        self.assertLess(bulk_price(1000, 50, False), bulk_price(1000, 49, False))


class NoDrift(unittest.TestCase):
    def test_half(self):
        # 50*1*0.925*1.07 = 49.4875 -> 49 ; 10*... ตรวจ .5 พอดี: 1 ถุง 50 สตางค์ *1.07 = 53.5 -> 54
        self.assertEqual(bulk_price(50, 1, False), 54)
        self.assertEqual(bulk_price(0, 5, True), 0)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
                  ("1", 1, False), (True, 1, False), (1, 1.0, False), (1, True, False),
                  (1, 1, 1), (1, 1, None), (None, 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
