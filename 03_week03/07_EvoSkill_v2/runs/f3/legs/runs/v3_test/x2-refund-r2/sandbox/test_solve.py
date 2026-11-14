import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_half(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_unused(self):
        self.assertEqual(refund(8000, 0, True), 7000)


class Boundary(unittest.TestCase):
    def test_at_80(self):
        self.assertEqual(refund(1000, 80, False), 200)

    def test_over_80(self):
        self.assertEqual(refund(1000, 81, False), 0)

    def test_used_100(self):
        self.assertEqual(refund(1000, 100, True), 0)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_floor_half(self):
        self.assertEqual(refund(1001, 50, False), 500)  # 500.5 -> 500

    def test_floor_restock(self):
        self.assertEqual(refund(999, 33, True), 585)  # 585.66 -> 585

    def test_tiny(self):
        self.assertEqual(refund(1, 0, False), 1)
        self.assertEqual(refund(1, 0, True), 0)  # 0.875 -> 0


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
        for args in [(-1, 10, False), (100, -1, False), (100, 101, False)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_bool_int(self):
        with self.assertRaises(ValueError):
            refund(True, 10, False)

    def test_validate_before_shortcut(self):
        with self.assertRaises(ValueError):
            refund(100, 90, "x")


if __name__ == "__main__":
    unittest.main()
