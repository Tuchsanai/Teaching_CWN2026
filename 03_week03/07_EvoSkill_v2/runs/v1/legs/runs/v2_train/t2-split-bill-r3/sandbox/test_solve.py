import unittest
from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])


class Boundary(unittest.TestCase):
    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 10 * 105 / 100 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        # 30*115/100 = 34.5 -> 35
        self.assertEqual(split_bill(30, 1, 15), [35])

    def test_sum(self):
        for t in (1, 99, 12345):
            for p in (1, 3, 7):
                r = split_bill(t, p, 7)
                self.assertEqual(sum(r), (t * 107 * 2 + 100) // 200)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                  (1.0, 1, 0), (1, 1.0, 0), (1, 1, 5.0), ("1", 1, 0),
                  (True, 1, 0), (1, True, 0), (1, 1, True), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
