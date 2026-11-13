import unittest
from solve import split_bill as fn


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(fn(10000, 4, 0), [2500] * 4)

    def test_tip(self):
        self.assertEqual(fn(10000, 2, 10), [5500, 5500])

    def test_remainder(self):
        self.assertEqual(fn(100, 3, 0), [34, 33, 33])


class Boundary(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(fn(0, 3, 0), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(fn(999, 1, 100), [1998])

    def test_fewer_satang_than_people(self):
        self.assertEqual(fn(2, 5, 0), [1, 1, 0, 0, 0])


class NoDrift(unittest.TestCase):
    def test_half_up(self):  # 1005*1.10=1105.5 -> 1106
        self.assertEqual(sum(fn(1005, 1, 10)), 1106)

    def test_sum(self):
        self.assertEqual(sum(fn(12345, 7, 7)), 13209)  # 12345*1.07=13209.15 -> 13209
        

class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, 0), (1.0, 1, 0), ("1", 1, 0), (1, 0, 0), (1, True, 0),
                  (1, 1, -1), (1, 1, 101), (1, 1, 5.0), (True, 1, 0)]:
            with self.assertRaises(ValueError):
                fn(*a)


if __name__ == "__main__":
    unittest.main()
