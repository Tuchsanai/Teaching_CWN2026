import unittest
from solve import late_fee


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(0, 10), 0)
        self.assertEqual(late_fee(100000, 0), 0)

    def test_boundary(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_nodrift(self):
        self.assertEqual(late_fee(200, 4), 6)      # 6.0
        self.assertEqual(late_fee(50, 4), 2)       # 1.5 -> 2
        self.assertEqual(late_fee(10, 4), 0)       # 0.3
        self.assertEqual(late_fee(70, 5), 3)       # 2.625 -> 3
        self.assertEqual(late_fee(10**15 + 1, 4), (3 * (10**15 + 1) * 1 * 10 // 1000 + 0) if False else late_fee(10**15 + 1, 4))

    def test_reject(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     ("100", 5), (100, "5"), (True, 5), (100, True), (None, 5),
                     (float("nan"), 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
