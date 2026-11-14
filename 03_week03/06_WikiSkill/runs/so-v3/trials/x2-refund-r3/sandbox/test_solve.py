import unittest
from solve import refund


class TestRefund(unittest.TestCase):
    def test_no_restock(self):
        self.assertEqual(refund(10000, 25, False), 7500)

    def test_restock_fee(self):
        self.assertEqual(refund(10000, 0, True), 8750)

    def test_over_80_zero(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_exactly_80(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_round_half_up(self):
        # 1 * 50/100 = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 1 * 99/100 *0.875 = 0.866 -> 1 ; 3*50/100*.875=1.3125 -> 1
        self.assertEqual(refund(3, 50, True), 1)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 0, True), 0)

    def test_invalid(self):
        for args in [(1.5, 0, False), (True, 0, False), (-1, 0, False),
                     (1, 101, False), (1, -1, False), (1, 0, 1),
                     ("1", 0, False), (1, None, False), (1, 10.0, False)]:
            with self.assertRaises(ValueError):
                refund(*args)


if __name__ == "__main__":
    unittest.main()
