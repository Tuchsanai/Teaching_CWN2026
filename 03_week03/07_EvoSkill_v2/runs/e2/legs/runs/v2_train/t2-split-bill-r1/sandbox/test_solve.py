import unittest
from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_less_than_people(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])


class NoDrift(unittest.TestCase):
    def test_half_up_total(self):
        # 105*107/100 = 112.35 -> 112
        self.assertEqual(split_bill(105, 1, 7), [112])
        # 50*105/100 = 52.5 -> 53
        self.assertEqual(split_bill(50, 1, 5), [53])
        self.assertEqual(split_bill(50, 2, 5), [27, 26])

    def test_sum(self):
        r = split_bill(12345, 7, 13)
        self.assertEqual(sum(r), 13950)  # 12345*1.13=13949.85
        self.assertLessEqual(max(r) - min(r), 1)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 2, 0), (100, 0, 0), (100, 2, -1), (100, 2, 101),
                  (100.0, 2, 0), ("100", 2, 0), (True, 2, 0), (100, 2.0, 0),
                  (100, True, 0), (100, 2, 5.0), (None, 2, 0), (100, 2, False)]:
            with self.assertRaises(ValueError, msg=str(a)):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
