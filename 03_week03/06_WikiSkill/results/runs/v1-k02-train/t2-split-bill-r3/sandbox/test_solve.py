import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)

    def test_half_up(self):
        # 1005 * 1.10 = 1105.5 -> 1106
        self.assertEqual(sum(split_bill(1005, 1, 10)), 1106)

    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum_and_order(self):
        r = split_bill(1001, 7, 15)
        self.assertEqual(sum(r), (2 * 1001 * 115 + 100) // 200)
        self.assertEqual(r, sorted(r, reverse=True))

    def test_invalid(self):
        for args in [(-1, 1, 0), (100, 0, 0), (100, -1, 0), (100, 1, -1),
                     (100, 1, 101), (100.0, 1, 0), (100, 1.0, 0),
                     (100, 1, 5.0), (True, 1, 0), (100, True, 0),
                     (100, 1, True), ("100", 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
