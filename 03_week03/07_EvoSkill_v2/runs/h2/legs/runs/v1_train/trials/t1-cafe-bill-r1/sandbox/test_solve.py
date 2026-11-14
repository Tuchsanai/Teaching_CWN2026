"""ทดสอบ cafe_bill. expected คำนวณด้วยสคริปต์ Fraction แล้ว (ดูค่าในคอมเมนต์)"""
import unittest

from solve import cafe_bill


def one(price, qty=1):
    return [{"price": price, "qty": qty}]


class Normal(unittest.TestCase):
    def test_discount_no_member(self):
        # 60000 * 0.95 * 1.07 = 60990
        self.assertEqual(cafe_bill(one(20000, 3), False), 60990)

    def test_discount_and_member(self):
        # 60000 * 0.95 * 0.90 * 1.07 = 54891
        self.assertEqual(cafe_bill(one(20000, 3), True), 54891)

    def test_member_below_threshold(self):
        # 49999 * 0.90 * 1.07 = 48149.037 -> 48149
        self.assertEqual(cafe_bill(one(49999), True), 48149)

    def test_multiple_items_sum(self):
        items = [{"price": 15000, "qty": 2}, {"price": 7000, "qty": 3}]  # 30000+21000=51000
        # 51000 * 0.95 * 1.07 = 51841.5 -> 51842 (ปัดครึ่งขึ้น)
        self.assertEqual(cafe_bill(items, False), 51842)

    def test_empty_items(self):
        self.assertEqual(cafe_bill([], False), 0)
        self.assertEqual(cafe_bill([], True), 0)


class Boundary(unittest.TestCase):
    def test_at_threshold_gets_discount(self):
        # 50000 * 0.95 * 1.07 = 50825 (ลดเพราะ >= 500 บาท)
        self.assertEqual(cafe_bill(one(50000), False), 50825)

    def test_just_below_threshold_no_discount(self):
        # 49999 * 1.07 = 53498.93 -> 53499 (ไม่ลด)
        self.assertEqual(cafe_bill(one(49999), False), 53499)

    def test_zero_price_and_zero_qty_threshold(self):
        self.assertEqual(cafe_bill(one(0, 5), True), 0)

    def test_qty_one_is_minimum(self):
        # 1 * 1.07 = 1.07 -> 1
        self.assertEqual(cafe_bill(one(1, 1), False), 1)


class NoDrift(unittest.TestCase):
    def test_single_rounding_differs_from_stepwise(self):
        # 50010 * 0.95 * 1.07 = 50835.165 -> 50835
        # (ปัดทุกขั้นจะได้ 50836 ซึ่งผิด)
        self.assertEqual(cafe_bill(one(50010), False), 50835)

    def test_half_up_at_exact_half(self):
        # 50000 * 0.95 * 0.90 * 1.07 = 45742.5 -> 45743 (ปัดครึ่งขึ้น)
        self.assertEqual(cafe_bill(one(50000), True), 45743)


class Reject(unittest.TestCase):
    def test_member_must_be_bool(self):
        with self.assertRaises(ValueError):
            cafe_bill(one(1000), 1)
        with self.assertRaises(ValueError):
            cafe_bill(one(1000), "yes")

    def test_items_must_be_list(self):
        with self.assertRaises(ValueError):
            cafe_bill(("price",), False)

    def test_item_must_be_dict(self):
        with self.assertRaises(ValueError):
            cafe_bill([(1000, 1)], False)

    def test_missing_key(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 1000}], False)
        with self.assertRaises(ValueError):
            cafe_bill([{"qty": 1}], False)

    def test_price_float_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500.0, "qty": 1}], False)

    def test_price_bool_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": True, "qty": 1}], False)

    def test_price_negative_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": -1, "qty": 1}], False)

    def test_qty_zero_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 1000, "qty": 0}], False)

    def test_qty_string_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 1000, "qty": "2"}], False)

    def test_qty_float_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 1000, "qty": 2.0}], False)


if __name__ == "__main__":
    unittest.main()
