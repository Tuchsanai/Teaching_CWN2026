import unittest
from fractions import Fraction
from solve import cafe_bill


def I(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([I(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([I(10000, 2)], True), 19260)
        self.assertEqual(cafe_bill([], False), 0)

    def test_boundary(self):
        self.assertEqual(cafe_bill([I(49999)], False), 53499)
        self.assertEqual(cafe_bill([I(50000)], False), 50825)
        self.assertEqual(cafe_bill([I(25000), I(25000)], True), 45743)

    def test_nodrift(self):
        for p in range(49990, 50010):
            for m in (False, True):
                t = Fraction(p)
                if p >= 50000:
                    t *= Fraction(95, 100)
                if m:
                    t *= Fraction(90, 100)
                t *= Fraction(107, 100)
                self.assertEqual(cafe_bill([I(p)], m), int((t * 2 + 1) // 2))
        self.assertIs(type(cafe_bill([I(1)], False)), int)

    def test_reject(self):
        for bad in ([I(100, 0)], [I(-1)], [I(100.0)], [I("3")], [I(True)],
                    [I(100, True)], [{"price": 1}], ["x"], None, "abc"):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)
        for m in (1, 0, None, "true"):
            with self.assertRaises(ValueError):
                cafe_bill([I(100)], m)


if __name__ == "__main__":
    unittest.main()
