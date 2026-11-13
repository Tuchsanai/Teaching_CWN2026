import unittest
from fractions import Fraction
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([it(10000, 2)], True), 19260)
        self.assertEqual(cafe_bill([], False), 0)

    def test_boundary(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)
        self.assertEqual(cafe_bill([it(50000)], False), 50825)  # 50000*.95*1.07
        self.assertEqual(cafe_bill([it(25000, 2)], False), 50825)
        self.assertEqual(cafe_bill([it(50000)], True), 45743)  # 45742.5 half-up

    def test_nodrift(self):
        for p in range(1, 400):
            for m in (False, True):
                t = p * 3
                a = Fraction(t)
                if t >= 50000:
                    a *= Fraction(95, 100)
                if m:
                    a *= Fraction(9, 10)
                a *= Fraction(107, 100)
                exp = int((a * 2 + 1) // 2)
                r = cafe_bill([it(p, 3)], m)
                self.assertEqual(r, exp)
                self.assertIs(type(r), int)
        self.assertEqual(cafe_bill([it(50, 1)], False), 54)  # 53.5 -> 54

    def test_reject(self):
        bad = [
            ([it(100, 0)], False), ([it(-1, 1)], False), ([it(100, -1)], False),
            ([it(100.0, 1)], False), ([it(100, 1.0)], False), ([it("3", 1)], False),
            ([it(True, 1)], False), ([it(100, True)], False),
            ([{"price": 1}], False), ([5], False), ("x", False), (None, False),
            ([it(100)], 1), ([it(100)], None), ([it(100)], "true"),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
