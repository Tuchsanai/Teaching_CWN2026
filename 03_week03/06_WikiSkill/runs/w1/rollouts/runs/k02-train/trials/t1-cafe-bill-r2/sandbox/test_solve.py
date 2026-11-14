import unittest
from solve import cafe_bill


def I(p, q=1):
    return {"price": p, "qty": q}


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([I(10000)], False), 10700)
        self.assertEqual(cafe_bill([I(10000)], True), 9630)
        self.assertEqual(cafe_bill([I(6000, 3), I(5000, 2)], False), 29960)

    def test_member_big(self):
        # 100000*0.95*0.9*1.07 = 91485
        self.assertEqual(cafe_bill([I(50000, 2)], True), 91485)

    def test_boundary(self):
        # พอดี 500 บาท ได้ลด 5%: 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill([I(50000)], False), 50825)
        # ต่ำกว่า 1 สตางค์ ไม่ลด: 49999*1.07 = 53498.93
        self.assertEqual(cafe_bill([I(49999)], False), 53499)
        self.assertEqual(cafe_bill([I(50001)], False), 50826)

    def test_rounding_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([I(50)], False), 54)
        # 10*1.07 = 10.7 -> 11
        self.assertEqual(cafe_bill([I(10)], False), 11)

    def test_reject(self):
        bad = [
            (None, False), ("x", False), ([], False),
            ([I(100)], 1), ([I(100)], None),
            ([I(100.0)], False), ([I(True)], False), ([I(-1)], False),
            ([I(100, 0)], False), ([I(100, -1)], False), ([I(100, 1.0)], False),
            ([I(100, True)], False), ([{"price": 100}], False), (["a"], False),
            ([I(100), {"price": "1", "qty": 1}], False),
        ]
        for items, m in bad:
            with self.subTest(items=items, m=m):
                with self.assertRaises(ValueError):
                    cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
