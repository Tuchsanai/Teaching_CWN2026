"""เทสต์ของเฉลยอ้างอิง: python3 -m unittest -q test_solve"""
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(split_bill(30000, 3, 0), [10000, 10000, 10000])

    def test_normal_2(self):
        self.assertEqual(split_bill(30000, 4, 10), [8250, 8250, 8250, 8250])

    def test_normal_3(self):
        self.assertEqual(split_bill(12000, 2, 5), [6300, 6300])


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(split_bill(0, 3, 10), [0, 0, 0])

    def test_boundary_2(self):
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])

    def test_boundary_3(self):
        self.assertEqual(split_bill(9999, 1, 0), [9999])


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_no_drift_2(self):
        self.assertEqual(split_bill(10000, 7, 10), [1572, 1572, 1572, 1571, 1571, 1571, 1571])


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            split_bill(10000, 0, 0)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            split_bill(10000, -2, 0)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            split_bill(10000.0, 2, 0)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            split_bill(10000, '3', 0)


if __name__ == "__main__":
    unittest.main()
