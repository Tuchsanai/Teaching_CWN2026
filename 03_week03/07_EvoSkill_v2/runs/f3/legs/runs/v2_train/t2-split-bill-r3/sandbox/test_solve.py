import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 2, 0), [5000, 5000])

    def test_tip_remainder(self):
        # 10000*1.10 = 11000 -> 3667,3667,3666
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_single(self):
        self.assertEqual(split_bill(1000, 1, 100), [2000])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_half_satang_rounds_up(self):
        # 1005*1.10 = 1105.5 -> 1106 -> 553,553
        self.assertEqual(split_bill(1005, 2, 10), [553, 553])

    def test_more_people_than_satang(self):
        # 1*1.5 = 1.5 -> 2 -> [1,1,0]
        self.assertEqual(split_bill(1, 3, 50), [1, 1, 0])


class NoDrift(unittest.TestCase):
    def test_sum_equals_grand(self):
        self.assertEqual(sum(split_bill(99999, 7, 15)), 114999)  # 99999*1.15=114998.85
        self.assertEqual(split_bill(99999, 7, 15), [16429] * 3 + [16428] * 4)

    def test_order(self):
        r = split_bill(100, 3, 0)
        self.assertEqual(r, [34, 33, 33])


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(100.0, 2, 0), (100, "2", 0), (100, 2, None), (True, 2, 0),
                     (-1, 2, 0), (100, 0, 0), (100, 2, -1), (100, 2, 101),
                     (100, 2, 10.0), (100, True, 0), (100, 2, True)]:
            with self.assertRaises(ValueError, msg=str(args)):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
