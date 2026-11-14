import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(1001, 10, False), 8000)
        self.assertEqual(f(5000, 100, False), 8000)
        self.assertEqual(f(5001, 101, False), 9602)  # 8001.5*1.2=9601.8
        self.assertEqual(f(10000, 10, True), int((8000 + 7500) * 1.5))
        self.assertEqual(f(1000, 101, True), 7200)
        self.assertEqual(f(20000, 5, True), 45 * 0 + int((8000 + 22500) * 1.5))

    def test_edges(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(30000, 1, False), 8000 + 37500)
        self.assertEqual(f(5, 0, False), 0)
        self.assertEqual(type(f(5001, 1, False)), int)

    def test_reject(self):
        for a in [(0, 1, False), (30001, 1, False), (1, -1, False), (1.0, 1, False),
                  ("1", 1, False), (True, 1, False), (1, 1, 1), (1, 1, None),
                  (20001, 1, True), (1, 1.5, False), (1, True, False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
