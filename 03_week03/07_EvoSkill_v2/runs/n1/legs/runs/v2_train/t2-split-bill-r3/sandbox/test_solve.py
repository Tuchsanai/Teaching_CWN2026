import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_normal_2(self):
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])

    def test_normal_3(self):
        self.assertEqual(split_bill(1000, 4, 0), [250, 250, 250, 250])

    def test_normal_4(self):
        self.assertEqual(split_bill(999, 7, 15), [165] + [164] * 6)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(split_bill(0, 1, 0), [0])

    def test_boundary_2(self):
        self.assertEqual(split_bill(0, 3, 100), [0, 0, 0])

    def test_boundary_3(self):
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_boundary_4(self):
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_boundary_5(self):
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])

    def test_boundary_6(self):
        self.assertEqual(split_bill(3, 3, 0), [1, 1, 1])

    def test_boundary_7(self):
        self.assertEqual(split_bill(100, 1, 0), [100])


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 1.5 -> 2 (floor ได้ 1)
        self.assertEqual(split_bill(1, 1, 50), [2])

    def test_no_drift_2(self):  # 1.49 -> 1
        self.assertEqual(split_bill(1, 1, 49), [1])

    def test_no_drift_3(self):  # 1.51 -> 2
        self.assertEqual(split_bill(1, 1, 51), [2])

    def test_no_drift_4(self):  # 4.5 -> 5 (round() ได้ 4)
        self.assertEqual(split_bill(3, 1, 50), [5])

    def test_no_drift_5(self):  # รวมก่อนปัด: 5.5 -> 6 แล้วหาร 2 = [3,3]
        self.assertEqual(split_bill(5, 2, 10), [3, 3])


class Reject(unittest.TestCase):
    def check(self, *a):
        with self.assertRaises(ValueError):
            split_bill(*a)

    def test_reject_1(self): self.check(-1, 2, 10)
    def test_reject_2(self): self.check(100, 0, 10)
    def test_reject_3(self): self.check(100, -1, 10)
    def test_reject_4(self): self.check(100, 2, -1)
    def test_reject_5(self): self.check(100, 2, 101)
    def test_reject_6(self): self.check(100.0, 2, 10)
    def test_reject_7(self): self.check(100, 2.0, 10)
    def test_reject_8(self): self.check(100, 2, 10.0)
    def test_reject_9(self): self.check('100', 2, 10)
    def test_reject_10(self): self.check(100, '2', 10)
    def test_reject_11(self): self.check(100, 2, '10')
    def test_reject_12(self): self.check(True, 2, 10)
    def test_reject_13(self): self.check(100, True, 10)
    def test_reject_14(self): self.check(100, 2, False)
    def test_reject_15(self): self.check(None, 2, 10)
    def test_reject_16(self): self.check(100, None, 10)
    def test_reject_17(self): self.check(100, 2, None)


if __name__ == "__main__":
    unittest.main()
