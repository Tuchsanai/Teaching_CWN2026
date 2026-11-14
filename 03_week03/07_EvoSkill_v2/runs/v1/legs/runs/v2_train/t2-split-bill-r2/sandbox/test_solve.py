import unittest
from fractions import Fraction
from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(10001, 3, 0), [3334, 3334, 3333])

    def test_tip(self):
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])


class Boundary(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 0), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])


class NoDrift(unittest.TestCase):
    def test_half_rounds_up(self):
        # 5*105/100 = 5.25 -> 5 ; 10*105/100=10.5 -> 11
        self.assertEqual(sum(split_bill(10, 1, 5)), 11)
        self.assertEqual(sum(split_bill(5, 1, 5)), 5)

    def test_sum(self):
        for t in range(0, 300, 7):
            for p in range(1, 9):
                for tip in (0, 7, 10, 15, 100):
                    g = int((Fraction(t * (100 + tip), 100) * 2 + 1) // 2)
                    self.assertEqual(sum(split_bill(t, p, tip)), g)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                  (1.0, 1, 0), ("1", 1, 0), (1, 1.0, 0), (1, 1, 5.0),
                  (True, 1, 0), (1, True, 0), (1, 1, True), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
