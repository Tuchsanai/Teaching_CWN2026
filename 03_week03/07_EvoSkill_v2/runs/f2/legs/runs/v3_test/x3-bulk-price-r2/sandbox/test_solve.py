import unittest
from solve import bulk_price


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_tier1_coupon(self):
        # 10000*10*0.965*0.975*1.07 = 100,677.... compute by hand: 100000*.965=96500; *.975=94087.5; *1.07=100673.625
        self.assertEqual(bulk_price(10000, 10, True), 100674)

    def test_tier2(self):
        # 100000*5=500000... 10000*50=500000*.925=462500*1.07=494875
        self.assertEqual(bulk_price(10000, 50, False), 494875)


class Boundary(unittest.TestCase):
    def test_9_vs_10(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)  # 96500*1.07=103255

    def test_49_vs_50(self):
        self.assertEqual(bulk_price(1000, 49, False), 50595)  # 49000*.965=47285*1.07=50594.95
    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 1 * 1 * 1.07 = 1.07 -> 1 ; 50 * 0.5 cases: price 50, qty1 -> 53.5 -> 54
        self.assertEqual(bulk_price(50, 1, False), 54)

    def test_single_rounding(self):
        # 10000*10*.965*.975*1.07 = 100673.625 -> 100674
        self.assertEqual(bulk_price(10000, 10, True), 100674)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
                  ("1", 1, False), (True, 1, False), (1, True, False), (1, 1, 1), (1, 1, None)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
