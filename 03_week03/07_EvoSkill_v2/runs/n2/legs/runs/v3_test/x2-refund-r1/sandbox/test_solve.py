import unittest
from solve import refund


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_boundary(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(0, 0, True), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_half(self):
        # 1*0.5*0.875 = 0.4375 -> 0 ; 10*0.95*0.875=8.3125 -> 8
        self.assertEqual(refund(1, 50, True), 0)
        self.assertEqual(refund(1, 0, False), 1)
        self.assertEqual(refund(1, 50, False), 1)   # 0.5 -> 1
        self.assertEqual(refund(3, 50, False), 2)   # 1.5 -> 2
        self.assertEqual(refund(8, 0, True), 7)     # 7.0
        self.assertEqual(refund(12, 50, True), 5)   # 5.25 -> 5
        self.assertEqual(refund(4, 0, True), 4)     # 3.5 -> 4

    def test_reject(self):
        for a in [(-1, 0, False), (1, -1, False), (1, 101, False), (1.0, 0, False),
                  ("1", 0, False), (True, 0, False), (None, 0, False), (1, 0.0, False),
                  (1, True, False), (1, 0, 1), (1, 0, None), (1, "0", True), (1, 0, [])]:
            with self.assertRaises(ValueError):
                refund(*a)


if __name__ == "__main__":
    unittest.main()
