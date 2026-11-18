import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([it(10000)], False), 10700)
        self.assertEqual(cafe_bill([it(6000, 2)], False), 12840)
        self.assertEqual(cafe_bill([it(10000), it(5000, 2)], True), 19260)

    def test_member_small(self):
        self.assertEqual(cafe_bill([it(10000)], True), 9630)

    def test_boundary(self):
        # พอดี 50000 ได้ลด 5% (สมมติ "ตั้งแต่" รวมค่าเกณฑ์)
        self.assertEqual(cafe_bill([it(50000)], False), 50825)
        self.assertEqual(cafe_bill([it(49999)], False), 53499)  # 49999*1.07=53498.93
        self.assertEqual(cafe_bill([it(50001)], False), 50826)  # 50001*.95*1.07=50825.5 -> half up

    def test_rounding(self):
        self.assertEqual(cafe_bill([it(50001)], False), 50826)
        self.assertEqual(cafe_bill([it(1)], False), 1)  # 1.07
        self.assertEqual(cafe_bill([it(50)], False), 54)  # 53.5 half up

    def test_reject(self):
        bad = [
            ("x", False), ([it(1)], 1), ([it(1)], None),
            ([1], False), ([{"price": 1}], False), ([{"qty": 1}], False),
            ([it(1.0)], False), ([it(True)], False), ([it(-1)], False),
            ([it(1, 0)], False), ([it(1, -1)], False), ([it(1, 1.0)], False),
            ([it(1, True)], False), ([it("1")], False),
        ]
        for items, m in bad:
            with self.subTest(items=items, m=m):
                with self.assertRaises(ValueError):
                    cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
