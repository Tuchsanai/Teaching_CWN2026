import unittest
from solve import bulk_price


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)  # 1000*1.07
        self.assertEqual(bulk_price(1000, 5, False), 5350)  # 5000*1.07

    def test_tier_10(self):
        self.assertEqual(bulk_price(1000, 20, False), 20651)  # 20000*.965*1.07=20651

    def test_tier_50(self):
        self.assertEqual(bulk_price(2000, 100, False), 197950)  # 200000*.925*1.07

    def test_coupon_only(self):
        self.assertEqual(bulk_price(1000, 1, True), 1043)  # 975*1.07=1043.25

    def test_tier10_coupon(self):
        self.assertEqual(bulk_price(1000, 10, True), 10067)  # 9650*.975*1.07=10067.36

    def test_tier50_coupon(self):
        self.assertEqual(bulk_price(1000, 50, True), 48250)  # 46250*.975*1.07=48250.31

    def test_not_stacked(self):
        # 50 ถุงใช้ 7.5% อย่างเดียว ไม่ใช่ 3.5% ซ้อน
        self.assertEqual(bulk_price(1000, 50, False), 49488)


class Boundary(unittest.TestCase):
    def test_qty_9_10_11(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)    # 9000*1.07
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 9650*1.07=10325.5
        self.assertEqual(bulk_price(1000, 11, False), 11358)  # 10615*1.07=11358.05

    def test_qty_49_50_51(self):
        self.assertEqual(bulk_price(1000, 49, False), 50595)  # 49000*.965*1.07=50594.95
        self.assertEqual(bulk_price(1000, 51, False), 50477)  # 51000*.925*1.07=50477.25

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 1, False), 0)
        self.assertEqual(bulk_price(0, 1000, True), 0)

    def test_qty_max(self):
        self.assertEqual(bulk_price(1, 1000, False), 990)  # 925*1.07=989.75


class NoDrift(unittest.TestCase):
    def test_half_up_not_even(self):
        self.assertEqual(bulk_price(150, 1, False), 161)  # 160.5 -> 161 (half-even ได้ 160)

    def test_half_up_not_floor(self):
        self.assertEqual(bulk_price(50, 1, False), 54)  # 53.5

    def test_single_rounding(self):
        # 123*10: 1230*.965=1186.95 (ปัดกลางทาง=1187) *1.07 = 1270.0365 -> 1270; ตรงกัน แต่ต้องไม่ปัดก่อน VAT
        self.assertEqual(bulk_price(123, 10, False), 1270)
        # 1*10: 9.65*1.07=10.3255 -> 10 (ถ้าปัด 9.65->10 ก่อน จะได้ 10.7 -> 11)
        self.assertEqual(bulk_price(1, 10, False), 10)


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            bulk_price(*a)

    def test_unit_price(self):
        for v in (-1, 1.5, 10.0, "100", True, None):
            self.bad(v, 1, False)

    def test_qty(self):
        for v in (0, -1, 1001, 1.5, 5.0, "2", True, None):
            self.bad(1000, v, False)

    def test_coupon(self):
        for v in (0, 1, "yes", None, 1.0):
            self.bad(1000, 1, v)

    def test_invalid_even_with_zero_price(self):
        self.bad(0, 0, False)
        self.bad(0, 1, 1)


if __name__ == "__main__":
    unittest.main()
