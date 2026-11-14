import unittest
from fractions import Fraction
from solve import cafe_bill


def ref(sub, member):
    t = Fraction(sub)
    if sub >= 50000:
        t *= Fraction(95, 100)
    if member:
        t *= Fraction(90, 100)
    t *= Fraction(107, 100)
    return int((t * 2 + 1) // 2)


def one(p, q=1):
    return [{"price": p, "qty": q}]


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill(one(4500, 2), False), 9630)

    def test_member(self):
        self.assertEqual(cafe_bill(one(4500, 2), True), ref(9000, True))

    def test_discount_both(self):
        self.assertEqual(cafe_bill(one(10000, 6), True), ref(60000, True))

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)


class Boundary(unittest.TestCase):
    def test_edges(self):
        for s in (49999, 50000, 50001):
            for m in (False, True):
                self.assertEqual(cafe_bill(one(s), m), ref(s, m))
        self.assertLess(cafe_bill(one(50000), False), cafe_bill(one(49999), False))


class NoDrift(unittest.TestCase):
    def test_many(self):
        for s in range(1, 300):
            self.assertEqual(cafe_bill(one(s), True), ref(s, True))
            self.assertEqual(cafe_bill(one(s * 7), False), ref(s * 7, False))


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100, "qty": 0}], False),
            ([{"price": 100.0, "qty": 1}], False),
            ([{"price": "100", "qty": 1}], False),
            ([{"price": True, "qty": 1}], False),
            ([{"price": 100, "qty": 1.0}], False),
            ([{"price": 100}], False),
            ([5], False),
            (None, False),
            (one(100), 1),
            (one(100), None),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
