import unittest
from solve import bulk_price


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10000*.975*1.07=10432.5

    def test_boundary_exact(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)  # 100000*.965*1.07
        self.assertEqual(bulk_price(10000, 50, False), 494875)  # 500000*.925*1.07

    def test_boundary_below(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 49, False), 505950)  # .5 half up

    def test_boundary_above(self):
        self.assertEqual(bulk_price(10000, 11, False), 113581)  # 113580.5
        self.assertEqual(bulk_price(10000, 51, False), 504773)  # 504772.5

    def test_half_up(self):
        self.assertEqual(bulk_price(1, 1, True), 1)  # 1.04325 -> 1
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # .5 exactly
        self.assertEqual(bulk_price(50, 1, False), 54)  # 53.5 -> 54

    def test_reject_value(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False), (100, -5, True)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_reject_type(self):
        for args in [(100.0, 1, False), (100, 1.0, False), (True, 1, False),
                     (100, True, False), ("100", 1, False), (100, None, False),
                     (100, 1, 1), (100, 1, None)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_zero_or_cap(self):
        self.assertEqual(bulk_price(0, 1, False), 0)
        self.assertEqual(bulk_price(0, 1000, True), 0)
        self.assertEqual(bulk_price(10000, 1000, True), 9650063)


if __name__ == "__main__":
    unittest.main()
