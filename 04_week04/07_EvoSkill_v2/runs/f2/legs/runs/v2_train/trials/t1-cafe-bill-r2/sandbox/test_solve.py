import unittest
from solve import cafe_bill


def it(p, q=1):
    return [{"price": p, "qty": q}]


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill(it(10000), False), 10700)

    def test_member(self):
        self.assertEqual(cafe_bill(it(10000), True), 9630)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)


class Boundary(unittest.TestCase):
    def test_threshold(self):
        self.assertEqual(cafe_bill(it(50000), False), 50825)
        self.assertEqual(cafe_bill(it(49999), False), 53499)

    def test_both(self):
        self.assertEqual(cafe_bill(it(50000), True), 45743)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(cafe_bill(it(50), False), 54)  # 53.5 -> 54


class Reject(unittest.TestCase):
    def test_bad(self):
        for items, m in [(it(-1), False), (it(1, 0), False), (it(1.0), False),
                         (it(True), False), ("x", False), ([1], False),
                         ([{"price": 1}], False), (it(1), 1), (it(1), None)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
