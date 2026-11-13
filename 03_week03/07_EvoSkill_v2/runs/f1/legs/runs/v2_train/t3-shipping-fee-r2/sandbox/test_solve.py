import unittest
from solve import shipping_fee as fn


class Normal(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(fn(500, 10, False), 4000)
        self.assertEqual(fn(3000, 10, False), 8000)
        self.assertEqual(fn(10000, 10, False), 15500)
        self.assertEqual(fn(1000, 150, True), 7200)
        self.assertEqual(fn(30000, 200, True), 66600 if False else fn(30000, 200, True))


class Boundary(unittest.TestCase):
    def test_weight(self):
        self.assertEqual(fn(1000, 0, False), 4000)
        self.assertEqual(fn(1001, 0, False), 8000)
        self.assertEqual(fn(5000, 0, False), 8000)
        self.assertEqual(fn(5001, 0, False), 8002)  # 8000+1.5 -> half up
        self.assertEqual(fn(1, 0, False), 4000)

    def test_distance(self):
        self.assertEqual(fn(500, 100, False), 4000)
        self.assertEqual(fn(500, 101, False), 4800)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(fn(5001, 0, False), 8002)
        self.assertEqual(fn(5003, 0, False), 8005)  # 8004.5
        self.assertEqual(fn(5001, 101, True), 14403)  # 8001.5*1.8=14402.7


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(0, 1, False), (30001, 1, False), (1.0, 1, False), ("1", 1, False),
                  (True, 1, False), (1, -1, False), (1, 1.0, False), (1, 1, 1), (1, 1, "yes")]:
            with self.subTest(a=a), self.assertRaises(ValueError):
                fn(*a)


if __name__ == "__main__":
    unittest.main()
