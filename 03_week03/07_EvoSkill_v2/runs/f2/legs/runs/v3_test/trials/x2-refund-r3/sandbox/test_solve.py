import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(10000, 0, False), 10000)


class Boundary(unittest.TestCase):
    def test_80_81(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_zero(self):
        self.assertEqual(refund(0, 10, True), 0)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        self.assertEqual(refund(1, 0, True), 0)
        self.assertEqual(refund(3, 50, False), 1)
        self.assertEqual(refund(999, 33, True), 585)  # 669.33*0.875=585.66


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 0, False), (1.0, 0, False), ("1", 0, False), (True, 0, False),
                  (1, -1, False), (1, 101, False), (1, 5.0, False), (1, True, False),
                  (1, 0, 1), (1, 0, None), (-1, 90, False)]:
            with self.assertRaises(ValueError):
                refund(*a)


if __name__ == "__main__":
    unittest.main()
