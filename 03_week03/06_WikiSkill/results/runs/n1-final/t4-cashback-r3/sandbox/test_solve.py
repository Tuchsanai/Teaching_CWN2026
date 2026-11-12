import unittest
from solve import cashback


class TestCashback(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(50000, "silver", False), 750)
        self.assertEqual(cashback(50000, "gold", False), 1250)
        self.assertEqual(cashback(50000, "platinum", False), 2000)

    def test_boundary_below(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_boundary_at(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10001, "silver", False), 150)

    def test_half_up(self):
        self.assertEqual(cashback(10100, "silver", False), 152)  # 151.5
        self.assertEqual(cashback(10020, "gold", False), 251)    # 250.5

    def test_birthday_and_cap(self):
        self.assertEqual(cashback(50000, "gold", True), 2500)
        self.assertEqual(cashback(1000000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(400000, "gold", True), 20000)

    def test_reject_range(self):
        with self.assertRaises(ValueError):
            cashback(-1, "silver", False)
        with self.assertRaises(ValueError):
            cashback(10000, "bronze", False)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, "silver", False)

    def test_reject_bool_or_type(self):
        with self.assertRaises(ValueError):
            cashback(True, "silver", False)
        with self.assertRaises(ValueError):
            cashback(10000, None, False)
        with self.assertRaises(ValueError):
            cashback(10000, "silver", 1)


if __name__ == "__main__":
    unittest.main()
