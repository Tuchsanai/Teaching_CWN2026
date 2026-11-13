import unittest
from fractions import Fraction as F
from solve import bulk_price


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        # 10000*10*0.965*1.07 = 103255
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        # 10000*50*0.925*1.07 = 494875
        self.assertEqual(bulk_price(10000, 50, False), 494875)
        # 10000*50*0.925*0.975*1.07 = 482503.125
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_half(self):
        # 50*1*... : unit 100, qty 1 -> 107 ; find .5: unit 1,qty 50 coupon no: 50*.925*1.07=49.4875
        self.assertEqual(bulk_price(1, 50, False), 49)
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_reject(self):
        for a in [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
                  ("1", 1, False), (True, 1, False), (1, 1.0, False), (1, True, False),
                  (1, 1, 1), (1, 1, None), (None, 1, False), (1, [], False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
