import unittest
from solve import cashback


class Normal(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)
        self.assertEqual(cashback(100000, "gold", True), 5000)
        self.assertEqual(cashback(100000, "platinum", True), 8000)


class Boundary(unittest.TestCase):
    def test_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999)
        self.assertEqual(cashback(400000, "platinum", True), 20000)

    def test_silver_birthday(self):
        self.assertEqual(cashback(100000, "silver", True), 1500)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        # 10001*0.015=150.015 -> 150 ; 10033*0.025=250.825 -> 250
        self.assertEqual(cashback(10001, "silver", False), 150)
        self.assertEqual(cashback(10033, "gold", False), 250)
        # 10013*0.025*2=500.65 -> 500
        self.assertEqual(cashback(10013, "gold", True), 500)
        # 10099*0.015=151.485 -> 151
        self.assertEqual(cashback(10099, "silver", False), 151)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in (-1, 1000.0, "1000", True, None):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("bronze", "Gold", None, 1):
            with self.assertRaises(ValueError):
                cashback(10000, t, False)
        for b in (0, 1, "True", None):
            with self.assertRaises(ValueError):
                cashback(10000, "gold", b)


if __name__ == "__main__":
    unittest.main()
