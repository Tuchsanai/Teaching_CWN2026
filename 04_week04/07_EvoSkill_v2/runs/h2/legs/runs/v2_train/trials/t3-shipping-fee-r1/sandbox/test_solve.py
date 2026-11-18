"""ชุดทดสอบ shipping_fee. รัน: python3 -m unittest -v test_solve

expected ทุกค่าคำนวณด้วยสคริปต์ Fraction แยกต่างหากก่อนใส่ (ไม่ได้คัดลอกจากผลของ solve.py)
หน่วยเป็นสตางค์
"""
import unittest

from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_light_tier(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)
        self.assertEqual(shipping_fee(1, 0, False), 4000)

    def test_mid_tier(self):
        self.assertEqual(shipping_fee(3000, 50, False), 8000)

    def test_heavy_tier_with_extra_grams(self):
        # 8000 + 1.5 * (8000 - 5000) = 12500 -> express x1.5 = 18750
        self.assertEqual(shipping_fee(8000, 80, True), 18750)

    def test_far_and_express_combined(self):
        self.assertEqual(shipping_fee(3000, 150, False), 9600)
        self.assertEqual(shipping_fee(3000, 150, True), 14400)

    def test_max_weight(self):
        self.assertEqual(shipping_fee(30000, 0, False), 45500)
        self.assertEqual(shipping_fee(30000, 0, True), 68250)


class Boundary(unittest.TestCase):
    def test_weight_at_1000(self):
        self.assertEqual(shipping_fee(1000, 50, False), 4000)

    def test_weight_just_above_1000(self):
        self.assertEqual(shipping_fee(1001, 50, False), 8000)

    def test_weight_at_5000(self):
        self.assertEqual(shipping_fee(5000, 50, False), 8000)

    def test_weight_just_above_5000(self):
        self.assertEqual(shipping_fee(5001, 50, False), 8002)  # 8001.5 -> ปัดครึ่งขึ้น

    def test_distance_at_100_no_surcharge(self):
        self.assertEqual(shipping_fee(3000, 100, False), 8000)

    def test_distance_just_above_100(self):
        self.assertEqual(shipping_fee(3000, 100.5, False), 9600)

    def test_zero_distance(self):
        self.assertEqual(shipping_fee(3000, 0, False), 8000)


class NoDrift(unittest.TestCase):
    def test_single_rounding_with_surcharge_then_express(self):
        # 8003 * 1.2 * 1.5 = 14405.4 -> 14405
        # ถ้าปัดหลังคิดระยะทางก่อน (9603.6 -> 9604) แล้วค่อย x1.5 จะได้ 14406 ซึ่งผิด
        self.assertEqual(shipping_fee(5002, 101, True), 14405)

    def test_half_satang_rounds_up_once(self):
        # 8001.5 -> 8002 (ไม่ใช่ 8001 แบบปัดลง)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_half_satang_after_surcharge(self):
        # 8001.5 * 1.2 = 9601.8 -> 9602
        self.assertEqual(shipping_fee(5001, 101, False), 9602)


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

    def test_weight_negative_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(-1, 10, False)

    def test_weight_above_max_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(30001, 10, False)

    def test_distance_negative_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, -0.1, False)

    def test_distance_str_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, "10", False)

    def test_distance_bool_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, True, False)

    def test_distance_nan_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, float("nan"), False)

    def test_distance_inf_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, float("inf"), False)

    def test_express_int_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, 10, 1)

    def test_express_str_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, 10, "yes")

    def test_invalid_weight_rejected_before_business_rule(self):
        # ค่าผิดต้อง raise ไม่ใช่ผ่านเข้าเงื่อนไขธุรกิจ
        with self.assertRaises(ValueError):
            shipping_fee(-5, 200, True)


if __name__ == "__main__":
    unittest.main()
