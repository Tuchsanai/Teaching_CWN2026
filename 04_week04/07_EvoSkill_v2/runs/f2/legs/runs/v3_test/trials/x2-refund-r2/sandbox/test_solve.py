import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(10000, 0, False), 10000)


class Boundary(unittest.TestCase):
    def test_80_90(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_zero(self):
        self.assertEqual(refund(0, 10, True), 0)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        self.assertEqual(refund(1, 0, True), 0)      # 0.875 -> 0
        self.assertEqual(refund(999, 33, True), 585)  # 999*.67*.875=585.69


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 0, False), (1.0, 0, False), ("1", 0, False), (True, 0, False),
                  (100, -1, False), (100, 101, False), (100, 50.0, False),
                  (100, 50, 1), (100, 50, None), (100, True, False)]:
            with self.assertRaises(ValueError):
                refund(*a)
        with self.assertRaises(ValueError):
            refund(100, 101, True)


if __name__ == "__main__":
    unittest.main()
