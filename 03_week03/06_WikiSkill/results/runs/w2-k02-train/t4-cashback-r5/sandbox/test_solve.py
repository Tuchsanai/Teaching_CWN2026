import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_half_up(self):
        # 10010 * 0.015 = 150.15 -> 150 ; 10100*0.015=151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)
        self.assertEqual(cashback(10010, "silver", False), 150)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(500000, "gold", True), 20000)
        self.assertEqual(cashback(10**9, "platinum", True), 20000)

    def test_reject(self):
        bad = [(-1, "gold", False), (20000.0, "gold", False),
               (True, "gold", False), ("100", "gold", False),
               (None, "gold", False), (20000, "bronze", False),
               (20000, None, False), (20000, "gold", 1),
               (20000, "gold", None)]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    cashback(*args)


if __name__ == "__main__":
    unittest.main()
