"""BaanKafe: คิดเงินคืนสมาชิกต่อบิล (หน่วยเป็นสตางค์ทั้งหมด)"""

from fractions import Fraction

MIN_AMOUNT = 10000  # 100 บาท ต้องถึงเกณฑ์นี้จึงได้เงินคืน
CAP = 20000         # เพดาน 200 บาทต่อบิล
RATES = {
    "silver": Fraction(15, 1000),   # 1.5%
    "gold": Fraction(25, 1000),     # 2.5%
    "platinum": Fraction(40, 1000), # 4%
}


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ Fraction ที่ไม่ติดลบ"""
    return int((x * 2 + 1) // 2)


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนเป็นจำนวนเต็มสตางค์

    amount   : ยอดซื้อ (สตางค์ int ตั้งแต่ 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (ได้ 2 เท่า)
    """
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    if amount < MIN_AMOUNT:
        return 0

    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= 2
    # เพดานเป็นจำนวนเต็ม จึงปัดก่อนหรือหลังเพดานได้ผลเท่ากัน
    return min(_half_up(value), CAP)


if __name__ == "__main__":
    import unittest

    class CashbackTests(unittest.TestCase):
        def test_below_threshold_is_zero(self):
            self.assertEqual(cashback(9999, "platinum", True), 0)
            self.assertEqual(cashback(0, "gold", False), 0)

        def test_threshold_inclusive(self):
            self.assertEqual(cashback(10000, "silver", False), 150)   # 1.5 บาท
            self.assertEqual(cashback(10000, "gold", False), 250)
            self.assertEqual(cashback(10000, "platinum", False), 400)

        def test_half_up_rounding(self):
            # 10100 * 1.5% = 151.5 สตางค์ -> 152 (banker's rounding จะได้ 152 เช่นกัน)
            self.assertEqual(cashback(10100, "silver", False), 152)
            # 10300 * 1.5% = 154.5 สตางค์ -> 155 (banker's rounding จะได้ 154)
            self.assertEqual(cashback(10300, "silver", False), 155)

        def test_rounding_down_below_half(self):
            # 12345 * 1.5% = 185.175 -> 185
            self.assertEqual(cashback(12345, "silver", False), 185)

        def test_birthday_doubles_before_cap(self):
            # 5000 บาท * 2.5% = 12500 สตางค์ *2 = 25000 -> เพดาน 20000
            self.assertEqual(cashback(500000, "gold", True), 20000)
            # 1000 บาท * 2.5% = 2500 สตางค์ *2 = 5000
            self.assertEqual(cashback(100000, "gold", True), 5000)

        def test_cap_without_birthday(self):
            # 500000 * 4% = 20000 พอดีเพดาน
            self.assertEqual(cashback(500000, "platinum", False), 20000)
            # 600000 * 4% = 24000 -> 20000
            self.assertEqual(cashback(600000, "platinum", False), 20000)
            # 499999 * 4% = 19999.96 -> 20000 (ปัดขึ้น แล้วถูกจำกัดเพดาน)
            self.assertEqual(cashback(499999, "platinum", False), 20000)

        def test_cap_boundary_just_below(self):
            # 499000 * 4% = 19960 (ยังไม่ถึงเพดาน)
            self.assertEqual(cashback(499000, "platinum", False), 19960)

        def test_rejects_bad_amount(self):
            with self.assertRaises(ValueError):
                cashback(-1, "gold", False)
            with self.assertRaises(ValueError):
                cashback(10000.0, "gold", False)
            with self.assertRaises(ValueError):
                cashback("10000", "gold", False)
            with self.assertRaises(ValueError):
                cashback(True, "gold", False)

        def test_rejects_bad_tier(self):
            for bad in ["Gold", "bronze", "", None, 1]:
                with self.assertRaises(ValueError):
                    cashback(10000, bad, False)

        def test_rejects_bad_birthday(self):
            for bad in [1, 0, "True", None]:
                with self.assertRaises(ValueError):
                    cashback(10000, "gold", bad)

    unittest.main(verbosity=2)
