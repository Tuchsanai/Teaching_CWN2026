import unittest
from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)
        self.assertEqual(f(1000, 200, True), 7200)


class Boundary(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)
        self.assertEqual(f(5000, 1, False), 8000)
        self.assertEqual(f(5001, 1, False), 8002)
        self.assertEqual(f(1, 100, False), 4000)
        self.assertEqual(f(1, 101, False), 4800)
        self.assertEqual(f(30000, 1, False), 8000 + 37500)
        self.assertEqual(f(20000, 1, True), (8000 + 22500) * 3 // 2)

    def test_pickup(self):
        self.assertEqual(f(500, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_half(self):
        self.assertEqual(f(5001, 1, True), 12002)  # 12002.25
        self.assertEqual(f(5001, 101, False), 9602)  # 8001.5*1.2=9601.8
        self.assertEqual(f(5003, 1, False), 8005)  # 8004.5 -> 8005


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(0, 1, False), (30001, 1, False), (1, -1, False), (1.0, 1, False),
                  ("5", 1, False), (True, 1, False), (1, 1.0, False), (1, 1, 1),
                  (1, 1, None), (20001, 1, True), (20001, 0, True)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
