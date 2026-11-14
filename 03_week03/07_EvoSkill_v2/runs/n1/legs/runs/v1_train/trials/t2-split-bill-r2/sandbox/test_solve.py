"""python3 -m unittest -q test_solve"""
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_tip(self):
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 105*110/100 = 115.5 -> 116
        self.assertEqual(split_bill(105, 1, 10), [116])

    def test_below_half(self):
        # 101*105/100 = 106.05 -> 106
        self.assertEqual(split_bill(101, 1, 5), [106])

    def test_sum(self):
        r = split_bill(12345, 7, 13)
        self.assertEqual(sum(r), 13950)  # 12345*1.13=13949.85
        self.assertLessEqual(max(r) - min(r), 1)


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 1, 0), (1, 0, 0), (1, -1, 0), (1, 1, -1), (1, 1, 101),
               (1.0, 1, 0), (1, 1.0, 0), (1, 1, 5.0), ('1', 1, 0), (1, '1', 0),
               (1, 1, '5'), (True, 1, 0), (1, True, 0), (1, 1, True),
               (None, 1, 0), (1, None, 0), (1, 1, None)]
        for a in bad:
            with self.subTest(a=a), self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
