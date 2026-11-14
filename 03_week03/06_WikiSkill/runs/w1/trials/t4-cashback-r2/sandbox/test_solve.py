import unittest
from solve import cashback


class TestSolve(unittest.TestCase):
    def test_normal_silver(self):
        self.assertEqual(cashback(20000, "silver", False), 300)

    def test_normal_gold(self):
        self.assertEqual(cashback(20000, "gold", False), 500)

    def test_normal_platinum(self):
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_birthday_double(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_min_below(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_min_exact(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_zero_amount(self):
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap_exact(self):
        # platinum 4%: 500000 -> 20000 พอดีเพดาน
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_cap_above(self):
        self.assertEqual(cashback(500001, "platinum", False), 20000)

    def test_cap_after_birthday(self):
        # 400000*4%*2 = 32000 -> จำกัด 20000
        self.assertEqual(cashback(400000, "platinum", True), 20000)

    def test_below_cap(self):
        self.assertEqual(cashback(499987, "platinum", False), 19999)

    def test_round_half_up(self):
        # 10010*1.5% = 150.15 -> 150 ; 10030*1.5%=150.45 -> 150 ; 10040 -> 150.6 -> 151
        self.assertEqual(cashback(10030, "silver", False), 150)
        # 10050*1.5% = 150.75 -> 151
        self.assertEqual(cashback(10050, "silver", False), 151)
        # 10010*2.5% = 250.25 -> 250 ; 10030*2.5%=250.75 -> 251
        self.assertEqual(cashback(10030, "gold", False), 251)

    def test_half_exact(self):
        # 10100*2.5% = 252.5 -> 253 (ปัดครึ่งขึ้น)
        self.assertEqual(cashback(10100, "gold", False), 253)

    def test_result_is_int(self):
        self.assertIs(type(cashback(12345, "gold", True)), int)
        self.assertIs(type(cashback(100, "gold", True)), int)

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
