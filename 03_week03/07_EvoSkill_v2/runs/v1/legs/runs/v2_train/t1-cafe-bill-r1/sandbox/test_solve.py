import unittest
from fractions import Fraction
from solve import cafe_bill


def ref(sub, member):
    t = Fraction(sub)
    if sub >= 50000:
        t *= Fraction(95, 100)
    if member:
        t *= Fraction(9, 10)
    t *= Fraction(107, 100)
    return int((t * 2 + 1) // 2)


def one(p, q=1):
    return [{"price": p, "qty": q}]


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill(one(4500, 2), False), 9630)

    def test_member(self):
        self.assertEqual(cafe_bill(one(4500, 2), True), 8667)

    def test_discount_both(self):
        self.assertEqual(cafe_bill(one(10000, 6), True), ref(60000, True))

    def test_empty(self):
        self.assertEqual(cafe_bill([], True), 0)


class Boundary(unittest.TestCase):
    def test_edges(self):
        self.assertEqual(cafe_bill(one(49999), False), ref(49999, False))
        self.assertEqual(cafe_bill(one(50000), False), ref(50000, False))
        self.assertEqual(cafe_bill(one(50000), False), 50825)
        self.assertEqual(cafe_bill(one(49999), False), 53499)


class NoDrift(unittest.TestCase):
    def test_many(self):
        for s in range(1, 300):
            for m in (False, True):
                self.assertEqual(cafe_bill(one(s), m), ref(s, m))
        for s in range(49990, 50010):
            self.assertEqual(cafe_bill(one(s), True), ref(s, True))


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [
            (one(-1), False), (one(100, 0), False), (one(100, -1), False),
            (one(100.0), False), (one("100"), False), (one(True), False),
            (one(100, 1.0), False), (one(100, True), False),
            (one(100), 1), (one(100), 0), (one(100), "yes"), (one(100), None),
            ([{"price": 100}], False), ([{"qty": 1}], False), ([5], False),
            (None, False), ("x", False), ({"price": 1, "qty": 1}, False),
            (one(float("nan")), False),
        ]
        for items, member in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, member)

    def test_reject_before_early_return(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 1}, {"price": "a", "qty": 1}], False)


if __name__ == "__main__":
    unittest.main()
