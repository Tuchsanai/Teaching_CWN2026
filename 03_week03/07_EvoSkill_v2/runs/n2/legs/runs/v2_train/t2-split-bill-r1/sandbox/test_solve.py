"""รัน: python3 -m unittest -q test_solve"""
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(split_bill(9000, 3, 10), [3300, 3300, 3300])

    def test_normal_2(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_normal_3(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(split_bill(0, 1, 0), [0])

    def test_boundary_2(self):
        self.assertEqual(split_bill(0, 3, 100), [0, 0, 0])

    def test_boundary_3(self):
        self.assertEqual(split_bill(1000, 3, 100), [667, 667, 666])  # 2000


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(split_bill(5, 1, 10), [6])  # 5.5 -> 6

    def test_no_drift_2(self):
        self.assertEqual(split_bill(101, 4, 5), [27, 27, 26, 26])  # 106.05 -> 106

    def test_no_drift_3(self):
        self.assertEqual(split_bill(1, 3, 49), [1, 0, 0])  # 1.49 -> 1

    def test_sum_matches(self):
        r = split_bill(12345, 7, 13)  # 13949.85 -> 13950
        self.assertEqual(sum(r), 13950)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        for args in [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            split_bill(1000.0, 2, 10)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            split_bill("1000", 2, 10)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            split_bill(True, 2, 10)
        with self.assertRaises(ValueError):
            split_bill(1000, 2, 10.5)


if __name__ == "__main__":
    unittest.main()
