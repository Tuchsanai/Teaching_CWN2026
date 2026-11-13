import unittest
from fractions import Fraction

from solve import cafe_bill as fn


def it(p, q=1):
    return {"price": p, "qty": q}


class Normal(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(fn([it(10000, 2)], False), 21400)

    def test_big(self):
        self.assertEqual(fn([it(30000, 2)], False), 60990)

    def test_member(self):
        self.assertEqual(fn([it(10000, 2)], True), 19260)

    def test_empty(self):
        self.assertEqual(fn([], True), 0)


class Boundary(unittest.TestCase):
    def test_edge(self):
        self.assertEqual(fn([it(49999)], False), 53499)
        self.assertEqual(fn([it(50000)], False), 50825)
        self.assertEqual(fn([it(50001)], False), 50826)

    def test_member_edge(self):
        self.assertEqual(fn([it(50000)], True), 45743)  # 45742.5 -> up


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(fn([it(5)], False), 5)  # 5.35 -> 5
        self.assertEqual(fn([it(50)], False), 54)  # 53.5 -> 54

    def test_exact(self):
        for p, q, m in [(12345, 7, True), (333, 3, False), (99999, 1, True)]:
            s = p * q
            x = Fraction(s)
            if s >= 50000:
                x *= Fraction(95, 100)
            if m:
                x *= Fraction(9, 10)
            x *= Fraction(107, 100)
            self.assertEqual(fn([it(p, q)], m), int((x * 2 + 1) // 2))


class Reject(unittest.TestCase):
    def test_bad(self):
        for items, m in [([it(-1)], False), ([it(1.0)], False), ([it("1")], False),
                         ([it(1, 0)], False), ([it(1, True)], False), ([{"price": 1}], False),
                         ([5], False), ("x", False), ([it(1)], 1), ([it(1)], "yes")]:
            with self.assertRaises(ValueError):
                fn(items, m)


if __name__ == "__main__":
    unittest.main()
