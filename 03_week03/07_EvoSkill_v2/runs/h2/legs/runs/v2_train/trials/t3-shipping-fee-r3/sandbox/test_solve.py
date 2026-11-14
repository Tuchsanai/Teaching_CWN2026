"""ทดสอบ shipping_fee แยกหมวด Normal, Boundary, NoDrift, Reject
expected ทุกค่าคำนวณด้วยสคริปต์ Fraction แยกต่างหากแล้ว (สูตร: ฐาน -> ×1.2 ถ้าเกิน 100 กม. -> ×1.5 ถ้าด่วน -> ปัดครึ่งขึ้น)

รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_light_weight(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)

    def test_medium_weight(self):
        self.assertEqual(shipping_fee(3001, 0, False), 8000)

    def test_heavy_weight(self):
        self.assertEqual(shipping_fee(6000, 0, False), 9500)

    def test_flag_and_distance_combinations(self):
        self.assertEqual(shipping_fee(2000, 101, True), 14400)  # 80×1.2×1.5
        self.assertEqual(shipping_fee(1000, 100, True), 6000)   # 40×1.5 (ระยะ 100 ไม่เกิน)
        self.assertEqual(shipping_fee(4999, 0, True), 12000)    # 80×1.5


class Boundary(unittest.TestCase):
    def test_weight_threshold_1000(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)  # ไม่เกิน 1,000 = 40 บาท
        self.assertEqual(shipping_fee(1001, 0, False), 8000)  # เกิน 1,000 = 80 บาท

    def test_weight_threshold_5000(self):
        self.assertEqual(shipping_fee(5000, 0, False), 8000)  # ไม่เกิน 5,000 = 80 บาท

    def test_min_and_max_weight(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_distance_exactly_100_no_surcharge(self):
        self.assertEqual(shipping_fee(5001, 100, False), 8002)

    def test_distance_zero(self):
        self.assertEqual(shipping_fee(1000, 0, True), 6000)

    def test_distance_just_above_100(self):
        self.assertEqual(shipping_fee(5001, 100.01, False), 9602)


class NoDrift(unittest.TestCase):
    def test_single_rounding_with_express(self):
        # 8001.5 × 1.5 = 12002.25 -> 12002 (ถ้าปัดก่อนจะได้ 12003)
        self.assertEqual(shipping_fee(5001, 0, True), 12002)

    def test_single_rounding_with_distance(self):
        # 8001.5 × 1.2 × 1.5 = 14402.7 -> 14403 (ปัดครั้งเดียวตอนท้าย)
        self.assertEqual(shipping_fee(5001, 200, True), 14403)

    def test_half_up_on_weight_fraction(self):
        # 8001.5 -> 8002 (ปัดครึ่งขึ้น)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)


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

    def test_weight_out_of_range(self):
        with self.assertRaises(ValueError):
            shipping_fee(0, 10, False)
        with self.assertRaises(ValueError):
            shipping_fee(-1, 10, False)
        with self.assertRaises(ValueError):
            shipping_fee(30001, 10, False)

    def test_distance_negative_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, -0.1, False)

    def test_distance_bool_and_str_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, True, False)
        with self.assertRaises(ValueError):
            shipping_fee(1000, "10", False)

    def test_distance_nan_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, float("nan"), False)

    def test_express_must_be_bool(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, 10, 1)
        with self.assertRaises(ValueError):
            shipping_fee(1000, 10, "yes")


if __name__ == "__main__":
    unittest.main()
