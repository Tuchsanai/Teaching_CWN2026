import unittest
from solve import refund


class TestSolve(unittest.TestCase):
    def test_normal_no_restock(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_unused_full(self):
        self.assertEqual(refund(8000, 0, False), 8000)

    def test_unused_full_restock(self):
        self.assertEqual(refund(8000, 0, True), 7000)

    def test_edge_80_refunds(self):
        # สมมติ: 80% พอดี ยังคืน (ไม่ "เกิน" 80)
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_edge_81_none(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_edge_100_and_zero_paid(self):
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(0, 10, True), 0)

    def test_rounding_half_up(self):
        # 1*99/100*0.875 = 0.866 -> 1 ; 10*50%*0.875=4.375 -> 4 ; 2*50%=1 ; 1*50%=0.5 -> 1 (half up)
        self.assertEqual(refund(1, 1, True), 1)
        self.assertEqual(refund(10, 50, True), 4)
        self.assertEqual(refund(1, 50, False), 1)

    def test_result_is_int(self):
        self.assertIs(type(refund(1234, 33, True)), int)
        self.assertIs(type(refund(1234, 90, True)), int)

    def test_reject_paid(self):
        for v in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                refund(v, 10, False)

    def test_reject_used_percent(self):
        for v in (-1, 101, 10.0, True, "10", None):
            with self.assertRaises(ValueError):
                refund(100, v, False)

    def test_reject_restock(self):
        for v in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                refund(100, 10, v)


if __name__ == "__main__":
    unittest.main()
