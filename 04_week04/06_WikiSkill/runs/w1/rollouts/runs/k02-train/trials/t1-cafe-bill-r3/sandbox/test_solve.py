import unittest
from solve import cafe_bill


def I(p, q=1):
    return {"price": p, "qty": q}


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([I(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([I(6000, 2), I(3000)], False), 16050)
        self.assertEqual(cafe_bill([I(10000)], True), 9630)

    def test_threshold(self):
        # สมมติ: ยอดพอดี 500 บาท ได้ลด 5%
        self.assertEqual(cafe_bill([I(50000)], False), 50825)  # 47500*1.07
        self.assertEqual(cafe_bill([I(49999)], False), 53499)  # ไม่ลด
        self.assertEqual(cafe_bill([I(50001)], False), 50826)  # 47500.95*1.07=50825.97

    def test_member_stack(self):
        # 100000*.95*.9*1.07 = 91485
        self.assertEqual(cafe_bill([I(100000)], True), 91485)

    def test_rounding(self):
        # 105*1.07 = 112.35 -> 112 ; 150*1.07=160.5 -> 161 (half up)
        self.assertEqual(cafe_bill([I(105)], False), 112)
        self.assertEqual(cafe_bill([I(150)], False), 161)
        self.assertIs(type(cafe_bill([I(105)], False)), int)

    def test_reject(self):
        bad = [
            ("x", False), ([I(1)], 1), ([I(1)], None),
            ([I(1.0)], False), ([I(1, 0)], False), ([I(1, -1)], False),
            ([I(1, 1.0)], False), ([I(True)], False), ([I(1, True)], False),
            ([I(-1)], False), ([{"price": 1}], False), ([5], False),
            ([I(1), {"price": "a", "qty": 1}], False),
        ]
        for items, m in bad:
            with self.subTest(items=items, m=m):
                with self.assertRaises(ValueError):
                    cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
