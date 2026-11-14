import unittest
from fractions import Fraction
from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])


class NoDrift(unittest.TestCase):
    def test_half_up_total(self):
        # 1005*107/100 = 1075.35 -> 1075 ; 1075 / 4 = 268 r 3
        self.assertEqual(split_bill(1005, 4, 7), [269, 269, 269, 268])

    def test_half_up_tie(self):
        # 1*150/100 = 1.5 -> 2 (ไม่ใช่ banker's 2 / ตัวอย่างถัดไป 2.5 -> 3)
        self.assertEqual(split_bill(1, 1, 50), [2])
        self.assertEqual(split_bill(5, 1, 0), [5])
        self.assertEqual(split_bill(5, 1, 50), [8])  # 7.5 -> 8

    def test_sum(self):
        for t in (1, 7, 99, 12345):
            for p in (1, 3, 7):
                for tip in (0, 5, 13, 100):
                    g = (Fraction(t * (100 + tip), 100) * 2 + 1) // 2
                    self.assertEqual(sum(split_bill(t, p, tip)), g)


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [
            (-1, 1, 0), (1.0, 1, 0), ("1", 1, 0), (True, 1, 0), (None, 1, 0),
            (1, 0, 0), (1, -1, 0), (1, 1.0, 0), (1, True, 0), (1, None, 0),
            (1, 1, -1), (1, 1, 101), (1, 1, 5.0), (1, 1, True), (1, 1, "5"),
        ]
        for args in bad:
            with self.assertRaises(ValueError, msg=str(args)):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
