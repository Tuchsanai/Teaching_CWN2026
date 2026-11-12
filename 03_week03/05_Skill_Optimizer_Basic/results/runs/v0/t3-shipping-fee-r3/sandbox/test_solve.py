import unittest
from solve import shipping_fee as f, main


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(6000, 0, False), 9500)
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_proportional(self):
        self.assertEqual(f(5001, 0, False), 8002)  # 1.5 -> half-up
        self.assertEqual(f(5003, 0, False), 8005)  # 4.5 -> half-up

    def test_distance_express(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 100.5, False), 4800)
        self.assertEqual(f(500, 0, True), 6000)
        self.assertEqual(f(500, 101, True), 7200)
        self.assertEqual(f(6000, 150, True), 17100)

    def test_invalid(self):
        for a in [(0, 1, False), (30001, 1, False), (10, -1, False),
                  ("10", 1, False), (10, 1, 1), (True, 1, False), (float("nan"), 1, False)]:
            with self.assertRaises(ValueError):
                f(*a)

    def test_cli(self):
        self.assertEqual(main(['{"weight_g": 500, "distance_km": 0, "express": true}']), 0)
        self.assertEqual(main(['{"weight_g": 0, "distance_km": 0}']), 1)
        self.assertEqual(main(['not json']), 1)


if __name__ == "__main__":
    unittest.main()
