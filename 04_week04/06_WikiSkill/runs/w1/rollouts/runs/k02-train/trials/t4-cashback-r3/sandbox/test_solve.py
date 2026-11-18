import unittest
from solve import cashback


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)
        self.assertEqual(cashback(100000, "gold", True), 5000)

    def test_min_threshold(self):
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(9999, "platinum", True), 0)
        # สมมติ: พอดี 100 บาท ได้เงินคืน
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(10001, "platinum", False), 400)

    def test_cap(self):
        # platinum 4%: 500000 -> 20000 พอดีเพดาน
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 20000)  # 19999.96 -> 20000
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(10**9, "platinum", True), 20000)
        self.assertEqual(cashback(300000, "platinum", True), 20000)

    def test_rounding(self):
        # สมมติ: ปัดครึ่งขึ้น ปัดครั้งเดียวหลังคูณ 2
        self.assertEqual(cashback(10010, "silver", False), 150)   # 150.15
        self.assertEqual(cashback(10030, "silver", False), 150)   # 150.45
        self.assertEqual(cashback(10033, "silver", False), 150)   # 150.495
        self.assertEqual(cashback(10100, "silver", False), 152)   # 151.5 -> 152
        self.assertEqual(cashback(10001, "silver", True), 300)    # 300.03
        self.assertIs(type(cashback(10033, "gold", True)), int)

    def test_reject(self):
        bad = [
            (10000.0, "gold", False), (True, "gold", False), (-1, "gold", False),
            ("100", "gold", False), (None, "gold", False),
            (10000, "bronze", False), (10000, "Gold", False), (10000, None, False),
            (10000, "gold", 1), (10000, "gold", None), (10000, "gold", "True"),
        ]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    cashback(*args)


if __name__ == "__main__":
    unittest.main()
