import unittest
from solve import cafe_bill as fn


class Normal(unittest.TestCase):
    def test_none(self):
        self.assertEqual(fn([{"price": 10000, "qty": 2}], False), 21400)

    def test_member(self):
        self.assertEqual(fn([{"price": 10000, "qty": 2}], True), 19260)

    def test_both(self):
        self.assertEqual(fn([{"price": 30000, "qty": 2}], True), 54891)

    def test_empty(self):
        self.assertEqual(fn([], True), 0)


class Boundary(unittest.TestCase):
    def test_edges(self):
        self.assertEqual(fn([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(fn([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(fn([{"price": 50001, "qty": 1}], False), 50826)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 50000*.95*1.07 = 50825 ; 10*1.07=10.7 ; 50*1.07=53.5 -> 54
        self.assertEqual(fn([{"price": 50, "qty": 1}], False), 54)
        self.assertEqual(fn([{"price": 10, "qty": 1}], False), 11)


class Reject(unittest.TestCase):
    def test_bad(self):
        ok = [{"price": 100, "qty": 1}]
        for items, m in [(ok, 1), (ok, "yes"), ("x", False), ([1], False),
                         ([{"price": -1, "qty": 1}], False),
                         ([{"price": 1.0, "qty": 1}], False),
                         ([{"price": 100, "qty": 0}], False),
                         ([{"price": 100, "qty": True}], False),
                         ([{"price": 100}], False),
                         ([{"price": "100", "qty": 1}], False)]:
            with self.assertRaises(ValueError):
                fn(items, m)


if __name__ == "__main__":
    unittest.main()
