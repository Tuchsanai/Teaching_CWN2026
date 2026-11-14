import unittest
from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])


class Boundary(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 10), [0, 0, 0])

    def test_one_person_max_tip(self):
        self.assertEqual(split_bill(1000, 1, 100), [2000])


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 5*110/100 = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_sum(self):
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), 11299)
        self.assertLessEqual(max(r) - min(r), 1)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1),
                  (1.0, 1, 0), (1, True, 0), ("1", 1, 0), (1, 1, None), (0, 0, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
