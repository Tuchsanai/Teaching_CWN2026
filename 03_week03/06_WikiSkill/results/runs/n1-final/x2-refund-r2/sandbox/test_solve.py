import unittest
from solve import refund


class TestRefund(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_boundary_below(self):
        self.assertEqual(refund(10000, 79, False), 2100)

    def test_boundary_at(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_half_up(self):
        # 1*50/100 = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 401*50/100 = 200.5 -> 201
        self.assertEqual(refund(401, 50, False), 201)
        # 3*7/8 = 2.625 -> 3
        self.assertEqual(refund(3, 0, True), 3)

    def test_restock_fee(self):
        self.assertEqual(refund(10000, 50, True), 4375)
        # 4*(100)*7/800 = 3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)
        # 1*7/8 = 0.875 -> 1 ; 0 paid -> 0
        self.assertEqual(refund(1, 0, True), 1)
        self.assertEqual(refund(0, 0, True), 0)

    def test_reject_range(self):
        with self.assertRaises(ValueError):
            refund(-1, 10, False)
        with self.assertRaises(ValueError):
            refund(100, -1, False)
        with self.assertRaises(ValueError):
            refund(100, 101, False)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            refund(100.0, 10, False)
        with self.assertRaises(ValueError):
            refund(100, 10.0, False)

    def test_reject_bool_or_type(self):
        with self.assertRaises(ValueError):
            refund(True, 10, False)
        with self.assertRaises(ValueError):
            refund(100, False, False)
        with self.assertRaises(ValueError):
            refund(100, 10, 1)
        with self.assertRaises(ValueError):
            refund("100", 10, False)
        with self.assertRaises(ValueError):
            refund(100, None, True)


if __name__ == "__main__":
    unittest.main()
