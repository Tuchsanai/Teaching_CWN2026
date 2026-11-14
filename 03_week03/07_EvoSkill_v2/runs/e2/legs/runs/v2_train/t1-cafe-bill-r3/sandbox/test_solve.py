import unittest
from fractions import Fraction
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class Normal(unittest.TestCase):
    def test_small(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)

    def test_member_small(self):
        self.assertEqual(cafe_bill([it(10000, 2)], True), 19260)

    def test_big_member(self):
        # 100000*0.95*0.9*1.07 = 91485
        self.assertEqual(cafe_bill([it(50000, 2)], True), 91485)

    def test_empty(self):
        self.assertEqual(cafe_bill([], True), 0)


class Boundary(unittest.TestCase):
    def test_49999(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)  # 49999*1.07=53498.93

    def test_50000(self):
        self.assertEqual(cafe_bill([it(50000)], False), 50825)  # 47500*1.07

    def test_50001(self):
        self.assertEqual(cafe_bill([it(50001)], False), 50826)  # 47500.95*1.07=50826.0165


class NoDrift(unittest.TestCase):
    def test_half(self):
        # 50 *1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([it(50)], False), 54)

    def test_frac(self):
        exp = int((Fraction(12345) * Fraction(90, 100) * Fraction(107, 100) * 2 + 1) // 2)
        self.assertEqual(cafe_bill([it(12345)], True), exp)

    def test_multi(self):
        s = 333 * 3 + 777 * 7
        exp = int((Fraction(s) * Fraction(107, 100) * 2 + 1) // 2)
        self.assertEqual(cafe_bill([it(333, 3), it(777, 7)], False), exp)


class Reject(unittest.TestCase):
    def bad(self, items, member=False):
        with self.assertRaises(ValueError):
            cafe_bill(items, member)

    def test_items(self):
        self.bad(None)
        self.bad("x")
        self.bad([1])
        self.bad([{"price": 100}])
        self.bad([{"qty": 1}])

    def test_values(self):
        self.bad([it(100, 0)])
        self.bad([it(-1, 1)])
        self.bad([it(100.0, 1)])
        self.bad([it(100, 1.0)])
        self.bad([it("100", 1)])
        self.bad([it(True, 1)])
        self.bad([it(100, True)])

    def test_member(self):
        self.bad([it(100)], 1)
        self.bad([it(100)], None)
        self.bad([it(100)], "True")


if __name__ == "__main__":
    unittest.main()
