import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(0, 0, True), 0)


class Boundary(unittest.TestCase):
    def test_edges(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(10000, 0, False), 10000)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(refund(1, 50, False), 1)      # 0.5 -> 1
        self.assertEqual(refund(4, 0, True), 4)        # 3.5 -> 4
        self.assertEqual(refund(10001, 0, True), 8751)  # 8750.875


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(100.0, 0, False), ("1", 0, False), (-1, 0, False), (True, 0, False),
                  (None, 0, False), (100, 101, False), (100, -1, False), (100, 5.0, False),
                  (100, True, False), (100, 0, 1), (100, 0, None), (100, 90, "yes"),
                  (-5, 90, False)]:
            with self.assertRaises(ValueError):
                refund(*a)


if __name__ == "__main__":
    unittest.main()
