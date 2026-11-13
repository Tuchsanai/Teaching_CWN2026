"""BaanKafe cashback calculator.

cashback(amount, tier, birthday) -> int (satang)

- amount   : ยอดซื้อเป็นสตางค์ (int, >= 0)
- tier     : "silver" | "gold" | "platinum"
- birthday : True = ซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)

กฎ:
1. ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) ไม่ได้เงินคืน
2. อัตรา: silver 1.5%, gold 2.5%, platinum 4%
3. เดือนเกิดได้ 2 เท่า
4. เพดานเงินคืน 200 บาท (20000 สตางค์) ต่อบิล ใช้หลังคูณเดือนเกิดแล้ว
5. คำนวณด้วย Fraction ปัดครึ่งขึ้นครั้งเดียวตอนท้าย ได้จำนวนเต็มสตางค์
"""

from fractions import Fraction

MIN_AMOUNT = 10000        # 100 บาท
CAP = 20000               # 200 บาท ต่อบิล
RATES = {
    "silver": Fraction(3, 200),    # 1.5%
    "gold": Fraction(1, 40),       # 2.5%
    "platinum": Fraction(1, 25),   # 4%
}


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม ไม่ติดลบ รับ int หรือ Fraction"""
    return int((Fraction(x) * 2 + 1) // 2)


def cashback(amount, tier, birthday):
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if type(tier) is not str or tier not in RATES:
        raise ValueError('tier ต้องเป็น "silver", "gold" หรือ "platinum"')
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    if amount < MIN_AMOUNT:
        return 0

    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= 2
    value = min(value, CAP)
    return _half_up(value)


if __name__ == "__main__":
    import sys
    import unittest

    class CashbackTests(unittest.TestCase):
        # ค่าที่คำนวณมือไว้ก่อน (สตางค์)
        def test_below_minimum_gets_nothing(self):
            self.assertEqual(cashback(9999, "silver", False), 0)
            self.assertEqual(cashback(9999, "platinum", True), 0)
            self.assertEqual(cashback(0, "gold", True), 0)

        def test_minimum_boundary_qualifies(self):
            self.assertEqual(cashback(10000, "silver", False), 150)   # 100*1.5%
            self.assertEqual(cashback(10000, "gold", False), 250)     # 100*2.5%
            self.assertEqual(cashback(10000, "platinum", False), 400)  # 100*4%

        def test_birthday_doubles(self):
            self.assertEqual(cashback(10000, "silver", True), 300)
            self.assertEqual(cashback(10000, "platinum", True), 800)

        def test_cap_exact_and_over(self):
            self.assertEqual(cashback(500000, "platinum", False), 20000)  # พอดีเพดาน
            self.assertEqual(cashback(600000, "platinum", False), 20000)  # เกินเพดาน
            self.assertEqual(cashback(1000000, "gold", False), 20000)     # 25000 -> 20000
            self.assertEqual(cashback(1000000, "silver", True), 20000)    # 30000 -> 20000

        def test_half_up_once(self):
            # gold: 10020 * 2.5% = 250.5 -> 251 (banker's rounding would give 250)
            self.assertEqual(cashback(10020, "gold", False), 251)
            # silver: 10100 * 1.5% = 151.5 -> 152
            self.assertEqual(cashback(10100, "silver", False), 152)

        def test_rejects_bad_types(self):
            with self.assertRaises(ValueError):
                cashback(10000.0, "silver", False)
            with self.assertRaises(ValueError):
                cashback("10000", "silver", False)
            with self.assertRaises(ValueError):
                cashback(True, "silver", False)
            with self.assertRaises(ValueError):
                cashback(10000, "silver", 1)

        def test_rejects_bad_values(self):
            with self.assertRaises(ValueError):
                cashback(-1, "silver", False)
            with self.assertRaises(ValueError):
                cashback(10000, "Gold", False)
            with self.assertRaises(ValueError):
                cashback(10000, "bronze", False)

        def test_returns_int(self):
            self.assertIs(type(cashback(10020, "gold", False)), int)

    unittest.main(argv=[sys.argv[0]], exit=True, verbosity=2)
