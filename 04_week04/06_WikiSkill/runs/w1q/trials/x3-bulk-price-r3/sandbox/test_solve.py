import unittest
from solve import bulk_price


class TestSolve(unittest.TestCase):
    def test_normal_no_discount(self):
        # 100*5*1.07 = 535
        self.assertEqual(bulk_price(100, 5, False), 535)

    def test_normal_tier10(self):
        # 10000*10*0.965*1.07 = 103255
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_normal_tier50_coupon(self):
        # 10000*50*0.925*0.975*1.07 = 482503.125 -> 482503
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_coupon_small_qty(self):
        # 10000*1*0.975*1.07 = 10432.5 -> half-up 10433
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_edge_10(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)    # 9000*1.07
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 9650*1.07=10325.5 -> 10326

    def test_edge_50(self):
        # 49 ถุงยังได้ 3.5%: 49000*0.965*1.07 = 50594.95 -> 50595
        self.assertEqual(bulk_price(1000, 49, False), 50595)
        # 50 ถุงได้ 7.5% (ไม่ซ้อนกับ 3.5%): 50000*0.925*1.07 = 49487.5 -> 49488
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_int_type(self):
        self.assertIs(type(bulk_price(333, 7, True)), int)

    def test_max_qty(self):
        # 1*1000*0.925*1.07 = 989.75 -> 990
        self.assertEqual(bulk_price(1, 1000, False), 990)

    def test_reject_unit_price(self):
        for v in (-1, 10.0, True, "5", None):
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
