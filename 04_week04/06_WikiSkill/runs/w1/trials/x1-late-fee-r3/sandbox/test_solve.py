import unittest
from solve import late_fee


class TestSolve(unittest.TestCase):
    def test_normal_short(self):
        self.assertEqual(late_fee(100000, 2), 0)

    def test_normal_mid(self):
        # 100000 * 0.75% * 10 = 7500
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_normal_cap(self):
        self.assertEqual(late_fee(100000, 100), 15000)

    def test_edge_grace_exact(self):
        self.assertEqual(late_fee(100000, 3), 0)

    def test_edge_after_grace(self):
        # 4 วัน: 100000 * 0.75% * 4 = 3000 (นับรวม 3 วันแรก)
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_edge_cap_boundary(self):
        # 20 วัน = 15% พอดี; 19 วัน = 14.25%; 21 วัน ถูกจำกัดที่ 15%
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)

    def test_edge_zero_and_max(self):
        self.assertEqual(late_fee(0, 50), 0)
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_rounding(self):
        # 101*75*4=30300 -> 3.03 -> 3 ; 130*75*4=39000 -> 3.9 -> 4
        self.assertEqual(late_fee(101, 4), 3)
        self.assertEqual(late_fee(130, 4), 4)
        # ครึ่งพอดีปัดขึ้น (สมมติ): 50*75*4=15000 -> 1.5 -> 2
        self.assertEqual(late_fee(50, 4), 2)

    def test_result_is_int(self):
        self.assertIs(type(late_fee(12345, 7)), int)
        self.assertIs(type(late_fee(12345, 1)), int)

    def test_reject_amount(self):
        for bad in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                late_fee(bad, 5)

    def test_reject_days_late(self):
        for bad in (-1, 366, 5.0, True, "5", None):
            with self.assertRaises(ValueError):
                late_fee(1000, bad)


if __name__ == "__main__":
    unittest.main()
