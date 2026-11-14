import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 2, 0), [5000, 5000])

    def test_remainder(self):
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_single(self):
        self.assertEqual(split_bill(1000, 1, 20), [1200])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_max_tip(self):
        self.assertEqual(split_bill(1001, 2, 100), [1001, 1001])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 4, 0), [1, 1, 0, 0])


class NoDrift(unittest.TestCase):
    def test_half_satang_rounds_up(self):
        # 1005 * 1.10 = 1105.5 -> 1106
        self.assertEqual(split_bill(1005, 2, 10), [553, 553])
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_sum_preserved(self):
        r = split_bill(9999, 7, 13)  # 9999*1.13=11298.87 -> 11299
        self.assertEqual(sum(r), 11299)
        self.assertEqual(r, [1615, 1614, 1614, 1614, 1614, 1614, 1614])


class Reject(unittest.TestCase):
    def test_bad_values(self):
        for args in [(-1, 1, 0), (100, 0, 0), (100, 1, -1), (100, 1, 101)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_bad_types(self):
        for args in [(100.0, 1, 0), (100, "2", 0), (100, 1, None), (True, 1, 0), (100, True, 0), (100, 1, 10.0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
