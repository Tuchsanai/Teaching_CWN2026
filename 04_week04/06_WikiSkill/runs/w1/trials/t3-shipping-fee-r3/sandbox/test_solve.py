import unittest
from solve import shipping_fee as f


class TestSolve(unittest.TestCase):
    def test_normal_light(self):
        self.assertEqual(f(500, 10, False), 4000)

    def test_normal_mid(self):
        self.assertEqual(f(3000, 50, False), 8000)

    def test_normal_heavy(self):
        # 80 + 5*15 = 155 บาท
        self.assertEqual(f(10000, 50, False), 15500)

    def test_far_distance(self):
        self.assertEqual(f(500, 150, False), 4800)

    def test_express(self):
        self.assertEqual(f(500, 10, True), 6000)

    def test_far_and_express(self):
        # 8000*1.2*1.5 = 14400
        self.assertEqual(f(3000, 101, True), 14400)

    def test_edge_1000(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)

    def test_edge_5000(self):
        self.assertEqual(f(5000, 0, False), 8000)
        # 8001.5 ปัดครึ่งขึ้น
        self.assertEqual(f(5001, 0, False), 8002)

    def test_edge_100km(self):
        # 100 พอดี ไม่เพิ่ม; เกิน 100 เพิ่ม 20%
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 100.5, False), 4800)

    def test_max_weight(self):
        # 8000 + 25000*1.5 = 45500
        self.assertEqual(f(30000, 0, False), 45500)

    def test_rounding_once(self):
        # 8001.5*1.2 = 9601.8 -> 9602
        self.assertEqual(f(5001, 101, False), 9602)
        # 8001.5*1.5 = 12002.25 -> 12002
        self.assertEqual(f(5001, 0, True), 12002)

    def test_returns_int(self):
        self.assertIs(type(f(5001, 101, True)), int)

    def test_reject_weight_g(self):
        for bad in (0, -1, 30001, 4500.0, True, "100", None):
            with self.assertRaises(ValueError):
                f(bad, 10, False)

    def test_reject_distance_km(self):
        for bad in (-1, -0.1, float("nan"), float("inf"), True, "5", None):
            with self.assertRaises(ValueError):
                f(500, bad, False)

    def test_reject_express(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                f(500, 10, bad)


if __name__ == "__main__":
    unittest.main()
