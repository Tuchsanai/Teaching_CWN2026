"""รัน: python3 -m unittest -q test_solve"""
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(split_bill(1000, 3, 10), [367, 367, 366])  # 1100/3

    def test_normal_2(self):
        self.assertEqual(split_bill(1200, 4, 0), [300] * 4)

    def test_normal_3(self):
        self.assertEqual(split_bill(1001, 2, 5), [526, 525])  # 1051.05 -> 1051


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_boundary_2(self):
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_boundary_3(self):
        self.assertEqual(split_bill(5, 7, 0), [1] * 5 + [0] * 2)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(split_bill(10, 1, 5), [11])  # 10.5 -> 11 (half-up)

    def test_no_drift_2(self):
        self.assertEqual(split_bill(999, 4, 1), [253, 252, 252, 252])  # 1008.99 -> 1009

    def test_no_drift_3(self):
        self.assertEqual(split_bill(1, 1, 50), [2])  # 1.5 -> 2

    def test_sum_equals_total(self):
        self.assertEqual(sum(split_bill(9999, 7, 13)), 11299)  # 9999*1.13=11298.87


class Reject(unittest.TestCase):
    def test_reject_1(self):
        for args in [(-1, 2, 0), (10, 0, 0), (10, -1, 0), (10, 2, -1), (10, 2, 101)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_reject_2(self):
        for args in [(10.0, 2, 0), (10, 2.0, 0), (10, 2, 5.0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_reject_3(self):
        for args in [("10", 2, 0), (10, "2", 0), (10, 2, "5")]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_reject_4(self):
        for args in [(True, 2, 0), (10, True, 0), (10, 2, False)]:
            with self.assertRaises(ValueError):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
