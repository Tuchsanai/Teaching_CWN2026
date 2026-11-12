import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(6000, 0, False), 9500)
        self.assertEqual(f(30000, 0, False), 8000 + 25 * 1500)

    def test_proportional_and_rounding(self):
        self.assertEqual(f(5001, 0, False), 8002)  # 1.5 -> half up
        self.assertEqual(f(5001, 0, True), 12002)  # 8001.5*1.5=12002.25

    def test_distance_express(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 100.5, False), 4800)
        self.assertEqual(f(500, 0, True), 6000)
        self.assertEqual(f(500, 101, True), 7200)

    def test_invalid(self):
        for a in [(0, 0, False), (30001, 0, False), (10, -1, False),
                  (10, 0, 1), ("5", 0, False), (True, 0, False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
