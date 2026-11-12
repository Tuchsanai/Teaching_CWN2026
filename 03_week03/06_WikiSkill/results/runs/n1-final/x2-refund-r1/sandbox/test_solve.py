import unittest
from solve import refund


class TestRefund(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_boundary_below(self):
        self.assertEqual(refund(10000, 79, False), 2100)

    def test_boundary_at(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 80, True), 1750)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_half_up(self):
        # 1*50/100 = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 10*90... used 20: 10*80*7/800 = 7.0 ; paid 1 used 0 restock: 0.875 -> 1
        self.assertEqual(refund(1, 0, True), 1)
        # 4*50*7/800 = 1.75 -> 2 ; 2*50*7/800=0.875 -> 1; 1*... 
        self.assertEqual(refund(4, 50, True), 2)
        # paid 1, used 40: 60*7/800 = 0.525 -> 1 ; used 60: 0.35 -> 0
        self.assertEqual(refund(1, 40, True), 1)
        self.assertEqual(refund(1, 60, True), 0)

    def test_reject_range(self):
        for args in [(-1, 10, False), (100, -1, False), (100, 101, True)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            refund(100.0, 10, False)
        with self.assertRaises(ValueError):
            refund(100, 10.0, False)

    def test_reject_bool_or_type(self):
        for args in [(True, 10, False), (100, True, False), (100, 10, 1),
                     ("100", 10, False), (100, None, False), (100, 10, None)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 0, True), 0)


if __name__ == "__main__":
    unittest.main()
