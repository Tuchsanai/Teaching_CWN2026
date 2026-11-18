import unittest
from solve import bulk_price


class TestSolve(unittest.TestCase):
    def test_normal_no_discount(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)

    def test_normal_tier1(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5 -> half up

    def test_normal_tier2(self):
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 49487.5 -> half up

    def test_coupon_single(self):
        self.assertEqual(bulk_price(1000, 1, True), 1043)  # 1043.25

    def test_coupon_with_tier1(self):
        # ข้อสมมติ: คูปองลดต่อจากส่วนลดปริมาณ (คูณต่อกัน)
        self.assertEqual(bulk_price(1000, 10, True), 10067)  # 10067.0625

    def test_coupon_with_tier2(self):
        self.assertEqual(bulk_price(1000, 50, True), 48250)  # 48250.3125

    def test_edge_9_vs_10(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_edge_49_vs_50(self):
        self.assertEqual(bulk_price(1000, 49, False), 50595)  # 50594.95
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_edge_qty_max_and_zero_price(self):
        self.assertEqual(bulk_price(0, 1000, True), 0)
        self.assertEqual(bulk_price(1000, 1000, False), 989750)  # 925000*1.07

    def test_rounding_half_up(self):
        self.assertEqual(bulk_price(1, 1, False), 1)  # 1.07
        self.assertEqual(bulk_price(5, 1, False), 5)  # 5.35

    def test_result_is_int(self):
        self.assertIs(type(bulk_price(1234, 17, True)), int)

    def test_reject_unit_price(self):
        for bad in (-1, 10.0, True, "100", None):
            with self.assertRaises(ValueError):
                bulk_price(bad, 1, False)

    def test_reject_qty(self):
        for bad in (0, -1, 1001, 5.0, True, "5", None):
            with self.assertRaises(ValueError):
                bulk_price(100, bad, False)

    def test_reject_coupon(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                bulk_price(100, 1, bad)


if __name__ == "__main__":
    unittest.main()
