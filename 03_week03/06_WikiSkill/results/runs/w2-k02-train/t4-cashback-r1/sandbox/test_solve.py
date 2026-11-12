import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", True), 1600)

    def test_edges(self):
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "silver", True), 300)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(500000, "gold", True), 20000)
        self.assertEqual(cashback(10**9, "platinum", True), 20000)

    def test_half_up(self):
        # 10010*0.015 = 150.15 -> 150 ; 10033*0.015=150.495 ; 10100*.025=252.5 -> 253
        self.assertEqual(cashback(10100, "gold", False), 253)
        # 10050*0.015=150.75 -> 151 ; 10034*0.015=150.51 ->151
        self.assertEqual(cashback(10034, "silver", False), 151)
        # exactly .5: 10010*0.025=250.25; 10030*.025=250.75; 10020*.015=150.3
        # 10100*0.015=151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)

    def test_reject(self):
        for args in [(-1, "gold", False), (20000.0, "gold", False),
                     (True, "gold", False), ("20000", "gold", False),
                     (20000, "bronze", False), (20000, None, False),
                     (20000, "gold", 1), (20000, "gold", None),
                     (-1, "bad", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
