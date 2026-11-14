"""python3 -m unittest -q test_solve"""
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_tip(self):
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])

    def test_remainder(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(12345, 1, 100), [24690])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_sum_matches(self):
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), 11299)  # 9999*1.13=11298.87 -> 11299
        self.assertEqual(len(r), 7)


class NoDrift(unittest.TestCase):
    def test_half_up_exact_half(self):
        self.assertEqual(split_bill(1050, 1, 5), [1103])  # 1102.5 -> 1103

    def test_below_half(self):
        self.assertEqual(split_bill(1049, 1, 5), [1101])  # 1101.45

    def test_above_half(self):
        self.assertEqual(split_bill(1051, 1, 5), [1104])  # 1103.55


class Reject(unittest.TestCase):
    def check(self, *a):
        with self.assertRaises(ValueError):
            split_bill(*a)

    def test_bad_total(self):
        for v in (-1, 100.0, "100", True, None):
            self.check(v, 2, 10)

    def test_bad_people(self):
        for v in (0, -1, 2.0, "2", True, None):
            self.check(100, v, 10)

    def test_bad_tip(self):
        for v in (-1, 101, 10.0, "10", True, None):
            self.check(100, 2, v)


if __name__ == "__main__":
    unittest.main()
