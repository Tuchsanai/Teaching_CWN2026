import unittest
from solve import shipping_fee as f


class TestSolve(unittest.TestCase):
    def test_normal_light(self):
        self.assertEqual(f(500, 10, False), 4000)

    def test_normal_mid(self):
        self.assertEqual(f(3000, 50, False), 8000)

    def test_normal_heavy_far_express(self):
        # 80+15*15=305 ; *1.2=366 ; *1.5=549 บาท
        self.assertEqual(f(20000, 150, True), 54900)

    def test_edge_1000(self):
        self.assertEqual(f(1000, 10, False), 4000)
        self.assertEqual(f(1001, 10, False), 8000)

    def test_edge_5000(self):
        self.assertEqual(f(5000, 10, False), 8000)
        # 5001 g -> 80.015 บาท = 8001.5 สตางค์ ปัดครึ่งขึ้น (ข้อสมมติ) = 8002
        self.assertEqual(f(5001, 10, False), 8002)

    def test_edge_distance_100(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 100.5, False), 4800)

    def test_pickup_zero_distance(self):
        self.assertEqual(f(500, 0, False), 0)
        self.assertEqual(f(500, 0, True), 0)

    def test_express_limit(self):
        # 305 * 1.5 = 457.5 บาท
        self.assertEqual(f(20000, 10, True), 45750)
        with self.assertRaises(ValueError):
            f(20001, 10, True)
        # 80 + 25*15 = 455 บาท (ไม่ด่วนไม่จำกัด 20,000)
        self.assertEqual(f(30000, 10, False), 45500)

    def test_rounding_and_int(self):
        # 5003 g -> 8004.5 สตางค์ -> 8005
        self.assertEqual(f(5003, 10, False), 8005)
        self.assertIs(type(f(5001, 150, True)), int)

    def test_reject_weight_g(self):
        for bad in (0, -1, 30001, 4500.0, True, "100", None):
            with self.assertRaises(ValueError):
                f(bad, 10, False)

    def test_reject_distance_km(self):
        for bad in (-1, -0.1, True, "10", None, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                f(500, bad, False)

    def test_reject_express(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                f(500, 10, bad)


if __name__ == "__main__":
    unittest.main()
