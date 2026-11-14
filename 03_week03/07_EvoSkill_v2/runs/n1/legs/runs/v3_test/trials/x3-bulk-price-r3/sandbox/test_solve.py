"""python3 -m unittest -q test_solve"""
import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_tier1(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_tier1_coupon(self):
        self.assertEqual(bulk_price(10000, 10, True), 100674)

    def test_tier2(self):
        self.assertEqual(bulk_price(10000, 50, False), 494875)


class Boundary(unittest.TestCase):
    def test_9_vs_10(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_49_vs_50(self):
        self.assertEqual(bulk_price(10000, 49, False), 505950)
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_zero_price_and_max_qty(self):
        self.assertEqual(bulk_price(0, 5, True), 0)
        self.assertEqual(bulk_price(1, 1000, False), 990)


class NoDrift(unittest.TestCase):
    def test_exact_half_up(self):
        # 1 * 10 * .965 * 1.07 = 10.3255 -> 10; 5*10*... ตรวจ .5 พอดี
        self.assertEqual(bulk_price(1, 10, False), 10)
        self.assertEqual(bulk_price(50, 1, False), 54)  # 53.5 -> 54

    def test_single_rounding(self):
        self.assertEqual(bulk_price(4505, 10, True), 45353)


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 1, False), (100, 0, False), (100, 1001, False), (100, -1, False),
               (100.0, 1, False), ('100', 1, False), (None, 1, False), (True, 1, False),
               (100, 1.0, False), (100, '2', False), (100, None, False), (100, True, False),
               (100, 1, 0), (100, 1, 1), (100, 1, 'yes'), (100, 1, None)]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    bulk_price(*args)


if __name__ == "__main__":
    unittest.main()
