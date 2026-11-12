import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)

    def test_min_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_birthday(self):
        self.assertEqual(cashback(100000, "gold", True), 5000)

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 20000)

    def test_half_up(self):
        # 10010*0.015 = 150.15 -> 150 ; 10050*0.015=150.75 -> 151
        self.assertEqual(cashback(10010, "silver", False), 150)
        self.assertEqual(cashback(10050, "silver", False), 151)
        # 10020*0.025 = 250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_invalid(self):
        for args in [(-1, "gold", False), (1000.0, "gold", False),
                     (True, "gold", False), (10000, "bronze", False),
                     (10000, "gold", 1), (10000, None, False)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
