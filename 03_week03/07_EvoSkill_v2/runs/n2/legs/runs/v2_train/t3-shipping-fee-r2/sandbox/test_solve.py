import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1001, 101, False), 9600)
        self.assertEqual(f(1000, 0, True), 6000)
        self.assertEqual(f(5000, 101, True), 14400)
        self.assertEqual(f(30000, 200, True), int((8000 + 37500) * 1.8))

    def test_rounding(self):
        # 5001 g: 8000+1.5=8001.5 -> half-up 8002
        self.assertEqual(f(5001, 0, False), 8002)
        # 5003 g: 8004.5 *1.5 = 12006.75 -> 12007
        self.assertEqual(f(5003, 0, True), 12007)

    def test_reject(self):
        for a in [(0, 1, False), (30001, 1, False), (-1, 1, False), (1.0, 1, False),
                  ("1", 1, False), (True, 1, False), (None, 1, False),
                  (1, -1, False), (1, 1.0, False), (1, "1", False), (1, True, False),
                  (1, 1, 1), (1, 1, None), (1, 1, "True")]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
