import unittest
from fractions import Fraction
from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)
        self.assertEqual(shipping_fee(3000, 10, False), 8000)
        self.assertEqual(shipping_fee(10000, 10, False), 8000 + 7500)

    def test_modifiers(self):
        self.assertEqual(shipping_fee(500, 101, False), 4800)
        self.assertEqual(shipping_fee(500, 10, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)


class Boundary(unittest.TestCase):
    def test_weight(self):
        self.assertEqual(shipping_fee(1000, 1, False), 4000)
        self.assertEqual(shipping_fee(1001, 1, False), 8000)
        self.assertEqual(shipping_fee(5000, 1, False), 8000)
        self.assertEqual(shipping_fee(5001, 1, False), 8002)  # 1.5 สต. -> 2

    def test_distance(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)
        self.assertEqual(shipping_fee(500, 0, False), 0)

    def test_express_cap(self):
        self.assertEqual(shipping_fee(20000, 1, True), int((Fraction(8000 + 22500) * 3 / 2)))
        self.assertEqual(shipping_fee(30000, 1, False), 8000 + 37500)


class NoDrift(unittest.TestCase):
    def test_fraction(self):
        for w in (5001, 5333, 12345, 29999):
            for d in (1, 101):
                for e in (False, True):
                    if e and w > 20000:
                        continue
                    f = Fraction(8000) + Fraction(1500 * (w - 5000), 1000)
                    if d > 100:
                        f *= Fraction(6, 5)
                    if e:
                        f *= Fraction(3, 2)
                    self.assertEqual(shipping_fee(w, d, e), int((f * 2 + 1) // 2))


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [
            (0, 1, False), (30001, 1, False), (-5, 1, False), (1000.0, 1, False),
            ("1000", 1, False), (True, 1, False), (None, 1, False),
            (500, -1, False), (500, 10.5, False), (500, 10.0, False),
            (500, "5", False), (500, None, False), (500, True, False),
            (500, 1, 1), (500, 1, None), (500, 1, "true"),
            (20001, 1, True), (30000, 1, True), (20001, 0, True),
        ]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                shipping_fee(*a)


if __name__ == "__main__":
    unittest.main()
