"""python3 -m unittest -q test_solve"""
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

    def test_100(self):
        self.assertEqual(refund(10000, 100, True), 0)

    def test_paid_zero(self):
        self.assertEqual(refund(0, 10, True), 0)


class NoDrift(unittest.TestCase):
    def test_floor_half(self):
        self.assertEqual(refund(1, 50, False), 0)  # 0.5 -> floor 0

    def test_floor_restock(self):
        self.assertEqual(refund(999, 33, True), 585)  # 999*.67*.875=585.64..

    def test_floor_51(self):
        self.assertEqual(refund(101, 50, False), 50)  # 50.5 -> 50


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 10, False), (1.0, 10, False), ('1', 10, False), (True, 10, False), (None, 10, False),
               (100, -1, False), (100, 101, False), (100, 10.0, False), (100, '10', False),
               (100, True, False), (100, None, False),
               (100, 10, 1), (100, 10, 0), (100, 10, 'yes'), (100, 10, None),
               (100, 90, 1)]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    refund(*args)


if __name__ == "__main__":
    unittest.main()
