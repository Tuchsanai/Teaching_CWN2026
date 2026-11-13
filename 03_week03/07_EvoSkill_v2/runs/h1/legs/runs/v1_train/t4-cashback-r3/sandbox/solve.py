"""คำนวณเงินคืนสมาชิกของร้าน BaanKafe

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม) และปัดครึ่งขึ้นครั้งเดียวตอนท้าย
"""

from fractions import Fraction

# อัตราเงินคืนเป็นเปอร์เซ็นต์ เก็บเป็น Fraction เพื่อไม่ให้มี float
_RATE_PERCENT = {
    "silver": Fraction(3, 2),    # 1.5%
    "gold": Fraction(5, 2),      # 2.5%
    "platinum": Fraction(4, 1),  # 4%
}

_MIN_AMOUNT = 100 * 100          # ยอดซื้อขั้นต่ำ 100 บาท = 10000 สตางค์
_BIRTHDAY_MULTIPLIER = 2         # เดือนเกิดได้ 2 เท่า
_CAP = 200 * 100                 # เพดานเงินคืนต่อบิล 200 บาท = 20000 สตางค์


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ Fraction ที่ไม่ติดลบ"""
    return int((x * 2 + 1) // 2)


def cashback(amount, tier, birthday):
    """คืนจำนวนเงินคืนเป็นสตางค์ (int)

    amount   : ยอดซื้อเป็นสตางค์ จำนวนเต็มตั้งแต่ 0
    tier     : "silver", "gold" หรือ "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด
    """
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if type(tier) is not str or tier not in _RATE_PERCENT:
        raise ValueError('tier ต้องเป็น "silver", "gold" หรือ "platinum"')
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    # ยอดต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if amount < _MIN_AMOUNT:
        return 0

    value = Fraction(amount) * _RATE_PERCENT[tier] / 100
    if birthday:
        value *= _BIRTHDAY_MULTIPLIER

    # ปัดครั้งเดียวตอนท้าย แล้วค่อยใช้เพดาน
    return min(_half_up(value), _CAP)


if __name__ == "__main__":
    import unittest

    class CashbackTests(unittest.TestCase):
        def test_below_minimum_is_zero(self):
            self.assertEqual(cashback(9999, "gold", True), 0)
            self.assertEqual(cashback(0, "platinum", False), 0)

        def test_minimum_boundary_qualifies(self):
            # 10000 * 1.5% = 150
            self.assertEqual(cashback(10000, "silver", False), 150)

        def test_rates(self):
            self.assertEqual(cashback(10000, "gold", False), 250)
            self.assertEqual(cashback(10000, "platinum", False), 400)

        def test_birthday_doubles(self):
            self.assertEqual(cashback(10000, "gold", True), 500)
            self.assertEqual(cashback(10000, "platinum", True), 800)

        def test_cap(self):
            self.assertEqual(cashback(1000000, "platinum", False), 20000)
            # 4% ของ 1,000,000 = 40000 ก่อนเพดาน
            # เดือนเกิด gold: 2.5% * 2 = 5% ของ 400000 = 20000 พอดีเพดาน
            self.assertEqual(cashback(400000, "gold", True), 20000)
            self.assertEqual(cashback(400000, "gold", False), 10000)

        def test_half_up_rounding(self):
            # 10300 * 1.5% = 154.5 -> ปัดขึ้นเป็น 155 (banker's rounding จะได้ 154)
            self.assertEqual(cashback(10300, "silver", False), 155)
            # 10100 * 1.5% = 151.5 -> 152
            self.assertEqual(cashback(10100, "silver", False), 152)

        def test_rounding_before_birthday_not_applied(self):
            # 10300 * 1.5% = 154.5, เดือนเกิด x2 = 309 พอดี ไม่มีการปัดระหว่างทาง
            self.assertEqual(cashback(10300, "silver", True), 309)

        def test_rejects_bad_amount(self):
            for bad in (10000.0, "10000", True, -1, None):
                with self.subTest(amount=bad):
                    with self.assertRaises(ValueError):
                        cashback(bad, "gold", False)

        def test_rejects_bad_tier(self):
            for bad in ("Gold", "bronze", "", None, 1):
                with self.subTest(tier=bad):
                    with self.assertRaises(ValueError):
                        cashback(10000, bad, False)

        def test_rejects_bad_birthday(self):
            for bad in (1, 0, "True", None):
                with self.subTest(birthday=bad):
                    with self.assertRaises(ValueError):
                        cashback(10000, "gold", bad)

        def test_returns_int(self):
            self.assertIs(type(cashback(10300, "silver", True)), int)

    unittest.main()
