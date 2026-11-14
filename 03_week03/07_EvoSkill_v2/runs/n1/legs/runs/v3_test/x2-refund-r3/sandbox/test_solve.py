import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_no_restock(self):
        self.assertEqual(refund(10000, 30, False), 7000)  # 10000*70%

    def test_restock(self):
        self.assertEqual(refund(10000, 30, True), 6125)  # 7000*0.875

    def test_unused_full(self):
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(10000, 0, True), 8750)

    def test_fully_used(self):
        self.assertEqual(refund(10000, 100, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 10, True), 0)


class Boundary(unittest.TestCase):
    def test_exactly_80_refunds(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 80, True), 1750)

    def test_81_no_refund(self):
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 81, True), 0)

    def test_79(self):
        self.assertEqual(refund(10000, 79, False), 2100)


class NoDrift(unittest.TestCase):
    def test_floor_not_half_up(self):
        self.assertEqual(refund(1, 50, False), 0)  # 0.5 -> 0
        self.assertEqual(refund(3, 50, False), 1)  # 1.5 -> 1

    def test_restock_floor(self):
        self.assertEqual(refund(99, 0, True), 86)  # 86.625 -> 86
        self.assertEqual(refund(1001, 33, True), 586)  # 1001*.67=670.67*.875=586.836

    def test_single_rounding(self):
        # 101*0.99=99.99 ; *0.875=87.49125 -> 87 (ปัดกลางทางเป็น 99 จะได้ 86)
        self.assertEqual(refund(101, 1, True), 87)


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            refund(*a)

    def test_paid(self):
        for v in (-1, 1.5, 100.0, "100", True, None):
            self.bad(v, 10, False)

    def test_used(self):
        for v in (-1, 101, 10.0, 10.5, "10", True, False, None):
            self.bad(100, v, False)

    def test_restock(self):
        for v in (0, 1, "yes", None, 1.0):
            self.bad(100, 10, v)

    def test_invalid_even_when_no_refund(self):
        self.bad(100, 90, "x")
        self.bad(-5, 90, False)


if __name__ == "__main__":
    unittest.main()
