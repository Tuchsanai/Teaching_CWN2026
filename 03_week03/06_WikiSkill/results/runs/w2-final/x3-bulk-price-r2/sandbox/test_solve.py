import unittest
from solve import bulk_price


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10432.5 -> half up

    def test_boundary_exact(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)  # 103255.0
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_boundary_below(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 49, False), 505950)  # 505949.5

    def test_boundary_above(self):
        self.assertEqual(bulk_price(10000, 11, False), 113581)  # 113580.5
        self.assertEqual(bulk_price(10000, 51, True), 492153)

    def test_half_up(self):
        self.assertEqual(bulk_price(10000, 1, True), 10433)
        self.assertEqual(bulk_price(1, 1, False), 1)  # 1.07

    def test_reject_value(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False), (100, -5, True)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_reject_type(self):
        for args in [(100.0, 1, False), (100, 1.0, False), (True, 1, False),
                     (100, True, False), ("1", 1, False), (None, 1, False),
                     (100, 1, 1), (100, 1, None)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_zero_or_cap(self):
        self.assertEqual(bulk_price(0, 5, True), 0)
        self.assertEqual(bulk_price(10000, 1000, True), 9650063)  # 9650062.5


if __name__ == "__main__":
    unittest.main()
