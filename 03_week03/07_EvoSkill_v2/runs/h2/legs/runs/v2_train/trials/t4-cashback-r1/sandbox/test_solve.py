"""ทดสอบ cashback แยกหมวด Normal, Boundary, NoDrift, Reject
expected คำนวณด้วยสคริปต์ Fraction แล้ว (ดู solve.py กฎ 1-8)

รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_basic_each_tier(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_flag_combinations(self):
        self.assertEqual(cashback(10000, "gold", True), 500)
        self.assertEqual(cashback(10000, "silver", True), 300)
        self.assertEqual(cashback(20000, "silver", True), 600)


class Boundary(unittest.TestCase):
    def test_at_threshold(self):
        # 100 บาทพอดี ได้เงินคืน
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_just_below_and_above(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10001, "silver", False), 150)

    def test_zero_and_max(self):
        self.assertEqual(cashback(0, "gold", True), 0)
        # เพดานพอดี: 800000 * 2.5% = 20000
        self.assertEqual(cashback(800000, "gold", False), 20000)
        self.assertEqual(cashback(4000000, "silver", True), 20000)

    def test_cap_boundary(self):
        self.assertEqual(cashback(799999, "gold", False), 19999)
        self.assertEqual(cashback(800000, "gold", False), 20000)
        self.assertEqual(cashback(1000000, "gold", False), 20000)


class NoDrift(unittest.TestCase):
    def test_single_rounding(self):
        # 10030 * 2.5% = 250.75 -> ×2 = 501.5 -> 501
        # ถ้าปัดก่อนคูณจะได้ 500 (ผิด)
        self.assertEqual(cashback(10030, "gold", True), 501)
        # 250.75 -> 250 (ปัดลงครั้งเดียว)
        self.assertEqual(cashback(10030, "gold", False), 250)

    def test_fraction_no_float_drift(self):
        # 500001 * 4% = 20000.04 -> ติดเพดาน 20000
        self.assertEqual(cashback(500001, "platinum", False), 20000)


class Reject(unittest.TestCase):
    def test_bool_is_not_int(self):
        with self.assertRaises(ValueError):
            cashback(True, "gold", False)

    def test_float_is_not_int(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, "gold", False)

    def test_string_is_not_int(self):
        with self.assertRaises(ValueError):
            cashback("10000", "gold", False)

    def test_negative_below_threshold_raises(self):
        # -1 ต่ำกว่าเกณฑ์ 100 บาท แต่ต้อง raise ไม่ใช่คืน 0
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
