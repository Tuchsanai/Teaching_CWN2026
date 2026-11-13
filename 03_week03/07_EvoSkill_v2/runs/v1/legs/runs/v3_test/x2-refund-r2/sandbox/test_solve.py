import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(0, 10, True), 0)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 1*50/100=0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 10*50/100*0.875=4.375 -> 4 ; 12*50/100*.875=5.25 -> 5
        self.assertEqual(refund(10, 50, True), 4)
        # 4*75/100... 2*50/100*.875=.875 -> 1
        self.assertEqual(refund(2, 50, True), 1)
        # 100*1*0.875/100 = 0.875 ; 4*99/100*.875=3.465 -> 3
        self.assertEqual(refund(4, 1, True), 3)
        # exact .5: 4*... paid=40,used=75 -> 10 ; *.875=8.75 ->9
        self.assertEqual(refund(40, 75, True), 9)
        # 8*... paid=4,used=0 restock -> 3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 0, False), (100, -1, False), (100, 101, False),
                     (100.0, 0, False), (100, 10.0, False), ("100", 0, False),
                     (True, 0, False), (100, True, False), (None, 0, False),
                     (100, 0, 1), (100, 0, None), (100, 0, "yes")]:
            with self.assertRaises(ValueError):
                refund(*args)


if __name__ == "__main__":
    unittest.main()
