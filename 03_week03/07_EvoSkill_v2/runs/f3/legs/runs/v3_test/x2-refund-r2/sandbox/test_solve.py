import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(0, 0, True), 0)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(10000, 0, False), 10000)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 1 * 0.5 *0.875 = 0.4375 -> 0 ; 10001*50/100*0.875=4375.4375 -> 4375
        self.assertEqual(refund(1, 50, False), 1)   # 0.5 -> 1
        self.assertEqual(refund(10001, 50, False), 5001)  # 5000.5 -> 5001
        self.assertEqual(refund(3, 0, True), 3)  # 2.625 -> 3


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 0, False), (1.0, 0, False), ("1", 0, False), (True, 0, False),
                     (1, -1, False), (1, 101, False), (1, 5.0, False), (1, True, False),
                     (1, 0, 1), (1, 0, None), (None, 0, False)]:
            with self.assertRaises(ValueError):
                refund(*args)


if __name__ == "__main__":
    unittest.main()
