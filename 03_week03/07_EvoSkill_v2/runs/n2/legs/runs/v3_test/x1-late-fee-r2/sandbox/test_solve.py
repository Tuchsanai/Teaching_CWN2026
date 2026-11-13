import unittest
from solve import late_fee


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)   # 4*0.75%=3%
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)  # exactly 15%
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_half(self):
        self.assertEqual(late_fee(50, 5), 2)    # 1.875 -> 2
        self.assertEqual(late_fee(200, 4), 6)   # 6.0
        self.assertEqual(late_fee(2, 20), 0)    # 0.3 -> 0
        self.assertEqual(late_fee(10, 20), 2)   # cap 1.5 -> 2
        self.assertEqual(late_fee(0, 100), 0)

    def test_reject(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     ("1", 5), (100, "5"), (True, 5), (100, True), (None, 5), (100, None)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
