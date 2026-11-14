"""ชุดทดสอบ shipping_fee. รัน: python3 -m unittest -v test_solve
expected คำนวณด้วยสคริปต์ Fraction แยกต่างหากแล้ว (ดูสูตรใน solve.py)
"""
import unittest

from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_light_tier_domestic(self):
        self.assertEqual(shipping_fee(800, 10, False), 4000)  # 40 บาท

    def test_mid_tier_domestic(self):
        self.assertEqual(shipping_fee(3000, 50, False), 8000)  # 80 บาท

    def test_heavy_tier_proportional(self):
        self.assertEqual(shipping_fee(6000, 50, False), 9500)  # 80 + 1 กก. * 15 = 95 บาท

    def test_distance_surcharge(self):
        self.assertEqual(shipping_fee(2000, 150, False), 9600)  # 80 * 1.2 = 96 บาท

    def test_express_only(self):
        self.assertEqual(shipping_fee(2000, 50, True), 12000)  # 80 * 1.5 = 120 บาท

    def test_distance_and_express_combined(self):
        # 6000 g: 95 บาท -> *1.2 = 114 -> *1.5 = 171 บาท
        self.assertEqual(shipping_fee(6000, 150, True), 17100)

    def test_flag_combinations(self):
        self.assertEqual(shipping_fee(800, 10, True), 6000)     # 40 * 1.5 = 60
        self.assertEqual(shipping_fee(800, 150, False), 4800)   # 40 * 1.2 = 48
        self.assertEqual(shipping_fee(800, 150, True), 7200)    # 40 * 1.2 * 1.5 = 72


class Boundary(unittest.TestCase):
    def test_weight_1000_is_light_tier(self):
        self.assertEqual(shipping_fee(1000, 10, False), 4000)

    def test_weight_1001_is_mid_tier(self):
        self.assertEqual(shipping_fee(1001, 10, False), 8000)

    def test_weight_5000_is_mid_tier(self):
        self.assertEqual(shipping_fee(5000, 10, False), 8000)

    def test_weight_5001_adds_fraction(self):
        # 80 + 1/1000 * 15 = 80.015 บาท -> 8001.5 สตางค์ -> ปัดครึ่งขึ้น 8002
        self.assertEqual(shipping_fee(5001, 10, False), 8002)

    def test_weight_min_and_max(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(30000, 0, False), 45500)  # 80 + 25 * 15 = 455 บาท

    def test_distance_100_is_not_surcharged(self):
        self.assertEqual(shipping_fee(1000, 100, False), 4000)

    def test_distance_just_above_100(self):
        self.assertEqual(shipping_fee(1000, 100.5, False), 4800)  # 40 * 1.2 = 48 บาท

    def test_distance_zero(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)

    def test_max_weight_with_surcharge_and_express(self):
        self.assertEqual(shipping_fee(30000, 200, True), 81900)  # 455 * 1.2 * 1.5 = 819 บาท


class NoDrift(unittest.TestCase):
    def test_single_rounding_half_up(self):
        # 5001 g ไม่ส่งด่วน: 8001.5 สตางค์ ต้องปัดครั้งเดียวเป็น 8002
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_single_rounding_express(self):
        # 80.015 * 1.5 = 120.0225 บาท -> 12002.25 สตางค์ -> 12002
        self.assertEqual(shipping_fee(5001, 0, True), 12002)

    def test_no_rounding_between_surcharge_and_express(self):
        # 2000 g, 101 km, express: 80 * 1.2 * 1.5 = 144 บาท (ไม่ควรปัดระหว่างทาง)
        self.assertEqual(shipping_fee(2000, 101, True), 14400)


class Reject(unittest.TestCase):
    def test_weight_bool_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(True, 10, False)

    def test_weight_float_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000.0, 10, False)

    def test_weight_str_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee("1000", 10, False)

    def test_weight_zero_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(0, 10, False)

    def test_weight_negative_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(-1, 10, False)

    def test_weight_over_max_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(30001, 10, False)

    def test_distance_negative_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, -0.1, False)

    def test_distance_bool_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, True, False)

    def test_distance_str_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, "10", False)

    def test_express_must_be_bool(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, 10, 1)
        with self.assertRaises(ValueError):
            shipping_fee(1000, 10, "yes")
        with self.assertRaises(ValueError):
            shipping_fee(1000, 10, None)


if __name__ == "__main__":
    unittest.main()
