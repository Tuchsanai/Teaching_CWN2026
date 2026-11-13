import unittest
from solve import refund


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(0, 10, True), 0)

    def test_boundary(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_half_up(self):
        # 1*0.5*0.875 = 0.4375 -> 0 ; 3*0.5=1.5 -> 2
        self.assertEqual(refund(3, 50, False), 2)
        # 4*0.5*0.875=1.75 -> 2 ; 10*0.8*.875... exact .5: 4*(1/2)*(7/8)=1.75
        self.assertEqual(refund(4, 50, True), 2)
        # 12*0.75*0.875 = 7.875 -> 8 ; 16*0.5*0.875=7
        self.assertEqual(refund(16, 50, True), 7)
        # exact .5: 8*0.5*0.875=3.5 -> 4
        self.assertEqual(refund(8, 50, True), 4)

    def test_reject(self):
        for a in [(-1, 0, True), (1, -1, True), (1, 101, True), (1.0, 0, True),
                  ("1", 0, True), (True, 0, True), (None, 0, True),
                  (1, 5.0, True), (1, True, True), (1, 5, 1), (1, 5, None)]:
            with self.assertRaises(ValueError):
                refund(*a)


unittest.main() if __name__ == "__main__" else None
