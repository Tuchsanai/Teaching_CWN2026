import unittest
from solve import shipping_fee as f


class TestSolve(unittest.TestCase):
    def test_light_near(self):
        self.assertEqual(f(500, 10, False), 4000)

    def test_mid_far(self):
        self.assertEqual(f(3000, 150, False), 9600)

    def test_heavy_express(self):
        # 80+15*5=155 บาท *1.5 = 232.50
        self.assertEqual(f(10000, 50, True), 23250)

    def test_heavy_far_express(self):
        # 155*1.2*1.5 = 279 บาท
        self.assertEqual(f(10000, 101, True), 27900)

    def test_edge_1000(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)

    def test_edge_5000(self):
        self.assertEqual(f(5000, 1, False), 8000)
        # 5001 g -> 80.015 บาท = 8001.5 สตางค์ -> ปัดขึ้น 8002 (ข้อสมมติ: half-up)
        self.assertEqual(f(5001, 1, False), 8002)

    def test_edge_distance_100(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 100.5, False), 4800)

    def test_edge_express_20000(self):
        self.assertEqual(f(20000, 1, True), 30000 * 0 + int((80 + 225) * 150))
        with self.assertRaises(ValueError):
            f(20001, 1, True)

    def test_pickup_zero_distance(self):
        self.assertEqual(f(500, 0, True), 0)

    def test_rounding_and_int(self):
        self.assertIs(type(f(5001, 101, True)), int)
        # 8001.5*1.8 = 14402.7 -> 14403
        self.assertEqual(f(5001, 101, True), 14403)

    def test_reject_weight_g(self):
        for v in (0, -1, 30001, 4500.0, True, "100", None):
            with self.assertRaises(ValueError):
                f(v, 10, False)

    def test_reject_distance_km(self):
        for v in (-1, -0.1, True, "5", None, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                f(500, v, False)

    def test_reject_express(self):
        for v in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                f(500, 10, v)


if __name__ == "__main__":
    unittest.main()
