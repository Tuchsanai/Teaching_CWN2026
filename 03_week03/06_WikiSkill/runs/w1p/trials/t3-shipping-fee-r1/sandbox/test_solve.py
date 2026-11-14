import unittest
from solve import shipping_fee as f


class TestSolve(unittest.TestCase):
    def test_light(self):
        self.assertEqual(f(500, 10, False), 4000)

    def test_mid(self):
        self.assertEqual(f(3000, 50, False), 8000)

    def test_heavy(self):
        self.assertEqual(f(10000, 50, False), 15500)

    def test_far_and_express(self):
        self.assertEqual(f(500, 101, True), 7200)

    def test_edge_1000(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)

    def test_edge_5000(self):
        self.assertEqual(f(5000, 1, False), 8000)
        self.assertEqual(f(5001, 1, False), 8002)  # 80.015 -> 8001.5 ปัดครึ่งขึ้น

    def test_edge_distance_100(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)
        self.assertEqual(f(500, 100.5, False), 4800)

    def test_pickup_zero(self):
        self.assertEqual(f(500, 0, True), 0)

    def test_express_limit(self):
        self.assertEqual(f(20000, 1, True), 45750)  # (80+225)*1.5=457.5
        with self.assertRaises(ValueError):
            f(20001, 1, True)

    def test_max_weight(self):
        self.assertEqual(f(30000, 1, False), 45500)
        self.assertEqual(f(25000, 101, False), 45600)

    def test_rounding_far(self):
        self.assertEqual(f(5001, 101, False), 9602)  # 9601.8

    def test_returns_int(self):
        self.assertIs(type(f(5001, 101, True)), int)

    def test_reject_weight_g(self):
        for v in (0, -1, 30001, 500.0, True, "500", None):
            with self.assertRaises(ValueError):
                f(v, 1, False)

    def test_reject_distance_km(self):
        for v in (-1, -0.1, True, "5", None, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                f(500, v, False)

    def test_reject_express(self):
        for v in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                f(500, 1, v)


if __name__ == "__main__":
    unittest.main()
