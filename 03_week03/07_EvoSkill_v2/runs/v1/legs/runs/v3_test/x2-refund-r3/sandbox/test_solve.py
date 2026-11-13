import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(0, 10, True), 0)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(10000, 80, True), 1750)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 1*50/100*0.875 = 0.4375 -> 0 ; 3*50/100=1.5 -> 2
        self.assertEqual(refund(3, 50, False), 2)
        self.assertEqual(refund(1, 50, True), 0)
        # 1234*(77/100)*7/8 = 831.4... ; 10*(100-1)/100*7/8=8.66 -> 9
        self.assertEqual(refund(10, 1, True), 9)
        # 4*50/100*7/8 = 1.75 -> 2 ; 2*75/100 = 1.5 -> 2 (ไม่ปัดระหว่างขั้น)
        self.assertEqual(refund(4, 50, True), 2)
        self.assertEqual(refund(2, 25, False), 2)


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 10, True), (100, -1, True), (100, 101, True),
               (100.0, 10, True), (100, 10.0, True), ("100", 10, True),
               (True, 10, True), (100, True, True), (None, 10, True),
               (100, 10, 1), (100, 10, "yes"), (100, 10, None)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                refund(*a)


if __name__ == "__main__":
    unittest.main()
