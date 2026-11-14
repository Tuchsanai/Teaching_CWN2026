import unittest
from solve import cafe_bill


def I(p, q=1):
    return {"price": p, "qty": q}


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([I(10000, 2)], False), 21400)

    def test_member(self):
        self.assertEqual(cafe_bill([I(10000, 2)], True), 19260)

    def test_both(self):
        # 60000*.95*.9*1.07 = 54891
        self.assertEqual(cafe_bill([I(30000, 2)], True), 54891)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)


class Boundary(unittest.TestCase):
    def test_499_99(self):
        self.assertEqual(cafe_bill([I(49999)], False), 53499)  # 49999*1.07=53498.93

    def test_500(self):
        self.assertEqual(cafe_bill([I(50000)], False), 50825)  # 50000*.95*1.07

    def test_501(self):
        self.assertEqual(cafe_bill([I(50001)], False), 50826)  # 50825.9 -> half up


class NoDrift(unittest.TestCase):
    def test_half(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([I(50)], False), 54)

    def test_small(self):
        # 1*0.9*1.07 = 0.963 -> 1
        self.assertEqual(cafe_bill([I(1)], True), 1)

    def test_big(self):
        # 3 * 33333 = 99999 *.95*1.07 = 101648.98...
        self.assertEqual(cafe_bill([I(33333, 3)], False), 101649)


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [
            ([I(100, 0)], False), ([I(-1)], False), ([I(100.0)], False),
            ([I(100, True)], False), ([{"price": 1}], False),
            ([{"qty": 1}], False), (None, False), ("x", False),
            ([5], False), ([I(100)], 1), ([I(100)], None), ([I("100")], False),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
