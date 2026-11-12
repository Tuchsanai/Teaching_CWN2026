import unittest
from solve import cafe_bill


def I(p, q=1):
    return [{"price": p, "qty": q}]


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill(I(10000, 2), False), 21400)
        self.assertEqual(cafe_bill(I(10000, 2), True), 19260)
        self.assertEqual(cafe_bill([], False), 0)

    def test_threshold(self):
        self.assertEqual(cafe_bill(I(49999), False), 53499)  # 53498.93
        self.assertEqual(cafe_bill(I(50000), False), 50825)  # 50000*.95*1.07
        self.assertEqual(cafe_bill(I(50001), False), 50826)  # 50825.9 -> 50826
        self.assertEqual(cafe_bill(I(50000), True), 45743)   # 45742.5 half up

    def test_half(self):
        self.assertEqual(cafe_bill(I(50), False), 54)  # 53.5 -> 54

    def test_reject(self):
        for items, m in [(I(1000.0), False), (I(100, 0), False), (I(-1), False),
                         (I(True), False), (I(100, 1.0), False), ("x", False),
                         ([1], False), ([{"price": 1}], False), (I(100), 1),
                         (I(100), None), (I("1"), False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
