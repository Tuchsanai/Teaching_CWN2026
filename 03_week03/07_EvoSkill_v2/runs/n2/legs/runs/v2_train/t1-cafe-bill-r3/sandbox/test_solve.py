import unittest
from solve import cafe_bill

def I(p, q=1): return [{"price": p, "qty": q}]

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill(I(10000, 2), False), 21400)
        self.assertEqual(cafe_bill([], False), 0)
    def test_boundary(self):
        self.assertEqual(cafe_bill(I(49999), False), 53499)   # 49999*1.07=53498.93
        self.assertEqual(cafe_bill(I(50000), False), 50825)   # 50000*.95*1.07
    def test_member(self):
        self.assertEqual(cafe_bill(I(10000), True), 9630)
        self.assertEqual(cafe_bill(I(50000), True), 45742.5 and 45743)
    def test_half(self):
        self.assertEqual(cafe_bill(I(50), False), 54)  # 53.5 -> 54
    def test_reject(self):
        for items, m in [(None, False), ([1], False), (I(1.0), False), (I(1, 0), False),
                         (I(-1), False), (I("1"), False), (I(True), False),
                         ([{"price": 1}], False), (I(1), None), (I(1), 1), (I(1, 1.0), False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)
unittest.main() if __name__ == "__main__" else None
