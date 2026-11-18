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
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_birthday_platinum_double(self):
        self.assertEqual(cashback(20000, "platinum", True), 1600)

    def test_birthday_silver_not_doubled(self):
        # นโยบายร้าน: silver ไม่ได้สิทธิ์ x2
        self.assertEqual(cashback(20000, "silver", True), 300)

    def test_min_amount_edge(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(10001, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap_edge(self):
        # platinum 4%: 500000 -> 20000 พอดี
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(250000, "platinum", True), 20000)  # x2 แล้วชนเพดาน
        self.assertEqual(cashback(10**9, "silver", False), 20000)

    def test_rounding_floor(self):
        # 10001*1.5% = 150.015 -> 150 ; 10033*1.5% = 150.495 -> 150
        self.assertEqual(cashback(10033, "silver", False), 150)
        # 10039*2.5% = 250.975 -> 250
        self.assertEqual(cashback(10039, "gold", False), 250)
        # 10039*2.5%*2 = 501.95 -> 501
        self.assertEqual(cashback(10039, "gold", True), 501)

    def test_result_is_int(self):
        self.assertIs(type(cashback(12345, "gold", True)), int)
        self.assertIs(type(cashback(50, "gold", False)), int)

    def test_reject_amount(self):
        for bad in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                cashback(bad, "gold", False)

    def test_reject_tier(self):
        for bad in ("bronze", "Gold", "", None, 1, True):
            with self.assertRaises(ValueError):
                cashback(20000, bad, False)

    def test_reject_birthday(self):
        for bad in (1, 0, "True", None, 1.0):
            with self.assertRaises(ValueError):
                cashback(20000, "gold", bad)


if __name__ == "__main__":
    unittest.main()
