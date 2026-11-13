import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_normal_2(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_normal_3(self):
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])

    def test_normal_4(self):
        self.assertEqual(split_bill(1005, 3, 10), [369, 369, 368])


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(split_bill(0, 1, 0), [0])

    def test_boundary_2(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_boundary_3(self):
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_boundary_4(self):
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_boundary_5(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_boundary_6(self):
        self.assertEqual(split_bill(1000, 1, 0), [1000])


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 1105.5 -> 1106
        self.assertEqual(split_bill(1005, 1, 10), [1106])

    def test_no_drift_2(self):  # 4.4 -> 4, 6.6 -> 7, 5.5 -> 6
        self.assertEqual(split_bill(4, 1, 10), [4])
        self.assertEqual(split_bill(6, 1, 10), [7])
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_no_drift_3(self):  # 27.5 -> 28
        self.assertEqual(split_bill(25, 1, 10), [28])

    def test_sum_preserved(self):
        self.assertEqual(sum(split_bill(12345, 7, 13)), 13950)  # 12345*1.13=13949.85


class Reject(unittest.TestCase):
    def test_reject(self):
        bad = [(-1, 1, 0), (10, 0, 0), (10, -1, 0), (10, 1, -1), (10, 1, 101),
               (10.0, 1, 0), (10, 1.0, 0), (10, 1, 10.0),
               ('10', 1, 0), (10, '1', 0), (10, 1, '0'),
               (True, 1, 0), (10, True, 0), (10, 1, True),
               (None, 1, 0), (10, None, 0), (10, 1, None)]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    split_bill(*args)


if __name__ == "__main__":
    unittest.main()
