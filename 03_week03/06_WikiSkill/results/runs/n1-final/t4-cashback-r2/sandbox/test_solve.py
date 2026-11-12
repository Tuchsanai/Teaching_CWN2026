import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_boundary_below(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_boundary_at(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10001, "silver", False), 150)

    def test_half_up(self):
        # 10010*0.015 = 150.15 -> 150 ; 10050*0.015=150.75 -> 151
        self.assertEqual(cashback(10050, "silver", False), 151)
        # 10020*0.025 = 250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_birthday_and_cap(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)
        self.assertEqual(cashback(10000000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "platinum", True), 20000)

    def test_reject_range(self):
        with self.assertRaises(ValueError):
            cashback(-1, "gold", False)
        with self.assertRaises(ValueError):
            cashback(10000, "bronze", False)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, "gold", False)

    def test_reject_bool_or_type(self):
        for a, t, b in [(True, "gold", False), ("1", "gold", False),
                        (None, "gold", False), (10000, None, False),
                        (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(a, t, b)


if __name__ == "__main__":
    unittest.main()
