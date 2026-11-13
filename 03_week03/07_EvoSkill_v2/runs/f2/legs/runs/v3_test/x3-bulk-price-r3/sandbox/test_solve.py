import unittest
from fractions import Fraction
from solve import bulk_price


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_tier10(self):
        # 10000*10*0.965*1.07 = 103255
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_tier50_coupon(self):
        # 10000*50*0.925*0.975*1.07 = 482503.125 -> 482503
        self.assertEqual(bulk_price(10000, 50, True), 482503)


class Boundary(unittest.TestCase):
    def test_9_10(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5 -> half up

    def test_49_50(self):
        self.assertEqual(bulk_price(1000, 49, False), 50595)  # 47285*1.07=50594.95
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 49487.5 half-up

    def test_zero_price_and_max(self):
        self.assertEqual(bulk_price(0, 5, True), 0)
        self.assertEqual(bulk_price(1, 1000, False), 990)  # 925*1.07=989.75


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_exact_fraction(self):
        for p, q, c in [(333, 17, True), (999, 77, False), (1, 10, True)]:
            r = Fraction(p * q)
            r *= Fraction(925, 1000) if q >= 50 else Fraction(965, 1000) if q >= 10 else 1
            if c:
                r *= Fraction(975, 1000)
            r *= Fraction(107, 100)
            self.assertEqual(bulk_price(p, q, c), int((r * 2 + 1) // 2))


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, False), (100, 0, False), (100, 1001, False),
                  (100.0, 1, False), ("1", 1, False), (True, 1, False),
                  (100, 1.0, False), (100, True, False),
                  (100, 1, 1), (100, 1, None), (100, 1, "True")]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
