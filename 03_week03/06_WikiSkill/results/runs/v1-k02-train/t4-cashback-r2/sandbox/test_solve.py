import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)
        self.assertEqual(cashback(100000, "gold", True), 5000)

    def test_min_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_half_up(self):
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15
        self.assertEqual(cashback(10030, "silver", False), 150)  # 150.45
        self.assertEqual(cashback(10040, "silver", False), 151)  # 150.6
        self.assertEqual(cashback(10100, "gold", False), 253)    # 252.5

    def test_cap(self):
        self.assertEqual(cashback(10**7, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_invalid(self):
        for a in (-1, 1000.0, True, "5", None):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("bronze", "", None, 1):
            with self.assertRaises(ValueError):
                cashback(10000, t, False)
        for b in (1, 0, None, "True"):
            with self.assertRaises(ValueError):
                cashback(10000, "gold", b)
        with self.assertRaises(ValueError):
            cashback(-5, "bad", 1)


if __name__ == "__main__":
    unittest.main()
