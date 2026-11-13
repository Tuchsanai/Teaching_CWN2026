import unittest
from solve import cashback


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)
        self.assertEqual(cashback(20000, "gold", True), 1000)


class Boundary(unittest.TestCase):
    def test_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(250000, "platinum", True), 20000)
        self.assertEqual(cashback(250000, "platinum", False), 10000)
        self.assertEqual(cashback(10**7, "silver", True), 20000)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(cashback(10020, "silver", True), 301)   # 300.6 -> 301
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15
        self.assertEqual(cashback(10030, "silver", False), 150)  # 150.45
        self.assertEqual(cashback(10050, "silver", False), 151)  # 150.75
        self.assertEqual(cashback(10010, "gold", False), 250)    # 250.25
        self.assertEqual(cashback(10020, "gold", False), 251)    # 250.5 -> 251


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, "gold", False), (100.0, "gold", False), ("100", "gold", False),
               (True, "gold", False), (None, "gold", False), (10000, "bronze", False),
               (10000, None, False), (10000, ["gold"], False), (10000, "gold", 1),
               (10000, "gold", None), (50, "bronze", False), (50, "gold", "x")]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    cashback(*args)


if __name__ == "__main__":
    unittest.main()
