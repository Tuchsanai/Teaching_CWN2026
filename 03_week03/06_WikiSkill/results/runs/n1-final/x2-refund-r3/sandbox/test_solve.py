import unittest
from solve import refund


class TestRefund(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(1000, 50, False), 500)
        self.assertEqual(refund(1000, 0, True), 875)

    def test_boundary_below(self):
        self.assertEqual(refund(1000, 79, False), 210)

    def test_boundary_at(self):
        self.assertEqual(refund(1000, 80, False), 200)
        self.assertEqual(refund(1000, 81, False), 0)

    def test_half_up(self):
        # 1001*50/100 = 500.5 -> 501
        self.assertEqual(refund(1001, 50, False), 501)
        # 4*7/8 = 3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)

    def test_reject_range(self):
        for args in [(-1, 0, False), (10, -1, False), (10, 101, True)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            refund(1000.0, 10, False)
        with self.assertRaises(ValueError):
            refund(1000, 10.0, False)

    def test_reject_bool_or_type(self):
        with self.assertRaises(ValueError):
            refund(True, 10, False)
        with self.assertRaises(ValueError):
            refund(1000, 10, 1)
        with self.assertRaises(ValueError):
            refund(None, 10, False)

    def test_combined(self):
        # 1000*0.5*0.875 = 437.5 -> 438
        self.assertEqual(refund(1000, 50, True), 438)
        self.assertEqual(refund(1000, 90, True), 0)


if __name__ == "__main__":
    unittest.main()
