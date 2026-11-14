import unittest
from solve import cafe_bill


def I(p, q=1):
    return {"price": p, "qty": q}


class Normal(unittest.TestCase):
    def test_small(self):
        self.assertEqual(cafe_bill([I(10000, 2)], False), 21400)

    def test_member_small(self):
        self.assertEqual(cafe_bill([I(10000, 2)], True), 19260)

    def test_discount(self):
        self.assertEqual(cafe_bill([I(10000, 5)], False), 50825)

    def test_empty(self):
        self.assertEqual(cafe_bill([], True), 0)


class Boundary(unittest.TestCase):
    def test_below(self):
        self.assertEqual(cafe_bill([I(49999)], False), 53499)  # 49999*1.07=53498.93

    def test_at(self):
        self.assertEqual(cafe_bill([I(50000)], False), 50825)

    def test_above(self):
        self.assertEqual(cafe_bill([I(50001)], False), 50826)  # 50826.0 ... 50001*.95*1.07=50825.96


class NoDrift(unittest.TestCase):
    def test_half(self):
        self.assertEqual(cafe_bill([I(10000, 5)], True), 45743)  # 45742.5 -> up

    def test_odd(self):
        self.assertEqual(cafe_bill([I(1, 3)], False), 3)  # 3.21


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [
            ("x", False), (None, False), ([I(1)], 1), ([I(1)], None),
            ([I(1, 0)], False), ([I(-1)], False), ([I(1.0)], False),
            ([I(1, True)], False), ([{"price": 1}], False), ([5], False),
            ([{"qty": 1}], False), ([I("1")], False),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError, msg=repr((items, m))):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
