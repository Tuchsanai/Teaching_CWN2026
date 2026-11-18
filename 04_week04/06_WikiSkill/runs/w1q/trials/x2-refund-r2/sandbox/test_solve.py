import unittest
from solve import refund


class TestSolve(unittest.TestCase):
    def test_normal_no_fee(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_with_fee(self):
        # 10000*0.5=5000 ; หัก 12.5% -> 4375
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_unused_full(self):
        self.assertEqual(refund(8000, 0, True), 7000)
        self.assertEqual(refund(8000, 0, False), 8000)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 10, True), 0)

    def test_edge_80_percent_refunds(self):
        # พอดี 80% ยังได้คืน: 1000*0.2=200
        self.assertEqual(refund(1000, 80, False), 200)

    def test_edge_81_percent_no_refund(self):
        self.assertEqual(refund(1000, 81, False), 0)
        self.assertEqual(refund(1000, 100, True), 0)

    def test_edge_79_percent(self):
        self.assertEqual(refund(1000, 79, False), 210)

    def test_rounding_half_up(self):
        # 101*0.5=50.5 -> 51 (สมมติปัดครึ่งขึ้น)
        self.assertEqual(refund(101, 50, False), 51)
        # 1*0.99*0.875=0.86625 -> 1
        self.assertEqual(refund(1, 1, True), 1)
        # 3*0.9*0.875=2.3625 -> 2
        self.assertEqual(refund(3, 10, True), 2)

    def test_result_is_int(self):
        self.assertIs(type(refund(999, 33, True)), int)
        self.assertIs(type(refund(999, 90, True)), int)

    def test_reject_paid(self):
        for v in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                refund(v, 10, False)

    def test_reject_used_percent(self):
        for v in (-1, 101, 10.0, True, "10", None):
            with self.assertRaises(ValueError):
                refund(1000, v, False)

    def test_reject_restock(self):
        for v in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                refund(1000, 10, v)


if __name__ == "__main__":
    unittest.main()
