import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)
        self.assertEqual(cashback(100000, "gold", True), 5000)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "gold", True), 20000)

    def test_half_up(self):
        # 10033*0.015 = 150.495 -> 150 ; 10100*0.015=151.5 -> 152
        self.assertEqual(cashback(10033, "silver", False), 150)
        self.assertEqual(cashback(10100, "silver", False), 152)
        # 10010*0.025 = 250.25 ; 10020*0.025=250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_reject(self):
        for a in (-1, 1.0, "1", None, True, [], 100000.0):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("bronze", None, 1, [], "Gold"):
            with self.assertRaises(ValueError):
                cashback(100000, t, False)
            with self.assertRaises(ValueError):
                cashback(5, t, False)
        for b in (None, 1, 0, "True"):
            with self.assertRaises(ValueError):
                cashback(100000, "gold", b)


if __name__ == "__main__":
    unittest.main()
