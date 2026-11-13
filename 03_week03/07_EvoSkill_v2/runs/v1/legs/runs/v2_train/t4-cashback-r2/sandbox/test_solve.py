import unittest
from solve import cashback


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(50000, "silver", False), 750)
        self.assertEqual(cashback(50000, "gold", False), 1250)
        self.assertEqual(cashback(50000, "platinum", False), 2000)
        self.assertEqual(cashback(50000, "gold", True), 2500)


class Boundary(unittest.TestCase):
    def test_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 20000)  # 19999.96 -> 20000
        self.assertEqual(cashback(499900, "platinum", False), 19996)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(cashback(10020, "silver", True), 301)   # 300.6
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15
        self.assertEqual(cashback(10030, "silver", False), 150)  # 150.45
        self.assertEqual(cashback(10010, "gold", False), 250)    # 250.25
        self.assertEqual(cashback(10030, "gold", False), 251)    # 250.75
        self.assertEqual(cashback(10010, "silver", True), 300)   # 300.3
        self.assertEqual(cashback(10050, "silver", False), 151)  # 150.75
        self.assertEqual(cashback(10010, "silver", True) + 0, 300)
        self.assertEqual(cashback(10030, "silver", True), 301)   # 300.9


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, "gold", False), (100.0, "gold", False), ("100", "gold", False),
                     (True, "gold", False), (None, "gold", False), (20000, "bronze", False),
                     (20000, None, False), (20000, ["gold"], False), (20000, "gold", 1),
                     (20000, "gold", "yes"), (5, "bronze", False), (5, "gold", None)]:
            with self.assertRaises(ValueError, msg=str(args)):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
