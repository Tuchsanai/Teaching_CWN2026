"""รัน: python3 -m unittest -q test_solve"""
import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cashback(20000, "silver", False), 300)

    def test_normal_2(self):
        self.assertEqual(cashback(40000, "gold", False), 1000)

    def test_normal_3(self):
        self.assertEqual(cashback(50000, "platinum", True), 4000)


class Boundary(unittest.TestCase):
    def test_min_amount(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_cap(self):
        self.assertEqual(cashback(250000, "platinum", True), 20000)
        self.assertEqual(cashback(250001, "platinum", True), 20000)
        self.assertEqual(cashback(249999, "platinum", True), 19999)

    def test_zero_and_silver_birthday(self):
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(10000, "silver", True), 150)  # silver ไม่ได้โบนัส
        self.assertEqual(cashback(10000, "gold", True), 500)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(cashback(10039, "gold", False), 250)  # 250.975 ปัดลง

    def test_no_drift_2(self):
        self.assertEqual(cashback(10019, "gold", True), 500)   # 500.95 ปัดลง

    def test_no_drift_3(self):
        self.assertEqual(cashback(12345, "silver", False), 185)  # 185.175


class Reject(unittest.TestCase):
    def test_reject_negative(self):
        with self.assertRaises(ValueError):
            cashback(-1, "gold", False)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            cashback(20000.0, "gold", False)

    def test_reject_str(self):
        with self.assertRaises(ValueError):
            cashback("20000", "gold", False)

    def test_reject_bool_amount(self):
        with self.assertRaises(ValueError):
            cashback(True, "gold", False)

    def test_reject_tier(self):
        for t in ("bronze", "Gold", None, 1):
            with self.assertRaises(ValueError):
                cashback(20000, t, False)

    def test_reject_birthday(self):
        for b in (1, 0, "yes", None):
            with self.assertRaises(ValueError):
                cashback(20000, "gold", b)


if __name__ == "__main__":
    unittest.main()
