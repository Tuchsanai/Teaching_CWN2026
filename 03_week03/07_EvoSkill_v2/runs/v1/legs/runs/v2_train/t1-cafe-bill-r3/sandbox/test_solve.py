import unittest
from fractions import Fraction
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class Normal(unittest.TestCase):
    def test_basic(self):
        # 9000*1.07 = 9630
        self.assertEqual(cafe_bill([it(4500, 2)], False), 9630)

    def test_member_small(self):
        # 10000*0.9*1.07 = 9630
        self.assertEqual(cafe_bill([it(5000, 2)], True), 9630)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)


class Boundary(unittest.TestCase):
    def test_49999(self):
        # 49999*1.07 = 53498.93
        self.assertEqual(cafe_bill([it(49999)], False), 53499)

    def test_50000(self):
        # 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill([it(50000)], False), 50825)

    def test_50000_member(self):
        # 50000*.95*.9*1.07 = 45742.5 -> 45743
        self.assertEqual(cafe_bill([it(50000)], True), 45743)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([it(50)], False), 54)

    def test_single_rounding(self):
        # 10001*.9*1.07 = 9630.9627 -> 9631
        self.assertEqual(cafe_bill([it(10001)], True), 9631)

    def test_many(self):
        total = 333 * 7
        exp = (Fraction(total) * Fraction(107, 100) * 2 + 1) // 2
        self.assertEqual(cafe_bill([it(333, 7)], False), exp)


class Reject(unittest.TestCase):
    def bad(self, items, member=False):
        with self.assertRaises(ValueError):
            cafe_bill(items, member)

    def test_cases(self):
        self.bad([it(100, 0)])
        self.bad([it(-1, 1)])
        self.bad([it(100.0, 1)])
        self.bad([it(100, 1.0)])
        self.bad([it("100", 1)])
        self.bad([it(True, 1)])
        self.bad([it(100, True)])
        self.bad([{"price": 100}])
        self.bad(["x"])
        self.bad(None)
        self.bad([it(100)], 1)
        self.bad([it(100)], "yes")


if __name__ == "__main__":
    unittest.main()
