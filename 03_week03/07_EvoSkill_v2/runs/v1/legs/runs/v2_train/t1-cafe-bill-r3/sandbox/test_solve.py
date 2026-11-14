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
        self.assertEqual(cafe_bill(one(4500, 2), True), ref(9000, True))

    def test_big_member(self):
        self.assertEqual(cafe_bill(one(30000, 2), True), ref(60000, True))

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)


class Boundary(unittest.TestCase):
    def test_edges(self):
        for s in (49999, 50000, 50001):
            for m in (False, True):
                self.assertEqual(cafe_bill(one(s), m), ref(s, m))
        self.assertGreater(cafe_bill(one(49999), False) , 49999)
        self.assertLess(cafe_bill(one(50000), False), cafe_bill(one(49999), False) + 1000)


class NoDrift(unittest.TestCase):
    def test_many(self):
        for s in range(1, 300):
            for m in (False, True):
                self.assertEqual(cafe_bill(one(s), m), ref(s, m))


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [
            (one(-1), False), (one(100, 0), False), (one(100.0), False),
            (one("100"), False), (one(True), False), (one(100, 1.0), False),
            (one(100), 1), (one(100), None), ("x", False), (None, False),
            ([{"price": 1}], False), ([5], False), (one(100, -2), False),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
