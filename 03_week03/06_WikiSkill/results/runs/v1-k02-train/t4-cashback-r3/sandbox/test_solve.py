import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "gold", False), 0)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(0, "gold", True), 0)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_half_up(self):
        # 10100*3/200 = 151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)

    def test_invalid(self):
        for args in [(-1, "gold", False), (1000.0, "gold", False),
                     (True, "gold", False), (10000, "bronze", False),
                     (10000, "gold", 1), (10000, "gold", None),
                     ("100", "gold", False), (10000, None, False)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
