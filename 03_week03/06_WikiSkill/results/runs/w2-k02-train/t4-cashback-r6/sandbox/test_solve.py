import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_threshold(self):
        self.assertEqual(cashback(0, "gold", True), 0)
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)  # exactly 20000
        self.assertEqual(cashback(499999, "platinum", False), 20000)  # 19999.96 -> 20000
        self.assertEqual(cashback(499900, "platinum", False), 19996)
        self.assertEqual(cashback(600000, "platinum", True), 20000)

    def test_half_up(self):
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15
        self.assertEqual(cashback(10050, "silver", False), 151)  # 150.75
        self.assertEqual(cashback(10030, "gold", False), 251)   # 250.75
        self.assertEqual(cashback(10020, "silver", False), 150)  # 150.3
        self.assertEqual(cashback(10100, "silver", False), 152)  # 151.5 -> 152
        self.assertEqual(cashback(10300, "silver", False), 155)  # 154.5 -> 155

    def test_reject(self):
        for args in [(-1, "gold", False), (10000.0, "gold", False),
                     (True, "gold", False), ("100", "gold", False),
                     (10000, "bronze", False), (10000, None, False),
                     (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
