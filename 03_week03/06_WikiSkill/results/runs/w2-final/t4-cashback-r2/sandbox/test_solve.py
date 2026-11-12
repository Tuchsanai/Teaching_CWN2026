import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_boundary_exact(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_boundary_below(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_boundary_above(self):
        self.assertEqual(cashback(10001, "gold", False), 250)

    def test_half_up(self):
        # 10010*0.015 = 150.15 -> 150 ; 10100*0.025=252.5 -> 253
        self.assertEqual(cashback(10100, "gold", False), 253)
        self.assertEqual(cashback(10100, "silver", False), 152)  # 151.5
        self.assertEqual(cashback(10033, "silver", False), 150)  # 150.495
    
    def test_reject_value(self):
        for a, t in [(-1, "gold"), (100, "bronze"), (100, "")]:
            with self.assertRaises(ValueError):
                cashback(a, t, False)

    def test_reject_type(self):
        for a, t, b in [(10000.0, "gold", False), (True, "gold", False),
                        ("10000", "gold", False), (None, "gold", False),
                        (10000, None, False), (10000, "gold", 1),
                        (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(a, t, b)

    def test_zero_or_cap(self):
        self.assertEqual(cashback(0, "gold", True), 0)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(400000, "gold", True), 20000)
        self.assertEqual(cashback(500000, "gold", False), 12500)


if __name__ == "__main__":
    unittest.main()
