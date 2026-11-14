import unittest
from solve import shipping_fee as f


class TestSolve(unittest.TestCase):
    def test_normal_light(self):
        self.assertEqual(f(500, 10, False), 4000)

    def test_normal_mid(self):
        self.assertEqual(f(3000, 50, False), 8000)

    def test_normal_heavy_far_express(self):
        # 8000+10000*1.5=23000 *1.2=27600 *1.5=41400
        self.assertEqual(f(15000, 150, True), 41400)

    def test_edge_1000(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)

    def test_edge_5000(self):
        self.assertEqual(f(5000, 1, False), 8000)
        # 5001 g: 8000 + 1.5 = 8001.5 -> ปัดครึ่งขึ้น 8002
        self.assertEqual(f(5001, 1, False), 8002)

    def test_edge_distance_100(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 100.5, False), 4800)

    def test_pickup_zero_distance(self):
        self.assertEqual(f(30000, 0, False), 0)

    def test_express_limit(self):
        self.assertEqual(f(20000, 1, True), int((8000 + 15000 * 1.5) * 1.5))
        with self.assertRaises(ValueError):
            f(20001, 1, True)

    def test_rounding(self):
        # 8001.5 * 1.5 = 12002.25 -> 12002
        self.assertEqual(f(5001, 1, True), 12002)

    def test_result_int(self):
        self.assertIs(type(f(5001, 150, True)), int)

    def test_reject_weight_g(self):
        for v in (0, -1, 30001, 4500.0, True, "100", None):
            with self.assertRaises(ValueError):
                f(v, 10, False)

    def test_reject_distance_km(self):
        for v in (-1, -0.1, True, "5", None, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                f(1000, v, False)

    def test_reject_express(self):
        for v in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                f(1000, 10, v)


if __name__ == "__main__":
    unittest.main()
