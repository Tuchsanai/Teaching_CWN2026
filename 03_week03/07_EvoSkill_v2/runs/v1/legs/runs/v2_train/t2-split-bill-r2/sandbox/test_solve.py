import unittest
from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_tip(self):
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])

    def test_sum(self):
        r = split_bill(12345, 7, 15)
        self.assertEqual(sum(r), 14197)  # 12345*1.15=14196.75 -> 14197
        self.assertEqual(len(r), 7)


class Boundary(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_more_people_than_money(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 10*1.05 = 10.5 -> 11 (ไม่ใช่ banker's 10)
        self.assertEqual(split_bill(10, 1, 5), [11])
        # 30*1.05 = 31.5 -> 32
        self.assertEqual(split_bill(30, 1, 5), [32])

    def test_large(self):
        self.assertEqual(sum(split_bill(10**15 + 1, 3, 7)), (10**15 + 1) * 107 // 100 + (1 if ((10**15 + 1) * 107) % 100 >= 50 else 0))


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                     (1.0, 1, 0), (1, 1.0, 0), (1, 1, 5.0),
                     ("1", 1, 0), (1, True, 0), (True, 1, 0), (1, 1, None)]:
            with self.assertRaises(ValueError, msg=args):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
