import unittest

from solve import cafe_bill


def one(p, q=1):
    return [{"price": p, "qty": q}]


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cafe_bill(one(10000), False), 10700)

    def test_normal_2(self):
        self.assertEqual(cafe_bill(one(10000), True), 9630)

    def test_normal_3(self):
        self.assertEqual(cafe_bill([{"price": 20000, "qty": 2}, {"price": 5000, "qty": 1}], False), 48150)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(cafe_bill(one(50000), False), 50825)

    def test_boundary_2(self):
        self.assertEqual(cafe_bill(one(49999), False), 53499)

    def test_boundary_3(self):
        self.assertEqual(cafe_bill([], True), 0)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(cafe_bill(one(50), False), 54)  # 53.5 -> 54

    def test_no_drift_2(self):
        self.assertEqual(cafe_bill(one(50000), True), 45743)  # 45742.5 -> 45743

    def test_no_drift_3(self):
        self.assertEqual(cafe_bill(one(49999), True), 48149)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        for bad in (one(-1), one(100, 0), [{"price": 100}], "x", [1]):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            cafe_bill(one(100.0), False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            cafe_bill(one("100"), False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            cafe_bill(one(True), False)
        with self.assertRaises(ValueError):
            cafe_bill(one(100), 1)


if __name__ == "__main__":
    unittest.main()
