import unittest
from solve import cashback


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(50000, "silver", False), 750)
        self.assertEqual(cashback(50000, "gold", False), 1250)
        self.assertEqual(cashback(50000, "platinum", False), 2000)

    def test_birthday(self):
        self.assertEqual(cashback(50000, "gold", True), 2500)

    def test_min_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)  # พอดี 100 บาทได้
        self.assertEqual(cashback(10001, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap_boundary(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 20000)  # 19999.96 -> 20000
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(250000, "platinum", True), 20000)
        self.assertEqual(cashback(10**9, "platinum", True), 20000)
        # cap ใช้หลังคูณ 2: 150000*4%=6000 -> x2=12000 ไม่ติดเพดาน
        self.assertEqual(cashback(150000, "platinum", True), 12000)

    def test_rounding(self):
        # ข้อสมมติ: ปัดครึ่งขึ้น
        self.assertEqual(cashback(10033, "silver", False), 150)  # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151)  # 150.51
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15
        self.assertEqual(cashback(10100, "gold", False), 253)  # 252.5 -> 253

    def test_reject(self):
        bad = [
            (10000.0, "gold", False), (True, "gold", False), (-1, "gold", False),
            ("100", "gold", False), (None, "gold", False),
            (10000, "bronze", False), (10000, "Gold", False), (10000, 1, False),
            (10000, None, False),
            (10000, "gold", 1), (10000, "gold", 0), (10000, "gold", None),
            (10000, "gold", "True"),
        ]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    cashback(*args)


if __name__ == "__main__":
    unittest.main()
