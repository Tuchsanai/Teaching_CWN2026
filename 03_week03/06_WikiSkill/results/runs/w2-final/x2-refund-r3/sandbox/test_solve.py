import unittest
from solve import refund


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(1000, 50, False), 500)
        self.assertEqual(refund(1000, 0, False), 1000)

    def test_boundary_exact(self):
        self.assertEqual(refund(1000, 80, False), 200)

    def test_boundary_below(self):
        self.assertEqual(refund(1000, 79, False), 210)

    def test_boundary_above(self):
        self.assertEqual(refund(1000, 81, False), 0)
        self.assertEqual(refund(1000, 100, True), 0)

    def test_half_up(self):
        self.assertEqual(refund(1000, 50, True), 438)   # 437.5
        self.assertEqual(refund(1, 50, False), 1)       # 0.5

    def test_reject_value(self):
        for args in [(-1, 10, False), (100, -1, False), (100, 101, True)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_reject_type(self):
        for args in [(1000.0, 10, False), (100, 10.0, False), (True, 10, False),
                     ("100", 10, False), (100, 10, None), (100, 10, 1), (None, 1, True)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_zero_or_cap(self):
        self.assertEqual(refund(0, 0, True), 0)
        self.assertEqual(refund(0, 90, False), 0)

    def test_restock_value(self):
        self.assertEqual(refund(800, 0, True), 700)


if __name__ == "__main__":
    unittest.main()
