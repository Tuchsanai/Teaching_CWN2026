import unittest

from solve import cafe_bill


def one(price, qty=1):
    return [{"price": price, "qty": qty}]


class Normal(unittest.TestCase):
    def test_bulk_discount_no_member(self):
        # 50,000 -> ลด 5% = 47,500 -> VAT 7% = 50,825
        self.assertEqual(cafe_bill(one(50_000), False), 50_825)

    def test_bulk_and_member(self):
        # 50,000 -> ลด 5% -> ลด 10% = 42,750 -> VAT 7% = 45,742.5 -> ปัดครึ่งขึ้น 45,743
        self.assertEqual(cafe_bill(one(50_000), True), 45_743)

    def test_below_threshold_member_only(self):
        # 30,000 -> ไม่ลด 5% -> ลด 10% = 27,000 -> VAT 7% = 28,890
        self.assertEqual(cafe_bill(one(30_000), True), 28_890)

    def test_below_threshold_no_member(self):
        # 20,000 -> VAT 7% = 21,400
        self.assertEqual(cafe_bill(one(20_000), False), 21_400)

    def test_multiple_items_sum(self):
        items = [{"price": 15_000, "qty": 2}, {"price": 9_000, "qty": 2}]  # 48,000
        self.assertEqual(cafe_bill(items, False), 51_360)  # 48,000*1.07 = 51,360

    def test_empty_items(self):
        self.assertEqual(cafe_bill([], False), 0)


class Boundary(unittest.TestCase):
    def test_at_threshold_gets_discount(self):
        # 50,000 พอดี ลด 5% (ตั้งแต่ 500 บาทขึ้นไป)
        self.assertEqual(cafe_bill(one(50_000), False), 50_825)

    def test_just_below_threshold_no_discount(self):
        # 49,999 ไม่ลด: 49,999 * 1.07 = 53,498.93 -> 53,499
        self.assertEqual(cafe_bill(one(49_999), False), 53_499)

    def test_just_above_threshold(self):
        # 50,001 ลด 5%: 47,500.95 * 1.07 = 50,826.0165 -> 50,826
        self.assertEqual(cafe_bill(one(50_001), False), 50_826)

    def test_zero_total(self):
        self.assertEqual(cafe_bill(one(0), True), 0)

    def test_qty_one_minimum(self):
        self.assertEqual(cafe_bill(one(100, 1), False), 107)


class NoDrift(unittest.TestCase):
    def test_single_rounding_at_end(self):
        # 49,999 + สมาชิก: 49,999*0.9*1.07 = 48,149.037 -> 48,149
        self.assertEqual(cafe_bill(one(49_999), True), 48_149)

    def test_half_up_exact_point_five(self):
        # 12,345 + สมาชิก: 12,345*0.9*1.07 = 11,888.235 -> 11,888 (ไม่ได้ปัดลงก่อนคูณ)
        self.assertEqual(cafe_bill(one(12_345), True), 11_888)

    def test_bulk_then_member_order_matters_not_for_result(self):
        # ค่าทั้งสองลำดับคูณได้ผลเท่ากัน เพราะไม่มีการปัดระหว่างทาง
        # 100,000 + สมาชิก: 100,000*0.95*0.9*1.07 = 91,485
        self.assertEqual(cafe_bill(one(100_000), True), 91_485)


class Reject(unittest.TestCase):
    def test_member_must_be_bool(self):
        with self.assertRaises(ValueError):
            cafe_bill(one(4500), 1)
        with self.assertRaises(ValueError):
            cafe_bill(one(4500), "yes")

    def test_items_must_be_list(self):
        with self.assertRaises(ValueError):
            cafe_bill(({"price": 4500, "qty": 1},), False)

    def test_item_must_be_dict(self):
        with self.assertRaises(ValueError):
            cafe_bill([(4500, 1)], False)

    def test_missing_key(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500}], False)

    def test_extra_key(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500, "qty": 1, "name": "latte"}], False)

    def test_price_float_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500.0, "qty": 1}], False)

    def test_price_bool_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": True, "qty": 1}], False)

    def test_price_string_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": "4500", "qty": 1}], False)

    def test_negative_price_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": -1, "qty": 1}], False)

    def test_qty_zero_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500, "qty": 0}], False)

    def test_qty_float_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500, "qty": 2.0}], False)

    def test_qty_string_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500, "qty": "2"}], False)


if __name__ == "__main__":
    unittest.main()
