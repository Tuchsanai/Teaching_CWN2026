import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], True), 19260)

    def test_boundary(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_nodrift(self):
        # 1*0.95*0.9*1.07 ไม่ใช่ครึ่งพอดี; 50000*.95*.9*1.07=45742.5 -> 45743
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_reject(self):
        for items, m in [([{"price": 1, "qty": 0}], False), ([{"price": 1.0, "qty": 1}], False),
                         ([{"price": True, "qty": 1}], False), ([{"price": 1}], False),
                         ([{"price": -1, "qty": 1}], False), ({}, False),
                         ([{"price": 1, "qty": 1}], 1), ([{"price": 1, "qty": "2"}], False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
