import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "gold", False), 12500)

    def test_half_up(self):
        # 10001*0.015 = 150.015 -> 150 ; 10100*0.025=252.5 -> 253
        self.assertEqual(cashback(10100, "gold", False), 253)
        # 10010*0.015=150.15 ; 10050*0.015=150.75 -> 151
        self.assertEqual(cashback(10050, "silver", False), 151)
        # 10100 silver = 151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)

    def test_reject(self):
        for args in [(-1, "gold", False), (20000.0, "gold", False),
                     (True, "gold", False), ("200", "gold", False),
                     (20000, "bronze", False), (20000, None, False),
                     (20000, "gold", 1), (20000, "gold", None),
                     (-1, "bad", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
