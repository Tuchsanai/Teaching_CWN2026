import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)
        self.assertEqual(f(10000, 150, True), round((8000 + 7500) * 1.8))

    def test_boundary(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 100, False), 8000)
        self.assertEqual(f(5000, 100.5, False), 9600)
        self.assertEqual(f(5001, 0, False), 8002)  # 8001.5 -> half up
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_nodrift(self):
        self.assertEqual(f(5001, 0, True), 12002)  # 12002.25
        self.assertEqual(f(5003, 101, False), 9605)  # 8004.5*1.2=9605.4
        
    def test_reject(self):
        for a in [(0, 1, False), (30001, 1, False), (True, 1, False), (5.0, 1, False),
                  ("5", 1, False), (5, -1, False), (5, "1", False), (5, True, False),
                  (5, 1, 1), (5, 1, None), (5, float("nan"), False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
