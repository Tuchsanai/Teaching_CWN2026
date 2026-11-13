import unittest
from solve import refund as fn


class Normal(unittest.TestCase):
    def test_no_fee(self):
        self.assertEqual(fn(20000, 50, False), 10000)

    def test_fee(self):
        self.assertEqual(fn(20000, 50, True), 8750)

    def test_unused(self):
        self.assertEqual(fn(10000, 0, True), 8750)

    def test_zero_paid(self):
        self.assertEqual(fn(0, 10, True), 0)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(fn(10000, 80, False), 2000)
        self.assertEqual(fn(10000, 80, True), 1750)

    def test_81(self):
        self.assertEqual(fn(10000, 81, False), 0)

    def test_79(self):
        self.assertEqual(fn(10000, 79, False), 2100)

    def test_100_and_0(self):
        self.assertEqual(fn(10000, 100, True), 0)
        self.assertEqual(fn(10000, 0, False), 10000)


class NoDrift(unittest.TestCase):
    def test_half_up(self):  # 1*0.5*0.875=0.4375 ->0 ; 10*.5=5*.875=4.375->4
        self.assertEqual(fn(1, 50, False), 1)  # 0.5 -> 1
        self.assertEqual(fn(1, 50, True), 0)   # 0.4375 -> 0
        self.assertEqual(fn(10, 50, True), 4)  # 4.375 -> 4

    def test_above_half(self):
        self.assertEqual(fn(10, 30, True), 6)  # 6.125 -> 6
        self.assertEqual(fn(9, 0, True), 8)    # 7.875 -> 8

    def test_exact_half(self):
        self.assertEqual(fn(4, 0, True), 4)    # 3.5 -> 4
        self.assertEqual(fn(3, 67, False), 1)  # 0.99 -> 1


class Reject(unittest.TestCase):
    def test_reject(self):
        bad = [(-1, 10, False), (10.0, 10, False), ("100", 10, False), (True, 10, False), (None, 10, False),
               (100, -1, False), (100, 101, False), (100, 10.0, False), (100, "10", False), (100, True, False),
               (100, None, False), (100, 10, 1), (100, 10, 0), (100, 10, "yes"), (100, 10, None)]
        for a in bad:
            with self.subTest(a=a):
                with self.assertRaises(ValueError):
                    fn(*a)


if __name__ == "__main__":
    unittest.main()
