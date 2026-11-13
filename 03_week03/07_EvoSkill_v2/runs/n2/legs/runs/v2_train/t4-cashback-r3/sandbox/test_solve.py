import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", True), 1600)
        self.assertEqual(cashback(50000, "silver", False), 750)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", True), 0)
        self.assertEqual(cashback(500000, "platinum", False), 20000)  # = cap
        self.assertEqual(cashback(1000000, "platinum", True), 20000)

    def test_half_up(self):
        # 10010*0.015 = 150.15 -> 150 ; 10100*0.025=252.5 -> 253
        self.assertEqual(cashback(10100, "gold", False), 253)
        # 10033*0.015=150.495->150 ; 10034*.015=150.51->151
        self.assertEqual(cashback(10034, "silver", False), 151)
        # 10010*.025*2=500.5 -> 501
        self.assertEqual(cashback(10010, "gold", True), 501)

    def test_reject(self):
        for a in (-1, 1.0, 20000.0, "2", True, None, [], ):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("bronze", "Gold", None, 1, [], ""):
            with self.assertRaises(ValueError):
                cashback(20000, t, False)
            with self.assertRaises(ValueError):
                cashback(5, t, False)
        for b in (1, 0, None, "True"):
            with self.assertRaises(ValueError):
                cashback(20000, "gold", b)


if __name__ == "__main__":
    unittest.main()
