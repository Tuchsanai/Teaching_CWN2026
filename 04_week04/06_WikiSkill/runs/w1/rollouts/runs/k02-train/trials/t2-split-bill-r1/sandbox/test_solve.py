import unittest
from solve import split_bill


class TestSolve(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_single(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_rounding(self):
        # สมมติ: ยอดรวมที่เป็นเศษสตางค์ปัดครึ่งขึ้น 105*1.05=110.25 -> 110
        self.assertEqual(sum(split_bill(105, 1, 5)), 110)
        # 10*1.05=10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_tip_bounds(self):
        self.assertEqual(split_bill(100, 1, 0), [100])
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_reject(self):
        bad = [(-1, 1, 0), (100.0, 1, 0), (True, 1, 0), ("1", 1, 0),
               (100, 0, 0), (100, -1, 0), (100, 1.0, 0), (100, True, 0),
               (100, 1, -1), (100, 1, 101), (100, 1, 5.0), (100, 1, True), (100, 1, None)]
        for a in bad:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
