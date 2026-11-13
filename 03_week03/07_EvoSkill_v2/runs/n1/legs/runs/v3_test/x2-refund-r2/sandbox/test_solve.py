import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_2(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_normal_3(self):
        self.assertEqual(refund(20000, 0, True), 17500)

    def test_normal_4(self):
        self.assertEqual(refund(0, 10, True), 0)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):  # 79% ยังคืน
        self.assertEqual(refund(10000, 79, False), 2100)

    def test_boundary_2(self):  # 80% พอดี ยังคืน
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_boundary_3(self):  # 81% ไม่คืน
        self.assertEqual(refund(10000, 81, False), 0)

    def test_boundary_4(self):
        self.assertEqual(refund(10000, 100, True), 0)

    def test_boundary_5(self):  # 80% + restock = 1750
        self.assertEqual(refund(10000, 80, True), 1750)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 1*0.5*0.875 = 0.4375 -> 0
        self.assertEqual(refund(1, 50, True), 0)

    def test_no_drift_2(self):  # 5*0.9=4.5 -> 5 (half-up)
        self.assertEqual(refund(5, 10, False), 5)

    def test_no_drift_3(self):  # 10*0.8*0.875=7.0 ; 3*0.5=1.5->2
        self.assertEqual(refund(3, 50, False), 2)

    def test_no_drift_4(self):  # 9*0.5*0.875=3.9375 -> 4 (ปัดทีเดียว)
        self.assertEqual(refund(9, 50, True), 4)

    def test_no_drift_5(self):  # 7*0.5=3.5 ->4 ; 3.5*0.875=3.0625 -> 3
        self.assertEqual(refund(7, 50, False), 4)
        self.assertEqual(refund(7, 50, True), 3)

    def test_no_drift_6(self):  # 100*0.97*0.875=84.875 -> 85
        self.assertEqual(refund(100, 3, True), 85)


class Reject(unittest.TestCase):
    def _bad(self, *a):
        with self.assertRaises(ValueError):
            refund(*a)

    def test_reject_1(self): self._bad(-1, 10, False)
    def test_reject_2(self): self._bad(100, -1, False)
    def test_reject_3(self): self._bad(100, 101, False)
    def test_reject_4(self): self._bad(100.0, 10, False)
    def test_reject_5(self): self._bad('100', 10, False)
    def test_reject_6(self): self._bad(True, 10, False)
    def test_reject_7(self): self._bad(None, 10, False)
    def test_reject_8(self): self._bad(100, 10.0, False)
    def test_reject_9(self): self._bad(100, '10', False)
    def test_reject_10(self): self._bad(100, True, False)
    def test_reject_11(self): self._bad(100, None, False)
    def test_reject_12(self): self._bad(100, 10, 1)
    def test_reject_13(self): self._bad(100, 10, 'True')
    def test_reject_14(self): self._bad(100, 10, None)


if __name__ == "__main__":
    unittest.main()
