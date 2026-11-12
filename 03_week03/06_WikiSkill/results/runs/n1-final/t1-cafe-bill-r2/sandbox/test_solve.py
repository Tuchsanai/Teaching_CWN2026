import unittest
from solve import cafe_bill


def I(p, q=1):
    return [{"price": p, "qty": q}]


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill(I(100), False), 107)
        self.assertEqual(cafe_bill(I(10000), True), 9630)

    def test_boundary_below(self):
        self.assertEqual(cafe_bill(I(49999), False), 53499)

    def test_boundary_at(self):
        self.assertEqual(cafe_bill(I(50000), False), 50825)
        self.assertEqual(cafe_bill(I(25000, 2), False), 50825)

    def test_half_up(self):
        self.assertEqual(cafe_bill(I(50), False), 54)  # 53.5
        self.assertEqual(cafe_bill(I(50000), True), 45743)  # 45742.5

    def test_combined(self):
        self.assertEqual(cafe_bill(I(50000), True), 45743)

    def test_reject_range(self):
        with self.assertRaises(ValueError):
            cafe_bill(I(100, 0), False)
        with self.assertRaises(ValueError):
            cafe_bill(I(-1), False)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            cafe_bill(I(100.0), False)
        with self.assertRaises(ValueError):
            cafe_bill(I(100, 1.0), False)

    def test_reject_bool_or_type(self):
        with self.assertRaises(ValueError):
            cafe_bill(I(100), 1)
        with self.assertRaises(ValueError):
            cafe_bill(I(True), False)
        with self.assertRaises(ValueError):
            cafe_bill(None, False)
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 1}], False)


if __name__ == "__main__":
    unittest.main()
