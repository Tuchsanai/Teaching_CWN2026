import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_boundary_exact(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_boundary_below(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_boundary_above(self):
        self.assertEqual(cashback(10001, "silver", False), 150)

    def test_half_up(self):
        self.assertEqual(cashback(10100, "silver", False), 152)  # 151.5
        self.assertEqual(cashback(10020, "gold", False), 251)    # 250.5

    def test_reject_value(self):
        for args in [(-1, "gold", False), (10000, "bronze", False),
                     (-1, "gold", True)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_reject_type(self):
        for args in [(10000.0, "gold", False), (True, "gold", False),
                     ("10000", "gold", False), (None, "gold", False),
                     (10000, None, False), (10000, "gold", 1),
                     (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_zero_or_cap(self):
        self.assertEqual(cashback(0, "gold", True), 0)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(10000000, "platinum", True), 20000)
        self.assertEqual(cashback(400000, "gold", True), 20000)

    def test_reject_before_zero_shortcut(self):
        with self.assertRaises(ValueError):
            cashback(50, "vip", False)


if __name__ == "__main__":
    unittest.main()
