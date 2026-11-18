import unittest
from solve import shipping_fee as f


class TestSolve(unittest.TestCase):
    def test_light_normal(self):
        self.assertEqual(f(500, 10, False), 4000)

    def test_mid_normal(self):
        self.assertEqual(f(3000, 50, False), 8000)

    def test_heavy_normal(self):
        # 80 + 5*15 = 155 บาท
        self.assertEqual(f(10000, 0, False), 15500)

    def test_far_and_express(self):
        # 40*1.2*1.5 = 72 บาท
        self.assertEqual(f(1000, 101, True), 7200)

    def test_edge_1000(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)

    def test_edge_5000(self):
        self.assertEqual(f(5000, 0, False), 8000)
        # เกิน 1 กรัม = 1.5 สตางค์ -> ปัดครึ่งขึ้นเป็น 2
        self.assertEqual(f(5001, 0, False), 8002)

    def test_edge_distance_100(self):
        # สมมติ: "เกิน 100" ต้องมากกว่า 100 จริง
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 100.5, False), 4800)

    def test_rounding_half_up(self):
        # 5003 g: 8004.5 -> 8005
        self.assertEqual(f(5003, 0, False), 8005)
        # 8001.5*1.5 = 12002.25 -> 12002
        self.assertEqual(f(5001, 0, True), 12002)

    def test_max_weight(self):
        # 80 + 25*15 = 455 บาท *1.2*1.5 = 819 บาท
        self.assertEqual(f(30000, 200, True), 81900)

    def test_result_int(self):
        self.assertIs(type(f(5001, 150.5, True)), int)

    def test_reject_weight_g(self):
        for bad in (0, -5, 30001, 4500.0, True, "100", None):
            with self.assertRaises(ValueError):
                f(bad, 10, False)

    def test_reject_distance_km(self):
        for bad in (-1, -0.1, "5", None, True, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                f(1000, bad, False)

    def test_reject_express(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                f(1000, 10, bad)


if __name__ == "__main__":
    unittest.main()
