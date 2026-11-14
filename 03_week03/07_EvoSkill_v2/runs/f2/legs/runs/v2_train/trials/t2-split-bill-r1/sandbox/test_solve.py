import unittest
from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_tip(self):
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])


class Boundary(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 100), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_extra(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])


class NoDrift(unittest.TestCase):
    def test_sum_and_half_up(self):
        r = split_bill(5, 1, 10)  # 5.5 -> 6
        self.assertEqual(r, [6])
        for t in range(0, 300, 7):
            for p in range(1, 9):
                for tip in (0, 7, 15, 100):
                    r = split_bill(t, p, tip)
                    self.assertEqual(sum(r), (t * (100 + tip) * 2 + 100) // 200)
                    self.assertLessEqual(max(r) - min(r), 1)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101), (1.0, 1, 0),
                  ("1", 1, 0), (True, 1, 0), (1, 1, 1.5), (1, True, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
