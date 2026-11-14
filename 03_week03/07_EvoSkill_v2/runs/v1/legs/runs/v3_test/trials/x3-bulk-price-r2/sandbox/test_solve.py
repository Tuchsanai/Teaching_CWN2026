import unittest
from solve import bulk_price


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5 half-up
    def test_boundary(self):
        self.assertEqual(bulk_price(100, 9, False), 963)
        self.assertEqual(bulk_price(100, 49, False), half_ref(4900, 965))
        self.assertEqual(bulk_price(100, 50, True), half_ref(5000, 925, 975))
    def test_reject(self):
        for a in [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
                  (1, 1, 1), (True, 1, False), (1, "3", False), (None, 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


def half_ref(base, *rates):
    from fractions import Fraction
    x = Fraction(base)
    for r in rates:
        x *= Fraction(r, 1000)
    return int((x * Fraction(107, 100) * 2 + 1) // 2)


if __name__ == "__main__":
    unittest.main()
