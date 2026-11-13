import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(10000, 0, False), 10000)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_zero(self):
        self.assertEqual(refund(0, 10, True), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 10*50/100=5 *0.875=4.375 -> 4
        self.assertEqual(refund(10, 50, True), 4)
        # 1*50/100=0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 4*50/100=2 *0.875=1.75 -> 2
        self.assertEqual(refund(4, 50, True), 2)
        # 12*50/100=6*.875=5.25 ->5 ; 4*75/100=3 *.875=2.625->3
        self.assertEqual(refund(4, 25, True), 3)
        # 0.5 exactly after restock: 4/7 not possible; paid=8,used=... 8*(100-u)/100*7/8 = 7(100-u)/100 -> u=93 n/a; u=50 ->3.5->4
        self.assertEqual(refund(8, 50, True), 4)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(100.0, 10, True), ("100", 10, True), (-1, 10, True), (True, 10, True),
                  (None, 10, True), (100, 10.0, True), (100, -1, True), (100, 101, True),
                  (100, True, True), (100, 10, 1), (100, 10, None), (100, 10, "yes"),
                  (100, 90, 1), (0, 101, False)]:
            with self.assertRaises(ValueError, msg=str(a)):
                refund(*a)


if __name__ == "__main__":
    unittest.main()
