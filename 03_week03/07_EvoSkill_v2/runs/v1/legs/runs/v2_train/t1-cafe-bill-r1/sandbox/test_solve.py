import unittest
from solve import cafe_bill


class Normal(unittest.TestCase):
    def test_basic(self):
        # 4500*2=9000 -> *1.07 = 9630
        self.assertEqual(cafe_bill([{"price": 4500, "qty": 2}], False), 9630)

    def test_member_no_discount5(self):
        # 10000*.9*1.07 = 9630
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_both(self):
        # 60000*.95*.9*1.07 = 54891
        self.assertEqual(cafe_bill([{"price": 30000, "qty": 2}], True), 54891)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)


class Boundary(unittest.TestCase):
    def test_49999(self):
        # 49999*1.07 = 53498.93
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_50000(self):
        # 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 50 *1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_single_rounding(self):
        # 50010*.95=47509.5; *1.07=50835.165 -> 50835
        self.assertEqual(cafe_bill([{"price": 50010, "qty": 1}], False), 50835)


class Reject(unittest.TestCase):
    def bad(self, items, member=False):
        with self.assertRaises(ValueError):
            cafe_bill(items, member)

    def test_cases(self):
        self.bad([{"price": 100, "qty": 0}])
        self.bad([{"price": -1, "qty": 1}])
        self.bad([{"price": 100.0, "qty": 1}])
        self.bad([{"price": "100", "qty": 1}])
        self.bad([{"price": True, "qty": 1}])
        self.bad([{"price": 100}])
        self.bad([{"price": 100, "qty": 1}], 1)
        self.bad("x")
        self.bad([5])


if __name__ == "__main__":
    unittest.main()
