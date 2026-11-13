import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)
        self.assertEqual(f(10000, 200, True), 27900)

    def test_boundary(self):
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1001, 100, False), 8000)
        self.assertEqual(f(5000, 101, False), 9600)
        self.assertEqual(f(5001, 0, False), 8002)  # 8001.5 -> half-up
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_half(self):
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(5001, 0, True), 12002)  # 12002.25

    def test_reject(self):
        for a in [(0, 1, False), (30001, 1, False), (1, -1, False), (1.0, 1, False),
                  (1, 1.0, False), ("1", 1, False), (True, 1, False), (1, 1, 1),
                  (1, 1, None), (None, 1, False), (1, True, False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
