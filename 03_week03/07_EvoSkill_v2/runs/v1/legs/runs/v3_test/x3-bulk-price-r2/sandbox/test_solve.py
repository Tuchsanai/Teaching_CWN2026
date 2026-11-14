import unittest
from fractions import Fraction
from solve import bulk_price


def ref(p, q, c):
    x = Fraction(p * q)
    if q >= 50: x *= Fraction(925, 1000)
    elif q >= 10: x *= Fraction(965, 1000)
    if c: x *= Fraction(975, 1000)
    x *= Fraction(107, 100)
    return int((x * 2 + 1) // 2)


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 50, True), ref(10000, 50, True))
        self.assertEqual(bulk_price(0, 5, True), 0)


class Boundary(unittest.TestCase):
    def test_tiers(self):
        for q in (1, 9, 10, 49, 50, 1000):
            for c in (False, True):
                self.assertEqual(bulk_price(1234, q, c), ref(1234, q, c))
        self.assertLess(bulk_price(10000, 10, False) / 10, bulk_price(10000, 9, False) / 9)


class NoDrift(unittest.TestCase):
    def test_many(self):
        for p in range(0, 300, 7):
            for q in (1, 3, 10, 11, 50, 77):
                for c in (False, True):
                    self.assertEqual(bulk_price(p, q, c), ref(p, q, c))


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
                  ("1", 1, False), (True, 1, False), (1, 1.0, False), (1, True, False),
                  (1, 1, 1), (1, 1, None), (None, 1, False), (1, 1, "yes")]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
