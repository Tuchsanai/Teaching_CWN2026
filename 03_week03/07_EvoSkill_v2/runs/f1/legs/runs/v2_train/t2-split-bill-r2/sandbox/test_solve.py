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
    def test_zero_total(self):
        self.assertEqual(fn(0, 3, 50), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(fn(999, 1, 100), [1998])

    def test_tip_edges(self):
        self.assertEqual(fn(100, 1, 0), [100])
        self.assertEqual(fn(100, 1, 100), [200])


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(fn(10, 1, 5), [11])  # 10.5 -> 11
        self.assertEqual(fn(1, 1, 50), [2])   # 1.5 -> 2

    def test_sum(self):
        r = fn(12345, 7, 7)
        self.assertEqual(sum(r), 13209)  # 13209.15 -> 13209
        self.assertLessEqual(max(r) - min(r), 1)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                  (1.0, 1, 0), (1, 1.0, 0), (1, 1, 0.0), ("1", 1, 0),
                  (True, 1, 0), (1, True, 0), (1, 1, False), (None, 1, 0)]:
            with self.subTest(a=a), self.assertRaises(ValueError):
                fn(*a)


if __name__ == "__main__":
    unittest.main()
