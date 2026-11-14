import unittest
from solve import cashback


class TestSolve(unittest.TestCase):
    def test_silver_normal(self):
        self.assertEqual(cashback(50000, "silver", False), 750)

    def test_gold_normal(self):
        self.assertEqual(cashback(50000, "gold", False), 1250)

    def test_platinum_birthday(self):
        self.assertEqual(cashback(50000, "platinum", True), 4000)

    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_at_min(self):
        # สมมติ: พอดี 100 บาท ได้เงินคืน (ต่ำกว่าเท่านั้นที่ไม่ได้)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10001, "silver", False), 150)

    def test_cap(self):
        # platinum 4% x2 = 8%; 300000 -> 24000 -> cap 20000
        self.assertEqual(cashback(300000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)  # พอดีเพดาน
        self.assertEqual(cashback(499975, "platinum", False), 19999)  # 19999.0

    def test_rounding(self):
        # 10001*1.5% = 150.015 -> 150 ; 10033*1.5% = 150.495 -> 150 ; 10034 -> 150.51 -> 151
        self.assertEqual(cashback(10033, "silver", False), 150)
        self.assertEqual(cashback(10034, "silver", False), 151)
        # ครึ่งพอดี: 10100*2.5%=252.5 -> 253 (ปัดครึ่งขึ้น)
        self.assertEqual(cashback(10100, "gold", False), 253)

    def test_returns_int(self):
        self.assertIs(type(cashback(12345, "gold", True)), int)
        self.assertIs(type(cashback(5, "gold", True)), int)

    def test_reject_amount(self):
        for bad in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                cashback(bad, "gold", False)

    def test_reject_tier(self):
        for bad in ("bronze", "Gold", "", None, 1):
            with self.assertRaises(ValueError):
                cashback(20000, bad, False)

    def test_reject_birthday(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                cashback(20000, "gold", bad)


if __name__ == "__main__":
    unittest.main()
