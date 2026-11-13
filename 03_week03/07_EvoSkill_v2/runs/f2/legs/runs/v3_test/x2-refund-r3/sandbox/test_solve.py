import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_zero_used(self):
        self.assertEqual(refund(8000, 0, True), 7000)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_81(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_100_and_zero_paid(self):
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(0, 10, True), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(refund(1, 50, False), 1)    # 0.5 -> 1
        self.assertEqual(refund(100, 50, True), 44)  # 43.75 -> 44
        self.assertEqual(refund(4, 0, True), 4)      # 3.5 -> 4
        self.assertEqual(refund(3, 50, False), 2)    # 1.5 -> 2


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 10, False), (100, -1, False), (100, 101, False),
                  (100.0, 10, False), ("3", 10, False), (True, 10, False),
                  (100, 10.0, False), (100, True, False), (100, 10, 1),
                  (100, 10, None)]:
            with self.assertRaises(ValueError):
                refund(*a)


if __name__ == "__main__":
    unittest.main()
