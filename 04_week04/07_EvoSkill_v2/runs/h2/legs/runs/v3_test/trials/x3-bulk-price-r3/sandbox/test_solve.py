"""ทดสอบ bulk_price แยกหมวด Normal, Boundary, NoDrift, Reject
expected ทุกค่าคำนวณด้วยสคริปต์ Fraction (ดู skills/solver-selftest-workflow/SKILL.md)
รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_no_discount_no_coupon(self):
        # 20000 * 1 * 1.07 = 21400
        self.assertEqual(bulk_price(20000, 1, False), 21400)

    def test_tier_10_no_coupon(self):
        # 20000 * 10 * 0.965 * 1.07 = 206510
        self.assertEqual(bulk_price(20000, 10, False), 206510)

    def test_tier_50_with_coupon(self):
        # 20000 * 50 * 0.925 * 0.975 * 1.07 = 3860025/4 = 965006.25 -> 965006
        self.assertEqual(bulk_price(20000, 50, True), 965006)

    def test_flag_combinations(self):
        # coupon เฉพาะ qty ต่ำกว่า 10 ก็ต้องลด 2.5%
        # 20000 * 1 * 0.975 * 1.07 = 20865
        self.assertEqual(bulk_price(20000, 1, True), 20865)
        # 20000 * 9 * 0.975 * 1.07 = 187785
        self.assertEqual(bulk_price(20000, 9, True), 187785)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)


class Boundary(unittest.TestCase):
    def test_at_tier_10(self):
        # qty = 10 ได้ลด 3.5% (ตั้งแต่ 10 ขึ้นไป)
        # 20000 * 10 * 0.965 * 1.07 = 206510
        self.assertEqual(bulk_price(20000, 10, False), 206510)

    def test_just_below_tier_10(self):
        # qty = 9 ไม่ลด: 20000 * 9 * 1.07 = 192600
        self.assertEqual(bulk_price(20000, 9, False), 192600)

    def test_at_tier_50(self):
        # qty = 50 ได้ลด 7.5%: 20000 * 50 * 0.925 * 1.07 = 989750
        self.assertEqual(bulk_price(20000, 50, False), 989750)

    def test_just_below_tier_50(self):
        # qty = 49 ได้ลดแค่ 3.5%: 20000 * 49 * 0.965 * 1.07 = 1011899
        self.assertEqual(bulk_price(20000, 49, False), 1011899)

    def test_zero_and_max(self):
        self.assertEqual(bulk_price(1, 1, False), 1)  # 1 * 1.07 = 1.07 -> 1
        # max qty = 1000, coupon: 20000 * 1000 * 0.925 * 0.975 * 1.07 = 19300125
        self.assertEqual(bulk_price(20000, 1000, True), 19300125)


class NoDrift(unittest.TestCase):
    def test_single_rounding_differs_from_stepwise(self):
        # 1000 * 10 * 0.965 * 0.975 * 1.07 = 805389/80 = 10067.3625... -> 10067
        # ถ้าปัดทุกขั้นจะได้ 10068 (ผิด)
        self.assertEqual(bulk_price(1000, 10, True), 10067)

    def test_exact_half_rounds_up(self):
        # 120 * 50 * 0.925 * 1.07 = 11877/2 = 5938.5 -> ปัดครึ่งขึ้น = 5939
        self.assertEqual(bulk_price(120, 50, False), 5939)

    def test_near_half_rounds_down(self):
        # 149 * 10 * 0.965 * 1.07 = 3076999/2000 = 1538.4995 -> 1538
        self.assertEqual(bulk_price(149, 10, False), 1538)


class Reject(unittest.TestCase):
    def test_bool_price_rejected(self):
        with self.assertRaises(ValueError):
            bulk_price(True, 10, False)

    def test_float_price_rejected(self):
        with self.assertRaises(ValueError):
            bulk_price(4500.0, 10, False)

    def test_string_price_rejected(self):
        with self.assertRaises(ValueError):
            bulk_price("4500", 10, False)

    def test_negative_price_rejected(self):
        # ต้อง raise ไม่ใช่คืน 0 เงียบ ๆ
        with self.assertRaises(ValueError):
            bulk_price(-1, 10, False)

    def test_qty_zero_rejected(self):
        with self.assertRaises(ValueError):
            bulk_price(20000, 0, False)

    def test_qty_over_max_rejected(self):
        with self.assertRaises(ValueError):
            bulk_price(20000, 1001, False)

    def test_qty_bool_rejected(self):
        with self.assertRaises(ValueError):
            bulk_price(20000, True, False)

    def test_qty_float_rejected(self):
        with self.assertRaises(ValueError):
            bulk_price(20000, 10.0, False)

    def test_coupon_not_bool_rejected(self):
        with self.assertRaises(ValueError):
            bulk_price(20000, 10, 1)
        with self.assertRaises(ValueError):
            bulk_price(20000, 10, "yes")


if __name__ == "__main__":
    unittest.main()
