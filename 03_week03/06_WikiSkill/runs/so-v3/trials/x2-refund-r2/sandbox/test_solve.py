import unittest
from solve import refund


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_over_80(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_exactly_80(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_round_half_up(self):
        self.assertEqual(refund(1, 50, False), 1)  # 0.5 -> 1
        self.assertEqual(refund(3, 50, False), 2)  # 1.5 -> 2

    def test_single_rounding(self):
        # 101*0.5*0.875 = 44.1875 -> 44
        self.assertEqual(refund(101, 50, True), 44)

    def test_zero(self):
        self.assertEqual(refund(0, 0, True), 0)

    def test_invalid(self):
        for a in ((1.0, 0, False), (True, 0, False), (-1, 0, False),
                  (1, 101, False), (1, -1, False), (1, 0, 1), (1, "0", False)):
            with self.assertRaises(ValueError):
                refund(*a)


if __name__ == "__main__":
    unittest.main()
