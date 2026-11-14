import unittest
from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_tip(self):
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_one_person_max_tip(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_half_satang(self):
        # 105*1.10=115.5 -> 116
        self.assertEqual(split_bill(105, 1, 10), [116])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])


class NoDrift(unittest.TestCase):
    def test_sum(self):
        for t in (1, 99, 12345, 99999):
            for p in (1, 3, 7, 11):
                for tip in (0, 7, 15, 100):
                    r = split_bill(t, p, tip)
                    self.assertEqual(sum(r), int((t * (100 + tip) * 2 + 100) // 200))
                    self.assertLessEqual(max(r) - min(r), 1)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, 0), (100, 0, 0), (100, 1, -1), (100, 1, 101),
                  (100.0, 1, 0), (100, 2.0, 0), (100, 1, 10.0), ("1", 1, 0),
                  (None, 1, 0), (True, 1, 0), (100, True, 0), (100, 1, True)]:
            with self.assertRaises(ValueError, msg=a):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
