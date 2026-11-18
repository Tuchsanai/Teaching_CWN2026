"""ชุดทดสอบ shipping_fee. expected คำนวณด้วยสคริปต์ Fraction แล้ว (หน่วยสตางค์)

รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_basic_tiers(self):
        self.assertEqual(shipping_fee(500, 50, False), 4000)    # 40 บาท
        self.assertEqual(shipping_fee(3000, 50, False), 8000)   # 80 บาท
        self.assertEqual(shipping_fee(6000, 50, False), 9500)   # 80 + 1 กก. * 15
        self.assertEqual(shipping_fee(30000, 50, False), 45500) # 80 + 25 กก. * 15

    def test_flag_combinations(self):
        self.assertEqual(shipping_fee(500, 50, True), 6000)     # ด่วน 40 * 1.5
        self.assertEqual(shipping_fee(6000, 150, True), 17100)  # 9500 * 1.2 * 1.5
        self.assertEqual(shipping_fee(6000, 150, False), 11400) # 9500 * 1.2
        self.assertEqual(shipping_fee(1000, 0, True), 6000)     # ระยะทาง 0 ได้

    def test_float_distance_accepted(self):
        self.assertEqual(shipping_fee(500, 100.5, False), 4800) # 40 * 1.2


class Boundary(unittest.TestCase):
    def test_weight_at_1000(self):
        self.assertEqual(shipping_fee(1000, 50, False), 4000)   # พอดี 1,000 ยังอยู่ขั้น 40 บาท
        self.assertEqual(shipping_fee(1001, 50, False), 8000)   # เกิน 1,000 เป็นขั้น 80 บาท

    def test_weight_at_5000(self):
        self.assertEqual(shipping_fee(5000, 50, False), 8000)   # พอดี 5,000 ยังเป็น 80 บาท
        self.assertEqual(shipping_fee(5001, 50, False), 8002)   # 8001.5 ปัดครึ่งขึ้น

    def test_distance_at_100(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)   # 100 พอดีไม่คิดเพิ่ม
        self.assertEqual(shipping_fee(500, 100.01, False), 4800)

    def test_zero_and_max(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)       # ต่ำสุดของช่วง
        self.assertEqual(shipping_fee(30000, 0, True), 68250)   # 45500 * 1.5


class NoDrift(unittest.TestCase):
    def test_single_rounding(self):
        # exact = 8001.5 * 1.2 * 1.5 = 14402.7 -> 14403
        # ถ้าปัดกลางทาง (8002 -> 9602.4 -> 14403.6) จะได้ 14404 ซึ่งผิด
        self.assertEqual(shipping_fee(5001, 101, True), 14403)

    def test_rounding_without_express(self):
        # exact = 8001.5 * 1.2 = 9601.8 -> 9602
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
            shipping_fee("2000", 10, False)

    def test_weight_out_of_range(self):
        with self.assertRaises(ValueError):
            shipping_fee(0, 10, False)
        with self.assertRaises(ValueError):
            shipping_fee(-1, 10, False)
        with self.assertRaises(ValueError):
            shipping_fee(30001, 10, False)

    def test_distance_negative_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, -0.1, False)

    def test_distance_bool_and_str_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, True, False)
        with self.assertRaises(ValueError):
            shipping_fee(500, "10", False)

    def test_distance_nan_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, float("nan"), False)

    def test_express_must_be_bool(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, 10, 1)
        with self.assertRaises(ValueError):
            shipping_fee(500, 10, "yes")
        with self.assertRaises(ValueError):
            shipping_fee(500, 10, None)


if __name__ == "__main__":
    unittest.main()
