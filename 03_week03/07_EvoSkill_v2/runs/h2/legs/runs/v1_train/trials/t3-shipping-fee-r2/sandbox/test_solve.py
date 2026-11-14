"""ทดสอบ shipping_fee. expected คำนวณด้วยสคริปต์ Fraction แล้ว (ดูค่าในคอมเมนต์)
รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_light_short_standard(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)      # 40 บาท

    def test_mid_weight_standard(self):
        self.assertEqual(shipping_fee(3000, 50, False), 8000)     # 80 บาท

    def test_heavy_standard(self):
        self.assertEqual(shipping_fee(30000, 150, True), 81900)   # 45500*1.2*1.5 = 819 บาท

    def test_long_distance_only(self):
        self.assertEqual(shipping_fee(1000, 101, False), 4800)    # 4000*1.2

    def test_express_only(self):
        self.assertEqual(shipping_fee(1000, 100, True), 6000)     # 4000*1.5

    def test_express_and_long_distance(self):
        self.assertEqual(shipping_fee(5000, 101, True), 14400)    # 8000*1.2*1.5


class Boundary(unittest.TestCase):
    def test_weight_1000_is_light_tier(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)

    def test_weight_1001_is_mid_tier(self):
        self.assertEqual(shipping_fee(1001, 0, False), 8000)

    def test_weight_5000_is_mid_tier_no_surcharge(self):
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_weight_5001_starts_surcharge(self):
        # 8000 + 1*1.5 = 8001.5 -> ปัดครึ่งขึ้น 8002
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_distance_100_no_surcharge(self):
        self.assertEqual(shipping_fee(1000, 100, False), 4000)

    def test_distance_100_1_has_surcharge(self):
        self.assertEqual(shipping_fee(1000, 100.1, False), 4800)

    def test_zero_distance_and_min_weight(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)

    def test_zero_distance_accepts_int_and_float(self):
        self.assertEqual(shipping_fee(1, 0.0, False), 4000)

    def test_max_weight_express_long(self):
        # 45500 * 1.2 * 1.5 = 81900 (100.5 > 100 จึงคิดเพิ่ม)
        self.assertEqual(shipping_fee(30000, 100.5, True), 81900)


class NoDrift(unittest.TestCase):
    def test_single_rounding_half_up(self):
        # 8001.5 * 1.2 * 1.5 = 14402.7 -> 14403 (ปัดครั้งเดียวตอนท้าย)
        self.assertEqual(shipping_fee(5001, 120, True), 14403)

    def test_no_intermediate_rounding(self):
        # 8001.5 * 1.5 = 12002.25 -> 12002 ; ถ้าปัดกลางทางเป็น 8002 แล้วคูณจะได้ 12003
        self.assertEqual(shipping_fee(5001, 0, True), 12002)


class Reject(unittest.TestCase):
    def test_weight_bool_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(True, 10, False)

    def test_weight_float_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(4500.0, 10, False)

    def test_weight_str_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee("4500", 10, False)

    def test_weight_zero_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(0, 10, False)

    def test_weight_over_max_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(30001, 10, False)

    def test_distance_negative_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, -1, False)

    def test_distance_str_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, "10", False)

    def test_distance_bool_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, True, False)

    def test_express_must_be_bool(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, 10, 1)

    def test_express_none_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, 10, None)


if __name__ == "__main__":
    unittest.main()
