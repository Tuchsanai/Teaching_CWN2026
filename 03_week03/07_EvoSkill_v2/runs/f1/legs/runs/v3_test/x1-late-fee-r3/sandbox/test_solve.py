import unittest
from solve import late_fee as fn


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(fn(1000, 4), 30)

    def test_normal_2(self):
        self.assertEqual(fn(100000, 10), 7500)

    def test_normal_3(self):
        self.assertEqual(fn(10000, 19), 1425)

    def test_zero_amount(self):
        self.assertEqual(fn(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_grace(self):
        self.assertEqual(fn(10000, 0), 0)
        self.assertEqual(fn(10000, 2), 0)
        self.assertEqual(fn(10000, 3), 0)
        self.assertEqual(fn(10000, 4), 300)

    def test_cap(self):
        self.assertEqual(fn(10000, 19), 1425)
        self.assertEqual(fn(10000, 20), 1500)
        self.assertEqual(fn(10000, 21), 1500)
        self.assertEqual(fn(10000, 365), 1500)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(fn(50, 4), 2)    # 1.5
        self.assertEqual(fn(1000, 7), 53)  # 52.5

    def test_below_half(self):
        self.assertEqual(fn(70, 4), 2)    # 2.1
        self.assertEqual(fn(10, 5), 0)    # 0.375

    def test_above_half(self):
        self.assertEqual(fn(90, 4), 3)    # 2.7
        self.assertEqual(fn(100, 5), 4)   # 3.75

    def test_cap_rounding(self):
        self.assertEqual(fn(30, 365), 5)  # 4.5
        self.assertEqual(fn(1, 365), 0)   # 0.15


class Reject(unittest.TestCase):
    def test_reject(self):
        bad = [(-1, 5), (1000, -1), (1000, 366), (1000.0, 5), (1000, 5.0),
               ("1000", 5), (1000, "5"), (True, 5), (1000, True),
               (None, 5), (1000, None)]
        for a in bad:
            with self.subTest(a=a), self.assertRaises(ValueError):
                fn(*a)


if __name__ == "__main__":
    unittest.main()
