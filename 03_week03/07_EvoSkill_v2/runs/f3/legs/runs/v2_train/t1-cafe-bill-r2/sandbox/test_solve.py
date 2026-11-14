import unittest

from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class Normal(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(cafe_bill([it(10000)], False), 10700)

    def test_member(self):
        self.assertEqual(cafe_bill([it(10000)], True), 9630)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)


class Boundary(unittest.TestCase):
    def test_below(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)

    def test_at(self):
        self.assertEqual(cafe_bill([it(50000)], False), 50825)

    def test_multi_item_at(self):
        self.assertEqual(cafe_bill([it(25000, 2)], False), 50825)


class NoDrift(unittest.TestCase):
    def test_half_up_member(self):
        self.assertEqual(cafe_bill([it(1500)], True), 1445)  # 1444.5

    def test_half_up_qty(self):
        self.assertEqual(cafe_bill([it(1500, 3)], True), 4334)  # 4333.5

    def test_discounts_stack_once_rounded(self):
        self.assertEqual(cafe_bill([it(50000)], True), 45743)  # 45742.5


class Reject(unittest.TestCase):
    def test_float(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(100.0)], False)

    def test_str_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(100, "1")], False)

    def test_qty_zero(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(100, 0)], False)

    def test_negative_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(-1)], False)

    def test_bool_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(100, True)], False)

    def test_member_not_bool(self):
        with self.assertRaises(ValueError):
            cafe_bill([], 1)

    def test_structure(self):
        for bad in ("x", None, [1], [{"price": 1}]):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)


if __name__ == "__main__":
    unittest.main()
