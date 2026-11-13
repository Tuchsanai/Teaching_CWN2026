import unittest

from solve import cashback


class CashbackTests(unittest.TestCase):
    # ขอบ 100 บาท
    def test_below_threshold_no_cashback(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_exactly_threshold_gets_cashback(self):
        # 10000 * 1.5% = 150
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_zero(self):
        self.assertEqual(cashback(0, "gold", True), 0)

    # อัตรา
    def test_rates(self):
        self.assertEqual(cashback(10000, "silver", False), 150)    # 1.5%
        self.assertEqual(cashback(10000, "gold", False), 250)      # 2.5%
        self.assertEqual(cashback(10000, "platinum", False), 400)  # 4%

    # เดือนเกิด 2 เท่า
    def test_birthday_doubles(self):
        self.assertEqual(cashback(10000, "gold", True), 500)
        self.assertEqual(cashback(10000, "silver", True), 300)

    # เพดาน 200 บาท
    def test_cap(self):
        self.assertEqual(cashback(1_000_000, "platinum", False), 20000)  # 40000 -> 20000
        self.assertEqual(cashback(1_000_000, "gold", True), 20000)       # 50000 -> 20000

    def test_cap_boundary(self):
        # 5000000 * 4% = 200000 ต้องได้ 20000 พอดี
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        # 499999 * 4% = 19999.96 -> ปัดครึ่งขึ้นเป็น 20000
        self.assertEqual(cashback(499999, "platinum", False), 20000)
        # 499000 * 4% = 19960 ไม่ถึงเพดาน
        self.assertEqual(cashback(499000, "platinum", False), 19960)

    # ปัดครึ่งขึ้นครั้งเดียว
    def test_half_up_rounding(self):
        # 10033 * 1.5% = 150.495 -> 150
        self.assertEqual(cashback(10033, "silver", False), 150)
        # 10034 * 1.5% = 150.51 -> 151
        self.assertEqual(cashback(10034, "silver", False), 151)
        # 10020 * 2.5% = 250.5 -> 251 (ครึ่งขึ้น)
        self.assertEqual(cashback(10020, "gold", False), 251)
        # 10020 * 2.5% * 2 = 501 พอดี
        self.assertEqual(cashback(10020, "gold", True), 501)

    def test_returns_int(self):
        self.assertIs(type(cashback(12345, "gold", False)), int)

    # การปฏิเสธ input ผิด
    def test_reject_float_amount(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, "gold", False)

    def test_reject_bool_amount(self):
        with self.assertRaises(ValueError):
            cashback(True, "gold", False)

    def test_reject_negative_amount(self):
        with self.assertRaises(ValueError):
            cashback(-1, "gold", False)

    def test_reject_str_amount(self):
        with self.assertRaises(ValueError):
            cashback("10000", "gold", False)

    def test_reject_unknown_tier(self):
        with self.assertRaises(ValueError):
            cashback(10000, "bronze", False)

    def test_reject_tier_case_mismatch(self):
        with self.assertRaises(ValueError):
            cashback(10000, "Gold", False)

    def test_reject_non_str_tier(self):
        with self.assertRaises(ValueError):
            cashback(10000, None, False)

    def test_reject_int_birthday(self):
        with self.assertRaises(ValueError):
            cashback(10000, "gold", 1)


if __name__ == "__main__":
    unittest.main()
