import unittest
from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)

    def test_modifiers(self):
        self.assertEqual(f(500, 150, False), 4800)
        self.assertEqual(f(500, 10, True), 6000)
        self.assertEqual(f(500, 150, True), 7200)


class Boundary(unittest.TestCase):
    def test_weight(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)
        self.assertEqual(f(5000, 1, False), 8000)
        self.assertEqual(f(5001, 1, False), 8002)  # 8001.5 -> 8002
        self.assertEqual(f(30000, 1, False), 8000 + 37500)

    def test_distance(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)
        self.assertEqual(f(500, 0, False), 0)

    def test_express_cap(self):
        self.assertEqual(f(20000, 1, True), 45750)
        with self.assertRaises(ValueError):
            f(20001, 1, True)


class NoDrift(unittest.TestCase):
    def test_half(self):
        self.assertEqual(f(5001, 1, False), 8002)
        self.assertEqual(f(5003, 101, False), 9605)  # 8004.5*1.2=9605.4


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(0, 1, False), (30001, 1, False), (-1, 1, False), (1000.0, 1, False),
                  ("1000", 1, False), (True, 1, False), (None, 1, False),
                  (100, -1, False), (100, 1.5, False), (100, "5", False), (100, True, False),
                  (100, 1, 1), (100, 1, "yes"), (100, 1, None), (100, float("nan"), False)]:
            with self.assertRaises(ValueError, msg=str(a)):
                f(*a)


if __name__ == "__main__":
    unittest.main()
