import unittest

from solve import cafe_bill as fn


def it(p, q=1):
    return [{"price": p, "qty": q}]


class Normal(unittest.TestCase):
    def test_a(self):
        self.assertEqual(fn(it(10000, 2), False), 21400)

    def test_member(self):
        self.assertEqual(fn(it(10000, 2), True), 19260)

    def test_discount(self):
        # 60000*.95*1.07 = 60990
        self.assertEqual(fn(it(30000, 2), False), 60990)

    def test_both(self):
        # 60000*.95*.9*1.07 = 54891
        self.assertEqual(fn(it(60000), True), 54891)

    def test_empty(self):
        self.assertEqual(fn([], True), 0)


class Boundary(unittest.TestCase):
    def test_edge(self):
        self.assertEqual(fn(it(49999), False), 53499)  # 49999*1.07=53498.93
        self.assertEqual(fn(it(50000), False), 50825)  # 50000*.95*1.07
        self.assertEqual(fn(it(50001), False), 50826)  # 50825.95 -> 50826


class NoDrift(unittest.TestCase):
    def test_half(self):
        self.assertEqual(fn(it(50), False), 54)  # 53.5 -> 54
        self.assertEqual(fn(it(10), True), 10)   # 9.63


class Reject(unittest.TestCase):
    def test_bad(self):
        for items, m in [(it(-1), False), (it(1.0), False), (it("1"), False),
                         (it(100, 0), False), (it(100, True), False),
                         (it(100), 1), ([{"price": 1}], False),
                         ("x", False), ([5], False), (None, False)]:
            with self.assertRaises(ValueError):
                fn(items, m)


if __name__ == "__main__":
    unittest.main()
