import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(cafe_bill([], False), 0)

    def test_boundary(self):
        # 49999*1.07 = 53498.93 ; 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_member_half(self):
        # 42750*1.07 = 45742.5 -> 45743 (half-up)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)
        # 50*0.9*1.07=48.15 -> 48 ; 5*1.07=5.35 ; 50*1.07=53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_reject(self):
        ok = [{"price": 100, "qty": 1}]
        for items, m in [(None, False), (ok, 1), (ok, None), ("x", True),
                         ([1], False), ([{"price": 100}], False),
                         ([{"price": 100, "qty": 0}], False),
                         ([{"price": -1, "qty": 1}], False),
                         ([{"price": 1.0, "qty": 1}], False),
                         ([{"price": "1", "qty": 1}], False),
                         ([{"price": 1, "qty": True}], False),
                         ([{"price": 1, "qty": 1.0}], False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
