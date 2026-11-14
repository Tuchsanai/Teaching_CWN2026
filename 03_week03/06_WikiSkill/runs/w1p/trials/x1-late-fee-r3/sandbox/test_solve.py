import unittest
from solve import late_fee


class TestSolve(unittest.TestCase):
    def test_normal_small(self):
        # 10000 * 0.75% * 10 = 750
        self.assertEqual(late_fee(10000, 10), 750)

    def test_normal_four_days(self):
        # นับรวม 3 วันแรก: 4 วัน = 3% ของ 20000 = 600
        self.assertEqual(late_fee(20000, 4), 600)

    def test_normal_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_edge_three_days_free(self):
        self.assertEqual(late_fee(100000, 3), 0)

    def test_edge_below_threshold(self):
        self.assertEqual(late_fee(100000, 0), 0)

    def test_edge_cap_exact_20_days(self):
        # 20 วัน = 15% พอดี
        self.assertEqual(late_fee(10000, 20), 1500)

    def test_edge_cap_above(self):
        # 21 วันขึ้นไปจำกัด 15%; 365 วันก็เท่ากัน
        self.assertEqual(late_fee(10000, 21), 1500)
        self.assertEqual(late_fee(10000, 365), 1500)

    def test_edge_below_cap(self):
        # 19 วัน = 14.25% ของ 10000 = 1425
        self.assertEqual(late_fee(10000, 19), 1425)

    def test_rounding_half_up(self):
        # 4 วัน = 3%: 50*0.03=1.5 -> 2 (สมมติปัดครึ่งขึ้น); 49*0.03=1.47 -> 1
        self.assertEqual(late_fee(50, 4), 2)
        self.assertEqual(late_fee(49, 4), 1)

    def test_result_is_int(self):
        self.assertIs(type(late_fee(12345, 7)), int)
        self.assertIs(type(late_fee(12345, 2)), int)

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
