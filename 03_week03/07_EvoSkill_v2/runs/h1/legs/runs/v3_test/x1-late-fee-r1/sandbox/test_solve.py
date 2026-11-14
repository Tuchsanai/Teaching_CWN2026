import unittest
from fractions import Fraction

from solve import late_fee


def expected(amount, days):
    # คำนวณความคาดหวังด้วย Fraction ปัดครึ่งขึ้นครั้งเดียว
    if days <= 3:
        return 0
    fee = min(Fraction(amount) * Fraction(75, 10000) * days,
              Fraction(amount) * Fraction(15, 100))
    return int(fee + Fraction(1, 2))


class TestLateFee(unittest.TestCase):
    def test_grace_period_no_fee(self):
        for d in range(0, 4):
            self.assertEqual(late_fee(100000, d), 0)

    def test_first_day_after_grace_counts_all_days(self):
        # 4 วัน x 0.75% ของ 100000 = 3000
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_linear_before_cap(self):
        self.assertEqual(late_fee(100000, 10), 7500)   # 7.5%
        self.assertEqual(late_fee(100000, 19), 14250)  # 14.25%

    def test_cap_reached_at_20_days(self):
        # 20 วัน x 0.75% = 15% พอดี
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 0), 0)
        self.assertEqual(late_fee(0, 365), 0)

    def test_half_up_rounding(self):
        # 1 สตางค์ x 4 วัน x 0.75% = 0.03 -> 0
        self.assertEqual(late_fee(1, 4), 0)
        # 10 x 20 วัน = 1.5 (ถึงเพดานพอดี) -> ปัดครึ่งขึ้นเป็น 2
        self.assertEqual(late_fee(10, 20), 2)
        # 6667 x 4 x 0.75% = 200.01 -> 200
        self.assertEqual(late_fee(6667, 4), 200)
        # 2000 x 4 x 0.75% = 60 พอดี
        self.assertEqual(late_fee(2000, 4), 60)
        # 66 x 5 x 0.75% = 2.475 -> 2 ; 67 x 5 x 0.75% = 2.5125 -> 3
        self.assertEqual(late_fee(66, 5), 2)
        self.assertEqual(late_fee(67, 5), 3)
        # 100 x 6 x 0.75% = 4.5 -> 5 (ครึ่งพอดี ปัดขึ้น)
        self.assertEqual(late_fee(100, 6), 5)

    def test_matches_reference_over_range(self):
        for amount in [0, 1, 99, 1234, 99999, 500000, 12345678]:
            for days in range(0, 366):
                self.assertEqual(late_fee(amount, days), expected(amount, days),
                                 (amount, days))

    def test_rejects_bad_types(self):
        for bad in [(True, 5), (100, True), (1000.0, 5), (1000, 5.0),
                    ("1000", 5), (1000, "5"), (None, 5)]:
            with self.assertRaises(ValueError, msg=str(bad)):
                late_fee(*bad)

    def test_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 5)
        with self.assertRaises(ValueError):
            late_fee(100, -1)
        with self.assertRaises(ValueError):
            late_fee(100, 366)


if __name__ == "__main__":
    unittest.main()
