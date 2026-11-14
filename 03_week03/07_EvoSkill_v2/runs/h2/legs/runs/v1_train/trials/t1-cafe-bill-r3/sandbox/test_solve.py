"""ทดสอบ cafe_bill. รัน: python3 -m unittest -v test_solve

expected คำนวณด้วยสคริปต์ Fraction แล้ว (หน่วยสตางค์)
"""
import unittest

from solve import cafe_bill


class Normal(unittest.TestCase):
    def test_under_threshold_no_member(self):
        # 250 บาท -> 25000 * 1.07 = 26750
        self.assertEqual(cafe_bill([{"price": 6500, "qty": 2}, {"price": 12000, "qty": 1}], False), 26750)

    def test_over_threshold_no_member(self):
        # 600 บาท -> 60000 * 0.95 * 1.07 = 60990
        self.assertEqual(cafe_bill([{"price": 30000, "qty": 2}], False), 60990)

    def test_member_under_threshold(self):
        # 100 บาท สมาชิก -> 10000 * 0.9 * 1.07 = 9630
        self.assertEqual(cafe_bill([{"price": 5000, "qty": 2}], True), 9630)

    def test_member_over_threshold(self):
        # 1000 บาท สมาชิก -> 100000 * 0.95 * 0.9 * 1.07 = 91485
        self.assertEqual(cafe_bill([{"price": 100000, "qty": 1}], True), 91485)

    def test_multiple_items_sum(self):
        items = [{"price": 3500, "qty": 3}, {"price": 4500, "qty": 2}, {"price": 1000, "qty": 1}]
        # รวม 10500+9000+1000 = 20500 -> 20500 * 1.07 = 21935
        self.assertEqual(cafe_bill(items, False), 21935)

    def test_empty_cart(self):
        self.assertEqual(cafe_bill([], True), 0)


class Boundary(unittest.TestCase):
    def test_exactly_threshold_gets_discount(self):
        # 500 บาทพอดี ต้องได้ส่วนลด 5%: 50000 * 0.95 * 1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_one_satang_below_threshold_no_discount(self):
        # 49999 * 1.07 = 53498.93 -> ปัดครึ่งขึ้น 53499
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_one_satang_above_threshold(self):
        # 50001 * 0.95 * 1.07 = 50826.0165 -> 50826 (ไม่มีส่วนลดสมาชิก)
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], False), 50826)

    def test_zero_price_item(self):
        self.assertEqual(cafe_bill([{"price": 0, "qty": 5}], False), 0)

    def test_qty_one_minimum(self):
        self.assertEqual(cafe_bill([{"price": 4500, "qty": 1}], False), 4815)


class NoDrift(unittest.TestCase):
    def test_single_rounding_member_half(self):
        # 500 บาท สมาชิก -> 50000 * 0.95 * 0.9 * 1.07 = 45742.5 -> 45743
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_single_rounding_not_per_step(self):
        # 50001 สตางค์ สมาชิก -> 45743.41... -> 45743
        # ถ้าปัดทุกขั้น (หลัง 5% ปัดเป็น 47501, หลังสมาชิกปัดเป็น 42751, แล้ว VAT) จะได้ 45744 ซึ่งผิด
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], True), 45743)

    def test_member_below_threshold_rounds_down_fraction(self):
        # 49999 สมาชิก ไม่ถึงเกณฑ์ -> 49999*0.9*1.07 = 48149.037 -> 48149
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], True), 48149)


class Reject(unittest.TestCase):
    def test_items_not_list(self):
        with self.assertRaises(ValueError):
            cafe_bill(({"price": 100, "qty": 1},), False)

    def test_item_not_dict(self):
        with self.assertRaises(ValueError):
            cafe_bill([(100, 1)], False)

    def test_missing_key(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100}], False)

    def test_price_float(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500.0, "qty": 1}], False)

    def test_price_str(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": "4500", "qty": 1}], False)

    def test_price_bool(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": True, "qty": 1}], False)

    def test_negative_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": -1, "qty": 1}], False)

    def test_qty_zero(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 0}], False)

    def test_qty_float(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 1.0}], False)

    def test_member_not_bool(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 1}], 1)

    def test_member_str(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 1}], "yes")


if __name__ == "__main__":
    unittest.main()
