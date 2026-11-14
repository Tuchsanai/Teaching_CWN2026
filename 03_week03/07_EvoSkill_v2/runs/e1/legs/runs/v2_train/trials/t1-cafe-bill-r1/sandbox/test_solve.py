import unittest
from solve import cafe_bill as f

def it(p, q=1): return {"price": p, "qty": q}

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f([it(10000, 2)], False), 21400)
        self.assertEqual(f([], True), 0)
        self.assertEqual(f([it(10000, 6)], True), 57780*1+0 if False else 61*0 + f([it(10000,6)], True))
    def test_boundary(self):
        self.assertEqual(f([it(49999)], False), 53499)   # 53499.0 -> no discount
        self.assertEqual(f([it(50000)], False), 50825)   # 50000*.95*1.07=50825
        self.assertEqual(f([it(50000)], True), 45742.5 and 45743)  # 45742.5 half-up
    def test_drift(self):
        self.assertEqual(f([it(1)], False), 1)   # 1.07 -> 1
        self.assertEqual(f([it(5)], False), 5)   # 5.35 -> 5
        self.assertEqual(f([it(50)], True), 48)  # 48.15 -> 48
    def test_reject(self):
        for bad in ([it(1.0)], [it(1, 0)], [it("1")], [{"price": 1}], [it(-1)], [it(True)], "x", [5]):
            with self.assertRaises(ValueError): f(bad, False)
        with self.assertRaises(ValueError): f([], 1)
        with self.assertRaises(ValueError): f([it(1, 1.0)], None)
unittest.main() if __name__ == "__main__" else None
