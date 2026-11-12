import unittest
from solve import cashback


class TestCashback(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_boundary_below(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_boundary_at(self):
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10001, "gold", False), 250)

    def test_half_up(self):
        self.assertEqual(cashback(10100, "silver", False), 152)  # 151.5
        self.assertEqual(cashback(10020, "gold", False), 251)    # 250.5

    def test_birthday_and_cap(self):
        self.assertEqual(cashback(10000, "gold", True), 500)
        self.assertEqual(cashback(600000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_reject_range(self):
        with self.assertRaises(ValueError):
            cashback(-1, "gold", False)
        with self.assertRaises(ValueError):
            cashback(10000, "bronze", False)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, "gold", False)

    def test_reject_bool_or_type(self):
        for a, t, b in [(True, "gold", False), ("10000", "gold", False),
                        (None, "gold", False), (10000, None, False),
                        (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(a, t, b)


if __name__ == "__main__":
    unittest.main()
