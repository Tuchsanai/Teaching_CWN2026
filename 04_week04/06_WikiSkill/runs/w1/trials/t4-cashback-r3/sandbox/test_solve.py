import unittest
from solve import cashback


class TestSolve(unittest.TestCase):
    def test_normal_silver(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_normal_gold(self):
        self.assertEqual(cashback(10000, "gold", False), 250)

    def test_normal_platinum(self):
        self.assertEqual(cashback(50000, "platinum", False), 2000)

    def test_birthday_double(self):
        self.assertEqual(cashback(10000, "silver", True), 300)

    def test_min_amount_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)   # ต่ำกว่า 100 บาท
        self.assertEqual(cashback(10000, "platinum", False), 400)  # พอดี 100 บาท
        self.assertEqual(cashback(10001, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap_boundary(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)  # พอดีเพดาน
        self.assertEqual(cashback(490000, "platinum", False), 19600)  # ต่ำกว่า
        self.assertEqual(cashback(600000, "platinum", False), 20000)  # เกิน

    def test_cap_applies_after_birthday(self):
        # สมมติ: เพดาน 200 บาทใช้หลังคูณ 2 แล้ว
        self.assertEqual(cashback(300000, "platinum", True), 20000)
        self.assertEqual(cashback(1000000, "silver", True), 20000)
        self.assertEqual(cashback(300000, "silver", True), 9000)

    def test_rounding_half_up(self):
        # 10300*1.5% = 154.5 -> 155 (สมมติ: ปัดครึ่งขึ้น)
        self.assertEqual(cashback(10300, "silver", False), 155)
        self.assertEqual(cashback(10001, "silver", False), 150)  # 150.015
        self.assertEqual(cashback(10034, "silver", False), 151)  # 150.51

    def test_result_is_int(self):
        self.assertIs(type(cashback(10300, "silver", False)), int)
        self.assertIs(type(cashback(5, "gold", True)), int)

    def test_reject_amount(self):
        for bad in (-1, 10000.0, True, "10000", None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    cashback(bad, "gold", False)

    def test_reject_tier(self):
        for bad in ("bronze", "Gold", "", None, 1):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    cashback(10000, bad, False)

    def test_reject_birthday(self):
        for bad in (1, 0, "True", None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    cashback(10000, "gold", bad)


if __name__ == "__main__":
    unittest.main()
