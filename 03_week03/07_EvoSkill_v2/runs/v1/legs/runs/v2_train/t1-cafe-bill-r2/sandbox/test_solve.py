import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([it(4500, 2)], False), 9630)  # 9000*1.07
    def test_member(self):
        self.assertEqual(cafe_bill([it(4500, 2)], True), 8667)  # 9000*.9*1.07
    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)
    def test_both(self):
        self.assertEqual(cafe_bill([it(60000)], True), 54891)  # 60000*.95*.9*1.07=54891


class Boundary(unittest.TestCase):
    def test_49999(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)  # 53498.93
    def test_50000(self):
        self.assertEqual(cafe_bill([it(50000)], False), 50825)  # 50000*.95*1.07=50825


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([it(50)], False), 54)
    def test_single_round(self):
        # 10*1.07=10.7 -> 11
        self.assertEqual(cafe_bill([it(10)], False), 11)


class Reject(unittest.TestCase):
    def test_bad(self):
        for items, m in [
            ([it(-1)], False), ([it(100, 0)], False), ([it(100.0)], False),
            ([it("1")], False), ([it(True)], False), ([it(100, True)], False),
            ([{"price": 1}], False), ([5], False), ("x", False), (None, False),
            ([it(100)], 1), ([it(100)], None), ([it(100)], "yes"),
        ]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
