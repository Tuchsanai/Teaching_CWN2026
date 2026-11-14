import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_zero_used(self):
        self.assertEqual(refund(10000, 0, False), 10000)


class Boundary(unittest.TestCase):
    def test_at_80(self):
        self.assertEqual(refund(1000, 80, False), 200)

    def test_over_80(self):
        self.assertEqual(refund(1000, 81, False), 0)

    def test_100(self):
        self.assertEqual(refund(1000, 100, True), 0)

    def test_paid_zero(self):
        self.assertEqual(refund(0, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_floor_plain(self):
        self.assertEqual(refund(999, 33, False), 669)  # 669.33

    def test_floor_restock(self):
        self.assertEqual(refund(999, 33, True), 585)  # 585.66

    def test_small(self):
        self.assertEqual(refund(1, 0, True), 0)  # 0.875

    def test_single_round(self):
        self.assertEqual(refund(100, 1, True), 86)  # 86.625


class Reject(unittest.TestCase):
    def test_float(self):
        with self.assertRaises(ValueError):
            refund(100.0, 10, False)

    def test_str(self):
        with self.assertRaises(ValueError):
            refund(100, "10", False)

    def test_bool_flag(self):
        with self.assertRaises(ValueError):
            refund(100, 10, 1)

    def test_range(self):
        for a in [(-1, 10, False), (100, -1, False), (100, 101, False), (True, 10, False), (100, None, True)]:
            with self.assertRaises(ValueError):
                refund(*a)

    def test_reject_before_shortcut(self):
        with self.assertRaises(ValueError):
            refund(100, 90, "no")


if __name__ == "__main__":
    unittest.main()
