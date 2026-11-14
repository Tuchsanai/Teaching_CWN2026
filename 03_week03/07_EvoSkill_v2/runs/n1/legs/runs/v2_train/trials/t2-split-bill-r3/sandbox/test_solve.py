"""python3 -m unittest -q test_solve"""
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_tip(self):
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 4, 0), [1, 1, 0, 0])

    def test_tip_100(self):
        self.assertEqual(sum(split_bill(12345, 7, 100)), 24690)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 1005*1.05 = 1055.25 -> 1055 ; 1010*1.05=1060.5 -> 1061
        self.assertEqual(split_bill(1010, 1, 5), [1061])
        self.assertEqual(split_bill(1005, 1, 5), [1055])

    def test_sum(self):
        for p in range(1, 12):
            self.assertEqual(sum(split_bill(9999, p, 7)), 10699)  # 9999*1.07=10698.93


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 1, 0), (1, 0, 0), (1, -1, 0), (1, 1, -1), (1, 1, 101),
               (1.0, 1, 0), (1, 1.0, 0), (1, 1, 1.0), ("1", 1, 0), (1, "1", 0),
               (1, 1, "0"), (None, 1, 0), (1, None, 0), (1, 1, None),
               (True, 1, 0), (1, True, 0), (1, 1, False)]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    split_bill(*args)


if __name__ == "__main__":
    unittest.main()
