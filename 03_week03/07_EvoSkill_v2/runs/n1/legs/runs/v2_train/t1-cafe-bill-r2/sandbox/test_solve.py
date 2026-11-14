import unittest
from fractions import Fraction
from solve import cafe_bill


def I(p, q=1):
    return [{"price": p, "qty": q}]


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill(I(10000, 2), False), 21400)
        self.assertEqual(cafe_bill(I(10000, 2), True), 19260)

    def test_boundary(self):
        self.assertEqual(cafe_bill(I(50000), False), 50825)  # 47500*1.07
        self.assertEqual(cafe_bill(I(49999), False), 53499)  # 49999*1.07=53498.93
        self.assertEqual(cafe_bill(I(50000), True), 45742.5 and 45743)

    def test_nodrift(self):
        # 1*0.9*1.07 = 0.963 -> 1 ; 5*1.07=5.35 -> 5 ; 50*1.07=53.5 -> 54
        self.assertEqual(cafe_bill(I(1), True), 1)
        self.assertEqual(cafe_bill(I(5), False), 5)
        self.assertEqual(cafe_bill(I(50), False), 54)

    def test_empty_and_zero(self):
        self.assertEqual(cafe_bill([], False), 0)
        self.assertEqual(cafe_bill(I(0), True), 0)

    def test_reject(self):
        bad = [
            (I(100.0), False), (I(100, 1.0), False), (I("1"), False),
            (I(True), False), (I(None), False), (I(-1), False),
            (I(100, 0), False), (I(100, -1), False), (I(100, True), False),
            (I(100), 1), (I(100), None), ("x", False), (None, False),
            ([1], False), ([{"price": 1}], False), ([{"qty": 1}], False),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError, msg=repr((items, m))):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
