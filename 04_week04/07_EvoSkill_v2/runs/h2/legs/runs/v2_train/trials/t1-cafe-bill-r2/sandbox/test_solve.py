"""ทดสอบ cafe_bill แยกหมวด Normal, Boundary, NoDrift, Reject
expected ทุกค่าคำนวณด้วย fractions.Fraction แล้ว (ดูคอมเมนต์แต่ละเคส)
รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import cafe_bill


class Normal(unittest.TestCase):
    def test_single_item_no_discount_no_member(self):
        # 600 บาท >= 500 ลด 5%: 60000*0.95*1.07 = 60990
        self.assertEqual(cafe_bill([{"price": 60000, "qty": 1}], False), 60990)

    def test_single_item_with_member(self):
        # 60000*0.95*0.9*1.07 = 54891
        self.assertEqual(cafe_bill([{"price": 60000, "qty": 1}], True), 54891)

    def test_below_threshold_no_member(self):
        # 400 บาท < 500 ไม่ลด: 40000*1.07 = 42800
        self.assertEqual(cafe_bill([{"price": 40000, "qty": 1}], False), 42800)

    def test_below_threshold_with_member(self):
        # 40000*0.9*1.07 = 38520 (สมาชิกลด 10% แม้ยอดต่ำกว่า 500)
        self.assertEqual(cafe_bill([{"price": 40000, "qty": 1}], True), 38520)

    def test_multiple_items_sum_before_discount(self):
        # 12500*3 + 9900*2 = 57300 >= 50000 ลด 5%; ไม่สมาชิก: 57300*0.95*1.07 = 58245.45 -> 58245
        items = [{"price": 12500, "qty": 3}, {"price": 9900, "qty": 2}]
        self.assertEqual(cafe_bill(items, False), 58245)

    def test_multiple_items_with_member(self):
        # 57300*0.95*0.9*1.07 = 52420.905 -> 52421
        items = [{"price": 12500, "qty": 3}, {"price": 9900, "qty": 2}]
        self.assertEqual(cafe_bill(items, True), 52421)

    def test_empty_cart_is_zero(self):
        self.assertEqual(cafe_bill([], False), 0)
        self.assertEqual(cafe_bill([], True), 0)


class Boundary(unittest.TestCase):
    def test_at_threshold_gets_discount(self):
        # 50000 พอดี (500 บาท) ต้องลด (>=): 50000*0.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_just_below_threshold_no_discount(self):
        # 49999 ไม่ลด: 49999*1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_zero_price_item(self):
        # ราคา 0 เป็นค่าขอบที่ยอมรับได้: 0
        self.assertEqual(cafe_bill([{"price": 0, "qty": 5}], True), 0)

    def test_qty_one_is_minimum(self):
        # qty = 1 ต้องรับได้: 1000*1.07 = 1070
        self.assertEqual(cafe_bill([{"price": 1000, "qty": 1}], False), 1070)


class NoDrift(unittest.TestCase):
    def test_single_rounding_exact_half_rounds_up(self):
        # 50000*0.95*0.9*1.07 = 45742.5 -> ปัดครึ่งขึ้น 45743
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_single_rounding_not_per_step(self):
        # 50001*0.95*0.9*1.07 = 45743.41485 -> 45743
        # ถ้าปัดทุกขั้นจะได้ 45744 (ยอดเบี่ยง 1 สตางค์)
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], True), 45743)


class Reject(unittest.TestCase):
    def test_bool_price_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": True, "qty": 1}], False)

    def test_float_price_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500.0, "qty": 1}], False)

    def test_string_price_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": "4500", "qty": 1}], False)

    def test_negative_price_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": -1, "qty": 1}], False)

    def test_qty_zero_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500, "qty": 0}], False)

    def test_float_qty_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500, "qty": 2.0}], False)

    def test_member_must_be_bool(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500, "qty": 1}], 1)
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500, "qty": 1}], "yes")

    def test_items_must_be_list(self):
        with self.assertRaises(ValueError):
            cafe_bill({"price": 4500, "qty": 1}, False)

    def test_item_must_be_dict(self):
        with self.assertRaises(ValueError):
            cafe_bill([(4500, 1)], False)

    def test_missing_key_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500}], False)
        with self.assertRaises(ValueError):
            cafe_bill([{"qty": 1}], False)


if __name__ == "__main__":
    unittest.main()
