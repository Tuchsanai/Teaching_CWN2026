import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_normal_2(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_normal_3(self):
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_normal_4(self):
        self.assertEqual(bulk_price(10000, 10, True), 100674)

    def test_normal_5(self):
        self.assertEqual(bulk_price(10000, 50, True), 482503)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)

    def test_boundary_2(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_boundary_3(self):
        self.assertEqual(bulk_price(10000, 11, False), 113581)  # 110000*.965*1.07=113580.5

    def test_boundary_4(self):
        self.assertEqual(bulk_price(10000, 49, False), 505950)

    def test_boundary_5(self):
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_boundary_6(self):
        self.assertEqual(bulk_price(10000, 51, False), 504773)  # 510000*.925*1.07=504772.5

    def test_boundary_7(self):
        self.assertEqual(bulk_price(10000, 1000, False), 9897500)

    def test_boundary_8(self):
        self.assertEqual(bulk_price(0, 5, True), 0)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 10432.5 -> 10433 (round() ได้ 10432)
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_no_drift_2(self):  # 505949.5 -> 505950 (floor ได้ 505949)
        self.assertEqual(bulk_price(10000, 49, False), 505950)

    def test_no_drift_3(self):  # 1016.83 -> 1017 (ปัดทีละขั้นได้ 1018)
        self.assertEqual(bulk_price(101, 10, True), 1017)

    def test_no_drift_4(self):  # 1.07 -> 1
        self.assertEqual(bulk_price(1, 1, False), 1)


class Reject(unittest.TestCase):
    def check(self, *a):
        with self.assertRaises(ValueError):
            bulk_price(*a)

    def test_reject_1(self): self.check(-1, 1, False)
    def test_reject_2(self): self.check(100, 0, False)
    def test_reject_3(self): self.check(100, 1001, False)
    def test_reject_4(self): self.check(100, -5, False)
    def test_reject_5(self): self.check(100.0, 1, False)
    def test_reject_6(self): self.check(100, 1.0, False)
    def test_reject_7(self): self.check('100', 1, False)
    def test_reject_8(self): self.check(100, '1', False)
    def test_reject_9(self): self.check(True, 1, False)
    def test_reject_10(self): self.check(100, True, False)
    def test_reject_11(self): self.check(None, 1, False)
    def test_reject_12(self): self.check(100, None, False)
    def test_reject_13(self): self.check(100, 1, 1)
    def test_reject_14(self): self.check(100, 1, None)
    def test_reject_15(self): self.check(100, 1, 'True')


if __name__ == "__main__":
    unittest.main()
