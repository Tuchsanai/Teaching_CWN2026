import unittest
from fractions import Fraction
from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)


class Boundary(unittest.TestCase):
    def test_weight(self):
        self.assertEqual(f(1, 1, False), 4000)
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)
        self.assertEqual(f(5000, 1, False), 8000)
        self.assertEqual(f(5001, 1, False), 8002)  # 1.5 สตางค์ปัดขึ้น
        self.assertEqual(f(30000, 1, False), 8000 + 37500)

    def test_distance(self):
        self.assertEqual(f(500, 0, False), 0)
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)

    def test_express(self):
        self.assertEqual(f(500, 10, True), 6000)
        self.assertEqual(f(500, 101, True), 7200)
        self.assertEqual(f(20000, 1, True), int(Fraction(8000 + 22500) * Fraction(3, 2)))
        with self.assertRaises(ValueError):
            f(20001, 1, True)


class NoDrift(unittest.TestCase):
    def test_half(self):
        for w in (5001, 5003, 5333, 12345):
            for d in (1, 101):
                for e in (False, True):
                    x = Fraction(8000) + Fraction(1500 * (w - 5000), 1000)
                    if d > 100:
                        x *= Fraction(6, 5)
                    if e:
                        x *= Fraction(3, 2)
                    self.assertEqual(f(w, d, e), int((x * 2 + 1) // 2))


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(0, 1, False), (30001, 1, False), (-1, 1, False), (1000.0, 1, False),
               ("1000", 1, False), (True, 1, False), (None, 1, False),
               (500, -1, False), (500, 1.5, False), (500, "3", False),
               (500, True, False), (500, float("nan"), False),
               (500, 1, 1), (500, 1, 0), (500, 1, "yes"), (500, 1, None)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                f(*a)


if __name__ == "__main__":
    unittest.main()
