import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_no_restock(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_unused(self):
        self.assertEqual(refund(8000, 0, True), 7000)


class Boundary(unittest.TestCase):
    def test_80_refunds(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_81_none(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_100_and_zero_paid(self):
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(0, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 1 * 50% = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 1 * 87.5% = 0.875 -> 1
        self.assertEqual(refund(1, 0, True), 1)
        # 10 * 0.5 * 0.875 = 4.375 -> 4
        self.assertEqual(refund(10, 50, True), 4)
        # 4 * 0.875 = 3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)

    def test_single_rounding(self):
        # 99*0.75*0.875 = 64.96875 -> 65
        self.assertEqual(refund(99, 25, True), 65)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 0, False), (100, -1, False), (100, 101, False),
                     (100.0, 0, False), ("100", 0, False), (True, 0, False),
                     (100, 50.0, False), (100, True, False),
                     (100, 0, 1), (100, 0, None), (None, 0, False)]:
            with self.assertRaises(ValueError, msg=str(args)):
                refund(*args)


if __name__ == "__main__":
    unittest.main()
