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
        self.assertEqual(f(5001, 1, False), 8002)  # 8001.5 -> half up
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)

    def test_pickup_and_express_cap(self):
        self.assertEqual(f(500, 0, True), 0)
        self.assertEqual(f(20000, 1, True), 45750)
        with self.assertRaises(ValueError):
            f(20001, 1, True)


class NoDrift(unittest.TestCase):
    def test_round(self):
        self.assertEqual(f(5001, 1, True), 12002)  # 12002.25
        self.assertEqual(f(5003, 101, False), 9605)  # 8004.5*1.2=9605.4
        

class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(0, 1, False), (30001, 1, False), (1, -1, False), (1.0, 1, False),
                  (True, 1, False), (1, 1.0, False), ("1", 1, False), (1, 1, 1), (1, 1, None)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
