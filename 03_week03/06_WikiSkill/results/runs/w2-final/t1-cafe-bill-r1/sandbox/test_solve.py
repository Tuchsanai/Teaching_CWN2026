import unittest
from solve import cafe_bill


def I(p, q=1):
    return [{"price": p, "qty": q}]


class T(unittest.TestCase):
    def test_basic(self):
        # 10000*2=20000 ; *1.07 = 21400
        self.assertEqual(cafe_bill(I(10000, 2), False), 21400)
        # member: 20000*0.9*1.07 = 19260
        self.assertEqual(cafe_bill(I(10000, 2), True), 19260)

    def test_boundary_exact(self):
        # 50000*0.95*1.07 = 50825
        self.assertEqual(cafe_bill(I(50000), False), 50825)

    def test_boundary_below(self):
        # 49999*1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill(I(49999), False), 53499)

    def test_boundary_above(self):
        # 50001*0.95*1.07 = 50826.01.. -> 50826
        self.assertEqual(cafe_bill(I(50001), False), 50826)

    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill(I(50), False), 54)
        # 10*1.07 = 10.7 -> 11 ; 
        self.assertEqual(cafe_bill(I(10), False), 11)

    def test_reject_value(self):
        for bad in (I(-1), I(100, 0), I(100, -2)):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100}], False)

    def test_reject_type(self):
        for bad in (I(100.0), I(100, 1.0), I("100"), I(None), I(True)):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)
        for m in (1, None, "yes"):
            with self.assertRaises(ValueError):
                cafe_bill(I(100), m)
        with self.assertRaises(ValueError):
            cafe_bill(None, False)
        with self.assertRaises(ValueError):
            cafe_bill([5], False)

    def test_zero_or_cap(self):
        self.assertEqual(cafe_bill([], False), 0)
        self.assertEqual(cafe_bill([], True), 0)
        # member + discount: 100000*.95*.9*1.07 = 91485
        self.assertEqual(cafe_bill(I(100000), True), 91485)


if __name__ == "__main__":
    unittest.main()
