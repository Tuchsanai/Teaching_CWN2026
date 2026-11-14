import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)
        self.assertEqual(f(500, 150, True), 7200)

    def test_boundary(self):
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1001, 101, False), 9600)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8002)  # 1.5 -> 2
        self.assertEqual(f(30000, 0, False), 8000 + 37500)
        self.assertEqual(f(1, 0, False), 4000)

    def test_nodrift(self):
        self.assertEqual(f(5001, 0, True), 12002)   # 8001.5*1.5=12002.25
        self.assertEqual(f(5003, 101, True), 14408)  # 8004.5*1.8=14408.1
        self.assertIsInstance(f(5001, 200, True), int)

    def test_reject(self):
        for a in [(0, 1, False), (30001, 1, False), (-1, 1, False), (1.0, 1, False),
                  ("1", 1, False), (True, 1, False), (1, -1, False), (1, 1.5, False),
                  (1, 1, 1), (1, 1, None), (None, 1, False), (1, True, False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
