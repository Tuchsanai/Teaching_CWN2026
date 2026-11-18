import unittest
from solve import cashback


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_birthday_double(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_min_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10001, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        # 200 บาท = 20000 สตางค์; ตรวจเพดานหลังคูณ 2
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999 + 1)  # 19999.96 -> 20000
        self.assertEqual(cashback(300000, "platinum", True), 20000)

    def test_rounding(self):
        # 10010*15/1000 = 150.15 -> 150 ; 10040*15/1000=150.6 -> 151
        self.assertEqual(cashback(10010, "silver", False), 150)
        self.assertEqual(cashback(10040, "silver", False), 151)
        # ครึ่งพอดี (สมมติปัดขึ้น): 10010*25/1000 = 250.25 ; 10030*15=150.45 ; 10100*15/1000=151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)
        self.assertIs(type(cashback(12345, "gold", True)), int)

    def test_reject(self):
        for args in [(100.0, "gold", False), (True, "gold", False), (-1, "gold", False),
                     ("100", "gold", False), (None, "gold", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)
        for t in ["bronze", "Gold", 1, None]:
            with self.assertRaises(ValueError):
                cashback(20000, t, False)
        for b in [1, 0, "True", None]:
            with self.assertRaises(ValueError):
                cashback(20000, "gold", b)


if __name__ == "__main__":
    unittest.main()
