import unittest
from solve import split_bill


class Normal(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 2, 0), [5000, 5000])

    def test_remainder(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_tip(self):
        self.assertEqual(split_bill(10000, 4, 10), [2750] * 4)

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 0), [999])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_tip_100(self):
        self.assertEqual(split_bill(101, 2, 100), [101, 101])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])


class NoDrift(unittest.TestCase):
    def test_half_up_grand(self):
        # 1*(105)/100 = 1.05 -> 1 ; 10*105/100=10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        self.assertEqual(split_bill(1, 1, 5), [1])

    def test_sum(self):
        for t in (1, 777, 12345):
            for p in (1, 3, 7):
                self.assertEqual(sum(split_bill(t, p, 15)), (t * 115 * 2 + 100) // 200)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                     (1.0, 1, 0), (1, 1.0, 0), (1, 1, 5.0), ("1", 1, 0),
                     (True, 1, 0), (1, True, 0), (1, 1, True), (None, 1, 0)]:
            with self.assertRaises(ValueError, msg=str(args)):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
