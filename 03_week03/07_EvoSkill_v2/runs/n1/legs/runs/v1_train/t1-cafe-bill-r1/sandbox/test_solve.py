import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([it(10000, 2)], True), 19260)

    def test_boundary(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)
        self.assertEqual(cafe_bill([it(50000)], False), 50825)
        self.assertEqual(cafe_bill([it(50000)], True), 45743)  # 45742.5 half-up

    def test_nodrift(self):
        self.assertEqual(cafe_bill([it(1, 1)], False), 1)
        self.assertEqual(cafe_bill([it(5)], False), 5)  # 5.35

    def test_reject(self):
        bad = [([it(1)], 1), ([it(1)], None), ("x", False), ([it(1, 0)], False),
               ([it(-1)], False), ([it(1.0)], False), ([it(True)], False),
               ([{"price": 1}], False), ([1], False), ([it("2")], False)]
        for a, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(a, m)


if __name__ == "__main__":
    unittest.main()
