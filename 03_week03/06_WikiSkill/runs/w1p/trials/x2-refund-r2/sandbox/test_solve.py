import unittest
from solve import refund


class TestSolve(unittest.TestCase):
    def test_normal_no_restock(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_restock(self):
        # 10000*50% = 5000; หัก 12.5% -> 4375
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_unused_full(self):
        self.assertEqual(refund(8000, 0, False), 8000)
        self.assertEqual(refund(8000, 0, True), 7000)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 10, True), 0)

    def test_edge_80_refunds(self):
        # พอดี 80% ยังคืน (เกิน 80 ถึงไม่คืน): 1000*20% = 200
        self.assertEqual(refund(1000, 80, False), 200)

    def test_edge_81_no_refund(self):
        self.assertEqual(refund(1000, 81, False), 0)

    def test_edge_79(self):
        self.assertEqual(refund(1000, 79, False), 210)

    def test_edge_100(self):
        self.assertEqual(refund(1000, 100, True), 0)

    def test_rounding_down(self):
        # 101*50% = 50.5 -> 50 ; restock: 101*50*7/800 = 44.1875 -> 44
        self.assertEqual(refund(101, 50, False), 50)
        self.assertEqual(refund(101, 50, True), 44)

    def test_result_is_int(self):
        self.assertIs(type(refund(101, 33, True)), int)
        self.assertIs(type(refund(101, 90, False)), int)

    def test_reject_paid(self):
        for bad in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                refund(bad, 10, False)

    def test_reject_used_percent(self):
        for bad in (-1, 101, 50.0, True, "50", None):
            with self.assertRaises(ValueError):
                refund(100, bad, False)

    def test_reject_restock(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                refund(100, 10, bad)


if __name__ == "__main__":
    unittest.main()
