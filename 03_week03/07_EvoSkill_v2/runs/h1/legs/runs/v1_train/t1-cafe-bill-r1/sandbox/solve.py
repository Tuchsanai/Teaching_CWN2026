"""BaanKafe: คำนวณยอดที่ลูกค้าต้องจ่ายหน้าร้าน

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
ลำดับการคิด:
  1. ยอดรวม = sum(price * qty)
  2. ยอดรวม >= 50000 สตางค์ (500 บาท, รวมขอบ) -> ลด 5%
  3. member = True -> ลดอีก 10% (คูณต่อจากข้อ 2)
  4. บวก VAT 7% เป็นขั้นสุดท้าย
  5. ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้ายสุด (คำนวณด้วย Fraction ตลอด)
"""

from fractions import Fraction

_DISCOUNT_THRESHOLD = 50000  # 500 บาท เป็นสตางค์
_BULK_DISCOUNT = Fraction(95, 100)  # ลด 5%
_MEMBER_DISCOUNT = Fraction(90, 100)  # ลดอีก 10%
_VAT = Fraction(107, 100)  # บวก VAT 7%


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ int หรือ Fraction ที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def _require_int(value, label, lo=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    return value


def _subtotal(items):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    total = 0
    for i, item in enumerate(items):
        label = f"items[{i}]"
        if type(item) is not dict:
            raise ValueError(f"{label} ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"{label} ต้องมี field price และ qty")
        price = _require_int(item["price"], f"{label}.price", lo=0)
        qty = _require_int(item["qty"], f"{label}.qty", lo=1)
        total += price * qty
    return total


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์

    items: list ของ {"price": ราคาต่อชิ้น (สตางค์, int >= 0), "qty": จำนวนชิ้น (int >= 1)}
    member: bool, True ถ้าเป็นสมาชิก
    """
    subtotal = _subtotal(items)
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")

    amount = Fraction(subtotal)
    if subtotal >= _DISCOUNT_THRESHOLD:
        amount *= _BULK_DISCOUNT
    if member:
        amount *= _MEMBER_DISCOUNT
    amount *= _VAT
    return _half_up(amount)


if __name__ == "__main__":
    import unittest

    class CafeBillTests(unittest.TestCase):
        def test_small_bill_no_member(self):
            # 20000 * 1.07 = 21400
            self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

        def test_threshold_inclusive(self):
            # 50000 * 0.95 = 47500, * 1.07 = 50825
            self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

        def test_just_below_threshold(self):
            # 49999 * 1.07 = 53498.93 -> 53499
            self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

        def test_member_compounds_and_rounds_half_up(self):
            # 50000 * 0.95 * 0.90 = 42750, * 1.07 = 45742.5 -> 45743
            self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

        def test_multiple_items_member_below_threshold(self):
            # 1234*3 + 5 = 3707, * 0.9 = 3336.3, * 1.07 = 3569.541 -> 3570
            items = [{"price": 1234, "qty": 3}, {"price": 5, "qty": 1}]
            self.assertEqual(cafe_bill(items, True), 3570)

        def test_empty_items(self):
            self.assertEqual(cafe_bill([], False), 0)

        def test_result_is_int(self):
            self.assertIs(type(cafe_bill([{"price": 100, "qty": 1}], True)), int)

        def test_reject_bad_items(self):
            with self.assertRaises(ValueError):
                cafe_bill("x", False)
            with self.assertRaises(ValueError):
                cafe_bill([{"price": 100}], False)
            with self.assertRaises(ValueError):
                cafe_bill([{"price": 100.0, "qty": 1}], False)
            with self.assertRaises(ValueError):
                cafe_bill([{"price": "100", "qty": 1}], False)
            with self.assertRaises(ValueError):
                cafe_bill([{"price": True, "qty": 1}], False)
            with self.assertRaises(ValueError):
                cafe_bill([{"price": 100, "qty": 0}], False)
            with self.assertRaises(ValueError):
                cafe_bill([{"price": -1, "qty": 1}], False)

        def test_reject_bad_member(self):
            with self.assertRaises(ValueError):
                cafe_bill([], 1)
            with self.assertRaises(ValueError):
                cafe_bill([], "True")

    unittest.main()
