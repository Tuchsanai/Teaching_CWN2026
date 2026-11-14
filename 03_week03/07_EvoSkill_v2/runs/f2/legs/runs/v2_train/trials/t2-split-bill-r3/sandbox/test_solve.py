import unittest
from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_tip(self):
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])


class Boundary(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])


class NoDrift(unittest.TestCase):
    def test_remainder(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_half_up(self):
        # 1*105/100 = 1.05 -> 1 ; 10*105/100=10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_sum(self):
        for p in range(1, 12):
            self.assertEqual(sum(split_bill(12345, p, 7)), 13209)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                  (1.0, 1, 0), (1, 1.0, 0), (1, 1, 5.0), ("1", 1, 0),
                  (True, 1, 0), (1, True, 0), (1, 1, True), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
