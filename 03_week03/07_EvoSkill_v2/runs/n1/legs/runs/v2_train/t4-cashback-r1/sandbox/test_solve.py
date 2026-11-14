import unittest
from solve import cashback


class Normal(unittest.TestCase):
    def test_rates(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)
        self.assertEqual(cashback(20000, "platinum", True), 1600)
        self.assertEqual(cashback(20000, "silver", True), 300)  # สมมติฐาน


class Boundary(unittest.TestCase):
    def test_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(300000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "gold", False), 12500)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        self.assertEqual(cashback(10001, "silver", False), 150)  # 150.015
        self.assertEqual(cashback(10033, "gold", False), 250)  # 250.825
        self.assertEqual(cashback(10033, "gold", True), 501)  # 501.65


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in (-1, 100.0, "100", True, None):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("bronze", "Gold", None, 1):
            with self.assertRaises(ValueError):
                cashback(20000, t, False)
        for b in (0, 1, "yes", None):
            with self.assertRaises(ValueError):
                cashback(20000, "gold", b)
        with self.assertRaises(ValueError):
            cashback(50, "bronze", 1)  # ตรวจก่อน early-return


if __name__ == "__main__":
    unittest.main()
