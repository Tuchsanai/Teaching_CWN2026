"""python3 -m unittest -q test_solve"""
import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_half_used(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_81(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_zero_and_full(self):
        self.assertEqual(refund(0, 0, True), 0)
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(10000, 100, True), 0)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        self.assertEqual(refund(1001, 0, True), 875)  # 875.875 ปัดลง
        self.assertEqual(refund(1, 50, False), 0)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 0, False), (100, -1, False), (100, 101, False),
                     (100.0, 0, False), ("1", 0, False), (True, 0, False), (None, 0, False),
                     (100, 50.0, False), (100, True, False), (100, "5", False),
                     (100, 50, 1), (100, 50, "yes"), (100, 50, None), (100, 90, 1)]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    refund(*args)


if __name__ == "__main__":
    unittest.main()
