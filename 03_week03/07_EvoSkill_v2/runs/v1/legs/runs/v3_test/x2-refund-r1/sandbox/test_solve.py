import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(0, 10, True), 0)


class Boundary(unittest.TestCase):
    def test_80_81(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 80, True), 1750)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 1*99/100*0.875 = 0.86625 -> 1
        self.assertEqual(refund(1, 1, True), 1)
        # 10*50/100 = 5 ; *0.875 = 4.375 -> 4
        self.assertEqual(refund(10, 50, True), 4)
        # 1*50/100 = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 30*75/100=22.5*0.875=19.6875 -> 20
        self.assertEqual(refund(30, 25, True), 20)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 0, False), (100, -1, False), (100, 101, False),
                     (100.0, 0, False), (100, 10.0, False), ("100", 0, False),
                     (True, 0, False), (100, True, False), (None, 0, False),
                     (100, 0, 1), (100, 0, "yes"), (100, 0, None)]:
            with self.assertRaises(ValueError, msg=str(args)):
                refund(*args)


if __name__ == "__main__":
    unittest.main()
