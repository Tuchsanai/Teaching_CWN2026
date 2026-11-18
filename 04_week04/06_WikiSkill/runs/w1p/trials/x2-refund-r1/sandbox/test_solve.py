import unittest
from solve import refund


class TestRefund(unittest.TestCase):
    def test_normal_no_restock(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_with_restock(self):
        # 5000 - 12.5% = 4375
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_zero_used_full_refund(self):
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 10, True), 0)

    def test_boundary_80_refunds(self):
        # สมมติ: เรียน 80% พอดี "ไม่เกิน 80" จึงยังคืน
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_boundary_81_no_refund(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_boundary_100_no_refund(self):
        self.assertEqual(refund(10000, 100, True), 0)

    def test_rounding_down(self):
        # 101*50/100=50.5 -> 50 ; restock: 50.5*0.875=44.1875 -> 44
        self.assertEqual(refund(101, 50, False), 50)
        self.assertEqual(refund(101, 50, True), 44)

    def test_result_is_int(self):
        self.assertIs(type(refund(999, 33, True)), int)

    def test_reject_paid(self):
        for bad in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                refund(bad, 10, False)

    def test_reject_used_percent(self):
        for bad in (-1, 101, 10.0, True, "10", None):
            with self.assertRaises(ValueError):
                refund(100, bad, False)

    def test_reject_restock(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                refund(100, 10, bad)


if __name__ == "__main__":
    unittest.main()
