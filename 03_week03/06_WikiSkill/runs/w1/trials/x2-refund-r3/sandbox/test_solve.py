import unittest
from solve import refund


class TestRefund(unittest.TestCase):
    def test_normal_no_restock(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_unused_full(self):
        self.assertEqual(refund(8000, 0, False), 8000)

    def test_boundary_80_refunds(self):
        # สมมติ: "เกิน 80%" = มากกว่า 80 ดังนั้น 80 ยังได้คืน
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_boundary_81_zero(self):
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_rounding_half_up(self):
        # 1*99/100 = 0.99 -> 1 ; 5*50/100=2.5 -> 3 (half-up)
        self.assertEqual(refund(1, 1, False), 1)
        self.assertEqual(refund(5, 50, False), 3)
        self.assertEqual(refund(10, 50, True), 4)  # 4.375 -> 4

    def test_zero_paid(self):
        self.assertEqual(refund(0, 10, True), 0)

    def test_result_is_int(self):
        self.assertIs(type(refund(999, 33, True)), int)

    def test_invalid_paid(self):
        for bad in (-1, 100.0, True, "5", None):
            with self.assertRaises(ValueError):
                refund(bad, 10, False)

    def test_invalid_used(self):
        for bad in (-1, 101, 10.0, True, "5", None):
            with self.assertRaises(ValueError):
                refund(100, bad, False)

    def test_invalid_restock(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                refund(100, 10, bad)


if __name__ == "__main__":
    unittest.main()
