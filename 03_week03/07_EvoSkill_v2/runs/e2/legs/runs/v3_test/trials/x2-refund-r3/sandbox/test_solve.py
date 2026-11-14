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
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(0, 0, True), 0)

    def test_nodrift(self):
        self.assertEqual(refund(999, 33, True), 585)  # 999*.67*.875=585.69 -> floor
        self.assertEqual(refund(1, 0, True), 0)
        self.assertIs(type(refund(999, 33, True)), int)

    def test_reject(self):
        for a in [(-1, 0, False), (100, -1, False), (100, 101, False),
                  (100.0, 0, False), (100, 5.0, False), ("1", 0, False),
                  (True, 0, False), (100, True, False), (100, 0, 1),
                  (100, 0, None), (100, 90, "x")]:
            with self.assertRaises(ValueError):
                refund(*a)


if __name__ == "__main__":
    unittest.main()
