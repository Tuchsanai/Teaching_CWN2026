import unittest
from fractions import Fraction as F
from solve import bulk_price


def ref(p, q, c):
    x = F(p) * q
    x *= F(925, 1000) if q >= 50 else F(965, 1000) if q >= 10 else 1
    if c:
        x *= F(975, 1000)
    x *= F(107, 100)
    return int((x * 2 + 1) // 2)


class T(unittest.TestCase):
    def test_values(self):
        for p in (0, 1, 5, 4500, 12345):
            for q in (1, 9, 10, 49, 50, 1000):
                for c in (False, True):
                    self.assertEqual(bulk_price(p, q, c), ref(p, q, c))
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 10, False), 10326 + 0 if False else ref(10000, 10, False))

    def test_half(self):
        # 50 ถุง x 1 สตางค์ ... ตรวจว่าเป็น int
        self.assertIs(type(bulk_price(1, 1, False)), int)
        self.assertEqual(bulk_price(1, 1, False), 1)  # 1.07 -> 1
        self.assertEqual(bulk_price(50, 1, False), 54)  # 53.5 -> 54

    def test_reject(self):
        for a in [(-1, 1, False), (1.0, 1, False), ("1", 1, False), (None, 1, False),
                  (True, 1, False), (1, 0, False), (1, 1001, False), (1, 1.0, False),
                  (1, True, False), (1, 1, 1), (1, 1, None), (1, [], False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


unittest.main() if __name__ == "__main__" else None
