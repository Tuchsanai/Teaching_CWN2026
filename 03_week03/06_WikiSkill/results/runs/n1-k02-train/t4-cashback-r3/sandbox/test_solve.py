import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "silver", True), 600)

    def test_half_up(self):
        # 10010*0.015 = 150.15 -> 150 ; 10050*0.025=251.25 -> 251
        self.assertEqual(cashback(10010, "silver", False), 150)
        # 10100*0.025 = 252.5 -> 253
        self.assertEqual(cashback(10100, "gold", False), 253)
        # 10010*0.015=150.15 ; 10040*.025=251.0 ; 10100*.015=151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)

    def test_cap(self):
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", True), 20000)

    def test_invalid(self):
        for args in [(-1, "gold", False), (100.0, "gold", False), (True, "gold", False),
                     ("1", "gold", False), (None, "gold", False), (10000, "bronze", False),
                     (10000, None, False), (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
