import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 15500)
        self.assertEqual(f(500, 200, True), 7200)

    def test_edges(self):
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1001, 100, False), 8000)
        self.assertEqual(f(5000, 101, False), 9600)
        self.assertEqual(f(5001, 0, False), 8002)  # 1.5 satang -> half up
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(30000, 0, False), 8000 + 25000 * 3 // 2)

    def test_half_up(self):
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(5001, 0, True), 12002)  # 8001.5*1.5=12002.25

    def test_reject(self):
        for a in [(0, 1, False), (30001, 1, False), (1, -1, False),
                  (1000.0, 1, False), (True, 1, False), (1, 1.0, False),
                  (1, 1, 1), ("1", 1, False), (None, 1, False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
