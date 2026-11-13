import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 100, False), 8000)
        self.assertEqual(f(5001, 0, False), 8002)  # 8000+1.5 -> half up
        self.assertEqual(f(10000, 0, False), 15500)
        self.assertEqual(f(5000, 101, False), 9600)
        self.assertEqual(f(5000, 101, True), 14400)
        self.assertEqual(f(1, 0, True), 6000)

    def test_reject(self):
        for a in [(0, 1, False), (30001, 1, False), (1.0, 1, False), (True, 1, False),
                  ("1", 1, False), (5, -1, False), (5, True, False), (5, "1", False),
                  (5, 1, 1), (5, 1, None), (5, float("nan"), False)]:
            with self.assertRaises(ValueError):
                f(*a)


unittest.main() if __name__ == "__main__" else None
