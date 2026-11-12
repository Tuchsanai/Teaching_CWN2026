import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)

    def test_threshold(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)
        self.assertEqual(cafe_bill([it(50000)], False), 50825)

    def test_member(self):
        self.assertEqual(cafe_bill([it(10000)], True), 9630)
        self.assertEqual(cafe_bill([it(50000)], True), 45743)  # 45742.5 -> up

    def test_invalid(self):
        for items, m in [([it(100, 0)], False), ([it(100, -1)], False),
                         ([it(100.0)], False), ([it(100, True)], False),
                         ([it(-1)], False), ([it(100)], 1), ("x", False),
                         ([{"price": 1}], False), ([5], False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
