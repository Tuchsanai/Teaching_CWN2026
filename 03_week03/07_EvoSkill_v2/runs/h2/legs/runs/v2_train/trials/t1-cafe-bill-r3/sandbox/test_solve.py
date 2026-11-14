"""ชุดทดสอบ cafe_bill แยกหมวด Normal, Boundary, NoDrift, Reject

รัน: python3 -m unittest -v test_solve
expected ทุกค่าคำนวณด้วยสคริปต์ Fraction แล้ว (ไม่ได้คำนวณในใจ)
"""
import unittest

from solve import cafe_bill


def item(price, qty=1):
    return {"price": price, "qty": qty}


class Normal(unittest.TestCase):
    def test_basic_under_threshold(self):
        # 385 บาท: 38500 * 1.07 = 41195
        items = [item(6500, 2), item(4500, 3), item(3000, 4)]
        self.assertEqual(cafe_bill(items, False), 41195)

    def test_basic_under_threshold_member(self):
        # 38500 * 0.9 * 1.07 = 37076 (ค่าเต็ม 37075.5 ปัดครึ่งขึ้น)
        items = [item(6500, 2), item(4500, 3), item(3000, 4)]
        self.assertEqual(cafe_bill(items, True), 37076)

    def test_over_threshold_flags(self):
        # 60000 * 0.95 * 1.07 = 60990
        self.assertEqual(cafe_bill([item(30000, 2)], False), 60990)
        # 60000 * 0.95 * 0.9 * 1.07 = 54891
        self.assertEqual(cafe_bill([item(30000, 2)], True), 54891)

    def test_flag_combinations_small_order(self):
        # 1000 * 1.07 = 1070 (ไม่ลด)
        self.assertEqual(cafe_bill([item(1000)], False), 1070)
        # 1000 * 0.9 * 1.07 = 963 (สมาชิกลด 10% เท่านั้น)
        self.assertEqual(cafe_bill([item(1000)], True), 963)

    def test_multiple_lines_summed_before_discount(self):
        # 3 รายการ รวม 60000 -> ได้ส่วนลดเกณฑ์ 500 บาท
        items = [item(20000), item(20000), item(20000)]
        self.assertEqual(cafe_bill(items, False), 60990)


class Boundary(unittest.TestCase):
    def test_exactly_500_baht_gets_discount(self):
        # 50000 * 0.95 * 1.07 = 50825 (ตั้งแต่ 500 ขึ้นไป = ลด)
        self.assertEqual(cafe_bill([item(25000, 2)], False), 50825)

    def test_exactly_500_baht_member(self):
        # 50000 * 0.95 * 0.9 * 1.07 = 45742.5 -> ปัดครึ่งขึ้น = 45743
        self.assertEqual(cafe_bill([item(50000)], True), 45743)

    def test_one_satang_below_threshold_no_discount(self):
        # 49999 * 1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill([item(49999)], False), 53499)

    def test_one_satang_below_threshold_member(self):
        # 49999 * 0.9 * 1.07 = 48149.037 -> 48149
        self.assertEqual(cafe_bill([item(49999)], True), 48149)

    def test_zero_empty_cart(self):
        self.assertEqual(cafe_bill([], False), 0)
        self.assertEqual(cafe_bill([], True), 0)

    def test_zero_price_item(self):
        self.assertEqual(cafe_bill([item(0, 5)], True), 0)

    def test_qty_one_is_minimum(self):
        # qty=1 ใช้ได้: 1 ชิ้นราคา 100 สตางค์ * 1.07 = 107
        self.assertEqual(cafe_bill([item(100, 1)], False), 107)


class NoDrift(unittest.TestCase):
    def test_single_final_rounding(self):
        # 50001 * 0.95 * 0.9 * 1.07 = 45743.41... -> 45743
        # ถ้าปัดทุกขั้น จะได้ 45744 ซึ่งผิด
        self.assertEqual(cafe_bill([item(50001)], True), 45743)

    def test_discounts_compound_not_additive(self):
        # คูณต่อกัน: 50001 * 0.95 * 0.9 * 1.07 -> 45743
        # ถ้าบวกเปอร์เซ็นต์รวม (ลด 15%): 50001 * 0.85 * 1.07 = 45475.9... -> 45476 (ผิดตามโจทย์)
        self.assertEqual(cafe_bill([item(50001)], True), 45743)
        self.assertNotEqual(cafe_bill([item(50001)], True), 45476)


class Reject(unittest.TestCase):
    def test_items_must_be_list(self):
        with self.assertRaises(ValueError):
            cafe_bill((item(1000),), False)

    def test_item_must_be_dict(self):
        with self.assertRaises(ValueError):
            cafe_bill([(1000, 1)], False)

    def test_item_missing_key(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 1000}], False)
        with self.assertRaises(ValueError):
            cafe_bill([{"qty": 1}], False)

    def test_price_bool_is_not_int(self):
        with self.assertRaises(ValueError):
            cafe_bill([item(True)], False)

    def test_price_float_is_not_int(self):
        with self.assertRaises(ValueError):
            cafe_bill([item(4500.0)], False)

    def test_price_string_is_not_int(self):
        with self.assertRaises(ValueError):
            cafe_bill([item("4500")], False)

    def test_negative_price_raises_even_below_threshold(self):
        # ต้อง raise ไม่ใช่คืน 0 หรือยอดอื่นเงียบ ๆ
        with self.assertRaises(ValueError):
            cafe_bill([item(-1)], False)

    def test_qty_zero_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([item(1000, 0)], False)

    def test_qty_negative_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([item(1000, -1)], False)

    def test_qty_float_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([item(1000, 2.0)], False)

    def test_member_must_be_bool(self):
        with self.assertRaises(ValueError):
            cafe_bill([item(1000)], 1)
        with self.assertRaises(ValueError):
            cafe_bill([item(1000)], "yes")
        with self.assertRaises(ValueError):
            cafe_bill([item(1000)], None)


if __name__ == "__main__":
    unittest.main()
