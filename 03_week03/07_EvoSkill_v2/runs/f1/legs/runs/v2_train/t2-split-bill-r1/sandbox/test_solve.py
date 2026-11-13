import unittest
from solve import split_bill as fn


class Normal(unittest.TestCase):
    def test_a(self):
        self.assertEqual(fn(10000, 4, 0), [2500] * 4)

    def test_b(self):
        self.assertEqual(fn(10000, 3, 10), [3667, 3667, 3666])

    def test_c(self):
        self.assertEqual(fn(5000, 1, 20), [6000])


class Boundary(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(fn(0, 3, 0), [0, 0, 0])

    def test_tip100(self):
        self.assertEqual(fn(101, 2, 100), [101, 101])

    def test_more_people(self):
        self.assertEqual(fn(2, 5, 0), [1, 1, 0, 0, 0])


class NoDrift(unittest.TestCase):
    def test_half(self):
        self.assertEqual(fn(1, 1, 50), [2])  # 1.5 -> 2

    def test_sum(self):
        r = fn(9999, 7, 13)
        self.assertEqual(sum(r), 11299)  # 11298.87 -> 11299


class Reject(unittest.TestCase):
    def test_all(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101), (1.0, 1, 0),
                  ("1", 1, 0), (1, True, 0), (1, 1, 0.0), (True, 1, 0)]:
            with self.assertRaises(ValueError):
                fn(*a)


if __name__ == "__main__":
    unittest.main()
