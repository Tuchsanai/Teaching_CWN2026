import unittest
from solve import cafe_bill


def it(p, q=1):
    return [{"price": p, "qty": q}]


class T(unittest.TestCase):
    def test_basic(self):
        # 10000*2=20000 -> *1.07 = 21400
        self.assertEqual(cafe_bill(it(10000, 2), False), 21400)

    def test_boundary_exact(self):
        # 50000 -> 47500 -> 50825
        self.assertEqual(cafe_bill(it(50000), False), 50825)

    def test_boundary_below(self):
        # 49999*1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill(it(49999), False), 53499)

    def test_boundary_above(self):
        # 50001*.95*1.07 = 50826.01.. -> 50826
        self.assertEqual(cafe_bill(it(50001), False), 50826)

    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill(it(50), False), 54)

    def test_member(self):
        # 10000*.9*1.07 = 9630
        self.assertEqual(cafe_bill(it(10000), True), 9630)
        # 50000*.95*.9*1.07 = 45742.5 -> 45743
        self.assertEqual(cafe_bill(it(50000), True), 45743)

    def test_reject_value(self):
        for bad in (it(-1), it(100, 0), it(100, -2)):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)

    def test_reject_type(self):
        for items, m in ((it(100.0), False), (it(100, 1.0), False),
                         (it(True), False), (it("100"), False),
                         (None, False), ([None], False),
                         ([{"price": 1}], False), (it(100), 1),
                         (it(100), None)):
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def test_zero_or_cap(self):
        self.assertEqual(cafe_bill([], False), 0)
        self.assertEqual(cafe_bill(it(0), True), 0)


if __name__ == "__main__":
    unittest.main()
