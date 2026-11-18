import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_basic_rates(self):
        self.assertEqual(cashback(10000, "silver", False), 150)    # 100 บาท × 1.5%
        self.assertEqual(cashback(10000, "gold", False), 250)      # 100 บาท × 2.5%
        self.assertEqual(cashback(10000, "platinum", False), 400)  # 100 บาท × 4%

    def test_flag_combinations(self):
        self.assertEqual(cashback(100000, "silver", True), 3000)   # 100,000 สตางค์ × 1.5% × 2
        self.assertEqual(cashback(100000, "gold", True), 5000)     # 1,000 × 2.5% × 2
        self.assertEqual(cashback(100000, "platinum", False), 4000)  # 1,000 × 4%


class Boundary(unittest.TestCase):
    def test_at_threshold(self):
        self.assertEqual(cashback(10000, "gold", False), 250)  # พอดี 100 บาท ได้เงินคืน

    def test_just_below_and_above(self):
        self.assertEqual(cashback(9999, "platinum", False), 0)     # ต่ำกว่า 100 บาท
        self.assertEqual(cashback(10001, "platinum", False), 400)  # 400.04 -> 400

    def test_zero_and_max(self):
        self.assertEqual(cashback(0, "platinum", True), 0)
        self.assertEqual(cashback(10**9, "platinum", True), 20000)  # เพดาน 200 บาท

    def test_cap_boundary(self):
        # platinum ไม่เดือนเกิด: 500,000 สตางค์ × 4% = 20,000 พอดีเพดาน
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999)


class NoDrift(unittest.TestCase):
    def test_single_rounding(self):
        # 10030 × 2.5% = 250.75 -> ×2 = 501.5 -> ปัดลงครั้งเดียว = 501 (ไม่ใช่ 500)
        self.assertEqual(cashback(10030, "gold", True), 501)

    def test_no_pre_rounding_on_plain_rate(self):
        # 10067 × 1.5% = 151.005 -> 151
        self.assertEqual(cashback(10067, "silver", False), 151)


class Reject(unittest.TestCase):
    def test_bool_is_not_int(self):
        with self.assertRaises(ValueError):
            cashback(True, "gold", False)

    def test_float_is_not_int(self):
        with self.assertRaises(ValueError):
            cashback(4500.0, "gold", False)

    def test_string_is_not_int(self):
        with self.assertRaises(ValueError):
            cashback("10000", "gold", False)

    def test_negative_amount(self):
        with self.assertRaises(ValueError):
            cashback(-1, "gold", False)

    def test_unknown_tier(self):
        with self.assertRaises(ValueError):
            cashback(10000, "bronze", False)

    def test_tier_case_sensitive(self):
        with self.assertRaises(ValueError):
            cashback(10000, "Gold", False)

    def test_birthday_must_be_bool(self):
        with self.assertRaises(ValueError):
            cashback(10000, "gold", 1)
        with self.assertRaises(ValueError):
            cashback(10000, "gold", "yes")


if __name__ == "__main__":
    unittest.main()
