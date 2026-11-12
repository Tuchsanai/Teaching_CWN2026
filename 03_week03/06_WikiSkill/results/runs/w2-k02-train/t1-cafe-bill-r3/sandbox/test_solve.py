import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([it(10000, 2)], True), 19260)

    def test_threshold(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)
        self.assertEqual(cafe_bill([it(50000)], False), 50825)
        self.assertEqual(cafe_bill([it(50001)], False), 50826)

    def test_member_discount_threshold(self):
        # 50000*.95*.9*1.07 = 45742.5 -> half up 45743
        self.assertEqual(cafe_bill([it(50000)], True), 45743)

    def test_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([it(50)], False), 54)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)

    def test_reject(self):
        bad = [
            ([it(100, 0)], False), ([it(-1)], False), ([it(100.0)], False),
            ([it(100, True)], False), ([it(100)], 1), ([it(100)], None),
            ("x", False), ([1], False), ([{"price": 1}], False),
            ([it("1")], False),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
