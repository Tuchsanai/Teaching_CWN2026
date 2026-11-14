import unittest
from solve import cashback


class TestSolve(unittest.TestCase):
    def test_silver_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)

    def test_gold_normal(self):
        self.assertEqual(cashback(20000, "gold", False), 500)

    def test_platinum_normal(self):
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_birthday_gold_double(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_birthday_platinum_double(self):
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_birthday_silver_not_doubled(self):
        # นโยบายร้าน: silver ไม่ได้สิทธิ์ 2 เท่า
        self.assertEqual(cashback(10000, "silver", True), 150)

    def test_min_amount_edge(self):
        self.assertEqual(cashback(9999, "platinum", False), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)  # พอดี 100 บาทได้
        self.assertEqual(cashback(10001, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", True), 0)

    def test_cap_edge(self):
        # platinum 4%: 500000 -> 20000 พอดี
        self.assertEqual(cashback(499999, "platinum", False), 19999)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(10**9, "silver", False), 20000)

    def test_cap_after_birthday_double(self):
        # gold 500000*2.5%=12500 x2 = 25000 -> เพดาน 20000
        self.assertEqual(cashback(500000, "gold", True), 20000)

    def test_rounding_down(self):
        # 10034*1.5% = 150.51 -> ปัดลง 150
        self.assertEqual(cashback(10034, "silver", False), 150)
        # 10039*2.5% = 250.975 -> 250
        self.assertEqual(cashback(10039, "gold", False), 250)

    def test_result_is_int(self):
        for t in ("silver", "gold", "platinum"):
            self.assertIs(type(cashback(12345, t, True)), int)
        self.assertIs(type(cashback(50, "gold", False)), int)

    def test_reject_amount(self):
        for bad in (-1, 10000.0, True, "10000", None):
            with self.assertRaises(ValueError):
                cashback(bad, "gold", False)

    def test_reject_tier(self):
        for bad in ("bronze", "Gold", "", None, 1):
            with self.assertRaises(ValueError):
                cashback(10000, bad, False)

    def test_reject_birthday(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                cashback(10000, "gold", bad)


if __name__ == "__main__":
    unittest.main()
