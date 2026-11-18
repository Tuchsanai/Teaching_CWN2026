import unittest
from solve import split_bill


class TestSolve(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder_first_pay_more(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)

    def test_tip_remainder(self):
        self.assertEqual(split_bill(1001, 2, 10), [551, 550])  # 1101.1 -> 1101

    def test_rounding_half_up(self):
        # 1005*1.10 = 1105.5 -> 1106 (สมมติปัดครึ่งขึ้น)
        self.assertEqual(sum(split_bill(1005, 1, 10)), 1106)

    def test_edges(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_reject(self):
        bad = [
            (-1, 1, 0), (10.0, 1, 0), (True, 1, 0), ("10", 1, 0),
            (10, 0, 0), (10, -1, 0), (10, 1.0, 0), (10, True, 0), (10, None, 0),
            (10, 1, -1), (10, 1, 101), (10, 1, 5.0), (10, 1, False), (10, 1, "5"),
        ]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    split_bill(*args)


if __name__ == "__main__":
    unittest.main()
