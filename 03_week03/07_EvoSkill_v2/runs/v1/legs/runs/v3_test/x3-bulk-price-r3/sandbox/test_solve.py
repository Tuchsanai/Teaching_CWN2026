import unittest
from fractions import Fraction
from solve import bulk_price


def ref(p, q, c):
    t = Fraction(p * q)
    t *= Fraction(925, 1000) if q >= 50 else Fraction(965, 1000) if q >= 10 else 1
    if c:
        t *= Fraction(975, 1000)
    t *= Fraction(107, 100)
    return int((t * 2 + 1) // 2)


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 50, True), ref(10000, 50, True))
        self.assertEqual(bulk_price(0, 5, True), 0)


class Boundary(unittest.TestCase):
    def test_edges(self):
        for q in (1, 9, 10, 11, 49, 50, 51, 1000):
            for c in (False, True):
                self.assertEqual(bulk_price(1234, q, c), ref(1234, q, c))
        self.assertEqual(bulk_price(10000, 49, False), ref(10000, 49, False))
        self.assertLess(bulk_price(10000, 50, False), bulk_price(10000, 49, False))


class NoDrift(unittest.TestCase):
    def test_many(self):
        for p in range(0, 400, 7):
            for q in (1, 10, 50, 333):
                for c in (False, True):
                    self.assertEqual(bulk_price(p, q, c), ref(p, q, c))


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
               ("1", 1, False), (True, 1, False), (1, True, False), (1, 1.0, False),
               (1, 1, 1), (1, 1, 0), (1, 1, None), (None, 1, False), (1, "3", True)]
        for a in bad:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
