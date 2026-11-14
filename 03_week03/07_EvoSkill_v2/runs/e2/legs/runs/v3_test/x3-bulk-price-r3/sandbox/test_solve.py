import unittest
from fractions import Fraction as F
from solve import bulk_price


def ref(p, q, c):
    v = F(p * q)
    if q >= 50:
        v = v * F(92500, 100000)
    elif q >= 10:
        v = v * F(96500, 100000)
    if c:
        v = v * F(97500, 100000)
    v = v * F(107, 100)
    return int((v * 2 + 1) // 2)


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)
        self.assertEqual(bulk_price(1000, 1, True), 1043)  # 1000*.975*1.07=1043.25
        self.assertEqual(bulk_price(1000, 20, False), 20000 * 965 * 107 // 100000 + 0 if False else ref(1000, 20, False))
        self.assertEqual(bulk_price(5333, 60, True), ref(5333, 60, True))
        self.assertEqual(bulk_price(0, 5, True), 0)


class Boundary(unittest.TestCase):
    def test_tiers(self):
        for q in (1, 9, 10, 11, 49, 50, 51, 1000):
            for c in (True, False):
                self.assertEqual(bulk_price(5001, q, c), ref(5001, q, c))
        self.assertLess(bulk_price(5001, 10, False), bulk_price(5001, 9, False) * 10 // 9)
        self.assertEqual(bulk_price(100000, 50, False), 4949 * 1000 * 1 // 1 * 0 + 4949750 if False else ref(100000, 50, False))
        self.assertEqual(bulk_price(100000, 10, False), 1032550)
        self.assertEqual(bulk_price(100000, 9, False), 963000)


class NoDrift(unittest.TestCase):
    def test_half(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5
        self.assertEqual(bulk_price(1000, 1, False), 1070)
        self.assertEqual(bulk_price(100, 10, False), 1033)  # 1032.55
        self.assertEqual(bulk_price(1, 1, False), 1)  # 1.07
        self.assertEqual(bulk_price(25075, 37, True), ref(25075, 37, True))

    def test_many(self):
        for p in (1, 7, 333, 5001, 25075):
            for q in (3, 10, 50, 77, 999):
                for c in (True, False):
                    self.assertEqual(bulk_price(p, q, c), ref(p, q, c))


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [
            (-1, 1, False), (1.0, 1, False), ("1", 1, False), (True, 1, False), (None, 1, False),
            (100, 0, False), (100, 1001, False), (100, -1, False), (100, 1.0, False),
            (100, "1", False), (100, True, False), (100, None, False),
            (100, 1, 1), (100, 1, 0), (100, 1, "True"), (100, 1, None),
        ]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
