import unittest
from solve import cafe_bill


def it(p, q=1):
    return [{"price": p, "qty": q}]


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill(it(10000, 2), False), 21400)

    def test_boundary_exact(self):
        # 50000 -> 47500 -> *1.07 = 50825
        self.assertEqual(cafe_bill(it(50000), False), 50825)

    def test_boundary_below(self):
        # 49999*1.07 = 53498.93
        self.assertEqual(cafe_bill(it(49999), False), 53499)

    def test_boundary_above(self):
        # 50001*.95*1.07 = 50826.01..
        self.assertEqual(cafe_bill(it(50001), False), 50826)

    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill(it(50), False), 54)

    def test_member(self):
        # 100000*.95*.9*1.07 = 91485
        self.assertEqual(cafe_bill(it(100000), True), 91485)

    def test_reject_value(self):
        for bad in (it(100, 0), it(-1, 1), it(100, -2)):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)

    def test_reject_type(self):
        for items, m in ((it(100.0), False), (it(True), False),
                         (it("1"), False), (None, False),
                         (it(100), 1), ([{"price": 1}], False)):
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def test_zero_or_cap(self):
        self.assertEqual(cafe_bill([], False), 0)
        self.assertEqual(cafe_bill([], True), 0)


if __name__ == "__main__":
    unittest.main()
