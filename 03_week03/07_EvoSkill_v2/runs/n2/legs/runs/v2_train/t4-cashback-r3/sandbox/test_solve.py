import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cashback(20000, "gold", False), 500)

    def test_normal_2(self):
        self.assertEqual(cashback(20000, "platinum", True), 1600)

    def test_normal_3(self):
        self.assertEqual(cashback(20000, "silver", True), 300)  # silver ไม่ได้โบนัส


class Boundary(unittest.TestCase):
    def test_min_below(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_min_at(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)  # พอดีเพดาน
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(250000, "platinum", True), 20000)  # 20000 -> x2 เกินเพดาน


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(cashback(10050, "silver", False), 150)  # 150.75 ปัดลง

    def test_no_drift_2(self):
        self.assertEqual(cashback(12345, "gold", True), 617)  # 617.25

    def test_no_drift_3(self):
        self.assertEqual(cashback(10030, "gold", True), 501)  # 501.5 ปัดลง


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            cashback(-1, "gold", False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, "gold", False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            cashback("10000", "gold", False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            cashback(True, "gold", False)

    def test_reject_5(self):
        with self.assertRaises(ValueError):
            cashback(10000, "bronze", False)

    def test_reject_6(self):
        with self.assertRaises(ValueError):
            cashback(10000, "gold", 1)

    def test_reject_7(self):
        with self.assertRaises(ValueError):
            cashback(10000, None, False)


if __name__ == "__main__":
    unittest.main()
