"""python3 -m unittest -q test_solve"""
import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_half_no_restock(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_half_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_zero_used(self):
        self.assertEqual(refund(10000, 0, False), 10000)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(refund(1000, 80, False), 200)

    def test_81(self):
        self.assertEqual(refund(1000, 81, False), 0)

    def test_100(self):
        self.assertEqual(refund(1000, 100, True), 0)

    def test_paid_zero(self):
        self.assertEqual(refund(0, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_floor_874_125(self):
        self.assertEqual(refund(999, 0, True), 874)

    def test_floor_875_875(self):
        self.assertEqual(refund(1001, 0, True), 875)  # ปัดลง ไม่ใช่ 876

    def test_floor_no_restock(self):
        self.assertEqual(refund(999, 33, False), 669)  # 669.33


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 0, False), (4500.0, 0, False), ('1', 0, False), (True, 0, False), (None, 0, False),
               (100, -1, False), (100, 101, False), (100, 5.0, False), (100, '5', False), (100, True, False),
               (100, None, False), (100, 5, 1), (100, 5, 0), (100, 5, 'yes'), (100, 5, None)]
        for args in bad:
            with self.assertRaises(ValueError, msg=str(args)):
                refund(*args)

    def test_reject_even_when_over_80(self):
        with self.assertRaises(ValueError):
            refund(100, 90, 1)


if __name__ == "__main__":
    unittest.main()
