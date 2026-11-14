import unittest
from fractions import Fraction
from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_tip_edges(self):
        self.assertEqual(sum(split_bill(777, 5, 0)), 777)
        self.assertEqual(sum(split_bill(777, 5, 100)), 1554)

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])


class NoDrift(unittest.TestCase):
    def test_half_rounds_up(self):
        # 10*105/100 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_sum_matches(self):
        for t in range(0, 300, 7):
            for p in (1, 2, 3, 7):
                for tip in (0, 5, 12, 100):
                    x = Fraction(t * (100 + tip), 100)
                    g = int(x + Fraction(1, 2) // 1) if False else (x * 2 + 1) // 2
                    self.assertEqual(sum(split_bill(t, p, tip)), g)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 2, 0), (10, 0, 0), (10, -1, 0), (10, 2, -1), (10, 2, 101),
                  (10.0, 2, 0), ("10", 2, 0), (10, 2.0, 0), (10, 2, 5.0),
                  (True, 2, 0), (10, True, 0), (10, 2, True), (None, 2, 0)]:
            with self.assertRaises(ValueError, msg=str(a)):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
