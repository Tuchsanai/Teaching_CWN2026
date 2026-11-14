import unittest
from solve import bulk_price


class TestSolve(unittest.TestCase):
    def test_no_discount(self):
        # 100*5=500 *1.07 = 535
        self.assertEqual(bulk_price(100, 5, False), 535)

    def test_tier1(self):
        # 10000*0.965=9650*1.07=10325.5 -> 10326 (half up)
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_tier2_coupon(self):
        # 50000*0.925*0.975*1.07=48250.3125 -> 48250
        self.assertEqual(bulk_price(1000, 50, True), 48250)

    def test_coupon_only(self):
        # 1000*0.975*1.07=1043.25 -> 1043
        self.assertEqual(bulk_price(1000, 1, True), 1043)

    def test_edge_10(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_edge_50(self):
        # 49 ถุง: 49000*0.965*1.07=50594.95 -> 50595
        self.assertEqual(bulk_price(1000, 49, False), 50595)
        # 50 ถุง: 50000*0.925*1.07=49487.5 -> 49488 (อัตราเดียว ไม่ซ้อน)
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 10, True), 0)

    def test_returns_int(self):
        self.assertIs(type(bulk_price(333, 77, True)), int)

    def test_reject_unit_price(self):
        for v in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                bulk_price(v, 1, False)

    def test_reject_qty(self):
        for v in (0, -1, 1001, 5.0, True, "5", None):
            with self.assertRaises(ValueError):
                bulk_price(100, v, False)

    def test_reject_coupon(self):
        for v in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                bulk_price(100, 1, v)


if __name__ == "__main__":
    unittest.main()
