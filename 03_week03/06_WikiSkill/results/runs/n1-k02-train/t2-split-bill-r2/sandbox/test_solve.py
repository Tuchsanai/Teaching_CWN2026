import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_half_up(self):
        # 1 * 150/100 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 201*1.05 = 211.05 -> 211
        self.assertEqual(sum(split_bill(201, 1, 5)), 211)

    def test_edges(self):
        self.assertEqual(split_bill(0, 3, 0), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])

    def test_invalid(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                     (1.0, 1, 0), (1, 1.0, 0), (1, 1, 5.0),
                     (True, 1, 0), (1, True, 0), (1, 1, True), ("1", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
