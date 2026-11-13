import unittest
from fractions import Fraction
from solve import bulk_price


def ref(p, q, c):
    r = Fraction(p * q)
    r *= Fraction(925, 1000) if q >= 50 else Fraction(965, 1000) if q >= 10 else 1
    if c:
        r *= Fraction(39, 40)
    r *= Fraction(107, 100)
    return (r.numerator * 2 + r.denominator) // (2 * r.denominator)


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 10, False), 103255)  # 100000*.965*1.07
        self.assertEqual(bulk_price(10000, 50, True), ref(10000, 50, True))
        self.assertEqual(bulk_price(0, 5, True), 0)


class Boundary(unittest.TestCase):
    def test_tiers(self):
        for q in (1, 9, 10, 49, 50, 1000):
            for c in (False, True):
                self.assertEqual(bulk_price(12345, q, c), ref(12345, q, c))
        self.assertEqual(bulk_price(100, 9, False), 963)
        self.assertEqual(bulk_price(100, 10, False), ref(100, 10, False))


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 1 * 0.975 * 1.07 = 1.04325 -> 1 ; 10 ถุง 1 สต. = 9.65*1.07=10.3255 -> 10
        self.assertEqual(bulk_price(1, 10, False), 10)
        # 50 ถุง 1 สต. = 46.25 -> *1.07 = 49.4875 -> 49
        self.assertEqual(bulk_price(1, 50, False), 49)
        # ครึ่งพอดี: 100*1*1.07... หาค่า .5 ด้วย ref
        for p in range(0, 400):
            for q in (1, 10, 50):
                self.assertEqual(bulk_price(p, q, True), ref(p, q, True))


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 1, False), (100, 0, False), (100, 1001, False), (100, -1, False),
               (100.0, 1, False), (100, 1.0, False), ("100", 1, False), (100, "1", False),
               (True, 1, False), (100, True, False), (None, 1, False),
               (100, 1, 1), (100, 1, 0), (100, 1, "yes"), (100, 1, None)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
