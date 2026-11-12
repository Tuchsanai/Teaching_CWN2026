import unittest
from solve import cafe_bill


def I(p, q=1):
    return [{"price": p, "qty": q}]


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill(I(10000, 2), False), 21400)

    def test_boundary_below(self):
        self.assertEqual(cafe_bill(I(49999), False), 53499)  # 49999*1.07=53498.93

    def test_boundary_at(self):
        self.assertEqual(cafe_bill(I(50000), False), 50825)  # 50000*.95*1.07=50825

    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54 (banker's/floor would give 53)
        self.assertEqual(cafe_bill(I(50), False), 54)

    def test_combined(self):
        # 100000*.95*.9*1.07 = 91485
        self.assertEqual(cafe_bill(I(50000, 2), True), 91485)

    def test_reject_range(self):
        for bad in (I(100, 0), I(-1, 1)):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)
        with self.assertRaises(ValueError):
            cafe_bill("x", False)

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
            cafe_bill([{"price": 1}], None)


if __name__ == "__main__":
    unittest.main()
