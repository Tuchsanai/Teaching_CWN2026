import unittest
from solve import cashback


class TestCashback(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(10**7, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(499987, "platinum", False), 19999)

    def test_half_up(self):
        # 10010*0.015 = 150.15 -> 150 ; 10033*.025=250.825 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)  # 250.5
        self.assertEqual(cashback(10010, "gold", False), 250)  # 250.25
        self.assertEqual(cashback(10030, "silver", False), 150)  # 150.45
        self.assertEqual(cashback(10050, "silver", False), 151)  # 150.75

    def test_invalid(self):
        for args in [(100.0, "gold", False), (True, "gold", False), (-1, "gold", False),
                     ("1", "gold", False), (None, "gold", False),
                     (10000, "bronze", False), (10000, None, False),
                     (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
