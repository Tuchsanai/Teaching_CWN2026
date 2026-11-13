import unittest
from fractions import Fraction
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)
        self.assertEqual(f(500, 200, True), 7200)

    def test_boundary(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 100, False), 8000)
        self.assertEqual(f(5001, 101, False), 9602 + 0 if False else f(5001, 101, False))
        self.assertEqual(f(5001, 100, False), 8002)
        self.assertEqual(f(5001, 101, False), 9602)
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_nodrift(self):
        for w in (5001, 5003, 5007, 12345, 29999):
            for d in (0, 101):
                for e in (False, True):
                    x = Fraction(8000) + Fraction((w - 5000) * 1500, 1000)
                    if d > 100:
                        x *= Fraction(6, 5)
                    if e:
                        x *= Fraction(3, 2)
                    self.assertEqual(f(w, d, e), int((x * 2 + 1) // 2))
        self.assertEqual(f(5001, 0, False), 8002)  # 8001.5 -> 8002
        self.assertIs(type(f(5001, 0, True)), int)

    def test_reject(self):
        bad = [(0, 1, False), (30001, 1, False), (-1, 1, False), (10.0, 1, False),
               ("5", 1, False), (True, 1, False), (None, 1, False),
               (10, -1, False), (10, 1.5, False), (10, "1", False), (10, True, False),
               (10, 1, 1), (10, 1, "true"), (10, 1, None)]
        for a in bad:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
