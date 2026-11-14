"""รัน: python3 -m unittest -q test_solve"""
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_normal_1(self):
        # 10000+10% = 11000 ; 11000/3 = 3666 เศษ 2
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_normal_2(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_normal_3(self):
        self.assertEqual(split_bill(9000, 3, 0), [3000, 3000, 3000])


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(split_bill(0, 2, 50), [0, 0])  # ยอด 0

    def test_boundary_2(self):
        self.assertEqual(split_bill(101, 1, 100), [202])  # tip 100, 1 คน

    def test_boundary_3(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])  # คนมากกว่ายอด


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        # 1*1.5 = 1.5 -> half-up 2 -> [1,1]
        self.assertEqual(split_bill(1, 2, 50), [1, 1])

    def test_no_drift_2(self):
        # 1*1.49 = 1.49 -> 1 -> [1,0]
        self.assertEqual(split_bill(1, 2, 49), [1, 0])

    def test_no_drift_3(self):
        # 15*1.1 = 16.5 -> 17
        self.assertEqual(split_bill(15, 1, 10), [17])

    def test_sum_matches(self):
        self.assertEqual(sum(split_bill(12345, 7, 13)), 13950)  # 12345*1.13=13949.85


class Reject(unittest.TestCase):
    def test_reject_1(self):
        for args in [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            split_bill(100.0, 2, 10)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            split_bill("100", 2, 10)

    def test_reject_4(self):
        for args in [(True, 1, 0), (10, True, 0), (10, 1, False), (10, 2, 5.0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
