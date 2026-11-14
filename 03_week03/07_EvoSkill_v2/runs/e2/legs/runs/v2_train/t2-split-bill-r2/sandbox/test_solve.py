import unittest
from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 4, 0), [1, 1, 0, 0])


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 1005*1.05 = 1055.25 -> 1055 ; 1055 = 3*351+2
        self.assertEqual(split_bill(1005, 3, 5), [352, 352, 351])
        # 10*1.05 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        # 1*1.5 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 1*1.49 = 1.49 -> 1
        self.assertEqual(split_bill(1, 1, 49), [1])

    def test_sum(self):
        r = split_bill(123457, 7, 13)
        self.assertEqual(sum(r), 139506)  # 123457*1.13=139506.41 -> 139506
        

class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101),
                     (10.0, 1, 0), ("10", 1, 0), (True, 1, 0), (10, 1.0, 0),
                     (10, True, 0), (10, 1, 5.0), (10, 1, None), (None, 1, 0)]:
            with self.assertRaises(ValueError, msg=str(args)):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
