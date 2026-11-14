import unittest
from solve import late_fee


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_boundary(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(0, 10), 0)

    def test_nodrift(self):
        self.assertEqual(late_fee(100, 4), 3)      # 3.0
        self.assertEqual(late_fee(10, 10), 1)      # 0.75 -> 1
        self.assertEqual(late_fee(2, 10), 0)       # 0.15
        self.assertEqual(late_fee(200, 5), 8)      # 7.5 -> 8
        self.assertIsInstance(late_fee(999, 7), int)

    def test_reject(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     ("100", 5), (100, "5"), (True, 5), (100, True), (None, 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)
        with self.assertRaises(ValueError):
            late_fee(100.0, 1)


if __name__ == "__main__":
    unittest.main()
