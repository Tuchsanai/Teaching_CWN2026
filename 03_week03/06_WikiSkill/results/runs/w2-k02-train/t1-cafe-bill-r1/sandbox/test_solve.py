import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([it(6000), it(4000, 2)], False), 14980)

    def test_threshold(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)  # 53498.93
        self.assertEqual(cafe_bill([it(50000)], False), 50825)  # 50825
        self.assertEqual(cafe_bill([it(50001)], False), 50826)  # 50825.95

    def test_member(self):
        self.assertEqual(cafe_bill([it(10000)], True), 9630)
        self.assertEqual(cafe_bill([it(50000)], True), 45742.5 and 45743)

    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([it(50)], False), 54)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)

    def test_reject(self):
        bad = [
            ([it(100, 0)], False), ([it(-1)], False), ([it(100.0)], False),
            ([it(100, 1.0)], False), ([it(True)], False), ([{"price": 1}], False),
            ("x", False), ([5], False), ([it(100)], 1), ([it(100)], None),
        ]
        for a in bad:
            with self.assertRaises(ValueError):
                cafe_bill(*a)


if __name__ == "__main__":
    unittest.main()
