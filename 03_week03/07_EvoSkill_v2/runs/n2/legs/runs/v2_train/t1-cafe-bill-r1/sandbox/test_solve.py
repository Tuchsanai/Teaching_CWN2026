import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(cafe_bill([], False), 0)

    def test_boundary(self):
        # 49999 ไม่ลด: 49999*1.07=53498.93 -> 53499
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        # 50000*.95*1.07=50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_member(self):
        # 50000*.95*.9*1.07=45742.5 -> 45743
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_half(self):
        # 50*1.07=53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_reject(self):
        bad = [
            ([{"price": 1, "qty": 0}], False), ([{"price": -1, "qty": 1}], False),
            ([{"price": 1.0, "qty": 1}], False), ([{"price": "1", "qty": 1}], False),
            ([{"price": True, "qty": 1}], False), ([{"price": 1}], False),
            ([None], False), (None, False), ([{"price": 1, "qty": 1}], 1),
            ([{"price": 1, "qty": 1}], None), ([{"price": 1, "qty": 1.0}], True),
        ]
        for a in bad:
            with self.assertRaises(ValueError):
                cafe_bill(*a)


if __name__ == "__main__":
    unittest.main()
