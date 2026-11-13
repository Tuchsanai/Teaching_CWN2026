import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", True), 1000)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)

    def test_half_up(self):
        # 10010*0.015 = 150.15 -> 150 ; 10100*.015=151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)
        self.assertEqual(cashback(10100, "gold", False), 253)  # 252.5

    def test_reject(self):
        for a in (-1, 100.0, "100", True, None):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("bronze", None, [], 1):
            with self.assertRaises(ValueError):
                cashback(20000, t, False)
        with self.assertRaises(ValueError):
            cashback(5, "bronze", False)
        for b in (1, None, "x"):
            with self.assertRaises(ValueError):
                cashback(20000, "gold", b)


if __name__ == "__main__":
    unittest.main()
