import unittest
from solve import cafe_bill


def I(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([I(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([I(10000, 2)], True), 19260)
        self.assertEqual(cafe_bill([], False), 0)

    def test_threshold(self):
        self.assertEqual(cafe_bill([I(49999)], False), 53499)  # 53498.93
        self.assertEqual(cafe_bill([I(50000)], False), 50825)  # 50000*.95*1.07
        self.assertEqual(cafe_bill([I(50001)], False), 50826)  # 50826.07
        self.assertEqual(cafe_bill([I(50000)], True), 45743)   # 45742.5 half up

    def test_half_up(self):
        self.assertEqual(cafe_bill([I(50)], True), 48)  # 48.15 -> 48
        self.assertEqual(cafe_bill([I(50, 1)], False), 54)  # 53.5 -> 54

    def test_reject(self):
        for bad in [([I(100.0)], False), ([I(100, 0)], False), ([I(-1)], False),
                    ([I(True)], False), ([I(100)], 1), ("x", False),
                    ([{"price": 1}], False), ([5], False), ([I(100, 1.0)], False)]:
            with self.assertRaises(ValueError):
                cafe_bill(*bad)


if __name__ == "__main__":
    unittest.main()
