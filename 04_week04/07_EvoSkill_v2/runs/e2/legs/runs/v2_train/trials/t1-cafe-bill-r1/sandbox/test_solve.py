import unittest
from solve import cafe_bill

def it(p, q=1):
    return {"price": p, "qty": q}

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([it(10000, 2)], True), 19260)
        self.assertEqual(cafe_bill([], False), 0)
    def test_boundary(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)
        self.assertEqual(cafe_bill([it(50000)], False), 50825)
        self.assertEqual(cafe_bill([it(50001)], False), 50826)
        self.assertEqual(cafe_bill([it(50000)], True), 45743)
    def test_nodrift(self):
        # 50000*.95*1.07 = 50825 exactly? 50825 -> check half-up case
        self.assertEqual(cafe_bill([it(1, 1)], False), 1)
        self.assertEqual(cafe_bill([it(5, 1)], False), 5)  # 5.35
        self.assertEqual(cafe_bill([it(50, 1)], True), 48)  # 48.15
        self.assertIsInstance(cafe_bill([it(333, 3)], True), int)
    def test_reject(self):
        for bad in [([it(100.0)], False), ([it(-1)], False), ([it(100, 0)], False),
                    ([it(100, 1.0)], False), ([it("1")], False), ([it(True)], False),
                    ([{"price": 1}], False), ([it(1)], 1), ([it(1)], None),
                    ("x", False), (None, False), ([5], False)]:
            with self.assertRaises(ValueError):
                cafe_bill(*bad)
if __name__ == "__main__":
    unittest.main()
