import unittest
from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(7000, 10, False), 8000 + 3000)
        self.assertEqual(f(3000, 150, True), 14400)


class Boundary(unittest.TestCase):
    def test_edges(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8002)  # 1.5 -> half-up
        self.assertEqual(f(30000, 0, False), 8000 + 37500)
        self.assertEqual(f(1, 100, False), 4000)
        self.assertEqual(f(1, 101, False), 4800)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(f(5001, 0, True), 12002)  # 8001.5*1.5=12002.25
        self.assertEqual(f(5003, 0, False), 8005)  # 8004.5 -> 8005
        self.assertEqual(f(5001, 101, False), 9602)  # 8001.5*1.2=9601.8


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(0, 1, False), (30001, 1, False), (-5, 1, False), (1.0, 1, False),
                  ("1", 1, False), (True, 1, False), (1, -1, False), (1, "5", False),
                  (1, None, False), (1, 1, 1), (1, 1, None), (1, float("nan"), False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
