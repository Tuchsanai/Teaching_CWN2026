import unittest

from solve import cashback


class CashbackTests(unittest.TestCase):
    def test_threshold_below_100_baht_gives_zero(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_exactly_100_baht_gets_cashback(self):
        # 10000 * 2.5% = 250
        self.assertEqual(cashback(10000, "gold", False), 250)

    def test_basic_rates(self):
        self.assertEqual(cashback(50000, "silver", False), 750)     # 1.5%
        self.assertEqual(cashback(50000, "gold", False), 1250)      # 2.5%
        self.assertEqual(cashback(50000, "platinum", False), 2000)  # 4%

    def test_birthday_doubles(self):
        self.assertEqual(cashback(50000, "silver", True), 1500)
        self.assertEqual(cashback(10300, "gold", True), 515)

    def test_half_up_rounding(self):
        # 10300 * 1.5% = 154.5 -> 155 (ปัดครึ่งขึ้น ไม่ใช่ banker's)
        self.assertEqual(cashback(10300, "silver", False), 155)
        # 10100 * 1.5% = 151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)

    def test_cap_200_baht(self):
        self.assertEqual(cashback(300000, "platinum", True), 20000)  # 240 บาท -> cap 200
        self.assertEqual(cashback(100000, "platinum", True), 8000)   # 80 บาท ไม่ถึงเพดาน
        self.assertEqual(cashback(100000, "platinum", False), 4000)  # 40 บาท ไม่ถึงเพดาน
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(1000000, "gold", False), 20000)    # 250 -> cap 200

    def test_cap_boundary(self):
        # 800000 * 2.5% = 20000 ตรงเพดานพอดี
        self.assertEqual(cashback(800000, "gold", False), 20000)
        # 799800 * 2.5% = 19995 ต่ำกว่าเพดาน
        self.assertEqual(cashback(799800, "gold", False), 19995)
        # 799999 * 2.5% = 19999.975 -> ปัดเป็น 20000 แล้วเท่ากับเพดาน
        self.assertEqual(cashback(799999, "gold", False), 20000)

    def test_returns_int(self):
        self.assertIs(type(cashback(50000, "silver", False)), int)

    def test_rejects_bad_amount(self):
        for bad in (100.0, "10000", True, -1, None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    cashback(bad, "gold", False)

    def test_rejects_bad_tier(self):
        for bad in ("Gold", "bronze", "", None, 1):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    cashback(10000, bad, False)

    def test_rejects_bad_birthday(self):
        for bad in (1, 0, "True", None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    cashback(10000, "gold", bad)


if __name__ == "__main__":
    unittest.main()
