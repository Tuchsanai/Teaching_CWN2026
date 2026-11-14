import unittest

from solve import refund


class RefundTests(unittest.TestCase):
    def test_no_usage_no_restock_full_refund(self):
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_proportional_refund(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(1000, 33, False), 670)

    def test_restock_fee_applied(self):
        # 10000 * 50% = 5000, หักค่าดำเนินการ 12.5% -> 4375
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_cutoff_boundary(self):
        self.assertEqual(refund(10000, 80, False), 2000)  # 80% ยังคืนได้
        self.assertEqual(refund(10000, 81, False), 0)     # เกิน 80% ไม่คืน
        self.assertEqual(refund(10000, 100, True), 0)

    def test_rounding_down_on_restock(self):
        # 999 * 7/8 = 874.125 -> 874
        self.assertEqual(refund(999, 0, True), 874)
        # 1003 * 7/8 = 877.625 -> 877 (ปัดลง ไม่ใช่ 878)
        self.assertEqual(refund(1003, 0, True), 877)
        # 1 * 7/8 = 0.875 -> 0
        self.assertEqual(refund(1, 0, True), 0)

    def test_rounding_down_on_half_satang(self):
        # 10 * 55% = 5.5 -> 5
        self.assertEqual(refund(10, 45, False), 5)

    def test_restock_with_partial_usage(self):
        # 1000 * 99% = 990, *7/8 = 866.25 -> 866
        self.assertEqual(refund(1000, 1, True), 866)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 0, True), 0)
        self.assertEqual(refund(0, 50, False), 0)

    def test_invalid_types_rejected(self):
        bad_calls = [
            (True, 0, False),        # bool ไม่ใช่ int
            (1000.0, 0, False),      # float
            ("1000", 0, False),      # string
            (1000, True, False),
            (1000, 50.0, False),
            (1000, "50", False),
            (1000, 0, 1),            # restock ต้องเป็น bool
            (1000, 0, None),
        ]
        for args in bad_calls:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    refund(*args)

    def test_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            refund(-1, 0, False)
        with self.assertRaises(ValueError):
            refund(1000, -1, False)
        with self.assertRaises(ValueError):
            refund(1000, 101, False)


if __name__ == "__main__":
    unittest.main()
