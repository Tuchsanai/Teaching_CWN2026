import unittest
from solve import refund


class TestSolve(unittest.TestCase):
    def test_normal_no_restock(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_restock(self):
        # 10000*50% = 5000 ; หัก 12.5% => 4375
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_unused_full(self):
        self.assertEqual(refund(8000, 0, False), 8000)
        self.assertEqual(refund(8000, 0, True), 7000)

    def test_edge_80_refunds(self):
        # สมมติ: เกิน 80% จึงไม่คืน; 80 พอดียังคืน
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_edge_81_zero(self):
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 81, True), 0)

    def test_edge_100_zero(self):
        self.assertEqual(refund(10000, 100, True), 0)

    def test_paid_zero(self):
        self.assertEqual(refund(0, 10, True), 0)

    def test_rounding_half_up(self):
        # 1*50/100 = 0.5 -> 1 (สมมติครึ่งปัดขึ้น)
        self.assertEqual(refund(1, 50, False), 1)
        # 999*70% = 699.3 -> 699 ; *7/8 = 611.8875 -> 612
        self.assertEqual(refund(999, 30, False), 699)
        self.assertEqual(refund(999, 30, True), 612)

    def test_result_is_int(self):
        self.assertIs(type(refund(999, 30, True)), int)
        self.assertIs(type(refund(10, 90, False)), int)

    def test_reject_paid(self):
        for v in (-1, 4500.0, True, "100", None):
            with self.assertRaises(ValueError):
                refund(v, 10, False)

    def test_reject_used_percent(self):
        for v in (-1, 101, 50.0, True, "50", None):
            with self.assertRaises(ValueError):
                refund(1000, v, False)

    def test_reject_restock(self):
        for v in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                refund(1000, 10, v)


if __name__ == "__main__":
    unittest.main()
