import unittest
from solve import cashback


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)

    def test_birthday(self):
        self.assertEqual(cashback(100000, "gold", True), 5000)
        self.assertEqual(cashback(100000, "platinum", True), 8000)
        self.assertEqual(cashback(100000, "silver", True), 1500)


class Boundary(unittest.TestCase):
    def test_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(10**7, "platinum", True), 20000)
        self.assertEqual(cashback(0, "gold", False), 0)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        self.assertEqual(cashback(10001, "silver", False), 150)  # 150.015
        self.assertEqual(cashback(10039, "gold", False), 250)    # 250.975


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, "gold", False), (100.0, "gold", False), ("1", "gold", False),
                  (True, "gold", False), (5, "gold", False) if False else (100000, "vip", False),
                  (100000, None, False), (100000, "gold", 1), (100000, "gold", None),
                  (-5, "bad", False)]:
            with self.assertRaises(ValueError):
                cashback(*a)

    def test_reject_before_zero(self):
        with self.assertRaises(ValueError):
            cashback(50, "vip", False)


if __name__ == "__main__":
    unittest.main()
