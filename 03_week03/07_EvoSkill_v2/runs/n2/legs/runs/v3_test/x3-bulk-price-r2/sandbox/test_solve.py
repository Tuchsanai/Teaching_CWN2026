"""รัน: python3 -m unittest -q test_solve (ค่าที่คาดคำนวณมือ)"""
import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_normal_2(self):
        # 100000*.965=96500 *1.07
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_normal_3(self):
        # 500000*.925*.975*1.07 = 482503.125
        self.assertEqual(bulk_price(10000, 50, True), 482503)


class Boundary(unittest.TestCase):
    def test_boundary_9_vs_10(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_boundary_49_vs_50(self):
        # 490000*.965*1.07 = 505949.5 -> 505950
        self.assertEqual(bulk_price(10000, 49, False), 505950)
        # 500000*.925*1.07 = 494875
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_boundary_limits(self):
        self.assertEqual(bulk_price(0, 1, False), 0)
        # 1000*.925*1.07 = 989.75 ถุงละ 1 สตางค์ -> 989.75*1 -> 990
        self.assertEqual(bulk_price(1, 1000, False), 990)


class NoDrift(unittest.TestCase):
    def test_half_rounds_up(self):
        self.assertEqual(bulk_price(10000, 49, False), 505950)

    def test_fraction_down(self):
        # 1*.975*1.07 = 1.04325 -> 1 ; 3*.975*1.07=3.12975 -> 3
        self.assertEqual(bulk_price(1, 1, True), 1)
        self.assertEqual(bulk_price(3, 1, True), 3)

    def test_fraction_up(self):
        # 7*10=70... 7*10*.965*1.07 = 72.2785 -> 72 ; 9*50*.925*1.07=445.4... 
        self.assertEqual(bulk_price(7, 10, False), 72)
        # 450*.925=416.25*1.07=445.3875 -> 445
        self.assertEqual(bulk_price(9, 50, False), 445)


class Reject(unittest.TestCase):
    def test_reject_negative_price(self):
        with self.assertRaises(ValueError):
            bulk_price(-1, 1, False)

    def test_reject_qty_range(self):
        for q in (0, 1001, -5):
            with self.assertRaises(ValueError):
                bulk_price(100, q, False)

    def test_reject_float_str(self):
        for args in ((100.0, 1, False), ("100", 1, False), (100, 1.0, False), (100, "1", False)):
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_reject_bool_coupon(self):
        for args in ((True, 1, False), (100, True, False), (100, 1, 1), (100, 1, "yes"), (100, 1, None)):
            with self.assertRaises(ValueError):
                bulk_price(*args)


if __name__ == "__main__":
    unittest.main()
