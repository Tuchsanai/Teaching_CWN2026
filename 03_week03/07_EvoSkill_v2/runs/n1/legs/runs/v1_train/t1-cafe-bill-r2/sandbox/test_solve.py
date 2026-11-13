import unittest
from fractions import Fraction
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([it(6000, 2)], False), 12840)
        self.assertEqual(cafe_bill([], False), 0)

    def test_boundary(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)  # 49999*1.07=53498.93
        self.assertEqual(cafe_bill([it(50000)], False), 50825)  # 50000*.95*1.07=50825
        self.assertEqual(cafe_bill([it(25000, 2)], True), 45743)  # 50000*.95*.9*1.07=45742.5

    def test_nodrift(self):
        for p, q, m in [(12345, 7, True), (50001, 1, True), (333, 3, False), (1, 1, True)]:
            t = p * q
            e = Fraction(t) * (Fraction(95, 100) if t >= 50000 else 1) * (Fraction(9, 10) if m else 1) * Fraction(107, 100)
            r = cafe_bill([it(p, q)], m)
            self.assertIs(type(r), int)
            self.assertEqual(r, int((e * 2 + 1) // 2))

    def test_reject(self):
        bad = [
            ([it(100, 0)], False), ([it(-1)], False), ([it(100.0)], False),
            ([it(100, "3")], False), ([it(True)], False), ([it(100, 1.0)], False),
            ([{"price": 1}], False), (["x"], False), (None, False), ((it(1),), False),
            ([it(100)], 1), ([it(100)], None),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
