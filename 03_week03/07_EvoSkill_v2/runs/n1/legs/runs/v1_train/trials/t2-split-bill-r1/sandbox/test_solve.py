"""python3 -m unittest -q test_solve"""
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_tip(self):
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])

    def test_remainder_first(self):
        self.assertEqual(split_bill(10, 3, 0), [4, 3, 3])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_tip_100(self):
        self.assertEqual(split_bill(101, 2, 100), [101, 101])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 105*107... tip 5%: 10*105/100 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_below_half(self):
        # 101*5%: 101*1.05=106.05 -> 106
        self.assertEqual(split_bill(101, 1, 5), [106])

    def test_above_half(self):
        # 109*1.05=114.45 -> 114 ; 111*1.05=116.55 -> 117
        self.assertEqual(split_bill(109, 1, 5), [114])
        self.assertEqual(split_bill(111, 1, 5), [117])

    def test_sum_exact(self):
        r = split_bill(12345, 7, 13)
        self.assertEqual(sum(r), 13950)  # 12345*1.13=13949.85 -> 13950
        self.assertLessEqual(max(r) - min(r), 1)


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [0, -1, 1.0, "3", None, True]
        for v in [-1, 1.0, "3", None, True]:
            with self.assertRaises(ValueError):
                split_bill(v, 2, 0)
        for v in bad:
            with self.assertRaises(ValueError):
                split_bill(100, v, 0)
        for v in [-1, 101, 5.0, "5", None, True]:
            with self.assertRaises(ValueError):
                split_bill(100, 2, v)


if __name__ == "__main__":
    unittest.main()
