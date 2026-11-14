import unittest
from fractions import Fraction
from solve import bulk_price


def ref(p, q, c):
    r = Fraction(1)
    if q >= 50:
        r *= Fraction(185, 200)
    elif q >= 10:
        r *= Fraction(193, 200)
    if c:
        r *= Fraction(39, 40)
    x = p * q * r * Fraction(107, 100)
    return int((x * 2 + 1) // 2)


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10432.5 ปัดครึ่งขึ้น
        self.assertEqual(bulk_price(10000, 10, False), ref(10000, 10, False))
        self.assertEqual(bulk_price(0, 5, True), 0)


class Boundary(unittest.TestCase):
    def test_edges(self):
        for q in (1, 9, 10, 11, 49, 50, 51, 1000):
            for c in (False, True):
                self.assertEqual(bulk_price(12345, q, c), ref(12345, q, c))
        self.assertLess(bulk_price(10000, 10, False), bulk_price(10000, 9, False) * 10 // 9)


class NoDrift(unittest.TestCase):
    def test_many(self):
        for p in range(0, 400, 7):
            for q in (1, 10, 50, 77):
                for c in (False, True):
                    self.assertEqual(bulk_price(p, q, c), ref(p, q, c))


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
               ("1", 1, False), (True, 1, False), (1, 1.0, False), (1, True, False),
               (1, 1, 1), (1, 1, None), (None, 1, False), (1, 1, "yes")]
        for a in bad:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
