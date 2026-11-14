import unittest
from solve import cafe_bill as f

def it(p, q=1): return {"price": p, "qty": q}

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f([it(10000, 2)], False), 21400)
        self.assertEqual(f([it(10000, 2)], True), 19260)
        self.assertEqual(f([], True), 0)
    def test_boundary(self):
        self.assertEqual(f([it(49999)], False), 53499)   # 53498.93
        self.assertEqual(f([it(50000)], False), 50825)   # 50825
        self.assertEqual(f([it(50000)], True), 45743)    # 45742.5 half-up
    def test_nodrift(self):
        self.assertEqual(f([it(1)], False), 1)           # 1.07
        self.assertEqual(f([it(50001)], True), 45743)    # 45743.4..
    def test_reject(self):
        bad = [([it(1, 0)], False), ([it(-1)], False), ([it(1.0)], False),
               ([it(1, True)], False), ([{"price": 1}], False), ([5], False),
               ("x", False), ([it(1)], 1), ([it(1)], None), ([it("3")], False)]
        for a, m in bad:
            with self.assertRaises(ValueError): f(a, m)
unittest.main() if __name__ == "__main__" else None
