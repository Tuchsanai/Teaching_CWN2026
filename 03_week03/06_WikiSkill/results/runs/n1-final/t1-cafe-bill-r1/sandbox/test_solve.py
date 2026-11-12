import unittest
from solve import cafe_bill


def I(p, q=1):
    return [{"price": p, "qty": q}]


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill(I(10000, 2), False), 21400)

    def test_boundary_below(self):
        # 49999*1.07 = 53498.93
        self.assertEqual(cafe_bill(I(49999), False), 53499)

    def test_boundary_at(self):
        # 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill(I(50000), False), 50825)
        self.assertEqual(cafe_bill(I(25000, 2), False), 50825)

    def test_half_up(self):
        # 50*1.07 = 53.5 -> 54 (banker's would give 54 too); 150*1.07=160.5 -> 161
        self.assertEqual(cafe_bill(I(150), False), 161)
        self.assertEqual(cafe_bill(I(50), False), 54)

    def test_combined(self):
        # 100000*.95*.9*1.07 = 91485
        self.assertEqual(cafe_bill(I(100000), True), 91485)
        # member below threshold: 10000*.9*1.07 = 9630
        self.assertEqual(cafe_bill(I(10000), True), 9630)

    def test_reject_range(self):
        with self.assertRaises(ValueError):
            cafe_bill(I(100, 0), False)
        with self.assertRaises(ValueError):
            cafe_bill(I(-1), False)
        with self.assertRaises(ValueError):
            cafe_bill({"price": 1, "qty": 1}, False)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            cafe_bill(I(100.0), False)
        with self.assertRaises(ValueError):
            cafe_bill(I(100, 1.0), False)

    def test_reject_bool_or_type(self):
        for bad in (1, "x", None):
            with self.assertRaises(ValueError):
                cafe_bill(I(100), bad)
        with self.assertRaises(ValueError):
            cafe_bill(I(True), False)
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 1}], False)


if __name__ == "__main__":
    unittest.main()
