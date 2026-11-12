import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_boundary_exact(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_boundary_below(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_boundary_above(self):
        self.assertEqual(cashback(10001, "gold", False), 250)

    def test_half_up(self):
        # 10100*0.015=151.5 -> 152 ; 10020*0.025=250.5 -> 251
        self.assertEqual(cashback(10100, "silver", False), 152)
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_reject_value(self):
        for a, t in [(-1, "gold"), (100, "bronze"), (-1, "x")]:
            with self.assertRaises(ValueError):
                cashback(a, t, False)

    def test_reject_type(self):
        for a, t, b in [(1000.0, "gold", False), (True, "gold", False),
                        ("1", "gold", False), (None, "gold", False),
                        (10000, None, False), (10000, "gold", 1),
                        (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(a, t, b)

    def test_zero_or_cap(self):
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(10**7, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)


if __name__ == "__main__":
    unittest.main()
