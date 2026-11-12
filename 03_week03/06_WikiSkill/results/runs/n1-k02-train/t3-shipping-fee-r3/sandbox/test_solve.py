import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8002)  # 8001.5 -> half-up
        self.assertEqual(f(10000, 0, False), 15500)

    def test_distance_express(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)
        self.assertEqual(f(500, 0, True), 6000)
        self.assertEqual(f(500, 101, True), 7200)

    def test_half_up(self):
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(5001, 0, True), 12002)
        self.assertEqual(f(5003, 0, True), 12007)
        self.assertEqual(f(5001, 101, False), 9602)

    def test_invalid(self):
        for args in [(0, 0, False), (30001, 0, False), (5.0, 0, False), (True, 0, False),
                     (10, -1, False), (10, 0, 1), (10, 0, None), (10, "1", False)]:
            with self.assertRaises(ValueError):
                f(*args)


if __name__ == "__main__":
    unittest.main()
