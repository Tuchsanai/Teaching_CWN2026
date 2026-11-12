import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_cap(self):
        self.assertEqual(cashback(10**6, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "gold", True), 20000)

    def test_half_up(self):
        # 10100*15/1000 = 151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)
        # 10020*25/1000 = 250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_invalid(self):
        for args in [(100.0, "gold", False), ("1", "gold", False), (True, "gold", False),
                     (-1, "gold", False), (10000, "bronze", False), (10000, None, False),
                     (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
