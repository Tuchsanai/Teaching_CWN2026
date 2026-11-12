import unittest
from solve import bulk_price


class T(unittest.TestCase):
    def test_basic(self):
        # 1000*5*1.07 = 5350
        self.assertEqual(bulk_price(1000, 5, False), 5350)
        # 1000*5*0.975*1.07 = 5216.25 -> 5216
        self.assertEqual(bulk_price(1000, 5, True), 5216)

    def test_boundary_exact(self):
        # 10 bags: 10000*0.965*1.07 = 10325.5 -> 10326
        self.assertEqual(bulk_price(1000, 10, False), 10326)
        # 50 bags: 50000*0.925*1.07 = 49487.5 -> 49488
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_boundary_below(self):
        # 9 bags: no discount 9000*1.07 = 9630
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        # 49 bags: 49000*0.965*1.07 = 50594.95 -> 50595
        self.assertEqual(bulk_price(1000, 49, False), 50595)

    def test_boundary_above(self):
        # 11 bags: 11000*0.965*1.07 = 11358.05 -> 11358
        self.assertEqual(bulk_price(1000, 11, False), 11358)
        # 51 bags: 51000*0.925*1.07 = 50477.25 -> 50477
        self.assertEqual(bulk_price(1000, 51, False), 50477)

    def test_half_up(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # .5 up
        self.assertEqual(bulk_price(1, 1, False), 1)  # 1.07 -> 1
        self.assertEqual(bulk_price(1500, 1, False), 1605)  # exact
        # 50 bags, coupon: 50000*0.925*0.975*1.07 = 48250.3125 -> 48250
        self.assertEqual(bulk_price(1000, 50, True), 48250)

    def test_reject_value(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False), (100, -5, True)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_reject_type(self):
        for args in [(1000.0, 1, False), (100, 1.0, False), (100, True, False),
                     ("100", 1, False), (None, 1, False), (100, 1, 1), (100, 1, None)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_zero_or_cap(self):
        self.assertEqual(bulk_price(0, 5, False), 0)
        self.assertEqual(bulk_price(0, 1000, True), 0)
        # 1000 bags, 100 each: 100000*0.925*1.07 = 98975
        self.assertEqual(bulk_price(100, 1000, False), 98975)


if __name__ == "__main__":
    unittest.main()
